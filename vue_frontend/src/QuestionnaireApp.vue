<template>
  <h2>VUE Qapp</h2>

  <template v-for="(question, id) in q_config" :key="id">

    <div v-if="question.type == 'single_choice'">
      <h4>Single Choice Question:</h4>
      <SingleChoiceQuestion
          :qid="question.question"
          :text="question.text"
          :items="question.items"
          @answerChanged="updateAnswers"
      ></SingleChoiceQuestion>
      <p>{{ question }}</p>
    </div>

    <div v-if="question.type == 'multi_choice'">
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
      <OpenQuestion
          :qid="question.question"
          :text="question.text"
          :options="question.options"
          @answerChanged="updateAnswers"
      ></OpenQuestion>
      <p>{{ question }}</p>
    </div>

    <div v-if="question.type == 'matrix'">
      <h4>Matrix Question:</h4>
      <MatrixQuestion
          :qid="question.question"
          :text="question.text"
          :items="question.items"
          :scale="question.scale"
          @answerChanged="updateAnswers"
      ></MatrixQuestion>
      <p>{{ question }}</p>
    </div>

    <div v-if="question.type == 'semantic_diff'">
      <h4>Semantic Differential:</h4>
      <SemanticDifferential
          :qid="question.question"
          :text="question.text"
          :items="question.items"
          :scale="question.scale"
          @answerChanged="updateAnswers"
      ></SemanticDifferential>
      <p>{{ question }}</p>
    </div>

    <div v-if="question.type == 'transition'">
      <h4>Transition Text:</h4>
      <TransitionQuestion
          :text="question.text"
          @answerChanged="updateAnswers"
      ></TransitionQuestion>
      <p>{{ question }}</p>
    </div>

  </template>

  {{ this.answers }}

  <div class="row float-right">
    <button
        class="btn btn-success fs-5 w-25"
        type="button"
        @click="submitData"
    >Weiter</button>
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
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
