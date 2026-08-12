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
 * - toggleShowHideData(): Expand or collapse the data table.
 *
 * Dependencies:
 * - vue-i18n for text translations.
 */

import ExtractionTable from "@uploader/components/ExtractionTable.vue";

import { useI18n } from 'vue-i18n';
import {BlueprintExtractionOutcome} from "@uploader/classes/BlueprintExtractionOutcome";
import {Blueprint} from "@uploader/types/Blueprint";
import {computed} from "vue";
import {ExtractionFieldLayout} from "@uploader/types/ExtractionFieldLayout";

const { t, te, locale } = useI18n();  // eslint-disable-line @typescript-eslint/no-unused-vars

const props = defineProps<{
  blueprintOutcome: BlueprintExtractionOutcome,
  blueprint: Blueprint,
  fieldLayout: ExtractionFieldLayout,
}>();

const currentGroup = computed(() => props.fieldLayout.groups[0] ?? { groupId: -1, rows: [] });

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
</script>

<template>
  <div>
    <!-- Preview Table of extracted entries. -->
    <div
      v-if="props.fieldLayout.isGrouped"
      class="table-wrapper preview-table"
    >
      <div
        v-if="props.fieldLayout.groups.length > 0"
        class="pb-2"
      >
        <span class="fw-bold">{{ t('feedback.element') }} 1</span>
      </div>
      <div
        v-if="currentGroupRootValues.length > 0"
        class="group-root-summary mb-2"
      >
        <div
          v-for="entry in currentGroupRootValues"
          :key="entry.label"
          class="group-root-summary-item"
        >
          <span class="variable-label">{{ entry.label }}:</span> {{ entry.value }}
        </div>
        <hr class="mt-2 mb-1">
      </div>
      <div
        ref="table-container"
        class="table-container"
      >
        <ExtractionTable
          :columns="props.fieldLayout.nestedColumns"
          :rows="currentGroup.rows.slice(0, 3)"
        />
      </div>
    </div>

    <div
      v-else
      class="table-wrapper"
    >
      <div
        ref="table-container"
        class="table-container"
      >
        <ExtractionTable
          :columns="blueprintOutcome.extractedFieldsMap"
          :rows="blueprintOutcome.extractedData.slice(0, 3)"
          table-class="preview-table"
        />
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
      :data-bs-target="'#reviewModal' + blueprint.id"
    >
      {{ t('extraction-table.show-complete-list') }}
    </button>
  </div>
</template>

<style scoped>
@import "@uploader/assets/styles/buttons.css";
@import "@uploader/assets/styles/typography.css";

.group-root-summary {
  display: flex;
  flex-direction: column;
  flex-wrap: wrap;
  gap: 4px 16px;
  font-family: var(--ff-mono), monospace;
}
.group-root-summary-item {
  white-space: nowrap;
}
.grouped-entry-container .group-root-summary-item {
  font-size: var(--fs-primary-mono) !important;
}

.modal-button {
  background: none;
  border: none;
  padding: 0;
  cursor: pointer;
  color: var(--ddm-primary-accent);
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
  min-width: 100px;
}
.table-container {
  overflow: auto;
}

.variable-label {
  font-weight: 600;
}
</style>
