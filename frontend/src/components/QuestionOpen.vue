<template>
  <div>
    <div v-html="text"></div>
    <div :id="'answer-' + qid" class="question-response-body">
      <input v-if="options.display == 'small'" type="text" :name="qid" @change="responseChanged($event)">
      <textarea class="open-question-textarea" v-if="options.display == 'large'" type="text" :name="qid" @change="responseChanged($event)"></textarea>
    </div>
  </div>
</template>

<script>
export default {
  name: 'OpenQuestion',
  props: ['qid', 'text', 'options'],
  emits: ['responseChanged'],
  data: function() {
    return {
      response: '-99'
    }
  },
  created() {
    this.$emit('responseChanged', {id: this.qid, response: this.response, question: this.text, items: null});
  },
  methods: {
    responseChanged(event) {
      this.response = event.target.value;
      this.$emit('responseChanged', {id: this.qid, response: this.response, question: this.text, items: null});
    }
  }
}
</script>

<style scoped>

</style>