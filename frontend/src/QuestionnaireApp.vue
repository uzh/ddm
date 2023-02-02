<i18n src="./translations/questionnaire_app.json"></i18n>

<template>

  <template v-for="(question, id) in parsedQuestConfig" :key="id">
    <div :data-page-index="question.index" v-show="currentIndex === question.index">

      <template v-if="question.type === 'single_choice'">
        <div class="question-container">
          <SingleChoiceQuestion
              :qid="question.question"
              :text="question.text"
              :items="question.items"
              @answerChanged="updateAnswers"
              class="question-body"
          ></SingleChoiceQuestion>
          <div :id="'required-hint-' + question.question" class="required-hint hidden">{{ $t('required-but-missing-hint') }}</div>
        </div>
      </template>

      <template v-if="question.type === 'multi_choice'">
        <div class="question-container">
          <MultiChoiceQuestion
              :qid="question.question"
              :text="question.text"
              :items="question.items"
              :required="question.required"
              @answerChanged="updateAnswers"
              class="question-body"
          ></MultiChoiceQuestion>
          <div :id="'required-hint-' + question.question" class="required-hint hidden">{{ $t('required-but-missing-hint') }}</div>
        </div>
      </template>

      <template v-if="question.type === 'open'">
        <div class="question-container">
          <OpenQuestion
              :qid="question.question"
              :text="question.text"
              :options="question.options"
              @answerChanged="updateAnswers"
              class="question-body"
          ></OpenQuestion>
          <div :id="'required-hint-' + question.question" class="required-hint hidden">{{ $t('required-but-missing-hint') }}</div>
        </div>
      </template>

      <template v-if="question.type === 'matrix'">
        <div class="question-container">
          <MatrixQuestion
              :qid="question.question"
              :text="question.text"
              :items="question.items"
              :scale="question.scale"
              @answerChanged="updateAnswers"
              class="question-body"
          ></MatrixQuestion>
          <div :id="'required-hint-' + question.question" class="required-hint hidden">{{ $t('required-but-missing-hint') }}</div>
        </div>
      </template>

      <template v-if="question.type === 'semantic_diff'">
        <div class="question-container">
          <SemanticDifferential
              :qid="question.question"
              :text="question.text"
              :items="question.items"
              :scale="question.scale"
              @answerChanged="updateAnswers"
              class="question-body"
          ></SemanticDifferential>
          <div :id="'required-hint-' + question.question" class="required-hint hidden">{{ $t('required-but-missing-hint') }}</div>
        </div>
      </template>

      <template v-if="question.type === 'transition'">
        <div class="question-container">
          <TransitionQuestion
              :text="question.text"
              @answerChanged="updateAnswers"
              class="question-body"
          ></TransitionQuestion>
          <div :id="'required-hint-' + question.question" class="required-hint hidden">{{ $t('required-but-missing-hint') }}</div>
        </div>
      </template>

    </div>

  </template>

  <div class="row flow-navigation">
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
      minIndex: 1,
      maxIndex: 1,
      locale: this.language,
      displayedRequiredHint: false,
    }
  },
  created() {
    this.setMaxIndex();
    this.currentIndex = this.minIndex;
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
      for (let key in this.parsedQuestConfig) {
        indices.push(this.parsedQuestConfig[key].index)
      }
      this.minIndex = Math.min(...indices);
      this.maxIndex = Math.max(...indices);
    },
    next() {
      if (this.displayedRequiredHint || this.checkRequired()) {
        if (this.currentIndex === this.maxIndex) {
          this.submitData();
        } else {
          this.currentIndex += 1;
          if (document.querySelector("[data-page-index='" + this.currentIndex + "']") === null) {
            this.next();
          }
        }
      }
    },
    getActiveQuestions() {
      let activeQuestions = [];
      for (let key in this.parsedQuestConfig) {
        if (this.currentIndex === this.parsedQuestConfig[key].index) {
          activeQuestions.push(key)
        }
      }
      return activeQuestions;
    },
    checkRequired() {
      let requiredButMissingElement = [];
      let missingQuestionIds = new Set();
      this.getActiveQuestions().forEach(q => {
        document.querySelectorAll("div[id*=answer-], tr[id*=answer-]").forEach((el) => el.classList.remove("required-but-missing"));
        document.querySelectorAll("div[class*=required-hint]").forEach((el) => el.classList.remove("show"));

        if (this.parsedQuestConfig[q].required) {
          let answers = this.answers[q];
          if (answers instanceof Object) {
            for (let i in answers) {
              if (answers[i] === -99 || answers[i] === "-99") {
                requiredButMissingElement.push("item-" + i);
                missingQuestionIds.add(q);
              }
            }
          } else if (answers === -99 || answers === "-99") {
            requiredButMissingElement.push(q);
            missingQuestionIds.add(q);
          }
        }
      })

      if (requiredButMissingElement.length === 0) {
        return true;
      } else {
        requiredButMissingElement.forEach(e => {
          let id = "answer-" + e;
          document.getElementById(id).classList.add("required-but-missing");
        })
        missingQuestionIds.forEach(q => {
          document.getElementById("required-hint-" + q).classList.add("show");
        })
        this.displayedRequiredHint = true;
        return false;
      }
    },
    submitData() {
      let form = new FormData()
      form.append("post_data", JSON.stringify(this.answers));

      let csrf = document.querySelector("input[name='csrfmiddlewaretoken']");
      form.append("csrfmiddlewaretoken", csrf.value);

      fetch(this.actionUrl, {method: "POST", body: form})
          .then(response => {
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
  font-size: 1rem;
  margin: 0px 20%;
  border-bottom: 1px solid lightgray;
  padding-bottom: 50px;
  padding-top: 50px;
}
.question-body {
  padding-left: 30px;
  padding-right: 30px;
}
.flow-navigation {
  padding-top: 50px;
  padding-right: 20%;
}
.required-but-missing {
  background: #ff480012 !important;
  border-radius: 5px;
}
.required-hint {
  font-size: 0.9rem;
  color: #c51c00;
  padding-left: 35px;
  display: none;
}
.show {
  display: block !important;
}
</style>
