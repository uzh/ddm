<template>
  <div>
    <div>{{ text }}</div>
    <div>
      <input v-if="options.display == 'regular'" type="text" :name="qid" @change="answerChanged($event)">
      <textarea v-if="options.display == 'big'" type="text" :name="qid" @change="answerChanged($event)"></textarea>
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
      answer: ''
    }
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