<script setup lang="ts">
import {onMounted, Ref } from 'vue';
import { updateMainScaleClasses, scrollToNext } from '@questionnaire/utils/scrollFunctions';

import { Item, ScalePoint, QuestionOptions } from "@questionnaire/types/questionnaire";
import {useI18n} from "vue-i18n";

const { t } = useI18n();

const props = defineProps<{
  qid: string;
  text: string;
  items: Item[];
  scale: ScalePoint[];
  options: QuestionOptions;
  hideObjectDict:  Ref<Record<string, boolean>>;
}>();

const emit = defineEmits<{
  (e: 'responseChanged', payload: { id: string; response: string; }): void;
}>();

onMounted(() => {
  updateMainScaleClasses('.scale-container');
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
          class="response-row"
          :id="'answer-' + item.id"
          v-show="!props.hideObjectDict[item.id]"
        >
          <div
            class="item-separate-line"
            :class="{ show: props.scale.length > 7 }"
            v-html="item.label"
          ></div>

          <div class="mq-item-container">
            <div v-if="props.options.show_scale_headings" class="heading-container">
              <div
                class="item-label-container item-label-placeholder"
                :class="{ hidden: props.scale.length > 7 }"
                v-html="item.label"
              ></div>
              <div class="scale-container scale-heading-container">
                <div
                  v-for="(point, id) in props.scale"
                  :key="id"
                  :class="[ 'scale-label-container', { 'main-scale': !point.secondary_point, 'secondary-scale': point.secondary_point } ]"
                >
                  <div class="scale-label scale-label-mockup">
                    <span class="scale-label-span" v-html="point.heading_label"></span>
                  </div>
                </div>
              </div>
            </div>

            <div class="response-container" :class="{ 'border-bottom-light': props.scale.length < 7 }">
              <div
                class="item-label-container"
                :class="{ hidden: props.scale.length > 7 }"
                v-html="item.label"
              ></div>
              <div class="scale-container scale-input-container">
                <div
                  v-for="(point, id) in props.scale"
                  :key="id"
                  :class="[ 'scale-label-container', { 'main-scale': !point.secondary_point, 'secondary-scale': point.secondary_point } ]"
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
                    <span class="scale-label-span" v-html="point.input_label"></span>
                  </label>
                </div>
              </div>
            </div>
          </div>
          <p :id="'required-hint-' + item.id" class="required-hint mb-0 hidden">
            {{ t('required-but-missing-hint') }}
          </p>
        </div>
      </template>
    </div>
  </div>
</template>

<style scoped>

.hidden {
  display: none !important;
}

.show {
  display: block !important;
}

.heading-container {
  width: auto;
  min-width: 10%;
  max-width: 30%;
}

.heading-container .scale-label-container {
  width: auto !important;
}

.response-row {
  padding-left: 10px;
  padding-right: 10px;
  min-height: 40vh;
  border-bottom: 1px solid #cdcdcd;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.response-body > .response-row:last-of-type {
  border-bottom: none;
}

.response-container {
  width: auto;
  min-width: 40%;
  max-width: 70%;
  align-items: center;
}

.mq-item-container {
  display: flex;
  padding-bottom: 50px;
  justify-content: center;
}

.item-separate-line {
  margin-bottom: 15px;
  padding-top: 25px;
  padding-bottom: 3px;
}

.scale-heading-container {
  display: flex;
  flex-direction: column;
  align-items: end;
  padding-right: 10px;
  width: auto;
}

.item-container {
  display: flex;
  flex-direction: column;
  padding-bottom: 20px;
  padding-top: 70px;
  border-bottom: 1px solid lightgrey;
  width: 70%;
  text-align: center;
  margin: auto;
}

.item-label-placeholder {
  opacity: 0;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  user-select: none;
}

.item-label-container {
  display: none;
  padding-bottom: 15px;
}

.scale-container {
  font-size: 0.9rem;
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
  word-break: break-word;
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

.scale-label-mockup {
  background: none !important;
  cursor: auto;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  user-select: none;
  width: auto !important;
  text-align: right;
  padding: 0;
}

.scale-label-mockup:hover {
  background: none !important;
}

.main-scale {}

.main-scale-first label {
  border-radius: 5px 5px 0 0;
}

.main-scale-last label {
  border-radius: 0 0 5px 5px;
}
.main-scale-last {
  margin-bottom: 20px;
}

.secondary-scale > label {
  background: #fff;
  border-radius: 5px;
  border: 1px solid #d1d1d1;
}

input[type="radio"] {
  display: none;
}

input[type="radio"]:checked + label {
  background-color: #45819e;
  color: white;
}

@media (min-width: 769px) {
  .mq-item-container {
    display: block;
    padding-bottom: 0;
  }

  .item-separate-line {
    display: none;
  }

  .item-label-container {
    display: block;
    padding-bottom: 15px;
  }

  .heading-container {
    display: flex;
    flex-direction: row;
    min-width: 0;
    max-width: 100%;
  }

  .response-row {
    height: auto;
    min-height: auto;
    padding-bottom: 13px;
    padding-top: 13px;
  }

  .response-container {
    display: flex;
    flex-direction: row;
    align-items: flex-start;
    min-width: 0;
    max-width: 100%;
  }

  .item-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding-bottom: 20px;
    padding-top: 20px;
    border-bottom: 1px solid lightgrey;
    width: 100%;
  }

  .scale-container {
    display: flex;
    flex-direction: row;
    min-height: 40px;
    width: 100%;
    height: 100%;
  }

  .scale-heading-container {
    align-items: flex-end;
    text-align: center;
    padding-right: 0;
  }

  .scale-input-container {
    align-items: stretch;
  }

  .scale-label-container {
    flex: 1;
    width: 100%;
    padding-left: 2px;
    padding-right: 2px;
    text-wrap: auto;
    word-break: break-word;
    overflow-wrap: break-word;
    white-space: normal;
  }

  .scale-label {}

  .scale-label-mockup {
    text-align: center;
    padding: 5px;
  }

  .item-label-placeholder {
    display: none;
    height: 1px;
  }

  .item-label-container {
    width: 30%;
    min-width: 30%;
    text-align: left;
    padding-bottom: 0;
    display: flex;
    align-items: flex-start;;
    overflow-wrap: anywhere;
    hyphens: auto;
    padding-right: 10px;
  }

  .main-scale-first label {
    border-radius: 5px 0 0 5px;
  }

  .main-scale-last label {
    border-radius: 0 5px 5px 0;
  }

  .main-scale-last {
    margin-right: 20px;
    margin-bottom: 0;
  }
}
</style>
