<template>
  <div>
    <div class="question-text" v-html="text"></div>

    <div :id="'answer-' + qid" class="response-body question-response-body item-container">

      <div v-for="(item, id) in items"
           :key="id"
           class="question-item">
        <input class="form-check-input"
               type="radio"
               :id="'q-' + this.qid + '-' + item.id"
               :dataid="qid"
               :name="'q-' + qid"
               :value="item.value"
               @change="responseChanged($event)">
        <label :for="'q-' + this.qid  + '-' + item.id"
               class="item-label">
          <span v-html="item.label"></span>
        </label>
      </div>

    </div>

  </div>

  <!-- Additional display option as dropdown select:
  <div>
    <div :ref_for="qid">{{ text }}</div>
    <select :id="qid" :name="qid" class="form-control" @change="answerChanged($event)">
      <option selected disabled>Choose</option>
      <option v-for="(item, id) in items" :key="id" :value="item.value">{{ item.label }}</option>
    </select>
  </div>
  -->
</template>

<script>
export default {
  name: 'SingleChoiceQuestion',
  props: ['qid', 'text', 'items'],
  emits: ['responseChanged'],
  data: function() {
    return {
      response: '',
    }
  },
  created() {
    this.response = -99;
    this.$emit('responseChanged', {id: this.qid, response: this.response, question: this.text, items: this.items});
  },
  methods: {
    responseChanged(event) {
      this.response = event.target.value;
      this.$emit('responseChanged', {id: this.qid, response: this.response, question: this.text, items: this.items});
    }
  }
}
</script>

<style scoped>
.item-container {
  display: flex;
  flex-direction: column;
}

.question-response-body {
  padding: 20px 10px;
  width: 100%;
}

.question-item {
  padding-bottom: 10px;
}

.item-label {
  width: 100%;
  background: #eaeaea;
  border-radius: 5px;
  cursor: pointer;
  padding: 10px;
}

.item-label:hover {
  background: #cfcfcf;
}

input[type="radio"] {
  display: none;
}

input[type="radio"]:checked + label {
  background-color: #45819e;
  color: white;
}
</style>
