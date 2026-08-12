<script setup lang="ts">
/**
 * Component: StepIndicator
 *
 * Renders the top step tracker (Instructions/Upload/Review) and the
 * current step's heading. The instructions step is omitted when the
 * uploader has none.
 *
 * Props:
 * - hasInstructions (boolean): Whether to include the instructions step.
 * - currentStep (number): Index of the active step, within activeSteps.
 */

import {computed} from "vue";
import {useI18n} from "vue-i18n";

const { t, locale } = useI18n();  // eslint-disable-line @typescript-eslint/no-unused-vars

const props = defineProps({
  hasInstructions: Boolean,
  currentStep: Number,
})

const INSTRUCTIONS_STEP = 'instructions';
const UPLOAD_STEP = 'upload';
const REVIEW_STEP = 'review-and-consent';

const steps = [
  INSTRUCTIONS_STEP,
  UPLOAD_STEP,
  REVIEW_STEP,
]

const activeSteps = computed(() => {
  if (props.hasInstructions) {
    return steps;
  } else {
    return steps.filter(step => step !== INSTRUCTIONS_STEP);
  }
})

</script>

<template>
  <div class="step-indicator-container row justify-content-center">
    <div class="step-flow-container col col-lg-10">
      <template
        v-for="(step, index) in activeSteps"
        :key="index"
      >
        <div
          class="step-indicator"
          :class="{ active: currentStep === index }"
        >
          <span
            class="step-number"
          >
            {{ index + 1 }}
          </span>
          <span class="step-label">
            {{ t(`step-indicator.${step}`) }}
          </span>
        </div>
        <div
          v-if="index < activeSteps.length - 1"
          class="step-connector d-none d-sm-block"
        />
      </template>
    </div>
  </div>

  <div class="step-heading-container">
    <div class="step-heading-eyebrow">
      {{ t('general.step') }} {{ currentStep + 1 }}
    </div>
    <div class="step-heading">
      <h2 v-if="activeSteps[currentStep] === INSTRUCTIONS_STEP">
        {{ t("instructions.heading") }}
      </h2>
      <h2 v-else-if="activeSteps[currentStep] === UPLOAD_STEP">
        {{ t("file-drop.heading") }}
      </h2>
      <h2 v-else-if="activeSteps[currentStep] === REVIEW_STEP">
        {{ t('feedback.check-data-heading') }}
      </h2>
    </div>
  </div>
</template>

<style scoped>
.step-indicator-container {
  margin-bottom: 50px;
}

.step-flow-container {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
}
.step-indicator {
  padding-left: 10px;
  padding-right: 10px;
  color: grey;
  font-size: 0.8rem;
  font-family: var(--ff-mono), monospace;
}
.step-number {
  border-radius: 50%;
  border: 1px solid var(--lightgrey);
  height: 22px;
  width: 22px;
  color: grey;
  line-height: 20px;
  text-align: center;
  font-size: 0.7rem;
  display: inline-block;
  margin-right: 8px;
}
.step-indicator.active .step-number {
  border: 1px solid var(--ddm-primary-accent) !important;
  color: var(--ddm-primary-accent);
}
.step-indicator.active .step-label {
  color: var(--ddm-primary-accent);
}
.step-label {
  margin-top: 5px;
}
.step-connector {
  flex: 1;
  height: 1px;
  background: var(--lightgrey);
}
@media (max-width: 767px) {
  .step-flow-container {
    align-items: baseline;
    justify-content: center;
  }

  .step-indicator {
    width: 33%;
  }
}
</style>
