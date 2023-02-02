<template>
  <div>

    <div class="surquest-question-text" v-html="text"></div>

    <div class="surquest-gq-response">
      <table class="dq-table">
        <thead>
        <tr>
          <th></th>
          <th v-for="(point, id) in scale" :key="id">{{ point.label }}</th>
          <th></th>
        </tr>
        </thead>
        <tbody>
        <tr v-for="(item, id) in items" :key="id" :id="'answer-item-' + item.id">
          <td class="mq-table-td-item dq-table-td-item-left">{{ item.label }}</td>
          <td v-for="(point, id) in scale" :key="id" class="dq-table-td-input">
            <label><input type="radio" :name="item.id" :value="point.value" @change="answerChanged($event)"></label>
          </td>
          <td class="mq-table-td-item dq-table-td-item-right">{{ item.label_alt }}</td>
        </tr>
        </tbody>
      </table>
    </div>

  </div>
</template>

<script>
export default {
  name: 'SingleChoiceQuestion',
  props: ['qid', 'text', 'items', 'scale'],
  emits: ['answerChanged'],
  data: function() {
    return {
      answer: {}
    }
  },
  created() {
    this.items.forEach(i => {
      this.answer[i.id] = -99;
    })
    this.$emit('answerChanged', {id: this.qid, answers: this.answer});
  },
  methods: {
    answerChanged(event) {
      this.answer[event.target.name] = event.target.value;
      this.$emit('answerChanged', {id: this.qid, answers: this.answer});
    }
  }
}
</script>

<style scoped>

</style>