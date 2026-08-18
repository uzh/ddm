<script setup lang="ts">
/**
 * Component: DDM Questionnaire
 *
 * The main dynamic questionnaire component of the DDM.
 *
 * - Renders various question types dynamically based on passed backend config.
 * - Tracks user responses and performs conditional filtering.
 * - Supports required-field validation and per-item hiding.
 * - Handles page navigation, scroll logic, and form submission.
 *
 * Props:
 * - `questionnaireConfig` (String): JSON string of questionnaire configuration.
 * - `filterConfig` (String): JSON string of filter condition configuration.
 * - `staticVariables`: Map of static variables and values passed from backend.
 * - `actionUrl` (String): Backend endpoint to POST final responses to.
 * - `progressUrl` (String): Backend endpoint to POST in-progress responses to
 *   on every page advance.
 * - `language` (String): Locale code to initialize i18n.
 */
import { useI18n } from 'vue-i18n';
const { t, locale } = useI18n();

import { ref, watch } from 'vue';
import { useFilterEngine } from '@questionnaire/composables/useFilterEngine';
import { usePageNavigation } from '@questionnaire/composables/usePageNavigation';
import { useScrollHandler } from '@questionnaire/composables/useScrollHandler';

import SingleChoiceQuestion from '@questionnaire/components/questions/QuestionSingleChoice.vue';
import MultiChoiceQuestion from '@questionnaire/components/questions/QuestionMultiChoice.vue';
import OpenQuestion from '@questionnaire/components/questions/QuestionOpen.vue';
import MatrixQuestion from '@questionnaire/components/questions/QuestionMatrix.vue';
import SemanticDifferential from '@questionnaire/components/questions/QuestionSemanticDifferential.vue';
import TransitionQuestion from '@questionnaire/components/questions/QuestionTransition.vue';

import type { QuestionnaireConfig, FilterConfig, QuestionConfig } from '@questionnaire/types/questionnaire';

import { usePersistedRef } from '@questionnaire/composables/usePersistedRef'

const props = defineProps<{
  questionnaireConfig: QuestionnaireConfig,
  filterConfig: FilterConfig,
  staticVariables: Record<string, string | number>,
  actionUrl: string,
  progressUrl?: string,
  language: string
}>();

// Constants
import { MISSING_VALUE, MISSING_FILTERED_VALUE } from '@questionnaire/constants/missings';

// Derived from props (static)
const questionItemMap: Record<string, string[]> = initializeQuestionItemMap(props.questionnaireConfig);

// Initialize core configuration and data structures.
const questionnaireConfig = ref<QuestionnaireConfig>(props.questionnaireConfig);

const { state: responses, clearProgress: clearResponses } = usePersistedRef(
  'questionnaire-responses',
  initializeResponses(questionnaireConfig.value),
  24 * 60 * 60 * 1000,
  questionnaireConfig.value,
)

// Initialize filtering functionality.
const filterConfig = ref<FilterConfig>(props.filterConfig);
const staticVariables = props.staticVariables;
const hideObjectDict = ref<Record<string, boolean>>({});
const { evaluateFilters, checkIfAllItemsHidden } = useFilterEngine(
    filterConfig,
    responses,
    staticVariables,
    hideObjectDict,
    questionItemMap
);

// Page navigation.
const questionnaireRoot = ref<HTMLElement | null>(null);
const { currentPage, lastPageSubmitted, next, clearCurrentPage, pageIndexMap } = usePageNavigation(
    questionnaireConfig,
    hideObjectDict,
    responses,
    questionItemMap,
    MISSING_VALUE,
    questionnaireRoot
);
const { scrollToTop, scrollToFirstValidationIssue } = useScrollHandler()

watch(lastPageSubmitted, (submitted) => {
  if (submitted) submitData();
});

// Component accessibility in template.
const questionTypeMap: Record<string, any> = {
  single_choice: SingleChoiceQuestion,
  multi_choice: MultiChoiceQuestion,
  open: OpenQuestion,
  matrix: MatrixQuestion,
  semantic_diff: SemanticDifferential,
  transition: TransitionQuestion,
};

const questionMap: Record<number, QuestionConfig> = Object.fromEntries(
  questionnaireConfig.value.map((q) => [q.question, q])
);

watch(() => props.language, (val) => {
  // @ts-ignore
  if (typeof val === 'string' && val.length > 0) {
    // @ts-ignore
    locale.value = val;
  }
});

/**
 * Updates the stored response for a given question or item and triggers dependent logic.
 *
 * - Stores the latest response data into `responses` using the event ID as key.
 * - If the response is not null, updates filter-related state:
 *   - Evaluates filters to update visibility.
 *   - Checks if all items in a question are hidden.
 */
function updateResponses(e: any) {
  responses.value[e.id] = e.response;
  if (e.response !== null) {
    evaluateFilters();
    checkIfAllItemsHidden();
  }
}

/**
 * Updates the response array to mark questions and items that have been filtered out with
 * the default missingFilteredOut value ('-77').
 */
function cleanResponses() {
  const hiddenKeys = Object.keys(hideObjectDict.value).filter(key => hideObjectDict.value[key]);

  hiddenKeys.forEach((key) => {
    // Directly mark the response as filtered out.
    if (key in responses.value) {
      responses.value[key] = MISSING_FILTERED_VALUE;
    }

    // If it's a question, mark its items as filtered too.
    if (key.startsWith('question-')) {
      const items = questionItemMap[key] || [];
      items.forEach((itemId) => {
        if (itemId in responses.value) {
          responses.value[itemId] = MISSING_FILTERED_VALUE;
        }
      });
    }
  });
}

/**
 * Builds the FormData payload shared by both the final submission and the
 * in-progress save: `responses`/`questionnaireConfig` as JSON in "post_data",
 * plus the CSRF token read from the DOM.
 */
function buildPostData(): FormData {
  const form = new FormData();
  cleanResponses();
  form.append(
    'post_data',
    JSON.stringify({
      responses: responses.value,
      questionnaire_config: questionnaireConfig.value
    })
  );

  const csrf = document.querySelector("input[name='csrfmiddlewaretoken']") as HTMLInputElement;
  if (csrf) form.append("csrfmiddlewaretoken", csrf.value);

  return form;
}

/**
 * Submits the response data to the backend via a POST request using FormData.
 *
 * - If the response triggers a redirect, it navigates to the new URL.
 * - Clears the locally cached progress, since the backend now holds the
 *   authoritative final submission.
 */
function submitData() {
  fetch(props.actionUrl, {
    method: "POST",
    body: buildPostData()
  } as RequestInit)
    .then(res => {
      if (res.redirected) {
        window.location.href = res.url;
      }
    })
    .catch(err => console.error("Submit error:", err));

  // Clear cached information.
  clearResponses();
  clearCurrentPage();
}

/**
 * Silently saves responses so far to the backend on a page advance, so
 * progress isn't lost if the participant abandons the questionnaire before
 * reaching the final page. Unlike `submitData()` - it's a background
 * save, not the participant's actual submission.
 */
function submitProgress() {
  if (!props.progressUrl) return;

  fetch(props.progressUrl, {
    method: "POST",
    body: buildPostData()
  } as RequestInit)
    .catch(err => console.error("Progress save error:", err));
}

function clickOnNextPage() {
  evaluateFilters();
  checkIfAllItemsHidden();   // To make sure filters are evaluated and questions hidden, even when all items are skipped.
  const advanced = next();
  if (advanced) {
    if (!lastPageSubmitted.value) submitProgress();
    scrollToTop();
  } else {
    scrollToFirstValidationIssue(questionnaireRoot.value ?? document);
  }
}

// Expose elements for testing.
if (process.env.NODE_ENV === 'test') {
  // @ts-ignore
  window.__expose__ = {
    hideObjectDict,
    responses,
    currentPage
  };
}

// Manage question stickyness
import { useStickyQuestions } from '@questionnaire/composables/useStickyQuestions';
import { initializeQuestionItemMap, initializeResponses } from "@questionnaire/utils/questionnaireInit";
import ProgressIndicator from "@questionnaire/components/ProgressIndicator.vue";

const { questionDivs, isSticky } = useStickyQuestions(questionMap, currentPage, hideObjectDict);

</script>

<template>
  <div
    id="ddm-questionnaire-app"
    ref="questionnaireRoot"
    class="ddm-questionnaire ddm-questionnaire-app"
  >

    <ProgressIndicator
      :current-page="currentPage"
      :page-index-map="pageIndexMap"
    />

    <template
      v-for="question in questionnaireConfig"
      :key="question.question"
    >
      <div
        v-show="currentPage === question.page && !hideObjectDict[question.question]"
        ref="questionDivs"
        :data-page-index="question.page"
        :data-question-id="question.question"
        class="question-app-container"
      >
        <div
          class="sticky-gap-mask"
          :class="{ 'is-active': isSticky[question.question] }"
        />
        <div class="question-container mb-5">
          <component
            :is="questionTypeMap[question.type]"
            :qid="question.question"
            :text="question.text"
            :items="question.items"
            :scale="question.scale"
            :options="question.options"
            :hide-object-dict="hideObjectDict"
            :responses="responses"
            class="question-body"
            :class="{ 'is-sticky': isSticky[question.question] }"
            @response-changed="updateResponses"
          />
          <div
            ref="sentinelRefs"
            class="end-sentinel"
            :data-question-id="question.question"
          />
        </div>
      </div>
    </template>

    <div class="row flow-navigation">
      <div class="col">
        <button
          id="next-page-btn"
          class="flow-btn"
          type="button"
          @click="() => { clickOnNextPage(); }"
        >
          <span class="pe-2">{{ t('next-btn-label') }}</span>
          <i class="step-chevron bi bi-chevron-right"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<style>
@import "@questionnaire/assets/styles/variables.css";
@import "@questionnaire/assets/styles/buttons.css";

.question-app-container {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  text-align: left;
}

.question-container {
  padding-bottom: 20px;
  font-size: 1rem;
  border: var(--border-components);
  background: var(--bg-components);
  border-radius: var(--border-radius-components);
}

.ddm-question {
  display: flex;
  flex-direction: column;
}

.question-body {
  text-align: center;
  display: flex;

  @media (min-width: 769px) {
    text-align: left;
  }
}

.question-text {
  padding: 40px 25px 15px;
  position: static;
  top: 0;
  background: var(--ddm-heading-bg);
  border-top-left-radius: var(--border-radius-components);
  border-top-right-radius: var(--border-radius-components);
  border-bottom: 1px solid var(--border-color-components);
  z-index: 999;
}

.question-body.is-sticky .question-text {
  position: sticky;
  top: 30px;
  border-top: 1px solid var(--border-color-components);
  border-left: 1px solid var(--border-color-components);
  border-right: 1px solid var(--border-color-components);
  margin-left: -1px;
  margin-right: -1px;
  margin-top: -1px;
}

.sticky-gap-mask {
  position: sticky;
  top: 0;
  height: 32px;
  background: var(--ddm-main-bg-color);
  border: 1px solid var(--ddm-main-bg-color);
  z-index: 2;
  visibility: hidden;
  pointer-events: none;
}

.sticky-gap-mask.is-active {
  visibility: visible;
}

.end-sentinel {
  height: 1px;
}

.response-body {
  padding-top: 15px;
  padding-left: 25px;
  padding-right: 25px;

  label {
    font-weight: normal;
  }
}

.prevent-select {
  -webkit-user-select: none;
  -ms-user-select: none;
  user-select: none;
}

@media (max-width: 992px) {
  .question-container {
    margin: 0;
  }
}

.required-but-missing {
  background: #fff3f4 !important;
  border-radius: 5px;
  border: 1px solid var(--ddm-error) !important;
  margin-bottom: 10px;
  margin-top: 5px;
}

.required-hint {
  font-size: 0.9rem;
  color: var(--ddm-error);
  display: none;
}

.required-hint.show {
  display: block !important;
}

input[type="text"],
input[type="email"],
input[type="number"] {
  display: inline-block;
}

.scrolling-overlay {
  filter: grayscale(80%);
  opacity: 0.4;
}
</style>
