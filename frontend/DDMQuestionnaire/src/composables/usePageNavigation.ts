import { onMounted, Ref, ref, watch } from 'vue';

import { QuestionConfig, QuestionnaireConfig, REQUIREMENT_LEVELS } from "@questionnaire/types/questionnaire";
import { usePersistedRef } from './usePersistedRef'

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
  const { state: currentPage, clearProgress: clearCurrentPage } = usePersistedRef(
    'questionnaire-current-page',
    1,
    24 * 60 * 60 * 1000,
    questionnaireConfig.value
  )
  const minPage = ref(1);
  const maxPage = ref(1);
  const pageIndexMap = ref<Map<number, number>>(new Map());
  const lastPageSubmitted = ref(false);
  const displayedSoftRequiredHint = ref<boolean>(false);
  const hardRequiredMissing = ref<boolean>(false);

  // Reset the soft required-hint on page advance.
  watch(currentPage, () => {
    displayedSoftRequiredHint.value = false;
  });

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
    const uniquePages = Array.from(new Set(pages)).sort((a, b) => a - b);
    pageIndexMap.value = new Map(uniquePages.map((page, index) => [page, index + 1]));
    if (pages.length === 0) {
      minPage.value = 0;
      maxPage.value = 0;
    } else {
      minPage.value = Math.min(...pages);
      maxPage.value = Math.max(...pages);
    }
    // Only default currentPage to minPage if it wasn't already restored
    // from persisted state (i.e. it's still at usePersistedRef's default).
    if (currentPage.value < minPage.value || currentPage.value > maxPage.value) {
      currentPage.value = minPage.value;
    }
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
   *
   * @returns {boolean} True if navigation was allowed to proceed, false if it was blocked.
   */
  function next(): boolean {
    if (!canProceedToNextPage()) return false;

    if (currentPage.value === maxPage.value) {
      lastPageSubmitted.value = true;
      return true;
    }
    currentPage.value++;
    const nextValid = foundNextValidPage();
    if (!nextValid || currentPage.value > maxPage.value) {
      lastPageSubmitted.value = true;
    }
    return true;
  }

  /**
   * Determines whether navigation to the next page is allowed.
   *
   * @returns {boolean} True if all required questions have been answered (or,
   * for soft-required ones, the hint has already been shown once on this
   * page), and all answered open questions satisfy their configured
   * length/value bounds.
   */
  function canProceedToNextPage(): boolean {
    const alreadyShownOnThisPage = displayedSoftRequiredHint.value;
    const requiredCheckPassed = checkRequired();
    const requiredOk = requiredCheckPassed || (alreadyShownOnThisPage && !hardRequiredMissing.value);
    const responsesOk = validateResponses();
    return requiredOk && responsesOk;
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
    hardRequiredMissing.value = false;

    // Reset existing required hints.
    root.querySelectorAll("div[id*=answer-], tr[id*=answer-]").forEach(el => el.classList.remove("required-but-missing"));
    root.querySelectorAll(".required-hint").forEach(el => el.classList.remove("show"));

    getActiveQuestions().forEach(q => {
      if (q.requirement_level === REQUIREMENT_LEVELS.NOT_REQUIRED) return;

      // Check if question is hidden/filtered out
      if (hideObjectDict.value[q.question]) return;

      // Check if question has items.
      const items: string[] = questionItemMap[q.question];
      if (items.length === 0) {
        const missing = responses.value[q.question] === MISSING;
        const visible = !hideObjectDict.value[q.question];
        if (missing && visible) {
          missingResponses.push(q.question);
          missingQuestions.add(q.question);
          if (!hardRequiredMissing.value) {
            hardRequiredMissing.value = q.requirement_level === REQUIREMENT_LEVELS.HARD;
          }
        }
      } else {
        items.forEach((item) => {
          const missing = responses.value[item] === MISSING;
          const visible = !hideObjectDict.value[item];
          if (missing && visible) {
            missingResponses.push(item);
            missingQuestions.add(q.question);
            if (!hardRequiredMissing.value) {
              hardRequiredMissing.value = q.requirement_level === REQUIREMENT_LEVELS.HARD;
            }
          }
        })
      }
    });

    if (missingResponses.length === 0) return true;

    // Add visual marks to required but missing elements.
    missingResponses.forEach(r => root.querySelector("#answer-" + r)?.classList.add("required-but-missing"));
    missingResponses.forEach(r => root.querySelector("#required-hint-" + r)?.classList.add("show"));
    displayedSoftRequiredHint.value = true;
    return false;
  }

  /**
   * Checks all open questions on the current page against their configured
   * length (text/email) or value (numbers) bounds, marking any offending
   * inputs and their dedicated hints, mirroring the `validLength`/`validValue`
   * directives so the visual state stays in sync regardless of whether the
   * field was ever blurred.
   *
   * Bounds are only enforced when a response has been entered; missing
   * required responses are handled separately by `checkRequired`.
   *
   * @returns {boolean} True if all answered open questions are within bounds.
   */
  function validateResponses(): boolean {
    const root = rootElement.value;
    if (!root) return true;

    let isValid = true;

    getActiveQuestions().forEach(q => {
      if (q.type !== 'open') return;
      if (hideObjectDict.value[q.question]) return;

      const options = q.options;
      const isNumberInput = options?.input_type === 'numbers';
      const keys = options?.multi_item_response
        ? questionItemMap[q.question] ?? []
        : [q.question];

      keys.forEach((key) => {
        if (hideObjectDict.value[key]) return;

        const input = root.querySelector<HTMLInputElement | HTMLTextAreaElement>(`[name="${key}"]`);
        if (!input) return;

        const value = responses.value[key];
        const hasValue = value !== undefined && value !== missingValue && String(value) !== '';

        const invalidClass = isNumberInput ? 'invalid-value' : 'invalid-length';
        const hintClass = isNumberInput ? 'hint-invalid-value' : 'hint-invalid-length';

        let fieldValid = true;
        if (hasValue) {
          if (isNumberInput) {
            const num = Number(value);
            const min = options?.min_number_value;
            const max = options?.max_number_value;
            fieldValid = (min == null || num >= min) && (max == null || num <= max);
          } else {
            const length = String(value).length;
            const min = options?.min_input_length;
            const max = options?.max_input_length;
            fieldValid = (min == null || length >= min) && (max == null || length <= max);
          }
        }

        input.classList.toggle(invalidClass, !fieldValid);
        const hint = input.parentElement?.querySelector(`.${hintClass}`);
        if (hint instanceof HTMLElement) {
          hint.style.display = fieldValid ? 'none' : 'block';
        }

        if (!fieldValid) isValid = false;
      });
    });

    return isValid;
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
    next,
    clearCurrentPage,
    pageIndexMap,
  };
}
