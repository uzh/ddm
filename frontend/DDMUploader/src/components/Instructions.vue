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

const { t, locale } = useI18n();

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

function setStep(step: number): void {
  currentStep.value = step;
  if (tableContainer.value.getBoundingClientRect().top < 0) {
    tableContainer.value.scrollIntoView();
  }
}

const canStepDown = computed(() => currentStep.value > 0);
const canStepUp = computed(() => currentStep.value < props.instructions.length - 1);
const currentInstruction = computed(() => props.instructions[currentStep.value].text);
</script>

<template>
  <div class="d-flex align-items-center" ref="instruction-heading">
    <span class="section-icon"><i class="bi bi-list-ol"></i></span>
    <span class="section-heading">{{ t("instructions.heading") }}</span>
  </div>

  <div class="d-flex flex-row align-items-center carousel">
    <div v-if="props.instructions.length > 1"
         class="control-container hidden-small">
    </div>

    <div class="carousel-inner">
      <transition name="fade" mode="out-in">
        <component :is="'div'" :key="currentStep" class="carousel-item active" v-html="currentInstruction" />
      </transition>
    </div>

    <div v-if="props.instructions.length > 1"
         class="control-container hidden-small">
    </div>

  </div>

  <div v-if="props.instructions.length > 1"
       class="text-center d-flex flex-row align-items-center justify-content-center pt-3">

    <div v-if="props.instructions.length > 1"
         class="control-container d-flex justify-content-start">
      <button v-if="canStepDown"
         @click="stepDown"
         class="button grey-button button-small"
         :class="{ 'btn-disabled': currentStep === 0 }">
        <i class="bi bi-chevron-left"></i>
        <span class="visually-hidden">Previous</span>
      </button>
    </div>

    <div class="d-flex flex-wrap flex-row align-items-center justify-content-center">
      <template v-for="(i, index) in props.instructions" :key="index">
        <button
          type="button"
          class="button grey-button button-small m-1"
          :class="{ 'active selected-button': index === currentStep }"
          :aria-label="`Slide ${index + 1}`"
          @click="setStep(index)"
        >
          <span>{{ index + 1 }}</span>
        </button>
      </template>
    </div>

    <div v-if="props.instructions.length > 1"
         class="control-container d-flex justify-content-end">
      <button v-if="canStepUp"
         @click="stepUp"
         class="button grey-button button-small"
         :class="{ 'btn-disabled': currentStep === props.instructions.length - 1 }">
        <i class="bi bi-chevron-right"></i>
        <span class="visually-hidden">Next</span>
      </button>
    </div>

  </div>
</template>

<style scoped>
@import "@uploader/assets/styles/buttons.css";
@import "@uploader/assets/styles/fonts.css";

.carousel {
  min-height: 250px;
  padding-top: 20px;
}

.control-container {
  width: 3rem;
}

.carousel-inner {
  padding-left: 42px;
  padding-right: 42px;
}

@media (min-width: 768px) {
  .small-only {
    display: none !important;
  }
}

@media (max-width: 767px) {
  .hidden-small {
    display: none;
  }

  .carousel-inner {
    padding-left: 10px;
    padding-right: 10px;
  }
}
.carousel-item {
  transition: transform 0.3s ease, opacity 0.3s ease-out;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>