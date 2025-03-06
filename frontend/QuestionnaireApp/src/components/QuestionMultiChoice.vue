<template>
  <div>
    <div v-html="text"></div>

    <div class="question-response-body item-container">

      <div v-for="(item, id) in items"
           :key="id" class="question-item">
          <input class="item-check"
                 type="checkbox"
                 :id="'q-' + this.qid + '-' + item.id"
                 :name="item.id"
                 :value="item.value"
                 @change="responseChanged($event)">
        <label :for="'q-' + this.qid  + '-' + item.id"
               class="item-label">
          <span class="span-check-icon">&#10003;</span>
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

input[type="checkbox"] {
  display: none;
}

input[type="checkbox"]:checked + label {
  background-color: #45819e;
  color: white;
}

input[type="checkbox"]:checked + label .span-check-icon {
  color: black;
}

.item-check {
  width: 1em;
  height: 1em;
  margin-top: .25em;
  vertical-align: top;
  background-color: #fff;
  background-repeat: no-repeat;
  background-position: center;
  background-size: contain;
  border: 1px solid rgba(0,0,0,.25);
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
  -webkit-print-color-adjust: exact;
  color-adjust: exact;
}

.span-check-icon {
  height: 15px;
  width: 15px;
  display: inline-block;
  background: white;
  margin-right: 10px;
  margin-left: 5px;
  font-size: 1rem;
  text-align: center;
  font-weight: bold;
  line-height: 15px;
  color: white;
}

@media (min-width: 769px) {
  .question-response-body {
    text-align: left;
  }
}
</style>