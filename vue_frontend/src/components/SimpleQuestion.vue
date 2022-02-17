<template>
  <form>
    <div class="qa">
      <label :ref_for="qid">{{ question }}</label>
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
      this.$emit('answerChanged', {id: this.qid, answers: this.answer});
    }
  }
};
</script>

<style scoped>

</style>
