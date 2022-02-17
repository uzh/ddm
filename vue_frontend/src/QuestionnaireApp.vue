<template>
  <div>VUE Qapp</div>
  <div>{{qconfig}}</div>

  <SimpleQuestion
    :qid="'SunQuestion'"
    :question="'is the sun hot?'" @answerChanged="updateAnswers"
  ></SimpleQuestion>

  {{ this.answers }}
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
import SimpleQuestion from "./components/SimpleQuestion.vue"

export default {
  name: 'QApp',
  components: {
    SimpleQuestion
  },
  props: {
    qconfig: String,
  },
  data() {
    return {
      answers: {

      }
    }
  },
  methods: {
    updateAnswers(e) {
      this.answers[e.name] = e.value;
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
