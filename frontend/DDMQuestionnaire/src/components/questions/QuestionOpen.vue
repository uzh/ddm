<script setup lang="ts">
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';

import { Item, QuestionOptions, Responses } from "@questionnaire/types/questionnaire";

const props = defineProps<{
  qid: string;
  text: string;
  options: QuestionOptions;
  items: Item[];
  hideObjectDict: Record<string, boolean>;
  responses: Responses;
}>();

// Constants
import { MISSING_VALUE, MISSING_FILTERED_VALUE } from '@questionnaire/constants/missings';

const emit = defineEmits<{
  (e: 'responseChanged', payload: { id: string; response: string; }): void;
}>();

const { t } = useI18n();

const getMaxLength = computed(() =>
  props.options.max_input_length !== null ? props.options.max_input_length : undefined
);

/**
 * Resolves the display value for a given response id, treating the
 * missing/filtered sentinel values as "nothing entered yet" rather than
 * literal text to show in the input.
 */
function displayValue(id: string): string {
  const raw = props.responses[id];
  if (raw === MISSING_VALUE || raw === MISSING_FILTERED_VALUE) return '';
  return String(raw ?? '');
}

function responseChanged(event: Event) {
  const target = event.target as HTMLInputElement;
  emit('responseChanged', {
    id: target.name,
    response: target.value,
  });
}
</script>

<template>
  <div class="ddm-question ddm-question--open">
    <div
      class="question-text"
      v-html="props.text"
    />

    <div
      v-if="!props.options.multi_item_response"
      :id="'answer-' + props.qid"
      class="response-body"
    >
      <template v-if="props.options.input_type === 'text'">
        <input
          v-if="props.options.display === 'small'"
          class="oq-input"
          type="text"
          :name="props.qid"
          :maxlength="getMaxLength"
          :value="displayValue(props.qid)"
          @change="responseChanged"
        >
        <textarea
          v-if="props.options.display === 'large'"
          class="open-question-textarea"
          :name="props.qid"
          :maxlength="getMaxLength"
          :value="displayValue(props.qid)"
          placeholder="|"
          @change="responseChanged"
        />
        <p
          :id="'required-hint-' + props.qid"
          class="required-hint mb-0"
        >
          {{ t('required-but-missing-hint') }}
        </p>
      </template>

      <template v-else-if="props.options.input_type === 'numbers'">
        <input
          v-only-digits
          type="text"
          class="oq-input"
          :name="props.qid"
          :maxlength="getMaxLength"
          :value="displayValue(props.qid)"
          @change="responseChanged"
        >
        <p class="input-hint">
          {{ t('hint-number-input') }}
        </p>
        <p
          :id="'required-hint-' + props.qid"
          class="required-hint mb-0"
        >
          {{ t('required-but-missing-hint') }}
        </p>
      </template>

      <template v-else-if="props.options.input_type === 'email'">
        <input
          v-valid-email
          type="email"
          class="oq-input"
          :name="props.qid"
          :maxlength="getMaxLength"
          :value="displayValue(props.qid)"
          @change="responseChanged"
        >
        <p class="input-hint hint-invalid-input pb-0 mb-0">
          {{ t('hint-invalid-email') }}
        </p>
        <p class="input-hint">
          {{ t('hint-email-input') }}
        </p>
        <p
          :id="'required-hint-' + props.qid"
          class="required-hint mb-0"
        >
          {{ t('required-but-missing-hint') }}
        </p>
      </template>
    </div>

    <div
      v-if="props.options.multi_item_response"
      :id="'answer-' + props.qid"
      class="response-body"
    >
      <div
        v-for="item in props.items"
        v-show="!props.hideObjectDict[item.id]"
        :id="'answer-' + item.id"
        :key="item.id"
        class="input-row"
      >
        <div v-html="item.label" />
        <div>
          <template v-if="props.options.input_type === 'text'">
            <input
              v-if="props.options.display === 'small'"
              class="oq-input"
              type="text"
              :name="item.id"
              :maxlength="getMaxLength"
              :value="displayValue(item.id)"
              @change="responseChanged"
            >
            <textarea
              v-if="props.options.display === 'large'"
              class="open-question-textarea"
              :name="item.id"
              :maxlength="getMaxLength"
              :value="displayValue(item.id)"
              placeholder="|"
              @change="responseChanged"
            />
          </template>

          <template v-else-if="props.options.input_type === 'numbers'">
            <input
              type="text"
              class="oq-input"
              v-only-digits
              :name="item.id"
              :maxlength="getMaxLength"
              :value="displayValue(item.id)"
              @change="responseChanged"
            >
            <p class="input-hint">
              {{ t('hint-number-input') }}
            </p>
          </template>

          <template v-else-if="props.options.input_type === 'email'">
            <input
              v-valid-email
              type="email"
              class="oq-input"
              :name="item.id"
              :maxlength="getMaxLength"
              :value="displayValue(item.id)"
              @change="responseChanged"
            >
            <p class="input-hint hint-invalid-input pb-0 mb-0">
              {{ t('hint-invalid-email') }}
            </p>
            <p class="input-hint">
              {{ t('hint-email-input') }}
            </p>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.input-hint {
  font-size: 0.8rem;
  color: grey;
}
.oq-input {
  width: 80%;
}
.invalid-email {
  border: 2px solid var(--ddm-error) !important;
  border-radius: 3px;
}
.hint-invalid-input {
  color: var(--ddm-error);
  display: none;
}
.open-question-textarea {
  resize: none;
  width: 100%;
  min-height: 150px;
  border-radius: 3px;
  border: 1px solid var(--border-color-components);
  padding: 10px;
  font-size: 0.9rem;
}
.input-row {
  padding: 15px 10px;
  border-bottom: 1px solid var(--border-color-components);
  display: flex;
  flex-direction: column;
  justify-content: center;
}
@media (min-width: 769px) {
  .oq-input {
    width: 50%;
  }
}
</style>
