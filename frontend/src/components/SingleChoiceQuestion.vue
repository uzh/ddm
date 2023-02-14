<template>
  <div>
    <div v-html="text"></div>
    <div :id="'answer-' + qid" class="question-response-body">
      <div v-for="(item, id) in items" :key="id" class="question-choice-item form-check">
        <label class="form-check-label rb-cb-label">
          <input class="form-check-input" type="radio" :dataid="qid" :name="'q-' + qid" :value="item.value" @change="answerChanged($event)">
          <span v-html="item.label"></span>
        </label>
      </div>
    </div>
  </div>

  <!-- Additional display option as dropdown select:
  <div>
    <div :ref_for="qid">{{ text }}</div>
    <select :id="qid" :name="qid" class="form-control" @change="answerChanged($event)">
      <option selected disabled>Choose</option>
      <option v-for="(item, id) in items" :key="id" :value="item.value">{{ item.label }}</option>
    </select>
  </div>
  -->
</template>

<script>
export default {
  name: 'SingleChoiceQuestion',
  props: ['qid', 'text', 'items'],
  emits: ['answerChanged'],
  data: function() {
    return {
      answer: ''
    }
  },
  created() {
    this.answer = -99;
    this.$emit('answerChanged', {id: this.qid, answers: this.answer});
  },
  methods: {
    answerChanged(event) {
      this.answer = event.target.value;
      this.$emit('answerChanged', {id: this.qid, answers: this.answer});
    }
  }
}
</script>

<style scoped>

</style>
