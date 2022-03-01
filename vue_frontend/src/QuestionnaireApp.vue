<template>
  <template v-for="(question, id) in q_config" :key="id">
    <div v-show="curr_index == question.index">

      <template v-if="question.type == 'single_choice'">
        <SingleChoiceQuestion
            :qid="question.question"
            :text="question.text"
            :items="question.items"
            @answerChanged="updateAnswers"
            class="question-container"
        ></SingleChoiceQuestion>
      </template>

      <template v-if="question.type == 'multi_choice'">
        <MultiChoiceQuestion
            :qid="question.question"
            :text="question.text"
            :items="question.items"
            @answerChanged="updateAnswers"
            class="question-container"
        ></MultiChoiceQuestion>
      </template>

      <template v-if="question.type == 'open'">
        <OpenQuestion
            :qid="question.question"
            :text="question.text"
            :options="question.options"
            @answerChanged="updateAnswers"
            class="question-container"
        ></OpenQuestion>
      </template>

      <template v-if="question.type == 'matrix'">
        <MatrixQuestion
            :qid="question.question"
            :text="question.text"
            :items="question.items"
            :scale="question.scale"
            @answerChanged="updateAnswers"
            class="question-container"
        ></MatrixQuestion>
      </template>

      <template v-if="question.type == 'semantic_diff'">
        <SemanticDifferential
            :qid="question.question"
            :text="question.text"
            :items="question.items"
            :scale="question.scale"
            @answerChanged="updateAnswers"
            class="question-container"
        ></SemanticDifferential>
      </template>

      <template v-if="question.type == 'transition'">
        <TransitionQuestion
            :text="question.text"
            @answerChanged="updateAnswers"
            class="question-container"
        ></TransitionQuestion>
      </template>

    </div>

  </template>

  <div class="row">
    <div class="col">
      <button
          class="btn btn-secondary fs-5 w-25 float-end"
          type="button"
          @click="next"
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
      answers: {},
      curr_index: 1,
      max_index: 1
    }
  },
  created() {
    this.setMaxIndex();
  },
  methods: {
    updateAnswers(e) {
      this.answers[e.id] = e.answers;
    },
    setMaxIndex() {
      let indices = [];
      this.q_config.forEach(q =>
          indices.push(q.index)
      )
      this.max_index = Math.max(...indices);
    },
    next() {
      if (this.curr_index == this.max_index) {
        this.submitData();
      } else {
        this.curr_index += 1;
      }
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
