<script setup lang="ts">
/**
 * Component: SubmittingOverlay
 *
 * A modal overlay that displays while form data is being submitted to the server.
 * This component provides visual feedback to users during asynchronous operations.
 *
 * Features:
 * - Fullscreen overlay with semi-transparent backdrop
 * - Animated entrance effect
 * - Animated loading indicator with floating dots
 * - Responsive design for different screen sizes
 * - Internationalized message through vue-i18n
 *
 * Usage:
 * This component should be conditionally rendered when a submission process
 * is active. It doesn't accept props or emit events - it's a pure presentational
 * component that should be shown/hidden by its parent.
 *
 * Dependencies:
 * - vue-i18n for translation of the waiting message
 */
import {useI18n} from 'vue-i18n';

const { t, locale } = useI18n();
</script>

<template>
  <div
      class="custom-modal"
      id="processingModal"
      role="dialog"
      aria-modal="true"
      aria-labelledby="loading-message"
      aria-live="assertive"
  >
    <div class="modal-dialog modal-dialog-centered custom-modal-container m-0">
      <div class="modal-content fs-1 text-center custom-modal-content">
        <div id="loading-message" class="p-3 modal-message">{{ t('submitting-modal.submit-wait') }}</div>
        <div class="dot-floating" aria-hidden="true"></div>
      </div>
    </div>
  </div>

  <div class="modal-backdrop"></div>
</template>

<style scoped>
.modal-backdrop {
  position: fixed;
  height: 100%;
  width: 100%;
  background: #959595;
  opacity: .75;
  z-index: 1000;
}
.custom-modal {
  z-index: 2000;
  position: fixed;
  top: 35%;
  left: 0;
  right: 0;
  width: 100%;
}
.custom-modal-container {
  width: 100%;
  max-width: none;
  animation: fade-in-right ease 0.6s forwards;
}
.custom-modal-content {
  background: #212529 !important;
  color: white !important;
  border: none;
  border-radius: 0px;
  font-size: 1.8rem;
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  overflow: hidden;
  padding-bottom: 30px;
  box-shadow: 0 3px #ffffff17;
}

/**
 * Animation: fade-in-right
 *
 * Fades in the modal while sliding it slightly from left to right,
 * creating a smooth entrance effect.
 */
@keyframes fade-in-right {
  from {
    opacity: 0;
    transform: translateX(-15px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.dot-floating {
  position: relative;
  width: 12px;
  height: 12px;
  border-radius: 6px;
  background-color: #009c94;
  color: #009c94;
  animation: dotFloating 3s infinite cubic-bezier(0.15, 0.6, 0.9, 0.1);
}

.dot-floating::before, .dot-floating::after {
  content: '';
  display: inline-block;
  position: absolute;
  top: 0;
}

.dot-floating::before {
  left: -14px;
  width: 12px;
  height: 12px;
  border-radius: 6px;
  background-color: #009c94;
  color: #009c94;
  animation: dotFloatingBefore 3s infinite ease-in-out;
}

.dot-floating::after {
  left: -26px;
  width: 12px;
  height: 12px;
  border-radius: 6px;
  background-color: #009c94;
  color: #009c94;
  animation: dotFloatingAfter 3s infinite cubic-bezier(0.4, 0, 1, 1);
}

@media (min-width: 769px) {
  .custom-modal-content {
    font-size: 2rem;
  }
}

/**
 * Animation: dotFloating, dotFloatingBefore, dotFloatingAfter
 *
 * Creates a three-dot loading animation where dots appear to
 * flow from left to right in a wave-like pattern.
 * The three animations work together to create the complete effect.
 */
@keyframes dotFloating {
  0% {
    left: calc(-50% - 5px);
  }
  75% {
    left: calc(50% + 105px);
  }
  100% {
    left: calc(50% + 105px);
  }
}

@keyframes dotFloatingBefore {
  0% {
    left: -50px;
  }
  50% {
    left: -14px;
  }
  75% {
    left: -50px;
  }
  100% {
    left: -50px;
  }
}

@keyframes dotFloatingAfter {
  0% {
    left: -100px;
  }
  50% {
    left: -26px;
  }
  75% {
    left: -100px;
  }
  100% {
    left: -100px;
  }
}
</style>