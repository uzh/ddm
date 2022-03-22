<template>
  <div>
    <div class="surquest-question-text" v-html="text"></div>
    <div v-for="(item, id) in items" :key="id" class="surquest-gq-response surquest-cq-response">
      <div class="surquest-choice-item form-check">
        <label class="form-check-label rb-cb-label">
          <input class="form-check-input" type="checkbox" :name="item.id" :value="item.value" @change="answerChanged($event)">
          {{ item.label }}
        </label>
      </div>
    </div>
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