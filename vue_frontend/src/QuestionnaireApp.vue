<template>
  <template v-for="(question, id) in q_config" :key="id">

    <div v-if="question.type == 'single_choice'">
      <SingleChoiceQuestion
          :qid="question.question"
          :text="question.text"
          :items="question.items"
          @answerChanged="updateAnswers"
          class="question-container"
      ></SingleChoiceQuestion>
    </div>

    <div v-if="question.type == 'multi_choice'">
      <MultiChoiceQuestion
          :qid="question.question"
          :text="question.text"
          :items="question.items"
          @answerChanged="updateAnswers"
          class="question-container"
      ></MultiChoiceQuestion>
    </div>

    <div v-if="question.type == 'open'">
      <OpenQuestion
          :qid="question.question"
          :text="question.text"
          :options="question.options"
          @answerChanged="updateAnswers"
          class="question-container"
      ></OpenQuestion>
    </div>

    <div v-if="question.type == 'matrix'">
      <MatrixQuestion
          :qid="question.question"
          :text="question.text"
          :items="question.items"
          :scale="question.scale"
          @answerChanged="updateAnswers"
          class="question-container"
      ></MatrixQuestion>
    </div>

    <div v-if="question.type == 'semantic_diff'">
      <SemanticDifferential
          :qid="question.question"
          :text="question.text"
          :items="question.items"
          :scale="question.scale"
          @answerChanged="updateAnswers"
          class="question-container"
      ></SemanticDifferential>
    </div>

    <div v-if="question.type == 'transition'">
      <TransitionQuestion
          :text="question.text"
          @answerChanged="updateAnswers"
          class="question-container"
      ></TransitionQuestion>
    </div>

  </template>

  {{ this.answers }}

  <div class="row">
    <div class="col">
      <button
          class="btn btn-secondary fs-5 w-25 float-end"
          type="button"
          @click="submitData"
      >Weiter</button>
    </div>
  </div>

</template>

<script>
import SingleChoiceQuestion from "./components/SingleChoiceQuestion.vue";
import MultiChoiceQuestion from "./components/MultiChoiceQuestion.vue";
import OpenQuestion from "./components/OpenQuestion";
import MatrixQuestion from "./components/MatrixQuestion";
import SemanticDifferential from "./components/SemanticDifferential";
import TransitionQuestion from "./components/TransitionQuestion";

export default {
  name: 'QApp',
  components: {
    SingleChoiceQuestion,
    MultiChoiceQuestion,
    OpenQuestion,
    MatrixQuestion,
    SemanticDifferential,
    TransitionQuestion
  },
  props: {
    qconfig: String,
    actionurl: String,
  },
  data() {
    return {
      q_config: JSON.parse(this.qconfig),
      answers: {}
    }
  },
  methods: {
    updateAnswers(e) {
      this.answers[e.id] = e.answers;
    },
    submitData() {
      let form = new FormData()
      form.append("post_data", JSON.stringify(this.answers));
      let csrf = document.querySelector("input[name='csrfmiddlewaretoken']");
      form.append("csrfmiddlewaretoken", csrf.value);
      fetch(this.actionurl, {method: "POST", body: form})
          .then(response => {
            console.log(response)
            if (response.redirected) {
              window.location.href = response.url;
            }
          })
          .catch(err => {
            console.info(err);
          });
    }
  }
}
</script>

<style>
#qapp {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: left;
  margin-top: 60px;
}
.question-container {
  margin-bottom: 50px;
}
</style>
