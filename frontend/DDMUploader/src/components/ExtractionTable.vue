<script setup lang="ts">
/**
 * Component: ExtractionTable
 *
 * Displays extracted blueprint data in a paginated, searchable table that can be expanded/collapsed.
 *
 * Features:
 * - Search/filter extracted data entries across all fields (case-insensitive).
 * - Pagination control (next/previous) with dynamic page indicators and automatic page adjustment.
 * - Expand/collapse table to show more or less data with smooth transition animation.
 * - Dynamic table layout that adapts to the available data fields.
 * - Handles empty data gracefully with appropriate messaging.
 *
 * Props:
 * - blueprintOutcome (BlueprintExtractionOutcome): Object containing extraction data for a blueprint,
 *   including extracted data rows and field mappings.
 *
 * Computed:
 * - filteredItems: Data entries that match the current search term.
 * - lowerPosition: Index of the first visible item on the current page.
 * - upperPosition: Index of the last visible item on the current page.
 * - maxPage: Maximum number of pages based on filtered data and page size.
 *
 * Internal State:
 * - pageSize: Number of items displayed per page (defaults to 20).
 * - currentPage: Current page being viewed.
 * - showData: Whether the table is expanded (true) or condensed (false).
 * - searchTerm: Current search filter text.
 *
 * Methods:
 * - nextTablePage(): Navigate to the next page if available.
 * - prevTablePage(): Navigate to the previous page if available.
 * - toggleShowHideData(): Expand or collapse the data table.
 *
 * Dependencies:
 * - vue-i18n for text translations.
 */

import { useI18n } from 'vue-i18n';
import {BlueprintExtractionOutcome} from "@uploader/classes/blueprintExtractionOutcome";
import {computed, Ref, ref, useTemplateRef, watch} from "vue";
import {debounce} from "@uploader/utils/debounce";

const { t, te, locale } = useI18n();

const props = defineProps<{
  blueprintOutcome: BlueprintExtractionOutcome
}>();

const pageSize: number = 20;
const currentPage: Ref<number> = ref(1);
const tableContainer = useTemplateRef('table-container');

const searchTerm: Ref<string> = ref('');
const debouncedSearch: Ref<string> = ref('');
const updateSearch = debounce((value: string) => {
  debouncedSearch.value = value.toLowerCase();
}, 300)

watch(searchTerm, (newValue) => {
  updateSearch(newValue);
});

/**
 * Filters the extracted data based on the current search term.
 *
 * Performs a case-insensitive search across all fields in each data item.
 * If any field contains the search term, the item is included in the results.
 *
 * @returns Array of data items that match the search criteria
 */
const filteredItems = computed(() => {
  const lowercasedSearchTerm = debouncedSearch.value.toLowerCase();
  return props.blueprintOutcome.extractedData.filter(item => {
    // Iterate through all the values of the current item
    for (const key in item) {
      if (Object.prototype.hasOwnProperty.call(item, key)) {
        const value = item[key];
        if (String(value).toLowerCase().includes(lowercasedSearchTerm)) {
          return true; // If any field matches, include the item
        }
      }
    }
    return false; // If no field matches, exclude the item
  });
});

/**
 * Calculates the index of the first item on the current page.
 *
 * @returns Zero-based index of the first visible item
 */
const lowerPosition = computed(() => {
  return Math.max((currentPage.value * pageSize) - pageSize, 0);
})

/**
 * Calculates the index of the last item on the current page.
 *
 * @returns Zero-based index of the last visible item
 */
const upperPosition = computed(() => {
  return Math.min(filteredItems.value.length, lowerPosition.value + pageSize);
})

const maxPage = computed(() => {
  return Math.ceil(filteredItems.value.length / pageSize);
});

watch(
  () => [maxPage.value],
  () => {
    if (currentPage.value > maxPage.value) {
      currentPage.value = maxPage.value;
    }

    if (currentPage.value < 1) {
      currentPage.value = 1;
    }
  },
  { immediate: true, deep: true }
);

const nextTablePage = (): void => {
  if (currentPage.value < maxPage.value) {
    currentPage.value += 1;
    tableContainer.value.scrollTop = 0;
  }
}

const prevTablePage = (): void => {
  if (currentPage.value > 1) {
    currentPage.value -= 1;
    tableContainer.value.scrollTop = 0;
  }
}

const showData: Ref<boolean> = ref(maxPage.value === 1 && upperPosition.value <= 5);

/**
 * Toggles between expanded and condensed table views.
 *
 * When expanded, the table shows all rows up to the page size.
 * When condensed, the table is height-limited and shows a gradient overlay.
 */
const toggleShowHideData = (): void => {
  showData.value = !showData.value;
  tableContainer.value.scrollTop = 0;
  tableContainer.value.scrollLeft = 0;
}

</script>

<template>

  <div class="pb-2">{{ t('extraction-table.donation-info') }}</div>

  <!-- Filter search field -->
  <div v-if="props.blueprintOutcome.extractedData.length > 1">
    <Transition name="slide-down">
      <div v-if="showData"
           class="fs-875 mb-2 pt-3">
        <div>
          <label for="data-search"
               class="visually-hidden">
            {{ t('extraction-table.search-entries') }}
          </label>
          <input
              id="data-search"
              type="text"
              v-model="searchTerm"
              :placeholder="t('extraction-table.search-entries')"
              aria-label="Search data entries"
          >
        </div>

        <div class="pt-2">
          <span v-if="filteredItems.length > 0">{{ t('extraction-table.entry-info', {'lower': lowerPosition + 1, 'upper': upperPosition, 'total': filteredItems.length}) }}</span>
          <span v-else>{{ t('extraction-table.all-filtered') }}</span>

          <span v-if="filteredItems.length < props.blueprintOutcome.extractedData.length"> ({{ props.blueprintOutcome.extractedData.length }} total)</span>
        </div>
      </div>

    </Transition>
  </div>

  <!-- Table of extracted entries. -->
  <div class="table-wrapper fs-875 pb-4"
       :class="{ 'table-condensed': !showData, 'table-expanded': showData}">
    <div ref="table-container"
         class="table-container"
         :class="{'no-scroll': !showData }">
      <table class="table table-sm mb-0">
        <thead>
        <tr>
          <th v-for="value in blueprintOutcome.extractedFieldsMap.values()" :key="value">{{ value }}</th>
        </tr>
        </thead>

        <tbody>
        <tr v-for="row in filteredItems.slice(lowerPosition, upperPosition)" :key="row">
          <template v-for="key in blueprintOutcome.extractedFieldsMap.keys()" :key="key">
            <td v-if="key in row" :key="row">{{ row[key] }}</td>
            <td v-else>–</td>
          </template>
        </tr>
        <tr v-if="filteredItems.length === 0">
          <td class="pb-3 pt-3">{{ t('extraction-table.all-filtered') }}</td>
        </tr>
        </tbody>
      </table>
    </div>

    <!-- Page control buttons -->
    <div v-if="props.blueprintOutcome.extractedData.length > pageSize"
         class="ps-2 pt-2">
      <!-- Prev button -->
      <button
          @click="prevTablePage"
          class="btn btn-pagination btn-sm me-2"
          :disabled="currentPage <= 1"
          aria-label="Previous page"
      >
        <i class="bi bi-chevron-left"></i>
      </button>

      <span>{{ t('extraction-table.page') }} {{currentPage}}/{{Math.max(maxPage, 1)}}</span>

      <!-- Next button -->
      <button
          @click="nextTablePage"
          class="btn btn-pagination btn-sm ms-2"
          :disabled="currentPage >= maxPage"
          aria-label="Next page"
      >
        <i class="bi bi-chevron-right"></i>
      </button>

    </div>
  </div>

  <!-- Expand-table control -->
  <div v-if="maxPage > 1 || (maxPage == 1 && upperPosition > 5)"
       class="show-data-control text-center fs-875 mb-3"
       :class="{ 'control-expanded': showData, 'control-condensed': !showData }">
    <a class="expansion-control-btn"
       :class="{ 'expansion-control-btn-expanded': showData, 'expansion-control-btn-condensed': !showData }"
       @click="toggleShowHideData">
      <template v-if="!showData">
        <span>{{ t('extraction-table.show-data') }}</span>
        <span class="extraction-table-show-arrow"><i class="bi bi-chevron-compact-down"></i></span>
      </template>
      <template v-else-if="showData">
        <span>{{ t('extraction-table.hide-data') }}</span>
        <span class="extraction-table-hide-arrow"><i class="bi bi-chevron-compact-up"></i></span>
      </template>
    </a>
  </div>

</template>

<style scoped>
a:hover {
  color: black !important;
}

.btn-pagination {
  background: #f4f4f4;
  border: none;
  color: black;
}
.btn-active:hover {
  color: black !important;
  background: #cacaca;
}
.btn-muted {
  display: inline-block;
  vertical-align: middle;
}

.table-wrapper {
  width: 100%;
  overflow-x: scroll;
  margin-bottom: 15px;
  display: block;
}
.table-wrapper table {
  table-layout: auto;
  min-width: 100%;
}
.table-wrapper table td {
  max-width: 33%;
  word-break: break-all;
}
.table-wrapper tbody {
  border-top: none;
}
.table-wrapper th {
  position: sticky;
  top: 0;
  z-index: 1;
  background-color: white !important;
  box-shadow: 0 1px black;
  min-width: 200px;
}

.table-container {
  max-height: 400px;
  overflow: auto;
  border-bottom: 2px solid lightgray;
}

.fs-875 {
  font-size: .875rem;
}

.table-condensed {
  max-height: 180px;
  overflow: hidden;
  transition: max-height 0.5s ease-in-out;
}

.table-expanded {
  color: black;
  max-height: 1000px;
  transition: max-height 0.5s ease-in-out;
}

.control-condensed,
.control-expanded {
  z-index: 10;
  border-bottom: 1px solid lightgrey;
}

.control-condensed {
  background: rgb(255, 255, 255);
  background: linear-gradient(180deg, rgba(255,255,255,0) 0%, rgba(255,255,255,1) 90%);
  height: 120px;
  margin-top: -120px;
  padding-top: 80px;
  z-index: 10;
  position: relative;
}
.control-expanded {
  background: white;
  margin-top: 0;
}

.expansion-control-btn {
  background: white;
  border: 1px solid lightgrey;
  border-radius: 5px;
  color: #000000;
  text-decoration: none;
  transform: translateY(24px) translateX(-100px);
  position: absolute;
  z-index: 50;
  width: 200px;
  height: 30px;
  cursor: pointer;
  font-weight: normal;
  padding: 3px 5px 25px 5px;
}

.expansion-control-btn-condensed {
  transform: translateY(24px) translateX(-100px);
}

.expansion-control-btn-expanded {
  transform: translateY(-15px) translateX(-100px);
}

.extraction-table-show-arrow {
  position: absolute;
  bottom: -18px;
  left: 93px;
  color: grey;
}

.extraction-table-hide-arrow {
  position: absolute;
  bottom: 28px;
  left: 93px;
  color: grey;
}

.no-scroll {
  overflow: hidden !important;
}

/* Slide down effect */
.slide-down-enter-active {
  transition: all 0.3s ease-out;
  overflow: hidden;
}

.slide-down-leave-active {
  transition: all 0.3s ease-in;
  overflow: hidden;
}

.slide-down-enter-from,
.slide-down-leave-to {
  transform: translateY(-10px);
  opacity: 0;
  max-height: 0;
}

.slide-down-enter-to,
.slide-down-leave-from{
  transform: translateY(0);
  opacity: 1;
  max-height: 100px;
}
</style>
