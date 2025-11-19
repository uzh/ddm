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
 * - `actionUrl` (String): Backend endpoint to POST responses to.
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

import type {QuestionnaireConfig, FilterConfig, Responses} from '@questionnaire/types/questionnaire';

const props = defineProps<{
  questionnaireConfigAsString: string,
  filterConfigAsString: string,
  staticVariables: string,
  actionUrl: string,
  language: string
}>();

// Initialize core configuration and data structures.
const questionnaireConfig = ref<QuestionnaireConfig>(JSON.parse(props.questionnaireConfigAsString));
const missingValue: string = '-99';
const missingFilteredValue: string = '-77';
const questionItemMap: Record<string, string[]> = initializeQuestionItemMap(questionnaireConfig.value);
const responses = ref<Responses>(initializeResponses(questionnaireConfig.value));
const staticVariables: Record<string, string | number> = JSON.parse(props.staticVariables);

// Initialize filtering functionality.
const filterConfig = ref<FilterConfig>(JSON.parse(props.filterConfigAsString));
const hideObjectDict = ref<Record<string, boolean>>({});
const {
  evaluateFilters,
  checkIfAllItemsHidden } = useFilterEngine(filterConfig, responses, staticVariables, hideObjectDict, questionItemMap);

// Page navigation.
const questionnaireRoot = ref<HTMLElement | null>(null);
const {
  currentPage,
  lastPageSubmitted,
  next
} = usePageNavigation(questionnaireConfig, hideObjectDict, responses, questionItemMap, missingValue, questionnaireRoot);
const { scrollToTop } = useScrollHandler(questionnaireRoot)

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

watch(() => props.language, (val) => {
  // @ts-ignore
  if (typeof val === 'string' && val.length > 0) {
    // @ts-ignore
    locale.value = val;
  }
});

/**
 * Builds a mapping from each question ID to its associated item IDs.
 *
 * Iterates over the questionnaire configuration and creates a dictionary where
 * each key is a `question_id`, and the value is an array of `item_id`s belonging to that question.
 * If a question has no items, the value will be an empty array.
 *
 * @param questionnaireConfig - The full questionnaire structure containing questions and optional items.
 * @returns A map of question IDs to arrays of their corresponding item IDs.
 */
function initializeQuestionItemMap(questionnaireConfig: QuestionnaireConfig) {
  const questionItemMap: Record<string, string[]> = {};
  questionnaireConfig.forEach((q) => {
    questionItemMap[q.question] = [];
    q.items.forEach((i) => {
      questionItemMap[q.question].push(i.id);
    })
  })
  return questionItemMap;
}

/**
 * Initializes the response object based on the received questionnaire configuration.
 *
 * Returns a flat map of response placeholders, with keys for both question IDs
 * and item IDs (if present). All values are initialized to the sentinel string '-99',
 * representing unanswered or uninitialized state.
 *
 * @param questionnaireConfig - The full questionnaire structure containing questions and items.
 * @returns A Record mapping each question and item ID to '-99'.
 */
function initializeResponses(questionnaireConfig: QuestionnaireConfig) {
  const responses: Responses = {};
  questionnaireConfig.forEach((q) => {
    if (q.type === 'single_choice') {
      responses[q.question] = missingValue;
    }

    else if (q.type === 'transition') {
      // skip.
    }

    else if (q.type === 'open') {
      if (q.options.multi_item_response === true) {
        q.items.forEach((i) => responses[i.id] = missingValue);
      } else {
        responses[q.question] = missingValue;
      }
    }

    else if (q.type === 'multi_choice') {
      q.items.forEach((i) => responses[i.id] = 0);
    }

    else {
      q.items.forEach((i) => responses[i.id] = missingValue);
    }
  })
  return responses;
}

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
      responses.value[key] = missingFilteredValue;
    }

    // If it's a question, mark its items as filtered too.
    if (key.startsWith('question-')) {
      const items = questionItemMap[key] || [];
      items.forEach((itemId) => {
        if (itemId in responses.value) {
          responses.value[itemId] = missingFilteredValue;
        }
      });
    }
  });
}

/**
 * Submits the response data to the backend via a POST request using FormData.
 *
 * - Serializes `responses` and `questionnaireConfig` as JSON and sends it in "post_data".
 * - Includes CSRF token from the DOM for security.
 * - If the response triggers a redirect, it navigates to the new URL.
 */
function submitData() {
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

  fetch(props.actionUrl, {
    method: "POST",
    body: form
  } as RequestInit)
    .then(res => {
      if (res.redirected) {
        window.location.href = res.url;
      }
    })
    .catch(err => console.error("Submit error:", err));
}

function clickOnNextPage() {
  evaluateFilters();
  checkIfAllItemsHidden();   // To make sure filters are evaluated and questions hidden, even when all items are skipped.
  next();
  scrollToTop();
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
</script>

<template>

  <div ref="questionnaireRoot">
    <template v-for="question in questionnaireConfig" :key="question.question">
      <div
        :data-page-index="question.page"
        :data-question-id="question.question"
        ref="questionDivs"
        v-show="currentPage === question.page && !hideObjectDict[question.question]"
        class="question-app-container"
      >
        <div class="question-container">
          <component
            :is="questionTypeMap[question.type]"
            :qid="question.question"
            :text="question.text"
            :items="question.items"
            :scale="question.scale"
            :options="question.options"
            :required="question.required"
            :hideObjectDict="hideObjectDict"
            @responseChanged="updateResponses"
            class="question-body"
          />

        </div>
      </div>
    </template>


    <div class="row flow-navigation">
      <div class="col">
        <button id="next-page-btn" class="flow-btn" type="button" @click="() => { clickOnNextPage(); }">
          {{ t('next-btn-label') }}
          &nbsp;&nbsp;&#8250;
        </button>
      </div>
    </div>
  </div>
</template>
6
<style>
.question-app-container {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  text-align: left;
}

.question-text {
  padding: 60px 10px 15px;
  position: sticky;
  top: 0;
  background: white;
  border-bottom: 3px solid #fbfbfb;
  z-index: 999;
}

.response-body {
  padding-top: 15px;
  padding-left: 10px;
  padding-right: 10px;
}

.question-container {
  font-size: 1rem;
  border-bottom: 2px solid #b8b8b8;
  padding-bottom: 100px;
}

.question-body {
  text-align: center;
  min-height: 50vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
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

@media (min-width: 769px) {
  .question-body {
    text-align: left;
    padding-left: 25px;
    padding-right: 25px;
  }
}

.flow-navigation {
  padding-top: 50px;
}

.required-but-missing {
  background: #fff3f4 !important;
  border-radius: 5px;
  border: 1px solid #c8270d !important;
  margin-bottom: 10px;
  margin-top: 5px;
}

.required-hint {
  font-size: 0.9rem;
  color: #c51c00;
  display: none;
}

.required-hint.show {
  display: block !important;
}
</style>
