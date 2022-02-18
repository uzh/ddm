<template>
  <div>

    <div>{{ text }}</div>

    <table>
      <thead>
      <tr>
        <th></th>
        <th v-for="(point, id) in scale" :key="id">{{ point.label }}</th>
        <th></th>
      </tr>
      </thead>
      <tbody>
      <template v-for="(item, id) in items" :key="id">
        <tr>
          <th>{{ item.label }}</th>
          <th v-for="(point, id) in scale" :key="id">
            <label><input type="radio" :name="item.id" :value="point.value" @change="answerChanged($event)"></label>
          </th>
          <th>{{ item.label_alt }}</th>
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