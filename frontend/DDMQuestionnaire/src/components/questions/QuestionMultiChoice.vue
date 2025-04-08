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
    <div class="response-body question-response-body item-container">
      <div
        v-for="item in props.items"
        :key="item.id"
        class="question-item"
        v-show="!props.hideObjectDict[item.id]"
      >
        <input
          class="item-check"
          type="checkbox"
          :id="'q-' + props.qid + '-' + item.id"
          :name="item.id"
          :value="item.value"
          @change="responseChanged"
        />
        <label
          :for="'q-' + props.qid + '-' + item.id"
          class="item-label prevent-select"
        >
          <span class="span-check-icon">&#10003;</span>
          <span v-html="item.label"></span>
        </label>
      </div>
      <p :id="'required-hint-' + props.qid" class="required-hint mb-0 hidden">
        {{ t('required-but-missing-hint') }}
      </p>
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

input[type="checkbox"] {
  display: none;
}

input[type="checkbox"]:checked + label {
  background-color: #45819e;
  color: white;
}

input[type="checkbox"]:checked + label .span-check-icon {
  color: black;
}

.item-check {
  width: 1em;
  height: 1em;
  margin-top: .25em;
  vertical-align: top;
  background-color: #fff;
  background-repeat: no-repeat;
  background-position: center;
  background-size: contain;
  border: 1px solid rgba(0,0,0,.25);
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
  -webkit-print-color-adjust: exact;
  print-color-adjust: exact;
}

.span-check-icon {
  height: 15px;
  width: 15px;
  display: inline-block;
  background: white;
  margin-right: 10px;
  margin-left: 5px;
  font-size: 1rem;
  text-align: center;
  font-weight: bold;
  line-height: 15px;
  color: white;
}

@media (min-width: 769px) {
  .question-response-body {
    text-align: left;
  }
}
</style>
