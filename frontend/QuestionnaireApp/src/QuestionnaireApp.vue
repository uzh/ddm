<i18n src="./translations/questionnaire_app.json"></i18n>

<template>

  <template v-for="question in parsedQuestConfig" :key="question.question">
    <div :data-page-index="question.page" v-show="currentPage === question.page" class="question-app-container">

      <template v-if="question.type === 'single_choice'">
        <div class="question-container">
          <SingleChoiceQuestion
              :qid="question.question"
              :text="question.text"
              :items="question.items"
              @responseChanged="updateResponses"
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
              @responseChanged="updateResponses"
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
              :items="question.items"
              @responseChanged="updateResponses"
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
              :options="question.options"
              @responseChanged="updateResponses"
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
              @responseChanged="updateResponses"
              class="question-body"
          ></SemanticDifferential>
          <div :id="'required-hint-' + question.question" class="required-hint hidden">{{ $t('required-but-missing-hint') }}</div>
        </div>
      </template>

      <template v-if="question.type === 'transition'">
        <div class="question-container">
          <TransitionQuestion
              :qid="question.question"
              :text="question.text"
              @responseChanged="updateResponses"
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
          @click="next(), scrollToTop()"
      >{{ $t('next-btn-label') }}&nbsp;&nbsp;&#8250;</button>
    </div>
  </div>

</template>

<script>
import SingleChoiceQuestion from "./components/QuestionSingleChoice.vue";
import MultiChoiceQuestion from "./components/QuestionMultiChoice.vue";
import OpenQuestion from "./components/QuestionOpen.vue";
import MatrixQuestion from "./components/QuestionMatrix.vue";
import SemanticDifferential from "./components/QuestionSemanticDifferential.vue";
import TransitionQuestion from "./components/QuestionTransition.vue";

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
      responses: {},
      currentPage: 1,
      minPage: 1,
      maxPage: 1,
      locale: this.language,
      displayedRequiredHint: false,
    }
  },
  created() {
    this.setMaxPage();
    this.currentPage = this.minPage;
  },
  watch: {
    locale (val){
      this.$i18n.locale = val
    }
  },
  methods: {
    scrollToTop() {
      this.$nextTick(() => {
        setTimeout(() => {
          document.documentElement.scrollTo({
            top: 0,
            behavior: 'smooth'
          });

          document.documentElement.scrollTop = 0;
          document.body.scrollTop = 0;
        }, 100);
      });
    },
    updateResponses(e) {
      this.responses[e.id] = {response: e.response, question: e.question, items: e.items}
    },
    setMaxPage() {
      let pages = [];
      this.parsedQuestConfig.forEach(q =>
          pages.push(q.page)
      )
      this.minPage = Math.min(...pages);
      this.maxPage = Math.max(...pages);
    },
    next() {
      if (this.displayedRequiredHint || this.checkRequired()) {
        if (this.currentPage === this.maxPage) {
          this.submitData();
        } else {
          this.currentPage += 1;
          if (document.querySelector("[data-page-index='" + this.currentPage + "']") === null) {
            this.next();
          }
        }
      }
    },
    getActiveQuestions() {
      let activeQuestions = [];
      this.parsedQuestConfig.forEach(q => {
        if (this.currentPage === q.page) {
          activeQuestions.push(q)
        }
      })
      return activeQuestions;
    },
    checkRequired() {
      let requiredButMissingElement = [];
      let missingQuestionIds = new Set();
      this.getActiveQuestions().forEach(q => {
        document.querySelectorAll("div[id*=answer-], tr[id*=answer-]").forEach((el) => el.classList.remove("required-but-missing"));
        document.querySelectorAll("div[class*=required-hint]").forEach((el) => el.classList.remove("show"));

        if (q.required) {
          let response = this.responses[q.question].response;
          if (response instanceof Object) {
            for (let i in response) {
              if (response[i] === -99 || response[i] === "-99") {
                requiredButMissingElement.push("item-" + i);
                missingQuestionIds.add(q.question);
              }
            }
          } else if (response === -99 || response === "-99") {
            requiredButMissingElement.push(q.question);
            missingQuestionIds.add(q.question);
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
      form.append("post_data", JSON.stringify(this.responses));

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

.question-text {
  padding: 60px 10px 15px;
  position: sticky;
  top: 0;
  background: white;
  border-bottom: 3px solid #fbfbfb;
  z-index: 999;
}

.response-body {
  padding-top: 15px;
  padding-left: 10px;
  padding-right: 10px;
}

.question-container {
  font-size: 1rem;
  border-bottom: 2px solid #b8b8b8;
  padding-bottom: 100px;
}
@media (max-width: 992px) {
  .question-container {
    margin: 0;
  }
}

.question-body {
  text-align: center;
  min-height: 50vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
}
.flow-navigation {
  padding-top: 50px;
  padding-right: 20%;
}
.required-but-missing {
  background: #ff480012 !important;
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
@media (min-width: 769px) {
  .question-body {
    text-align: left;
    padding-left: 25px;
    padding-right: 25px;
  }
}
</style>
