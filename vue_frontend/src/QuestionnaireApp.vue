<i18n src="./translations/questionnaire_app.json"></i18n>

<template>
  <template v-for="(question, id) in parsedQuestConfig" :key="id">
    <div v-show="currentIndex === question.index">

      <template v-if="question.type === 'single_choice'">
        <SingleChoiceQuestion
            :qid="question.question"
            :text="question.text"
            :items="question.items"
            @answerChanged="updateAnswers"
            class="question-container"
        ></SingleChoiceQuestion>
      </template>

      <template v-if="question.type === 'multi_choice'">
        <MultiChoiceQuestion
            :qid="question.question"
            :text="question.text"
            :items="question.items"
            @answerChanged="updateAnswers"
            class="question-container"
        ></MultiChoiceQuestion>
      </template>

      <template v-if="question.type === 'open'">
        <OpenQuestion
            :qid="question.question"
            :text="question.text"
            :options="question.options"
            @answerChanged="updateAnswers"
            class="question-container"
        ></OpenQuestion>
      </template>

      <template v-if="question.type === 'matrix'">
        <MatrixQuestion
            :qid="question.question"
            :text="question.text"
            :items="question.items"
            :scale="question.scale"
            @answerChanged="updateAnswers"
            class="question-container"
        ></MatrixQuestion>
      </template>

      <template v-if="question.type === 'semantic_diff'">
        <SemanticDifferential
            :qid="question.question"
            :text="question.text"
            :items="question.items"
            :scale="question.scale"
            @answerChanged="updateAnswers"
            class="question-container"
        ></SemanticDifferential>
      </template>

      <template v-if="question.type === 'transition'">
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
          class="flow-btn"
          type="button"
          @click="next"
      >{{ $t('next-btn-label') }}&nbsp;&nbsp;&#8250;</button>
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
    questionnaireConfig: String,
    actionUrl: String,
    language: String,
  },
  data() {
    this.$i18n.locale = this.language;
    return {
      parsedQuestConfig: JSON.parse(this.questionnaireConfig),
      answers: {},
      currentIndex: 1,
      maxIndex: 1,
      locale: this.language,
    }
  },
  created() {
    this.setMaxIndex();
  },
  watch: {
    locale (val){
      this.$i18n.locale = val
    }
  },
  methods: {
    updateAnswers(e) {
      this.answers[e.id] = e.answers;
    },
    setMaxIndex() {
      let indices = [];
      this.parsedQuestConfig.forEach(q =>
          indices.push(q.index)
      )
      this.maxIndex = Math.max(...indices);
    },
    next() {
      if (this.currentIndex === this.maxIndex) {
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

      fetch(this.actionUrl, {method: "POST", body: form})
          .then(response => {
            console.log(response)
            if (response.redirected) {
              window.location.href = response.url;
            }
          })
          .catch(e => {
            console.info(e);
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
}
.question-container {
  margin-bottom: 50px;
  font-size: 1.15rem;
}
</style>
