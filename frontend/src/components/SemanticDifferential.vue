<template>
  <div>

    <div v-html="text"></div>

    <div class="question-response-body">
      <table class="dq-table">
        <thead>
        <tr>
          <th></th>
          <th v-for="(point, id) in scale" :key="id" v-html="point.label"></th>
          <th></th>
        </tr>
        </thead>
        <tbody>
        <tr v-for="(item, id) in items" :key="id" :id="'answer-item-' + item.id">
          <td class="mq-table-td-item dq-table-td-item-left" v-html="item.label"></td>
          <td v-for="(point, id) in scale" :key="id" class="dq-table-td-input">
            <label><input type="radio" :name="item.id" :value="point.value" @change="responseChanged($event)"></label>
          </td>
          <td class="mq-table-td-item dq-table-td-item-right" v-html="item.label_alt"></td>
        </tr>
        </tbody>
      </table>
    </div>

  </div>
</template>

<script>
export default {
  name: 'SemanticDifferential',
  props: ['qid', 'text', 'items', 'scale'],
  emits: ['responseChanged'],
  data: function() {
    return {
      response: {}
    }
  },
  created() {
    this.items.forEach(i => {
      this.response[i.id] = -99;
    })
    this.$emit('responseChanged', {id: this.qid, response: this.response, question: this.text, items: this.items});
  },
  methods: {
    responseChanged(event) {
      this.response[event.target.name] = event.target.value;
      this.$emit('responseChanged', {id: this.qid, response: this.response, question: this.text, items: this.items});
    }
  }
}
</script>

<style scoped>

</style>