<template>
  <div>
    <div v-html="text"></div>
    <div :id="'answer-' + qid" class="question-response-body">
      <input v-if="options.display == 'small'" type="text" :name="qid" @change="answerChanged($event)">
      <textarea class="open-question-textarea" v-if="options.display == 'large'" type="text" :name="qid" @change="answerChanged($event)"></textarea>
    </div>
  </div>
</template>

<script>
export default {
  name: 'OpenQuestion',
  props: ['qid', 'text', 'options'],
  emits: ['answerChanged'],
  data: function() {
    return {
      answer: '-99'
    }
  },
  created() {
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