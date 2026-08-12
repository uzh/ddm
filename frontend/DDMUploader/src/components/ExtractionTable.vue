<script setup lang="ts">
/**
 * Component: ExtractionTable
 *
 * Purely presentational table: renders one header per `columns` entry and
 * one row per `rows` item (missing cells show "–"), or `emptyMessage` if
 * `rows` is empty. Used by both ExtractionPreview and ExtractionModal.
 */
defineProps<{
  columns: Map<string, string>,   // key -> label
  rows: Record<string, unknown>[],
  emptyMessage?: string,
  tableClass?: string
}>();
</script>

<template>
  <table
    class="table table-sm mb-0"
    :class="tableClass"
  >
    <thead>
      <tr>
        <th
          v-for="[key, label] in columns"
          :key="key"
        >
          <span class="variable-label pe-1">{{ label }}</span>
        </th>
      </tr>
    </thead>
    <tbody>
      <tr
        v-for="(row, i) in rows"
        :key="i"
      >
        <td
          v-for="[key] in columns"
          :key="key"
        >
          {{ key in row ? row[key] : '–' }}
        </td>
      </tr>
      <tr v-if="rows.length === 0">
        <td class="pb-3 pt-3">
          {{ emptyMessage }}
        </td>
      </tr>
    </tbody>
  </table>
</template>

<style scoped>
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
.variable-label {
  font-weight: 600;
}
</style>
