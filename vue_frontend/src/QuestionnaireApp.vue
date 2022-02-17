<template>
  <div>VUE Qapp</div>
  <div>{{qconfig}}</div>

  <!-- for page in qconfig:
    for question in questionnaire:
      if question is SingleChoice
      <SingleChoiceQuestion
        :id
        :question_text (as html?)
        :choices
        :choiceOrder
      >

      if question is MultiChoice
      <MultiChoiceQuestion
      >

      and so on...

    </div>
  -->

</template>

<script>

export default {
  name: 'QApp',
  components: {
  },
  props: {
    qconfig: String,
  },
  data() {
    return {
    }
  }
}
</script>

<style>
#qapp {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
