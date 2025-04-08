<script setup lang="ts">
import { onMounted } from 'vue';
import { updateMainScaleClasses, scrollToNext } from '@questionnaire/utils/scrollFunctions';

import { Item, ScalePoint } from "@questionnaire/types/questionnaire";
import {useI18n} from "vue-i18n";

const { t } = useI18n();

const props = defineProps<{
  qid: string;
  text: string;
  items: Item[];
  scale: ScalePoint[];
  hideObjectDict: Record<string, boolean>;
}>();

const emit = defineEmits<{
  (e: 'responseChanged', payload: { id: string; response: string; }): void;
}>();

onMounted(() => {
  updateMainScaleClasses('.item-container');
});

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
    <div class="response-body ps-0 pe-0">
      <template v-for="item in props.items" :key="item.id">
        <div
          :id="'answer-' + item.id"
          class="response-row"
          v-show="!props.hideObjectDict[item.id]"
        >
          <div class="item-container">
            <div class="item-label-container item-label-start" v-html="item.label"></div>

            <div class="scale-container">
              <template v-for="(point, idx) in props.scale" :key="idx">
                <div
                  v-if="!point.secondary_point"
                  class="scale-label-container main-scale"
                >
                  <input
                    type="radio"
                    :id="props.qid + '-' + item.id + '-' + point.value"
                    :name="item.id"
                    :value="point.value"
                    @change="responseChanged"
                    @click="scrollToNext"
                  />
                  <label
                    :for="props.qid + '-' + item.id + '-' + point.value"
                    class="scale-label prevent-select"
                    :class="{ 'main-label': !point.secondary_point }"
                  >
                    <span class="scale-label-span prevent-select" v-html="point.input_label"></span>
                  </label>
                </div>
              </template>
            </div>

            <div class="item-label-container" v-html="item.label_alt"></div>

            <div class="scale-container scale-container-secondary">
              <template v-for="(point, idx) in props.scale" :key="'sec-' + idx">
                <div
                  v-if="point.secondary_point"
                  class="scale-label-container secondary-scale"
                >
                  <input
                    type="radio"
                    :id="props.qid + '-' + item.id + '-' + point.value"
                    :name="item.id"
                    :value="point.value"
                    @change="responseChanged"
                  />
                  <label
                    :for="props.qid + '-' + item.id + '-' + point.value"
                    class="scale-label prevent-select"
                    :class="{ 'main-label': !point.secondary_point }"
                  >
                    <span class="scale-label-span prevent-select" v-html="point.input_label"></span>
                  </label>
                </div>
              </template>
            </div>
          </div>
          <p :id="'required-hint-' + item.id" class="required-hint mb-0 ps-10px hidden">
            {{ t('required-but-missing-hint') }}
          </p>
        </div>
      </template>
    </div>
  </div>
</template>

<style scoped>
.ps-10px {
  padding-left: 10px;
}

.response-row {
  padding-left: 10px;
  padding-right: 10px;
}

.item-container {
  display: flex;
  flex-direction: column;
  padding-bottom: 20px;
  padding-top: 70px;
  border-bottom: 1px solid #ededed;
  width: 70%;
  text-align: center;
  margin: auto;
}

.item-label-container {
  padding-bottom: 15px;
}

.item-label-start {
  padding-bottom: 15px;
}

.scale-label-container {
  flex: 1;
  width: 100%;
  padding-top: 2px;
  padding-bottom: 2px;
}

.scale-label {
  cursor: pointer;
  width: 100%;
  height: 100%;
  padding: 5px;
  text-align: center;
  background: #eaeaea;
  text-wrap: auto;
  word-wrap: break-word;
  overflow-wrap: break-word;
  white-space: normal;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 40px;
  font-size: 0.9rem;
}

.scale-label:hover {
  background: #cfcfcf;
}

.main-scale {}

.main-scale-first label {
  border-radius: 5px 5px 0 0;
}

.main-scale-last label {
  border-radius: 0 0 5px 5px;
}
.main-scale-last {
  margin-bottom: 15px;
}

.scale-container-secondary {
  padding-top: 30px;
}

.secondary-scale > label {
  background: #f4f4f4;
  border-radius: 5px;
}

input[type="radio"] {
  display: none;
}

input[type="radio"]:checked + label {
  background-color: #45819e;
  color: white;
}

@media (min-width: 769px) {
  .item-container {
    display: flex;
    flex-direction: row;
    align-items: center;
    padding-bottom: 20px;
    padding-top: 20px;
    border-bottom: 1px solid #ededed;
    width: 100%;
  }

  .item-label-start {
    text-align: right !important;
    padding-right: 8px;
    justify-content: end;
  }

  .scale-container {
    display: flex;
    flex-direction: row;
    align-items: stretch;
    min-height: 40px;
    width: 100%;
    height: 100%;
  }

  .scale-container-secondary {
    max-width: 10%;
    padding-top: 0;
  }

  .scale-label-container {
    flex: 1;
    width: 100%;
    padding-left: 2px;
    padding-right: 2px;
    text-wrap: auto;
    word-wrap: break-word;
    overflow-wrap: break-word;
    white-space: normal;
  }

  .scale-label {}

  .item-label-container {
    width: 20%;
    max-width: 20%;
    text-align: left;
    padding-bottom: 0;
    display: flex;
    align-items: center;
    overflow-wrap: anywhere;
    hyphens: auto;
  }

  .main-scale-first label {
    border-radius: 5px 0 0 5px;
  }

  .main-scale-last label {
    border-radius: 0 5px 5px 0;
  }

  .main-scale-last {
    margin-right: 8px;
    margin-bottom: 0;
  }
}
</style>
