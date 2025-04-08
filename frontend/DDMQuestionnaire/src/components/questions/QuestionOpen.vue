<script setup lang="ts">
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';

import { Item, QuestionOptions } from "@questionnaire/types/questionnaire";

const props = defineProps<{
  qid: string;
  text: string;
  options: QuestionOptions;
  items: Item[];
  hideObjectDict: Record<string, boolean>;
}>();

const emit = defineEmits<{
  (e: 'responseChanged', payload: { id: string; response: string; }): void;
}>();

const { t } = useI18n();

const getMaxLength = computed(() =>
  props.options.max_input_length !== null ? props.options.max_input_length : undefined
);

function responseChanged(event: Event) {
  const target = event.target as HTMLInputElement;
  emit('responseChanged', {
    id: target.name,
    response: target.value,
  });
}
</script>

<template>
  <div>
    <div class="question-text" v-html="props.text"></div>

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
          @change="responseChanged"
        />
        <textarea
          v-if="props.options.display === 'large'"
          class="open-question-textarea"
          :name="props.qid"
          :maxlength="getMaxLength"
          @change="responseChanged"
        ></textarea>
        <p :id="'required-hint-' + props.qid" class="required-hint mb-0 hidden">
          {{ t('required-but-missing-hint') }}
        </p>
      </template>

      <template v-else-if="props.options.input_type === 'numbers'">
        <input
          type="text"
          class="oq-input"
          v-only-digits
          :name="props.qid"
          :maxlength="getMaxLength"
          @change="responseChanged"
        />
        <p class="input-hint">{{ t('hint-number-input') }}</p>
        <p :id="'required-hint-' + props.qid" class="required-hint mb-0 hidden">
          {{ t('required-but-missing-hint') }}
        </p>
      </template>

      <template v-else-if="props.options.input_type === 'email'">
        <input
          type="email"
          class="oq-input"
          v-valid-email
          :name="props.qid"
          :maxlength="getMaxLength"
          @change="responseChanged"
        />
        <p class="input-hint hint-invalid-input pb-0 mb-0">{{ t('hint-invalid-email') }}</p>
        <p class="input-hint">{{ t('hint-email-input') }}</p>
        <p :id="'required-hint-' + props.qid" class="required-hint mb-0 hidden">
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
        :key="item.id"
        :id="'answer-' + item.id"
        v-show="!props.hideObjectDict[item.id]"
        class="input-row"
      >
        <div v-html="item.label"></div>
        <div>
          <template v-if="props.options.input_type === 'text'">
            <input
              v-if="props.options.display === 'small'"
              class="oq-input"
              type="text"
              :name="item.id"
              :maxlength="getMaxLength"
              @change="responseChanged"
            />
            <textarea
              v-if="props.options.display === 'large'"
              class="open-question-textarea"
              :name="item.id"
              :maxlength="getMaxLength"
              @change="responseChanged"
            ></textarea>
          </template>

          <template v-else-if="props.options.input_type === 'numbers'">
            <input
              type="text"
              class="oq-input"
              v-only-digits
              :name="item.id"
              :maxlength="getMaxLength"
              @change="responseChanged"
            />
            <p class="input-hint">{{ t('hint-number-input') }}</p>
          </template>

          <template v-else-if="props.options.input_type === 'email'">
            <input
              type="email"
              class="oq-input"
              v-valid-email
              :name="item.id"
              :maxlength="getMaxLength"
              @change="responseChanged"
            />
            <p class="input-hint hint-invalid-input pb-0 mb-0">{{ t('hint-invalid-email') }}</p>
            <p class="input-hint">{{ t('hint-email-input') }}</p>
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
  border: 2px solid #c51c00 !important;
  border-radius: 3px;
}
.hint-invalid-input {
  color: #c51c00;
  display: none;
}
.open-question-textarea {
  resize: none;
  width: 100%;
  min-height: 150px;
  border-radius: 3px;
  border: 1px solid gray;
  padding: 10px;
  font-size: 0.9rem;
}
.input-row {
  padding: 15px 10px;
  border-bottom: 1px solid #cdcdcd;
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