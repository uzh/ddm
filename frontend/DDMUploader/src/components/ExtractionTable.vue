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
import {BlueprintExtractionOutcome} from "@uploader/classes/BlueprintExtractionOutcome";
import {computed, Ref, ref, useTemplateRef, watch} from "vue";
import {debounce} from "@uploader/utils/debounce";

const { t, te, locale } = useI18n();  // eslint-disable-line @typescript-eslint/no-unused-vars

const props = defineProps<{
  blueprintId: number,
  blueprintName: string,
  blueprintOutcome: BlueprintExtractionOutcome
}>();

const searchInputId = `data-search-${props.blueprintOutcome.blueprintId}`;

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

watch(
  () => [props.blueprintOutcome.extractedData.length],
  () => {
    showData.value = (maxPage.value === 1 && upperPosition.value <= 5);
  },
  { immediate: true, deep: true }
);
</script>

<template>
  <div>
    <!-- Table of extracted entries. -->
    <div class="table-wrapper preview-table">
      <div
        ref="table-container"
        class="table-container"
      >
        <table class="table table-sm mb-0">
          <thead>
            <tr>
              <th
                v-for="value in blueprintOutcome.extractedFieldsMap.values()"
                :key="value"
              >
                {{ value }}
              </th>
            </tr>
          </thead>

          <tbody>
            <tr
              v-for="row in blueprintOutcome.extractedData.slice(0, 3)"
              :key="row"
            >
              <template
                v-for="key in blueprintOutcome.extractedFieldsMap.keys()"
                :key="key"
              >
                <td
                  v-if="key in row"
                  :key="row"
                >
                  {{ row[key] }}
                </td>
                <td v-else>
                  –
                </td>
              </template>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>

  <div
    v-if="blueprintOutcome.extractedData.length > 3"
    class="pt-2"
  >
    + {{ blueprintOutcome.extractedData.length - 3 }} {{ t('extraction-table.more-entries') }} —
    <button
      type="button"
      class="modal-button"
      data-bs-toggle="modal"
      :data-bs-target="'#reviewModal' + blueprintId"
    >
      {{ t('extraction-table.show-complete-list') }}
    </button>
  </div>

  <!-- Review Modal -->
  <div
    :id="'reviewModal' + blueprintId"
    class="modal"
    tabindex="-1"
  >
    <div class="modal-dialog modal-dialog-centered modal-dialog-scrollable modal-xl modal-fullscreen-lg-down review-modal">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">
            {{ blueprintName }}
          </h5>
          <button
            type="button"
            class="btn-close"
            data-bs-dismiss="modal"
            aria-label="Close"
          />
        </div>
        <div class="modal-body">
          <div>
            {{ t('extraction-table.donation-info') }}
          </div>

          <div>
            <!-- Table of extracted entries. -->
            <div class="table-wrapper table-expanded pt-2">
              <div
                ref="table-container"
                class="table-container"
                :class="{'no-scroll': !showData }"
              >
                <table class="table table-sm review-table mb-0">
                  <thead>
                    <tr>
                      <th
                        v-for="value in blueprintOutcome.extractedFieldsMap.values()"
                        :key="value"
                      >
                        {{ value }}
                      </th>
                    </tr>
                  </thead>

                  <tbody>
                    <tr
                      v-for="row in filteredItems.slice(lowerPosition, upperPosition)"
                      :key="row"
                    >
                      <template
                        v-for="key in blueprintOutcome.extractedFieldsMap.keys()"
                        :key="key"
                      >
                        <td
                          v-if="key in row"
                          :key="row"
                        >
                          {{ row[key] }}
                        </td>
                        <td v-else>
                          –
                        </td>
                      </template>
                    </tr>
                    <tr v-if="filteredItems.length === 0">
                      <td class="pb-3 pt-3">
                        {{ t('extraction-table.all-filtered') }}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <div>
            <div class="page-controls">
              <!-- Page control buttons -->
              <div
                v-if="props.blueprintOutcome.extractedData.length > pageSize"
                class="ps-2 pt-2 text-end text-md-start"
              >
                <!-- Prev button -->
                <button
                  class="ddm-secondary-button button-small me-2"
                  :disabled="currentPage <= 1"
                  aria-label="Previous page"
                  @click="prevTablePage"
                >
                  <i class="bi bi-chevron-left" />
                </button>

                <span>{{ t('extraction-table.page') }} {{ currentPage }}/{{ Math.max(maxPage, 1) }}</span>

                <!-- Next button -->
                <button
                  :disabled="currentPage >= maxPage"
                  class="ddm-secondary-button button-small ms-2"
                  aria-label="Next page"
                  @click="nextTablePage"
                >
                  <i class="bi bi-chevron-right" />
                </button>
              </div>
            </div>
          </div>

          <!-- Filter search field -->
          <div v-if="props.blueprintOutcome.extractedData.length > 1">
            <div class="mb-2 text-end text-md-start pe-2 pt-3">
              <div>
                <label
                  :for="searchInputId"
                  class="visually-hidden"
                >
                  {{ t('extraction-table.search-entries') }}
                </label>
                <input
                  :id="searchInputId"
                  v-model="searchTerm"
                  type="text"
                  :placeholder="t('extraction-table.search-entries')"
                  aria-label="Search data entries"
                >
              </div>

              <div class="ps-1 pt-1 pe-2">
                <span v-if="filteredItems.length > 0">{{ t('extraction-table.entry-info', {'lower': lowerPosition + 1, 'upper': upperPosition, 'total': filteredItems.length}) }}</span>
                <span v-else>{{ t('extraction-table.all-filtered') }}</span>

                <span v-if="filteredItems.length < props.blueprintOutcome.extractedData.length"> ({{ props.blueprintOutcome.extractedData.length }} total)</span>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button
            type="button"
            class="ddm-secondary-button"
            data-bs-dismiss="modal"
          >
            {{ t('extraction-table.modal-close') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
@import "@uploader/assets/styles/buttons.css";
@import "@uploader/assets/styles/typography.css";

.preview-table {
  color: var(--font-color-secondary) !important;
  font-size: 0.75rem !important;
}

.review-table th,
.preview-table th {
  text-transform: none;
  font-family: var(--ff-mono), monospace;
  font-weight: normal !important;
  letter-spacing: normal !important;
}

.preview-table td,
.preview-table th {
  box-shadow: none !important;
  color: var(--font-color-secondary) !important;
  font-family: var(--ff-mono), monospace;
  font-size: 0.75rem !important;
}

.review-table th {
  color: var(--font-color-primary) !important;
}

.review-table td {
  font-size: var(--fs-primary-mono) !important;
  font-family: var(--ff-mono), monospace;
}

.modal-button {
  background: none;
  border: none;
  padding: 0;
  cursor: pointer;
  color: var(--ddm-primary-accent);
}

.review-modal,
.review-modal .modal-content {
  max-height: 100vh !important;
  color: var(--font-color-primary) !important;
  font-size: var(--fs-primary) !important;
}

.review-modal .modal-footer {
  border-bottom-left-radius: var(--border-radius);
  border-bottom-right-radius: var(--border-radius);
}

a:hover {
  color: black !important;
}

.table-wrapper {
  width: 100%;
  overflow-x: scroll;
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
  box-shadow: 0 1px black;
  min-width: 200px;
}

.table-container {
  overflow: auto;
}

.table-expanded {
  color: black;
}

.no-scroll {
  overflow: hidden !important;
}
</style>
