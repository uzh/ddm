<script setup lang="ts">
/**
 * Component: Instructions
 *
 * This component displays a step-based instruction carousel.
 *
 * Props:
 * - `instructions`: An array of instruction objects containing HTML-formatted text.
 * - `componentId`: A unique identifier used to scope DOM elements (important for multiple instances).
 *
 * Features:
 * - Uses Bootstrap carousel styles without auto-sliding behavior.
 * - Fully reactive, supports transitions between steps.
 * - Displays step indicator buttons for navigation.
 */
import {computed, ref, useTemplateRef} from 'vue';
import { useI18n } from 'vue-i18n';
import {Instruction} from "@uploader/types/Instruction";

const { t, locale } = useI18n();  // eslint-disable-line @typescript-eslint/no-unused-vars

const props = defineProps<{
  instructions: Instruction[];
  componentId: number;
}>();

const tableContainer = useTemplateRef('instruction-heading');
const currentStep = ref(0);

function stepDown(): void {
  if (currentStep.value > 0) {
    currentStep.value--;
    if (tableContainer.value.getBoundingClientRect().top < 0) {
      tableContainer.value.scrollIntoView();
    }
  }
}

function stepUp(): void {
  if (currentStep.value < props.instructions.length - 1) {
    currentStep.value++;
    if (tableContainer.value.getBoundingClientRect().top < 0) {
      tableContainer.value.scrollIntoView();
    }
  }
}

const canStepDown = computed(() => currentStep.value > 0);
const canStepUp = computed(() => currentStep.value < props.instructions.length - 1);
</script>

<template>
  <div
    ref="instruction-heading"
    class="d-flex align-items-center"
  />

  <div class="instruction-container">
    <div class="instruction-content">
      <div
        v-for="(i, index) in props.instructions"
        v-show="index === currentStep"
        :key="index"
        class="instruction-page"
        v-html="i.text"
      />
    </div>
    <div
      v-if="instructions.length > 1"
      class="instruction-nav"
    >
      <div class="instruction-nav-prev">
        <button
          class="ddm-secondary-button"
          :class="{ 'btn-disabled': currentStep === 0 }"
          :disabled="!canStepDown"
          @click="stepDown"
        >
          <template v-if="canStepDown">
            <i class="step-chevron bi bi-chevron-left" />
            <span class="ps-2">{{ t("instructions.back") }}</span>
          </template>
          <template v-else>
            <span>{{ t("instructions.start") }}</span>
          </template>
        </button>
      </div>

      <div class="instruction-nav-dots">
        <div
          v-for="(i, index) in props.instructions"
          :key="index"
          class="instruction-nav-dot"
          :class="{ 'active': currentStep === index }"
        />
      </div>

      <div class="instruction-nav-next">
        <button
          class="ddm-secondary-button"
          :class="{ 'btn-disabled': currentStep === props.instructions.length - 1 }"
          :disabled="!canStepUp"
          @click="stepUp"
        >
          <template v-if="canStepUp">
            <span class="pe-2">{{ t("instructions.next-page") }}</span>
            <i class="step-chevron bi bi-chevron-right" />
          </template>
          <template v-else>
            <span>{{ t("instructions.end") }}</span>
          </template>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
@import "@uploader/assets/styles/buttons.css";
@import "@uploader/assets/styles/typography.css";

.step-chevron {
  font-size: 0.8rem;
}

.instruction-container {
  border: var(--border-components);
  border-radius: var(--border-radius-components);
  background: var(--bg-components);
}

.instruction-content {
  padding: 25px;
  min-height: 150px;
}

.instruction-page {
  overflow-y: scroll;
}

.instruction-nav {
  border-top: 1px solid var(--lightgrey);
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  padding: 20px;
}

.instruction-nav-dots,
.instruction-nav-next,
.instruction-nav-prev {
  flex: 1;
}
.instruction-nav-next,
.instruction-nav-prev {
  order: 1;
}
.instruction-nav-next {
  text-align: right;
}

.instruction-nav-dots {
  display: flex;
  gap: 6px;
  align-items: center;
  justify-content: center;
  order: 0;
  flex-basis: 100%;
  padding-bottom: 15px;
}
.instruction-nav-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--lightgrey);
  border: none;
  padding: 0;
}
.instruction-nav-dot.active {
  background: var(--ddm-primary-accent);
  width: 16px;
  border-radius: 4px;
}

@media(min-width: 768px) {
  .instruction-nav-dots,
  .instruction-nav-next,
  .instruction-nav-prev {
    order: 1;
  }

  .instruction-nav-dots {
    flex-basis: auto;
    padding-bottom: 0;
  }
}
</style>
