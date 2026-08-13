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

const getMinLength = computed(() =>
  props.options.min_input_length !== null ? props.options.min_input_length : undefined
);

const getMaxLength = computed(() =>
  props.options.max_input_length !== null ? props.options.max_input_length : undefined
);

const getMinValue = computed(() =>
  props.options.min_number_value !== null && props.options.min_number_value !== undefined
    ? props.options.min_number_value
    : undefined
);

const getMaxValue = computed(() =>
  props.options.max_number_value !== null && props.options.max_number_value !== undefined
    ? props.options.max_number_value
    : undefined
);

const lengthHint = computed(() => {
  const min = getMinLength.value;
  const max = getMaxLength.value;
  if (min !== undefined && max === undefined) {
    return t('open-question.hint-min-length', { min });
  }
  if (min !== undefined && max !== undefined) {
    return t('open-question.hint-min-max-length', { min, max });
  }
  if (min === undefined && max !== undefined) {
    return t('open-question.hint-max-length', { max });
  }
  return '';
});

const valueHint = computed(() => {
  const min = getMinValue.value;
  const max = getMaxValue.value;
  if (min !== undefined && max === undefined) {
    return t('open-question.hint-min-value', { min });
  }
  if (min !== undefined && max !== undefined) {
    return t('open-question.hint-min-max-value', { min, max });
  }
  if (min === undefined && max !== undefined) {
    return t('open-question.hint-max-value', { max });
  }
  return '';
});

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
          v-valid-length
          class="oq-input"
          type="text"
          :name="props.qid"
          :minlength="getMinLength"
          :maxlength="getMaxLength"
          :value="displayValue(props.qid)"
          @change="responseChanged"
        >
        <textarea
          v-if="props.options.display === 'large'"
          v-valid-length
          class="open-question-textarea"
          :name="props.qid"
          :minlength="getMinLength"
          :maxlength="getMaxLength"
          :value="displayValue(props.qid)"
          placeholder="|"
          @change="responseChanged"
        />
        <p class="input-hint hint-invalid-input hint-invalid-length pb-0 mb-0">
          {{ t('open-question.hint-invalid-length') }}
        </p>
        <p
          v-if="lengthHint"
          class="input-hint"
        >
          {{ lengthHint }}
        </p>
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
          v-valid-value
          type="text"
          class="oq-input"
          :name="props.qid"
          :min="getMinValue"
          :max="getMaxValue"
          :value="displayValue(props.qid)"
          @change="responseChanged"
        >
        <p class="input-hint hint-invalid-input hint-invalid-value pb-0 mb-0">
          {{ t('open-question.hint-invalid-value') }}
        </p>
        <p class="input-hint">
          {{ t('open-question.hint-number-input') }}
        </p>
        <p
          v-if="valueHint"
          class="input-hint"
        >
          {{ valueHint }}
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
          v-valid-length
          type="email"
          class="oq-input"
          :name="props.qid"
          :minlength="getMinLength"
          :maxlength="getMaxLength"
          :value="displayValue(props.qid)"
          @change="responseChanged"
        >
        <p class="input-hint hint-invalid-input hint-invalid-email pb-0 mb-0">
          {{ t('open-question.hint-invalid-email') }}
        </p>
        <p class="input-hint hint-invalid-input hint-invalid-length pb-0 mb-0">
          {{ t('open-question.hint-invalid-length') }}
        </p>
        <p class="input-hint">
          {{ t('open-question.hint-email-input') }}
        </p>
        <p
          v-if="lengthHint"
          class="input-hint"
        >
          {{ lengthHint }}
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
      <p
        v-if="props.options.input_type === 'email'"
        class="input-hint"
      >
        {{ t('open-question.hint-email-input') }}
      </p>
      <p
        v-if="props.options.input_type !== 'numbers' && lengthHint"
        class="input-hint"
      >
        {{ lengthHint }}
      </p>
      <p
        v-if="props.options.input_type === 'numbers'"
        class="input-hint"
      >
        {{ t('open-question.hint-number-input') }}
      </p>
      <p
        v-if="props.options.input_type === 'numbers' && valueHint"
        class="input-hint"
      >
        {{ valueHint }}
      </p>

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
              v-valid-length
              class="oq-input"
              type="text"
              :name="item.id"
              :minlength="getMinLength"
              :maxlength="getMaxLength"
              :value="displayValue(item.id)"
              @change="responseChanged"
            >
            <textarea
              v-if="props.options.display === 'large'"
              v-valid-length
              class="open-question-textarea"
              :name="item.id"
              :minlength="getMinLength"
              :maxlength="getMaxLength"
              :value="displayValue(item.id)"
              placeholder="|"
              @change="responseChanged"
            />
            <p class="input-hint hint-invalid-input hint-invalid-length pb-0 mb-0">
              {{ t('open-question.hint-invalid-length') }}
            </p>
          </template>

          <template v-else-if="props.options.input_type === 'numbers'">
            <input
              v-only-digits
              v-valid-value
              type="text"
              class="oq-input"
              :name="item.id"
              :min="getMinValue"
              :max="getMaxValue"
              :value="displayValue(item.id)"
              @change="responseChanged"
            >
            <p class="input-hint hint-invalid-input hint-invalid-value pb-0 mb-0">
              {{ t('open-question.hint-invalid-value') }}
            </p>
          </template>

          <template v-else-if="props.options.input_type === 'email'">
            <input
              v-valid-email
              v-valid-length
              type="email"
              class="oq-input"
              :name="item.id"
              :minlength="getMinLength"
              :maxlength="getMaxLength"
              :value="displayValue(item.id)"
              @change="responseChanged"
            >
            <p class="input-hint hint-invalid-input hint-invalid-email pb-0 mb-0">
              {{ t('open-question.hint-invalid-email') }}
            </p>
            <p class="input-hint hint-invalid-input hint-invalid-length pb-0 mb-0">
              {{ t('open-question.hint-invalid-length') }}
            </p>
          </template>
          <p
            :id="'required-hint-' + item.id"
            class="required-hint mb-0"
          >
            {{ t('required-but-missing-hint') }}
          </p>
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
.invalid-email,
.invalid-length,
.invalid-value {
  border: 2px solid var(--ddm-error) !important;
  border-radius: 3px;
}
.hint-invalid-input {
  color: var(--ddm-error);
  display: none;
}
.hint-invalid-input.show {
  display: block !important;
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
  display: flex;
  flex-direction: column;
  justify-content: center;
}
.response-body .input-row:not(:last-child) {
  border-bottom: 1px solid var(--border-color-lighter);
}
@media (min-width: 769px) {
  .oq-input {
    width: 50%;
  }
}
</style>
