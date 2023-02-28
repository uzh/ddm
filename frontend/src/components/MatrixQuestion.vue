<template>
  <div>

    <div v-html="text"></div>

    <table class="mq-table">
      <thead class="mq-header">
      <tr>
        <th></th>
        <th v-for="(point, id) in scale" :key="id" v-html="point.label"></th>
      </tr>
      </thead>
      <tbody>
      <template v-for="(item, id) in items" :key="id">
        <tr :id="'answer-item-' + item.id">
          <td class="mq-table-td-item" v-html="item.label"></td>
          <td v-for="(point, id) in scale" :key="id" class="mq-table-td-input">
            <label><input type="radio" :name="item.id" :value="point.value" @change="answerChanged($event)"></label>
          </td>
        </tr>
      </template>
      </tbody>
    </table>

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