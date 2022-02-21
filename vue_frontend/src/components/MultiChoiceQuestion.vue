<template>
  <div>
    <div>{{ text }}</div>
    <template v-for="(item, id) in items" :key="id">
      <div>
        <label>
          <input type="checkbox" :name="item.id" :value="item.value" @change="answerChanged($event)">
          {{ item.label }}
        </label>
      </div>
    </template>
  </div>
</template>

<script>
export default {
  name: 'MultiChoiceQuestion',
  props: ['qid', 'text', 'items'],
  emits: ['answerChanged'],
  data: function() {
    return {
      answer: {}
    }
  },
  created() {
    this.items.forEach(i => {
      this.answer[i.id] = false;
    })
    this.$emit('answerChanged', {id: this.qid, answers: this.answer});
  },
  methods: {
    answerChanged(event) {
      this.answer[event.target.name] = event.target.checked;
      this.$emit('answerChanged', {id: this.qid, answers: this.answer});
    }
  }
}
</script>

<style scoped>

</style>