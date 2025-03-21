<i18n src="./translations/questionnaire_app.json"></i18n>

<template>
  <template v-for="question in parsedQuestConfig" :key="question.question">
    <div :data-page-index="question.page"
         :data-question-id="question.question"
         ref="questionDivs"
         v-show="currentPage === question.page && !hideObjectDict['question-' + question.question]"
         class="question-app-container">

      <template v-if="question.type === 'single_choice'">
        <div class="question-container">
          <SingleChoiceQuestion
              :qid="question.question"
              :text="question.text"
              :items="question.items"
              :hideObjectDict="this.hideObjectDict"
              @responseChanged="updateResponses"
              class="question-body"
          ></SingleChoiceQuestion>
          <div :id="'required-hint-' + question.question" class="required-hint hidden">{{ $t('required-but-missing-hint') }}</div>
        </div>
      </template>

      <template v-if="question.type === 'multi_choice'">
        <div class="question-container">
          <MultiChoiceQuestion
              :qid="question.question"
              :text="question.text"
              :items="question.items"
              :required="question.required"
              :hideObjectDict="this.hideObjectDict"
              @responseChanged="updateResponses"
              class="question-body"
          ></MultiChoiceQuestion>
          <div :id="'required-hint-' + question.question" class="required-hint hidden">{{ $t('required-but-missing-hint') }}</div>
        </div>
      </template>

      <template v-if="question.type === 'open'">
        <div class="question-container">
          <OpenQuestion
              :qid="question.question"
              :text="question.text"
              :options="question.options"
              :items="question.items"
              :hideObjectDict="this.hideObjectDict"
              @responseChanged="updateResponses"
              class="question-body"
          ></OpenQuestion>
          <div :id="'required-hint-' + question.question" class="required-hint hidden">{{ $t('required-but-missing-hint') }}</div>
        </div>
      </template>

      <template v-if="question.type === 'matrix'">
        <div class="question-container">
          <MatrixQuestion
              :qid="question.question"
              :text="question.text"
              :items="question.items"
              :scale="question.scale"
              :options="question.options"
              :hideObjectDict="this.hideObjectDict"
              @responseChanged="updateResponses"
              class="question-body"
          ></MatrixQuestion>
          <div :id="'required-hint-' + question.question" class="required-hint hidden">{{ $t('required-but-missing-hint') }}</div>
        </div>
      </template>

      <template v-if="question.type === 'semantic_diff'">
        <div class="question-container">
          <SemanticDifferential
              :qid="question.question"
              :text="question.text"
              :items="question.items"
              :scale="question.scale"
              :hideObjectDict="this.hideObjectDict"
              @responseChanged="updateResponses"
              class="question-body"
          ></SemanticDifferential>
          <div :id="'required-hint-' + question.question" class="required-hint hidden">{{ $t('required-but-missing-hint') }}</div>
        </div>
      </template>

      <template v-if="question.type === 'transition'">
        <div class="question-container">
          <TransitionQuestion
              :qid="question.question"
              :text="question.text"
              :hideObjectDict="this.hideObjectDict"
              @responseChanged="updateResponses"
              class="question-body"
          ></TransitionQuestion>
          <div :id="'required-hint-' + question.question" class="required-hint hidden">{{ $t('required-but-missing-hint') }}</div>
        </div>
      </template>

    </div>

  </template>

  <div class="row flow-navigation">
    <div class="col">
      <button
          id="next-page-btn"
          class="flow-btn"
          type="button"
          @click="next(), scrollToTop()"
      >{{ $t('next-btn-label') }}&nbsp;&nbsp;&#8250;</button>
    </div>
  </div>

</template>

<script>
/**
 * Component: QApp
 *
 * The main dynamic questionnaire component.
 *
 * - Renders various question types dynamically based on backend config
 * - Tracks user responses and performs conditional filtering
 * - Supports required-field validation and per-item hiding
 * - Handles page navigation, scroll logic, and form submission
 *
 * Props:
 * - `questionnaireConfig` (String): JSON string of question configuration
 * - `filterConfig` (String): JSON string of filter condition config
 * - `actionUrl` (String): Backend endpoint to POST responses to
 * - `language` (String): Locale code to initialize i18n
 *
 * Emits:
 * - `responseChanged` (from child components)
 *
 * Uses:
 * - i18n integration
 * - Utility functions (`evaluateFilter`, `updateMostVisibleRow`)
 *
 */

import SingleChoiceQuestion from "./components/QuestionSingleChoice.vue";
import MultiChoiceQuestion from "./components/QuestionMultiChoice.vue";
import OpenQuestion from "./components/QuestionOpen.vue";
import MatrixQuestion from "./components/QuestionMatrix.vue";
import SemanticDifferential from "./components/QuestionSemanticDifferential.vue";
import TransitionQuestion from "./components/QuestionTransition.vue";

import {evaluateFilter, evaluateFilterChain} from './utils/filterEvaluation'
import {updateMostVisibleRow} from './utils/scrollFunctions';


export default {
  name: 'QApp',
  components: {
    SingleChoiceQuestion,
    MultiChoiceQuestion,
    OpenQuestion,
    MatrixQuestion,
    SemanticDifferential,
    TransitionQuestion
  },
  props: {
    questionnaireConfig: String,
    filterConfig: String,
    actionUrl: String,
    language: String,
  },
  data() {
    this.$i18n.locale = this.language;
    return {
      parsedQuestConfig: JSON.parse(this.questionnaireConfig),
      parsedFilterConfig: JSON.parse(this.filterConfig),
      responses: {},
      responsesForFilters: {},
      hideObjectDict: {},
      currentPage: 1,
      minPage: 1,
      maxPage: 1,
      locale: this.language,
      displayedRequiredHint: false,
      shouldScroll: window.innerWidth <= 768,
    }
  },
  created() {
    this.setMaxPage();
    this.currentPage = this.minPage;
  },

  mounted() {
    this.boundUpdateMostVisibleRow = () => updateMostVisibleRow(this.shouldScroll);
    window.addEventListener('resize', this.updateScrollSetting);
    window.addEventListener('scroll', this.boundUpdateMostVisibleRow);
    window.addEventListener('load', this.boundUpdateMostVisibleRow);
    window.addEventListener('resize', this.boundUpdateMostVisibleRow);
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.updateScrollSetting);
    window.removeEventListener('scroll', this.boundUpdateMostVisibleRow);
    window.removeEventListener('load', this.boundUpdateMostVisibleRow);
    window.removeEventListener('resize', this.boundUpdateMostVisibleRow);
  },

  watch: {
    locale (val){
      this.$i18n.locale = val
    }
  },
  methods: {
    updateScrollSetting() {
      this.shouldScroll = window.innerWidth <= 768;
    },

    /**
     * Smoothly scrolls the page to the top after the DOM is updated.
     *
     * Uses Vue's `$nextTick()` and a short delay to ensure the scroll occurs
     * after layout/rendering transitions.
     *
     * @returns {void}
     */
    scrollToTop() {
      this.$nextTick(() => {
        setTimeout(() => {
          document.documentElement.scrollTo({
            top: 0,
            behavior: "smooth"
          });

          document.documentElement.scrollTop = 0;
          document.body.scrollTop = 0;
        }, 100);
      });
    },

    /**
     * Updates the stored response for a given question or item and triggers dependent logic.
     *
     * - Stores the latest response data into `this.responses` using the event ID as key.
     * - If the response is not null, updates filter-related state:
     *   - Updates filter response values
     *   - Re-evaluates filters to update visibility
     *   - Checks if all items in a question are hidden
     *
     * @param {Object} e - The event payload containing response data.
     * @param {string|number} e.id - The identifier of the question or item.
     * @param {*} e.response - The actual user response (can be object or primitive).
     * @param {string} e.question - The question ID (may duplicate `e.id` in some contexts).
     * @param {Array|null} e.items - Optional items associated with the question.
     *
     * @returns {void}
     */
    updateResponses(e) {
      this.responses[e.id] = {
        response: e.response,
        question: e.question,
        items: e.items
      };

      if(e.response !== null) {
        this.updateFilterResponses(e);
        this.evaluateFilters();
        this.checkIfAllItemsHidden();
      }
    },

    /**
     * Updates the `responsesForFilters` object based on the response event payload.
     *
     * - If `e.items` is present, responses are assumed to be item-level and keys are prefixed with `item-`.
     * - Otherwise, the response is treated as question-level and prefixed with `question-`.
     *
     * This structure must match the key format expected by backend (Django) filter conditions.
     *
     * @param {Object} e - The event payload.
     * @param {Object} e.response - The user's response(s).
     * @param {Array|null} [e.items] - Optional list of items, indicating item-level response.
     * @param {string|number} e.id - The question ID.
     *
     * @returns {void}
     */
    updateFilterResponses(e) {
      let itemPrefix = "item-";
      let questionPrefix = "question-";

      if(Array.isArray(e.items) && e.items.length > 0) {
        // Add responses related to items.
        Object.entries(e.response).forEach(([key, value]) => {
          const itemKey = `${itemPrefix}${key}`;
          this.responsesForFilters[itemKey] = value;
        });
      } else {
        // Add responses related to questions.
        const questionKey = `${questionPrefix}${e.id}`;
        this.responsesForFilters[questionKey] = e.response;
      }
    },

    /**
     * Evaluates all configured filters and updates the `hideObjectDict` to control visibility.
     *
     * For each key in `parsedFilterConfig`, a set of filters is processed:
     * - If no filters exist, the object remains visible (`false` in `hideObjectDict`).
     * - Otherwise, all filter conditions are evaluated and chained using their combinators (`AND` / `OR`).
     * - The result of this logical chain determines if the object should be hidden.
     *
     * @returns {void}
     */
    evaluateFilters() {
      Object.entries(this.parsedFilterConfig).forEach(([key, filters]) => {
        if (filters.length === 0) {
          this.hideObjectDict[key] = false;
          return;
        }
        let filterChain = []
        let isFirst = true;
        filters.forEach(filter => {
          let response = this.responsesForFilters[filter.source];
          let filterEvaluation = evaluateFilter(response, filter.condition_value, filter.condition_operator)

          // Chain filters together
          if (isFirst) {
            isFirst = false;
          } else {
            filterChain.push(filter.combinator);
          }
          filterChain.push(filterEvaluation);
        })
        if (filterChain.length > 0) {
          this.hideObjectDict[key] = evaluateFilterChain(filterChain);
        } else {
          this.hideObjectDict[key] = filterChain[0];
        }
      });
    },

    /**
     * Checks whether all items of each question are hidden.
     *
     * For each question in `this.responses`, it inspects the visibility
     * of its associated items (via `this.hideObjectDict`). If all items
     * are hidden, it sets the corresponding `question-{id}` key in `hideObjectDict` to `true`.
     *
     * @returns {void}
     */
    checkIfAllItemsHidden() {
      Object.entries(this.responses).forEach(([qid, config]) => {
        const questionKey = `question-${qid}`;
        const items = config.items;

        if (!items || typeof items !== 'object') {
          return;
        }

        const allItemsHidden = Object.values(items).every(item =>
          this.hideObjectDict[`item-${item.id}`] !== false
        );

        if (allItemsHidden) {
          this.hideObjectDict[questionKey] = true;
        }
      })
    },

    /**
     * Computes the minimum and maximum page numbers from `parsedQuestConfig`
     * and stores them in `minPage` and `maxPage`.
     *
     * If no pages are found, both values are set to 0.
     *
     * @returns {void}
     */
    setMaxPage() {
      const pages = this.parsedQuestConfig.map(q => q.page);

      if (pages.length === 0) {
        this.minPage = 0;
        this.maxPage = 0;
        return;
      }

      this.minPage = Math.min(...pages);
      this.maxPage = Math.max(...pages);
    },

    /**
     * Handles advancing to the next valid page or submitting the data if at the end.
     *
     * @returns {void}
     */
    next() {
      if (this.canProceedToNextPage()) {
        if (this.currentPage >= this.maxPage) {
          this.submitData();
          return;
        }

        const nextValidPage = this.advanceToNextValidPage();

        if (!nextValidPage || this.currentPage === this.maxPage) {
          this.submitData();
        }
      }
    },

    /**
     * Determines whether navigation to the next page is allowed.
     *
     * @returns {boolean} True if validation passes or the required hint is showing.
     */
    canProceedToNextPage() {
      return this.displayedRequiredHint || this.checkRequired();
    },

    /**
     * Increments `currentPage` until a valid one is found,
     * or returns false if no valid pages exist.
     *
     * @returns {boolean} True if a valid page was found, false if we went past maxPage.
     */
    advanceToNextValidPage() {
      this.currentPage += 1;

      while (!this.pageIsValid()) {
        this.currentPage += 1;

        if (this.currentPage > this.maxPage) {
          return false;
        }
      }

      return true;
    },

    /**
     * Determines whether the current page is valid for display or progression.
     *
     * A page is considered valid if at least one `.question-app-container` element
     * on the page is not hidden according to `hideObjectDict`.
     *
     * @returns {boolean} True if the page has any visible questions; otherwise false.
     */
    pageIsValid() {
      const rawRefs = this.$refs.questionDivs;
      if (!rawRefs) return false;

      const elementsOnPage = (Array.isArray(rawRefs) ? rawRefs : [rawRefs])
        .filter(el => el.getAttribute("data-page-index") === String(this.currentPage));

      if (elementsOnPage.length === 0) return false;

      const anyVisible = elementsOnPage.some(el => {
        const questionId = el.getAttribute("data-question-id");
        return this.hideObjectDict["question-" + questionId] === false;
      });

      return anyVisible;
    },

    /**
     * Returns an array of question objects that are assigned to the current page.
     *
     * @returns {Array<Object>} The active questions on the current page.
     */
    getActiveQuestions() {
      return this.parsedQuestConfig.filter(q => q.page === this.currentPage);
    },

    /**
     * Checks all required questions on the current page and highlights any that are unanswered.
     *
     * - If a required question or item has a response value of -99 or "-99", and it's not filtered out,
     *   it's considered missing.
     * - Elements with missing responses will be visually marked.
     * - Returns `true` if all required inputs are valid, `false` otherwise.
     *
     * @returns {boolean} Whether all required inputs on the current page have valid responses.
     */
    checkRequired() {
      const MISSING_VALUE = -99;
      const requiredButMissingElement = [];
      const missingQuestionIds = new Set();

      // Clear all prior required field highlights
      document.querySelectorAll("div[id*=answer-], tr[id*=answer-]").forEach(el =>
        el.classList.remove("required-but-missing")
      );
      document.querySelectorAll("div[class*=required-hint]").forEach(el =>
        el.classList.remove("show")
      );

      this.getActiveQuestions().forEach(q => {
        if (!q.required) return;

        const response = this.responses[q.question].response;

        // Check that no response has been provided and that object is not filtered out.
        if (response instanceof Object) {
          for (const i in response) {
            const isMissing = response[i] === MISSING_VALUE || response[i] === String(MISSING_VALUE);
            const isVisible = !this.hideObjectDict["item-" + i];

            if (isMissing && isVisible) {
              requiredButMissingElement.push("item-" + i);
              missingQuestionIds.add(q.question);
            }
          }
        } else {
          const isMissing = response === MISSING_VALUE || response === String(MISSING_VALUE);
          const isVisible = !this.hideObjectDict["question-" + q.question];
          if (isMissing && isVisible) {
            requiredButMissingElement.push(q.question);
            missingQuestionIds.add(q.question);
          }
        }

      })

      if (requiredButMissingElement.length === 0) {
        return true;
      }

      // Highlight missing answers.
      requiredButMissingElement.forEach(e => {
        const el = document.getElementById("answer-" + e);
        if (el) el.classList.add("required-but-missing");
      });

      // Show required hint per question.
      missingQuestionIds.forEach(q => {
        const el = document.getElementById("required-hint-" + q);
        if (el) el.classList.add("show");
      });

      this.displayedRequiredHint = true;
      return false;
    },

    /**
     * Submits the response data to the backend via a POST request using FormData.
     *
     * - Serializes `this.responses` as JSON and sends it as `"post_data"`.
     * - Includes CSRF token from the DOM for security.
     * - If the response triggers a redirect, it navigates to the new URL.
     *
     * @returns {void}
     */
    submitData() {
      const form = new FormData()
      form.append("post_data", JSON.stringify(this.responses));

      const csrf = document.querySelector("input[name='csrfmiddlewaretoken']");
      if (csrf) {
        form.append("csrfmiddlewaretoken", csrf.value);
      } else {
        console.warn("CSRF token not found");
      }

      fetch(this.actionUrl, {
        method: "POST",
        body: form
      })
        .then(response => {
          if (response.redirected) {
            window.location.href = response.url;
          }
        })
        .catch(e => {
          console.error("Form submission failed:", e);
        });
    }
  }
}
</script>

<style>
#qapp {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
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
@media (max-width: 992px) {
  .question-container {
    margin: 0;
  }
}

.question-body {
  text-align: center;
  min-height: 50vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
}
.flow-navigation {
  padding-top: 50px;
  padding-right: 20%;
}
.required-but-missing {
  background: #ff480012 !important;
}
.required-hint {
  font-size: 0.9rem;
  color: #c51c00;
  padding-left: 35px;
  display: none;
}
.show {
  display: block !important;
}
@media (min-width: 769px) {
  .question-body {
    text-align: left;
    padding-left: 25px;
    padding-right: 25px;
  }
}
</style>
