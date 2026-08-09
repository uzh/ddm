<script setup lang="ts">

import { computed, onMounted, onUnmounted, ref } from "vue";
import { useI18n } from "vue-i18n";

const { t, locale } = useI18n();  // eslint-disable-line @typescript-eslint/no-unused-vars

const props = defineProps<{
  currentPage: number;
  pageIndexMap: Map<number, number>;
}>();

const pageCount = computed(() => props.pageIndexMap.size);
const stepSize = computed(() => 100 / props.pageIndexMap.size);
const progressMax = computed(() => (props.pageIndexMap.get(props.currentPage) ?? 0) * stepSize.value);
const progressMin = computed(() => progressMax.value - stepSize.value);

const scrollFraction = ref(0);

function updateScrollProgress() {
  const scrollTop = window.scrollY || document.documentElement.scrollTop;
  const scrollHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;

  scrollFraction.value = scrollHeight > 0
    ? Math.min(Math.max(scrollTop / scrollHeight, 0), 1)
    : 0;
}

const progressWidth = computed(() => {
  const raw = progressMin.value + scrollFraction.value * (progressMax.value - progressMin.value);
  return Math.min(Math.max(raw, 0), 100);
});

// Decompose width into tens / ones / tenths digits -> 0.1% resolution (1000 discrete steps)
const progressClasses = computed(() => {
  const tenths = Math.round(progressWidth.value * 10);
  const tensDigit = Math.floor(tenths / 100);
  const onesDigit = Math.floor(tenths / 10) % 10;
  const tenthsDigit = tenths % 10;

  return [
    `progress-tens-${tensDigit}`,
    `progress-ones-${onesDigit}`,
    `progress-tenths-${tenthsDigit}`,
  ];
});

onMounted(() => {
  window.addEventListener("scroll", updateScrollProgress, { passive: true });
  updateScrollProgress();
});

onUnmounted(() => {
  window.removeEventListener("scroll", updateScrollProgress);
});

</script>

<template>
  <div class="progress-indicator-header ps-2 pe-2">
    {{ t('questionnaire') }} {{ t('page') }} {{ currentPage }}/{{ pageCount }}
  </div>
  <div class="progress-indicator row justify-content-center ps-2 pe-2">
    <div class="progress-flow-container col">
      <div class="progress-container">
        <div
          class="progress-bar"
          :class="progressClasses"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.progress-indicator-header {
  color: grey;
  font-size: 0.8rem;
  font-family: var(--ff-mono), monospace;
}
.progress-indicator {
  position: sticky;
  top: 0;
  padding-top: 10px;
  padding-bottom: 10px;
  z-index: 9999;
  background: var(--bg-color-light);
  color: grey;
  font-size: 0.8rem;
  font-family: var(--ff-mono), monospace;
}

.progress-container {
  width: 100%;
  display: flex;
  flex-direction: column;
  justify-content: start;
  align-items: start;
  border-radius: 3px;
  border: 1px solid var(--border-color-components);
}

.progress-bar {
  height: 8px;
  background-color: var(--ddm-primary);
  border-radius: 3px;
  transition: width 0.05s ease-out;
  width: calc((var(--tens, 0) + var(--ones, 0) + var(--tenths, 0) * 0.1) * 1%);
}

/* Tens digit: 0, 10, 20 ... 100 */
.progress-tens-0  { --tens: 0; }
.progress-tens-1  { --tens: 10; }
.progress-tens-2  { --tens: 20; }
.progress-tens-3  { --tens: 30; }
.progress-tens-4  { --tens: 40; }
.progress-tens-5  { --tens: 50; }
.progress-tens-6  { --tens: 60; }
.progress-tens-7  { --tens: 70; }
.progress-tens-8  { --tens: 80; }
.progress-tens-9  { --tens: 90; }
.progress-tens-10 { --tens: 100; }

/* Ones digit: 0-9 */
.progress-ones-0 { --ones: 0; }
.progress-ones-1 { --ones: 1; }
.progress-ones-2 { --ones: 2; }
.progress-ones-3 { --ones: 3; }
.progress-ones-4 { --ones: 4; }
.progress-ones-5 { --ones: 5; }
.progress-ones-6 { --ones: 6; }
.progress-ones-7 { --ones: 7; }
.progress-ones-8 { --ones: 8; }
.progress-ones-9 { --ones: 9; }

/* Tenths digit: 0-9, each worth 0.1% */
.progress-tenths-0 { --tenths: 0; }
.progress-tenths-1 { --tenths: 1; }
.progress-tenths-2 { --tenths: 2; }
.progress-tenths-3 { --tenths: 3; }
.progress-tenths-4 { --tenths: 4; }
.progress-tenths-5 { --tenths: 5; }
.progress-tenths-6 { --tenths: 6; }
.progress-tenths-7 { --tenths: 7; }
.progress-tenths-8 { --tenths: 8; }
.progress-tenths-9 { --tenths: 9; }

</style>
