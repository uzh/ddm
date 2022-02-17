<template>
  <h2>VUE Qapp</h2>

  <template v-for="(question, id) in q_config" :key="id">

    <div v-if="question.type == 'single-choice'">
      <h4>Single Choice Question:</h4>
      <SingleChoiceQuestion
          :qid="question.question"
          :text="question.text"
          :items="question.items"
          @answerChanged="updateAnswers"
      ></SingleChoiceQuestion>
      <p>{{ question }}</p>
    </div>

    <div v-if="question.type == 'multi-choice'">
      <h4>Multi Choice Question:</h4>
      <MultiChoiceQuestion
          :qid="question.question"
          :text="question.text"
          :items="question.items"
          @answerChanged="updateAnswers"
      ></MultiChoiceQuestion>
      <p>{{ question }}</p>
    </div>

    <div v-if="question.type == 'open'">
      <h4>Open Question:</h4>
      <p>{{ question.text }}</p>
      <p>{{ question }}</p>
    </div>

    <div v-if="question.type == 'matrix'">
      <h4>Matrix Question:</h4>
      <p>{{ question.text }}</p>
      <p>{{ question }}</p>
    </div>

    <div v-if="question.type == 'semantic-diff'">
      <h4>Semantic Differential:</h4>
      <p>{{ question.text }}</p>
      <p>{{ question }}</p>
    </div>

    <div v-if="question.type == 'transition'">
      <h4>Transition Text:</h4>
      <p>{{ question.text }}</p>
      <p>{{ question }}</p>
    </div>

  </template>

  <SimpleQuestion
    :qid="'SunQuestion'"
    :question="'is the sun hot?'" @answerChanged="updateAnswers"
  ></SimpleQuestion>

  {{ this.answers }}

</template>

<script>
import SimpleQuestion from "./components/SimpleQuestion.vue"
import SingleChoiceQuestion from "./components/SingleChoiceQuestion.vue"
import MultiChoiceQuestion from "./components/MultiChoiceQuestion.vue"

export default {
  name: 'QApp',
  components: {
    SimpleQuestion,
    SingleChoiceQuestion,
    MultiChoiceQuestion
  },
  props: {
    qconfig: String,
  },
  data() {
    return {
      q_config: JSON.parse(this.qconfig),
      answers: {

      }
    }
  },
  methods: {
    updateAnswers(e) {
      this.answers[e.id] = e.answers;
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
