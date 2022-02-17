<template>
  <form>
    <div class="qa">
      <Label :ref_for="qid">{{ question }}</Label>
      <select :id="qid" :name="qid" class="form-control" @change="answerChanged($event)">
      <option selected disabled>Choose</option>
        <option value="yes">yes</option>
        <option value="no">no</option>
      </select>      
    </div>
  </form>
</template>

<script>

export default {  
  name: 'SimpleQuestion',
  props: ['qid', 'question'],
  emits: ['answerChanged'],
  data: function() {
    return {
      answer: ''
    }
  },
  methods: {
    answerChanged(event) {
      this.answer = event.target.value;
      this.$emit('answerChanged', event.target);
    }
  }
};
</script>

<style scoped>

</style>
