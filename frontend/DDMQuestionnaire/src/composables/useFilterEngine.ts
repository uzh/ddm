import {onMounted, Ref} from 'vue';
import { evaluateFilter, evaluateFilterChain } from '@questionnaire/utils/filterEvaluation';

import {FilterConfig, Responses} from "@questionnaire/types/questionnaire";

/**
 * Composable handling all logic related to filtering, related visibility, and response mapping.
 *
 * @param filterConfig
 * @param responses - Ref to object storing filterable responses.
 * @param hideObjectDict - Ref to object tracking hidden questions/items.
 * @param questionItemMap - Ref to question-item-map
 */
export function useFilterEngine(
  filterConfig: Ref<FilterConfig>,
  responses: Ref<Responses>,
  hideObjectDict: Ref<Record<string, boolean>>,
  questionItemMap: Record<string, string[]>
) {
  onMounted(() => {
    evaluateFilters();
  });

  /**
   * Evaluates all filter conditions and updates visibility in `hideObjectDict`.
   */
  function evaluateFilters(): void {
    Object.entries(filterConfig.value).forEach(([key, filters]) => {
      if (filters.length === 0) {
        hideObjectDict.value[key] = false;
        return;
      }

      const filterChain: (boolean | 'AND' | 'OR')[] = [];
      let isFirst = true;

      filters.forEach(filter => {
        const response = responses.value[filter.source];
        const evaluation = evaluateFilter(response, filter.condition_value, filter.condition_operator);

        if (!isFirst) {
          filterChain.push(filter.combinator);
        } else {
          isFirst = false;
        }

        filterChain.push(evaluation);
      });

      hideObjectDict.value[key] = evaluateFilterChain(filterChain);
    });
  }

  /**
   * Checks for each question if all its items are hidden and updates question visibility.
   */
  function checkIfAllItemsHidden(): void {
    Object.entries(questionItemMap).forEach(([question, items]) => {
      if (items.length === 0) {
        return;
      }

      const allHidden = items.every((item) => hideObjectDict.value[item] !== false)
      if (allHidden) {
        hideObjectDict.value[question] = true;
      }
    });
  }

  return {
    evaluateFilters,
    checkIfAllItemsHidden,
  };
}
