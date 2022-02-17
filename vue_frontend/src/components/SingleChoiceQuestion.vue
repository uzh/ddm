<template>
  <div>
    <div>{{ text }}</div>
    <div>{{ qid }}</div>
    <template v-for="(item, id) in items" :key="id">
      <div>
        <label>
          <input type="radio" :name="qid" :value="item.value" @change="answerChanged($event)">
          {{ item.label }}
        </label>
      </div>
    </template>

  </div>
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