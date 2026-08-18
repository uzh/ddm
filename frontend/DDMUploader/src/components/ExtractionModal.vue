<script setup lang="ts">
/**
 * Component: ExtractionModal
 *
 * The full-detail modal for reviewing a blueprint's extracted data, opened
 * from ExtractionPreview. In flat mode, shows a single searchable,
 * paginated table. When group_by_root_item is on, shows one root item
 * ("element") at a time with prev/next navigation, a root-value summary, a
 * per-entry search, a cross-entry search that jumps between matches, and
 * (if allowed) a control to exclude the current entry from the donation.
 *
 * Props:
 * - blueprintOutcome (BlueprintExtractionOutcome): Extraction data for the blueprint.
 * - blueprint (Blueprint): The blueprint configuration (used for id/name/nested_entry_exclusion_allowed).
 * - fieldLayout (ExtractionFieldLayout): Grouping/column info computed by ExtractionItem.
 */

import ExtractionTable from "@uploader/components/ExtractionTable.vue";
import {BlueprintExtractionOutcome} from "@uploader/classes/BlueprintExtractionOutcome";
import {Blueprint} from "@uploader/types/Blueprint";
import {useDebouncedSearch} from "@uploader/composables/useDebouncedSearch";
import {useGroupNavigation} from "@uploader/composables/useGroupNavigation";
import {computed, ref, Ref, useTemplateRef, watch} from "vue";
import {usePagination} from "@uploader/composables/usePagination";
import {useTranslation} from "@uploader/composables/useTranslation";
import {EntryGroup} from "@uploader/utils/entryGroup";
import {ExtractionFieldLayout} from "@uploader/types/ExtractionFieldLayout";

const { t, te, locale } = useTranslation();  // eslint-disable-line @typescript-eslint/no-unused-vars

const props = defineProps<{
  blueprintOutcome: BlueprintExtractionOutcome,
  blueprint: Blueprint,
  fieldLayout: ExtractionFieldLayout,
}>();

// Search ----------------------------------------------------------------------

const searchInputId = `data-search-${props.blueprint.id}`;
const { term: searchTerm, debouncedTerm: debouncedSearch } = useDebouncedSearch();

const elementSearchInputId = `element-search-${props.blueprint.id}`;
const { term: elementSearchTerm, debouncedTerm: debouncedElementSearch } = useDebouncedSearch();

const { term: groupSearchTerm, debouncedTerm: debouncedGroupSearch } = useDebouncedSearch();

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

// Group Navigation ------------------------------------------------------------

/**
 * Indices (into `groups`) of entries where at least one row has a field
 * matching the cross-element search term. Empty search matches every entry.
 */
const matchingGroupIndices = computed(() => {
  const term = debouncedElementSearch.value;
  if (!term) return props.fieldLayout.groups.map((_, index) => index);
  return props.fieldLayout.groups.reduce<number[]>((matches, group, index) => {
    const groupMatches = group.rows.some(row =>
      Object.keys(row).some(key => String(row[key]).toLowerCase().includes(term))
    );
    if (groupMatches) matches.push(index);
    return matches;
  }, []);
});

// While a cross-element search term matches at least one entry, navigation
// steps through matches only, skipping non-matching entries in between.
const groupIsFiltered = computed(() => (
  debouncedElementSearch.value.length > 0 && matchingGroupIndices.value.length > 0
));

const groupsRef = computed(() => props.fieldLayout.groups);
const {
  currentIndex: currentGroupIndex,
  currentMatchPosition,
  canGoPrev: canGoPrevGroup,
  canGoNext: canGoNextGroup,
  next: nextGroup,
  prev: prevGroup
} = useGroupNavigation(groupsRef, matchingGroupIndices, groupIsFiltered)

// Reset per-group search state whenever the visible group changes, so a
// filter typed for one entry doesn't silently carry over and hide rows in
// the next one.
watch(currentGroupIndex, () => {
  groupSearchTerm.value = '';
  debouncedGroupSearch.value = '';
});

// Jump to the first matching entry whenever the cross-element search term
// changes, so typing a term takes the researcher straight to it instead of
// only reporting a count while an unrelated entry stays on screen.
watch(debouncedElementSearch, () => {
  if (!debouncedElementSearch.value) return;
  if (matchingGroupIndices.value.length === 0) return;
  if (!matchingGroupIndices.value.includes(currentGroupIndex.value)) {
    currentGroupIndex.value = matchingGroupIndices.value[0];
  }
});

const currentGroup = computed<EntryGroup>(() =>
  props.fieldLayout.groups[currentGroupIndex.value] ?? { groupId: -1, rows: [] }
);

/** The current group's root-level values, taken from its first row (identical across all its rows). */
const currentGroupRootValues = computed(() => {
  const firstRow = currentGroup.value.rows[0] ?? {};
  return props.fieldLayout.rootFieldKeys
    .filter(key => key in firstRow)
    .map(key => ({
      label: props.blueprintOutcome.extractedFieldsMap.get(key),
      value: firstRow[key]
    }));
});

const filteredGroupRows = computed(() => {
  const term = debouncedGroupSearch.value;
  if (!term) return currentGroup.value.rows;
  return currentGroup.value.rows.filter(row => {
    for (const key in row) {
      if (Object.prototype.hasOwnProperty.call(row, key) && String(row[key]).toLowerCase().includes(term)) {
        return true;
      }
    }
    return false;
  });
});

const noGroupsMatchElementSearch = computed(() =>
  debouncedElementSearch.value.length > 0 && matchingGroupIndices.value.length === 0
);

// Pagination ------------------------------------------------------------------

const pageSize: number = 20;
const tableContainer = useTemplateRef('table-container');
const itemCount = computed(() => filteredItems.value.length);
const {
  currentPage,
  maxPage,
  lowerPosition,
  upperPosition,
  next,
  prev
} = usePagination(itemCount, pageSize, tableContainer)

const showData: Ref<boolean> = ref(maxPage.value === 1 && upperPosition.value <= 5);

watch(
  () => [props.blueprintOutcome.extractedData.length],
  () => {
    showData.value = (maxPage.value === 1 && upperPosition.value <= 5);
  },
  { immediate: true, deep: true }
);

// Group exclusion from donation -----------------------------------------------

/**
 * Whether the researcher has enabled letting participants exclude
 * individual entries (only meaningful -- and only ever true -- alongside
 * isGrouped, validated server-side).
 */
const isDeletionAllowed = computed(() => !!props.blueprint.nested_entry_exclusion_allowed);

const currentGroupExcluded = computed(() =>
  props.blueprintOutcome.excludedGroupIds.has(currentGroup.value.groupId)
);

const toggleCurrentGroupExclusion = (): void => {
  props.blueprintOutcome.toggleGroupExclusion(currentGroup.value.groupId);
};
</script>

<template>
  <div
    :id="'reviewModal' + blueprint.id"
    class="modal"
    tabindex="-1"
  >
    <div class="modal-dialog modal-dialog-centered modal-dialog-scrollable modal-xl modal-fullscreen-lg-down review-modal">
      <div class="modal-content">
        <div class="modal-header">
          <h6 class="modal-title">
            {{ blueprint.name }}
          </h6>
          <button
            type="button"
            class="btn-close"
            data-bs-dismiss="modal"
            aria-label="Close"
          />
        </div>
        <div class="modal-body">
          <div class="modal-body-intro">
            <div class="modal-body-intro-text">
              {{ t('extraction-table.donation-info') }}
            </div>

            <template v-if="fieldLayout.isGrouped">
              <!-- Grouped top navigation -->
              <div class="modal-body-intro-controls pt-3 pb-1">
                <!-- Entry (group) navigation. -->
                <div
                  v-if="fieldLayout.groups.length > 1 && !noGroupsMatchElementSearch"
                  class="page-controls text-end text-md-start"
                >
                  <div>
                    <button
                      class="ddm-secondary-button button-small me-2 py-1 px-2"
                      :disabled="!canGoPrevGroup"
                      aria-label="Previous entry"
                      @click="prevGroup"
                    >
                      <i class="bi bi-chevron-left" />
                    </button>
                  </div>

                  <div>
                    <span class="navigation-label">
                      {{ t('extraction-table.group-nav', { current: currentMatchPosition + 1 , total: matchingGroupIndices.length }) }}
                    </span>
                  </div>

                  <div>
                    <button
                      :disabled="!canGoNextGroup"
                      class="ddm-secondary-button button-small ms-2 py-1 px-2"
                      aria-label="Next entry"
                      @click="nextGroup"
                    >
                      <i class="bi bi-chevron-right" />
                    </button>
                  </div>
                </div>

                <!-- Filter search field, scoped to the currently visible entry. -->
                <div
                  v-if="currentGroup.rows.length > 1"
                  class="text-end text-md-start group-search-container pt-2 pt-md-0"
                >
                  <div>
                    <label
                      :for="searchInputId"
                      class="visually-hidden"
                    >
                      {{ t('extraction-table.search-entries') }}
                    </label>
                    <input
                      :id="searchInputId"
                      v-model="groupSearchTerm"
                      class="entry-search-input"
                      type="text"
                      :placeholder="t('extraction-table.search-entries-on-element')"
                      aria-label="Search data entries"
                    >
                  </div>

                  <div class="ps-1 pt-1 pe-2 group-search-info group-search-info">
                    <span v-if="filteredGroupRows.length > 0">{{ t('extraction-table.entry-info', {'lower': 1, 'upper': filteredGroupRows.length, 'total': filteredGroupRows.length}) }}</span>
                    <span v-else>{{ t('extraction-table.all-filtered') }}</span>
                  </div>
                </div>
              </div>

              <div class="group-table-top">
                <div
                  v-if="noGroupsMatchElementSearch"
                  class="grouped-entry-container grouped-entry-container-top navigation-label"
                >
                  {{ t('extraction-table.all-filtered') }}
                </div>

                <div
                  v-else
                  class="grouped-entry-container grouped-entry-container-top mt-2"
                >
                  <!-- Entry deletion control -->
                  <div
                    v-if="isDeletionAllowed"
                    class="pt-2 pb-3 entry-deletion-control"
                  >
                    <span
                      v-if="currentGroupExcluded"
                      class="element-removed-note"
                    >{{ t('extraction-table.element-removed') }}</span>
                    <span
                      v-else
                      class="element-kept-note"
                    >{{ t('extraction-table.element-kept') }}</span>

                    <div class="deletion-switch-container">
                      <button
                        type="button"
                        class="ddm-secondary-button exclude-button"
                        :class="{ selected: currentGroupExcluded }"
                        @click="toggleCurrentGroupExclusion"
                      >
                        {{ currentGroupExcluded ? t('extraction-table.restore-element') : t('extraction-table.remove-element') }}
                      </button>
                    </div>
                  </div>

                  <!-- General element information -->
                  <div
                    v-if="currentGroupRootValues.length > 0"
                    class="group-root-summary pt-2"
                  >
                    <div class="pb-2 fw-bold">
                      <h6>{{ t('feedback.element') }} {{ currentGroupIndex + 1 }}</h6>
                    </div>
                    <div
                      v-for="entry in currentGroupRootValues"
                      :key="entry.label"
                      class="group-root-summary-item"
                    >
                      <span class="variable-label">{{ entry.label }}:</span> {{ entry.value }}
                    </div>
                    <hr class="mt-3 mb-2">
                  </div>
                </div>
              </div>
            </template>
          </div>

          <template
            v-if="fieldLayout.isGrouped"
          >
            <!-- Grouped view: one table per root item, navigated one at a time. -->
            <div class="modal-table-wrapper modal-table-wrapper-grouped table-wrapper grouped-entry-container grouped-entry-container-bottom">
              <div
                v-if="!noGroupsMatchElementSearch"
                class="table-wrapper"
                :class="{ 'entry-excluded': currentGroupExcluded }"
              >
                <div class="table-container">
                  <ExtractionTable
                    :columns="fieldLayout.nestedColumns"
                    :rows="filteredGroupRows"
                    :empty-message="t('extraction-table.all-filtered')"
                    table-class="review-table review-table-grouped"
                  />
                </div>
              </div>
            </div>

            <!-- Filter search field across all elements. -->
            <div class="modal-body-bottom">
              <div
                v-if="fieldLayout.groups.length > 1"
                class="mb-2 text-end text-md-start pe-2 pt-3 group-search-container"
              >
                <div>
                  <label
                    :for="elementSearchInputId"
                    class="visually-hidden"
                  >
                    {{ t('extraction-table.search-elements') }}
                  </label>
                  <input
                    :id="elementSearchInputId"
                    v-model="elementSearchTerm"
                    type="text"
                    :placeholder="t('extraction-table.search-elements')"
                    aria-label="Search entries across all elements"
                  >
                </div>

                <div class="ps-1 pt-1 pe-2 group-search-info">
                  <span v-if="matchingGroupIndices.length > 0">{{ t('extraction-table.search-elements-info', { nElements: matchingGroupIndices.length, nTotal: fieldLayout.groups.length }) }}</span>
                  <span v-else>{{ t('extraction-table.all-filtered') }}</span>
                </div>
              </div>
            </div>
          </template>

          <!-- Flat view: a single combined table (unchanged default behavior). -->
          <template v-else>
            <div class="modal-table-wrapper table-wrapper mt-2">
              <!-- Table of extracted entries. -->
              <div
                ref="table-container"
                class="table-container"
                :class="{'no-scroll': !showData }"
              >
                <ExtractionTable
                  :columns="blueprintOutcome.extractedFieldsMap"
                  :rows="filteredItems.slice(lowerPosition, upperPosition)"
                  :empty-message="t('extraction-table.all-filtered')"
                  table-class="review-table"
                />
              </div>
            </div>

            <div class="modal-body-bottom">
              <!-- Page control buttons -->
              <div
                v-if="props.blueprintOutcome.extractedData.length > pageSize"
                class="page-controls ps-2 pt-2 text-end text-md-start"
              >
                <!-- Prev button -->
                <button
                  class="ddm-secondary-button button-small me-2 py-1 px-2"
                  :disabled="currentPage <= 1"
                  aria-label="Previous page"
                  @click="prev"
                >
                  <i class="bi bi-chevron-left" />
                </button>

                <span class="navigation-label">{{ t('extraction-table.page') }} {{ currentPage }}/{{ Math.max(maxPage, 1) }}</span>

                <!-- Next button -->
                <button
                  :disabled="currentPage >= maxPage"
                  class="ddm-secondary-button button-small ms-2 py-1 px-2"
                  aria-label="Next page"
                  @click="next"
                >
                  <i class="bi bi-chevron-right" />
                </button>
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

                  <div class="ps-1 pt-1 pe-2 group-search-info">
                    <span v-if="filteredItems.length > 0">{{ t('extraction-table.entry-info', {'lower': lowerPosition + 1, 'upper': upperPosition, 'total': filteredItems.length}) }}</span>
                    <span v-else>{{ t('extraction-table.all-filtered') }}</span>

                    <span
                      v-if="filteredItems.length < props.blueprintOutcome.extractedData.length"
                      class="ps-1 group-search-info"
                    >
                      ({{ props.blueprintOutcome.extractedData.length }} {{ t('extraction-table.total') }})
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </template>
        </div> <!-- modal-body -->

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
.modal-body {
  overflow: hidden;
  padding: 1rem;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
}

.modal-body-intro,
.modal-body-bottom {
  flex-shrink: 0;
}

.modal-table-wrapper {
  flex: 0 1 auto;
  min-height: 0;
  overflow: auto;
  border-bottom: 1px solid var(--border-color-components);
}

.modal-table-wrapper-grouped {
  border-bottom: none;
}

.modal-table-wrapper-grouped {
  overflow-y: scroll;
  scrollbar-width: thin;
  scrollbar-color: var(--border-color-components, #ccc) transparent;
}

.modal-table-wrapper-grouped::-webkit-scrollbar {
  width: 8px;
}
.modal-table-wrapper-grouped::-webkit-scrollbar-thumb {
  background: var(--border-color-components, #ccc);
  border-radius: 4px;
}

.modal-body-intro-controls {
  display: flex;
  flex-direction: column;
  justify-content: start;
  align-content: center;
  align-items: center;
}

@media (min-width: 576px) {
  .modal-body-intro-controls {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
  }
}

.page-controls {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  max-width: 300px;
}

.entry-search-input {
  margin-top: 0;
  padding: 3px 10px;
  border: 1px solid var(--lightgrey);
  border-radius: var(--border-radius);
  max-width: 300px;
  font-size: var(--fs-secondary);
  display: inline-block;
}

.entry-deletion-control {
  display: flex;
  align-items: center;
  border-bottom: var(--border-components);
  font-size: var(--fs-secondary);
  font-weight: 500;
}

.deletion-switch-container {
  padding-left: 10px;
  margin-left: 10px;
  border-left: 1px solid var(--border-color-components);
}

.exclude-button {
  padding: 5px 10px;
  background: white;
  border-color: var(--border-color-components);
  color: black;
  font-weight: 400;
  font-size: var(--fs-secondary);
}

.element-kept-note {
  color: var(--ddm-consent-agree);
}

.element-removed-note {
  color: var(--ddm-error, #c0392b);
}

.grouped-entry-container {
  padding: 10px 20px;
  background-color: var(--grouped-table-container-bg);
}

.grouped-entry-container-top {
  border-top-left-radius: var(--border-radius-components);
  border-top-right-radius: var(--border-radius-components);
  border-left: var(--border-components);
  border-top: var(--border-components);
  border-right: var(--border-components);
}

.grouped-entry-container-bottom {
  border-bottom-left-radius: var(--border-radius-components);
  border-bottom-right-radius: var(--border-radius-components);
  border-left: var(--border-components);
  border-bottom: var(--border-components);
  border-right: var(--border-components);
  padding-top: 0;
}

.group-search-info {
  font-size: var(--fs-secondary);
  color: var(--font-color-secondary) !important;
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
.variable-label {
  font-weight: 600;
}
.group-filter-info {
  font-size: var(--fs-secondary);
  color: var(--font-color-secondary);
}
.group-root-summary-item {
  font-family: var(--ff-mono), monospace;
  font-size: var(--fs-primary-mono);
  word-wrap: anywhere;
  overflow-wrap: anywhere;
}
.table-wrapper.entry-excluded {
  opacity: 0.45;
}
.navigation-label {
  font-size: var(--fs-secondary);
  color: var(--font-color-secondary);
}
</style>
