import {onMounted, Ref, ref} from 'vue';

import {QuestionConfig, QuestionnaireConfig} from "@questionnaire/types/questionnaire";

/**
 * Composable for handling questionnaire page navigation logic.
 *
 * Responsibilities:
 * - Tracks the current, minimum, and maximum pages
 * - Determines if navigation should proceed
 * - Finds next valid page and checks page visibility
 * - Extracts active questions for the current page
 *
 * @param questionnaireConfig - All questions in the questionnaire
 * @param hideObjectDict - Dict controlling visibility of items/questions
 * @param responses - Current response state
 * @param questionItemMap - A map of question IDs to arrays of their corresponding item IDs.
 * @param missingValue - The questionnaire's default missing value.
 * @param rootElement - The root element where the questions are rendered.
 */
export function usePageNavigation(
  questionnaireConfig: Ref<QuestionnaireConfig>,
  hideObjectDict: Ref<Record<string, boolean>>,
  responses: Ref<Record<string, any>>,
  questionItemMap: Record<string, string[]>,
  missingValue: string,
  rootElement: Ref<HTMLElement | null>
) {
  const currentPage = ref(1);
  const minPage = ref(1);
  const maxPage = ref(1);
  const lastPageSubmitted = ref(false);
  const displayedRequiredHint = ref<boolean>(false);

  onMounted(() => {
    setPageInitials();
  });

  /**
   * Computes the minimum and maximum page numbers from `parsedQuestConfig`
   * and stores them in `minPage` and `maxPage`. Also initializes currentPage to minPage.
   *
   * If no pages are found, all values are set to 0.
   */
  function setPageInitials(): void {
    const pages = questionnaireConfig.value.map(q => q.page);
    if (pages.length === 0) {
      minPage.value = 0;
      maxPage.value = 0;
    } else {
      minPage.value = Math.min(...pages);
      maxPage.value = Math.max(...pages);
    }
    currentPage.value = minPage.value;
  }

  /**
   * Returns an array of question objects that are assigned to the current page.
   *
   * @returns {QuestionConfig[]} The active questions on the current page.
   */
  function getActiveQuestions(): QuestionConfig[] {
    return questionnaireConfig.value.filter(q => q.page === currentPage.value);
  }

  /**
   * Handles advancing to the next valid page or signalling that the last page has been reached.
   */
  function next() {
    if (canProceedToNextPage()) {
      if (currentPage.value === maxPage.value) {
        lastPageSubmitted.value = true;
        return;
      }
      currentPage.value++;
      const nextValid = foundNextValidPage();
      if (!nextValid || currentPage.value > maxPage.value) {
        lastPageSubmitted.value = true;
      }
    }
  }

  /**
   * Determines whether navigation to the next page is allowed.
   *
   * @returns {boolean} True if all required questions have been answered or hint has already been shown
   */
  function canProceedToNextPage(): boolean {
    return displayedRequiredHint.value || checkRequired();
  }

  /**
   * Increments `currentPage` until a valid page is found,
   * or returns false if no valid pages exist.
   *
   * @returns {boolean} True if a valid page was found, false if currentPage > maxPage.
   */
  function foundNextValidPage(): boolean {
    while (!currentPageIsValid()) {
      currentPage.value++;
      if (currentPage.value > maxPage.value) {
        return false;
      }
    }
    return true;
  }

  /**
   * Checks all required questions on the current page and highlights any that are unanswered.
   *
   * - Elements with missing responses will be visually marked.
   * - Returns `true` if all required inputs are valid, `false` otherwise.
   */
  function checkRequired(): boolean {
    const MISSING = missingValue;
    const missingResponses: string[] = [];
    const missingQuestions = new Set<string>();
    const root = rootElement.value;

    // Reset existing required hints.
    root.querySelectorAll("div[id*=answer-], tr[id*=answer-]").forEach(el => el.classList.remove("required-but-missing"));
    root.querySelectorAll("div[class*=required-hint]").forEach(el => el.classList.remove("show"));

    getActiveQuestions().forEach(q => {
      if (!q.required) return;

      // Check if question has items.
      const items: string[] = questionItemMap[q.question];
      if (items.length === 0) {
        const missing = responses.value[q.question] === MISSING;
        const visible = !hideObjectDict.value[q.question];
        if (missing && visible) {
          missingResponses.push(q.question);
          missingQuestions.add(q.question);
        }
      } else {
        items.forEach((item) => {
          const missing = responses.value[item] === MISSING;
          const visible = !hideObjectDict.value[item];
          if (missing && visible) {
            missingResponses.push(item);
            missingQuestions.add(q.question);
          }
        })
      }
    });

    if (missingResponses.length === 0) return true;

    // Add visual marks to required but missing elements.
    missingResponses.forEach(r => root.querySelector("#answer-" + r)?.classList.add("required-but-missing"));
    missingResponses.forEach(r => root.querySelector("#required-hint-" + r)?.classList.add("show"));
    displayedRequiredHint.value = true;
    return false;
  }

  /**
   * Determines whether the current page is valid and should be displayed.
   *
   * A page is considered valid if at least one `.question-app-container` element
   * on the page is not hidden according to `hideObjectDict`.
   *
   * @returns {boolean} True if the page has any visible questions; otherwise false.
   */
  function currentPageIsValid(): boolean {
    const root = rootElement.value;
    if (!root) return false;
    const elements = root.querySelectorAll(`[data-page-index='${currentPage.value}']`);

    // Check if page has any questions that should be rendered.
    if (elements.length === 0) return false;

    // Check if not all questions must be hidden due to filter conditions.
    return Array.from(elements).some(el => {
      const questionId = el.getAttribute("data-question-id");
      return hideObjectDict.value[questionId] === false;
    });
  }

  return {
    currentPage,
    lastPageSubmitted,
    next
  };
}
