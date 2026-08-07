<script setup lang="ts">
import { onMounted } from 'vue';
import { updateMainScaleClasses, scrollToNext } from '@questionnaire/utils/scrollFunctions';

import { Item, Responses, ScalePoint } from "@questionnaire/types/questionnaire";
import { useI18n } from "vue-i18n";

const { t } = useI18n();

const props = defineProps<{
  qid: string;
  text: string;
  items: Item[];
  scale: ScalePoint[];
  hideObjectDict: Record<string, boolean>;
  responses: Responses;
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
  <div class="ddm-question ddm-question--semantic-diff">
    <div
      class="question-text"
      v-html="props.text"
    />
    <div class="response-body ps-0 pe-0">
      <template
        v-for="item in props.items"
        :key="item.id"
      >
        <div
          v-show="!props.hideObjectDict[item.id]"
          :id="'answer-' + item.id"
          class="response-row"
        >
          <div class="item-container">
            <div
              class="item-label-container item-label-start"
              v-html="item.label"
            />

            <div class="scale-container">
              <template
                v-for="(point, idx) in props.scale"
                :key="idx"
              >
                <div
                  v-if="!point.secondary_point"
                  class="scale-label-container main-scale"
                >
                  <input
                    :id="props.qid + '-' + item.id + '-' + point.value"
                    type="radio"
                    :name="item.id"
                    :value="point.value"
                    :checked="String(props.responses[item.id]) === String(point.value)"
                    @change="responseChanged"
                    @click="scrollToNext"
                  >
                  <label
                    :for="props.qid + '-' + item.id + '-' + point.value"
                    class="scale-label prevent-select"
                    :class="{ 'main-label': !point.secondary_point }"
                  >
                    <span
                      class="scale-label-span prevent-select"
                      v-html="point.input_label"
                    />
                  </label>
                </div>
              </template>
            </div>

            <div
              class="item-label-container"
              v-html="item.label_alt"
            />

            <div class="scale-container scale-container-secondary">
              <template
                v-for="(point, idx) in props.scale"
                :key="'sec-' + idx"
              >
                <div
                  v-if="point.secondary_point"
                  class="scale-label-container secondary-scale"
                >
                  <input
                    :id="props.qid + '-' + item.id + '-' + point.value"
                    type="radio"
                    :name="item.id"
                    :value="point.value"
                    :checked="String(props.responses[item.id]) === String(point.value)"
                    @change="responseChanged"
                  >
                  <label
                    :for="props.qid + '-' + item.id + '-' + point.value"
                    class="scale-label prevent-select"
                    :class="{ 'main-label': !point.secondary_point }"
                  >
                    <span
                      class="scale-label-span prevent-select"
                      v-html="point.input_label"
                    />
                  </label>
                </div>
              </template>
            </div>
          </div>
          <p
            :id="'required-hint-' + item.id"
            class="required-hint mb-0 ps-10px hidden"
          >
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
  margin-left: 10px;
  margin-right: 10px;
}

.response-body .response-row:not(:last-child) {
  border-bottom: 1px solid var(--border-color-lighter);
}

.item-container {
  display: flex;
  flex-direction: column;
  padding-top: 20px;
  padding-bottom: 20px;
  width: 70%;
  text-align: center;
  margin: auto;
}

.item-label-container {
  padding-bottom: 5px;
}

.item-label-start {
  padding-bottom: 5px;
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
  background: var(--ddm-item-bg);
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
  background: var(--ddm-item-bg-hover);
}

.main-scale-first label {
  border-radius: 5px 5px 0 0;
}

.main-scale-last label {
  border-radius: 0 0 5px 5px;
}
.main-scale-last {
  margin-bottom: 5px;
}

.secondary-scale > label {
  background: #f4f4f4;
  border-radius: 5px;
}

input[type="radio"] {
  display: none;
}

input[type="radio"]:checked + label {
  background-color: var(--ddm-primary);
  color: var(--ddm-primary-fg);
}

@media (min-width: 769px) {
  .item-container {
    display: flex;
    flex-direction: row;
    align-items: center;
    padding-bottom: 20px;
    padding-top: 20px;
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
