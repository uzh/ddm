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
            <label><input type="radio" :name="item.id" :value="point.value" @change="responseChanged($event)"><span class="ps-2 d-sm-none" v-html="point.label"></span></label>
          </td>
        </tr>
      </template>
      </tbody>
    </table>

  </div>
</template>

<script>
export default {
  name: 'MatrixQuestion',
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