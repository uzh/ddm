<script setup lang="ts">
import { Item } from "@questionnaire/types/questionnaire";
import {useI18n} from "vue-i18n";

const { t } = useI18n();

const props = defineProps<{
  qid: string;
  text: string;
  items: Item[];
  hideObjectDict: Record<string, boolean>;
}>();

const emit = defineEmits<{
  (e: 'responseChanged', payload: { id: string; response: string; }): void;
}>();

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

    <div :id="'answer-' + props.qid" class="response-body question-response-body item-container">
      <div
        v-for="item in props.items"
        :key="item.id"
        class="question-item"
        v-show="!props.hideObjectDict[item.id]"
      >
        <input
          class="form-check-input"
          type="radio"
          :id="'q-' + props.qid + '-' + item.id"
          :name="props.qid"
          :value="item.value"
          @change="responseChanged"
        />
        <label
          :for="'q-' + props.qid + '-' + item.id"
          class="item-label prevent-select"
        >
          <span v-html="item.label"></span>
        </label>
      </div>
    </div>
  </div>
</template>

<style scoped>
.item-container {
  display: flex;
  flex-direction: column;
}

.question-response-body {
  padding: 20px 10px;
  width: 100%;
}

.question-item {
  padding-bottom: 10px;
}

.item-label {
  width: 100%;
  background: #eaeaea;
  border-radius: 5px;
  cursor: pointer;
  padding: 10px;
}

.item-label:hover {
  background: #cfcfcf;
}

input[type="radio"] {
  display: none;
}

input[type="radio"]:checked + label {
  background-color: #45819e;
  color: white;
}
</style>
