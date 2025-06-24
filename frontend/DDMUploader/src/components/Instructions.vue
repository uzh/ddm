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
import {computed, ref} from 'vue';
import { useI18n } from 'vue-i18n';
import {Instruction} from "@uploader/types/Instruction";

const { t, locale } = useI18n();

const props = defineProps<{
  instructions: Instruction[];
  componentId: number;
}>();

const currentStep = ref(0);

function stepDown(): void {
  if (currentStep.value > 0) {
    currentStep.value--;
  }
}

function stepUp(): void {
  if (currentStep.value < props.instructions.length - 1) {
    currentStep.value++;
  }
}

function setStep(step: number): void {
  currentStep.value = step;
}

const canStepDown = computed(() => currentStep.value > 0);
const canStepUp = computed(() => currentStep.value < props.instructions.length - 1);
const currentInstruction = computed(() => props.instructions[currentStep.value].text);
</script>

<template>
  <div class="d-flex align-items-center">
    <span class="section-icon"><i class="bi bi-list-ol"></i></span>
    <span class="section-heading">{{ t("instructions.heading") }}</span>
  </div>

  <div class="d-flex flex-row align-items-center carousel">
    <div class="control-container">
      <a v-if="canStepDown"
         @click="stepDown"
         class="control-btn control-prev"
         :class="{ 'btn-disabled': currentStep === 0 }">
        <i class="bi bi-caret-left-fill"></i>
        <span class="visually-hidden">Previous</span>
      </a>
    </div>

    <div class="carousel-inner">
      <transition name="fade" mode="out-in">
        <component :is="'div'" :key="currentStep" class="carousel-item active" v-html="currentInstruction" />
      </transition>
    </div>

    <div class="control-container">
      <a v-if="canStepUp"
         @click="stepUp"
         class="control-btn control-next"
         :class="{ 'btn-disabled': currentStep === props.instructions.length - 1 }">
        <i class="bi bi-caret-right-fill"></i>
        <span class="visually-hidden">Next</span>
      </a>
    </div>

  </div>

  <div class="text-center">

    <template v-for="(i, index) in props.instructions" :key="index">
      <button
        type="button"
        class="step-indicator"
        :class="{ 'active step-indicator-active': index === currentStep }"
        :aria-label="`Slide ${index + 1}`"
        @click="setStep(index)"
      />
    </template>

  </div>
</template>

<style scoped>
.carousel {
  min-height: 250px;
  padding-top: 20px;
}

.control-container {
  width: 3rem;
}

.control-btn {
  background: #f8f9fa;
  color: #4c4c4c;
  border-radius: 50%;
  cursor: pointer;
  display: block;
  width: 3rem;
  height: 3rem;
  outline: 0;
  align-content: center;
  font-size: 1.5rem;
  text-align: center;
}

.control-btn:hover {
  color: black !important;
}

.carousel-inner {
  padding-left: 42px;
  padding-right: 42px;
}
@media (max-width: 768px) {
  .carousel-inner {
    padding-left: 10px;
    padding-right: 10px;
  }
  .control-next,
  .control-prev {
    width: 30px;
    opacity: 0.1;
  }
}
.carousel-item {
  transition: transform 0.3s ease, opacity 0.3s ease-out;
}
.step-indicator {
  height: 0.7rem;
  width: 0.7rem;
  background: #d6d6d6;
  border-radius: 50%;
  border: none;
  margin-left: 5px;
  margin-right: 5px;
}
.step-indicator-active {
  background: #4c4c4c;
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