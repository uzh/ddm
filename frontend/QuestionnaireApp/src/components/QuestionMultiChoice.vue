<template>
  <div>
    <div v-html="text"></div>
    <div class="question-response-body">
      <div v-for="(item, id) in items" :key="id" class="question-choice-item form-check">
        <label class="form-check-label rb-cb-label">
          <input class="form-check-input" type="checkbox" :name="item.id" :value="item.value" @change="responseChanged($event)">
          <span v-html="item.label"></span>
        </label>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'MultiChoiceQuestion',
  props: ['qid', 'text', 'items'],
  emits: ['responseChanged'],
  data: function() {
    return {
      response: {}
    }
  },
  created() {
    this.items.forEach(i => {
      this.response[i.id] = false;
    })
    this.$emit('responseChanged', {id: this.qid, response: this.response, question: this.text, items: this.items});
  },
  methods: {
    responseChanged(event) {
      this.response[event.target.name] = event.target.checked;
      this.$emit('responseChanged', {id: this.qid, response: this.response, question: this.text, items: this.items});
    }
  }
}
</script>

<style scoped>

</style>