<template>
  <div>
    <div v-html="text"></div>
    <div :id="'answer-' + qid" class="question-response-body">
      <template v-if="options.input_type === 'text'">
        <input v-if="options.display === 'small'"
               type="text"
               :name="qid"
               :maxlength="getMaxLength"
               @change="responseChanged($event)">
        <textarea v-if="options.display === 'large'"
                  class="open-question-textarea"
                  type="text"
                  :name="qid"
                  :maxlength="getMaxLength"
                  @change="responseChanged($event)"></textarea>
      </template>

      <template v-else-if="options.input_type === 'numbers'">
        <input type="text"
               v-only-digits
               :name="qid"
               :maxlength="getMaxLength"
               @change="responseChanged($event)">
        <p class="input-hint">{{ $t('hint-number-input') }}</p>
      </template>

      <template v-else-if="options.input_type === 'email'">
        <input type="email"
               v-valid-email
               :name="qid"
               :maxlength="getMaxLength"
               @change="responseChanged($event)">
        <p class="input-hint hint-invalid-input pb-0 mb-0">{{ $t('hint-invalid-email') }}</p>
        <p class="input-hint">{{ $t('hint-email-input') }}</p>
      </template>

    </div>
  </div>
</template>

<script>
export default {
  name: 'OpenQuestion',
  props: ['qid', 'text', 'options'],
  emits: ['responseChanged'],
  data: function() {
    return {
      response: '-99'
    }
  },
  computed: {
    getMaxLength() {
      return this.options.max_input_length !== null ? this.options.max_input_length : undefined;
    }
  },
  created() {
    this.$emit('responseChanged', {id: this.qid, response: this.response, question: this.text, items: null});
  },
  methods: {
    responseChanged(event) {
      if (event.target.value === '' || event.target.value === null) {
        this.response = '-99'
      } else {
        this.response = event.target.value;
      }
      this.$emit('responseChanged', {id: this.qid, response: this.response, question: this.text, items: null});
    }
  },
  directives: {
    onlyDigits: {
      mounted(el) {
        el.addEventListener("input", function () {
          el.value = el.value.replace(/\D/g, ""); // Remove non-numeric characters
        });
      }
    },
    validEmail: {
      mounted(el) {
        el.addEventListener("blur", function () {
          const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
          const hint = el.nextElementSibling;
          if (!emailRegex.test(el.value)) {
            el.classList.add("invalid-email");
            if (hint && hint.classList.contains("hint-invalid-input")) {
              hint.style.display = "block";
            }
          } else {
            el.classList.remove("invalid-email");
            if (hint && hint.classList.contains("hint-invalid-input")) {
              hint.style.display = "none";
            }
          }
        });

        el.addEventListener("focus", function () {
          const hint = el.nextElementSibling;
          if (hint && hint.classList.contains("hint-invalid-input")) {
            hint.style.display = "none";
          }
        });
      }
    }
  }
}
</script>

<style scoped>
.input-hint {
  font-size: 0.8rem;
  color: grey;
}
.invalid-email {
  border: 2px solid red !important;
  border-radius: 3px;
}
.hint-invalid-input {
  color: red;
  display: none;
}
</style>