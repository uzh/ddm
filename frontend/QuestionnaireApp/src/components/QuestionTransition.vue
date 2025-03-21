<template>
  <div class="question-text">
    <div v-html="text"></div>
  </div>
</template>

<script>
export default {
  name: 'TransitionQuestion',
  props: ['qid', 'text'],
  emits: ['responseChanged'],
  created() {
    // Simulates response changed to emit the question configuration once to the questionnaire app.
    this.$emit('responseChanged', {id: this.qid, response: null, question: this.text, items: null});
  },
}
</script>

<style scoped>

</style>
