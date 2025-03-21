<template>
  <div>
    <div class="question-text" v-html="text"></div>

    <div v-if="!this.options.multi_item_response"
         :id="'answer-' + qid"
         class="response-body">
      <template v-if="options.input_type === 'text'">
        <input v-if="options.display === 'small'"
               class="oq-input"
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
               class="oq-input"
               v-only-digits
               :name="qid"
               :maxlength="getMaxLength"
               @change="responseChanged($event)">
        <p class="input-hint">{{ $t('hint-number-input') }}</p>
      </template>

      <template v-else-if="options.input_type === 'email'">
        <input type="email"
               class="oq-input"
               v-valid-email
               :name="qid"
               :maxlength="getMaxLength"
               @change="responseChanged($event)">
        <p class="input-hint hint-invalid-input pb-0 mb-0">{{ $t('hint-invalid-email') }}</p>
        <p class="input-hint">{{ $t('hint-email-input') }}</p>
      </template>
    </div>

    <div v-if="this.options.multi_item_response"
         :id="'answer-' + qid"
         class="response-body">
      <div v-for="(item, id) in items"
           :id="'answer-item-' + item.id"
           v-show="!hideObjectDict['item-' + item.id]"
           class="input-row">
        <div v-html="item.label"></div>
        <div>
          <template v-if="options.input_type === 'text'">
            <input v-if="options.display === 'small'"
                   class="oq-input"
                   type="text"
                   :name="item.id"
                   :maxlength="getMaxLength"
                   @change="responseChanged($event)">
            <textarea v-if="options.display === 'large'"
                      class="open-question-textarea"
                      type="text"
                      :name="item.id"
                      :maxlength="getMaxLength"
                      @change="responseChanged($event)"></textarea>
          </template>

          <template v-else-if="options.input_type === 'numbers'">
            <input type="text"
                   class="oq-input"
                   v-only-digits
                   :name="item.id"
                   :maxlength="getMaxLength"
                   @change="responseChanged($event)">
            <p class="input-hint">{{ $t('hint-number-input') }}</p>
          </template>

          <template v-else-if="options.input_type === 'email'">
            <input type="email"
                   class="oq-input"
                   v-valid-email
                   :name="item.id"
                   :maxlength="getMaxLength"
                   @change="responseChanged($event)">
            <p class="input-hint hint-invalid-input pb-0 mb-0">{{ $t('hint-invalid-email') }}</p>
            <p class="input-hint">{{ $t('hint-email-input') }}</p>
          </template>

        </div>
      </div>
    </div>

  </div>
</template>

<script>
export default {
  name: 'OpenQuestion',
  props: ['qid', 'text', 'options', 'items', 'hideObjectDict'],
  emits: ['responseChanged'],
  data: function() {
    return {
      response: this.options.max_input_length ? {} : '-99'
    }
  },
  computed: {
    getMaxLength() {
      return this.options.max_input_length !== null ? this.options.max_input_length : undefined;
    }
  },
  created() {
    if (this.options.multi_item_response) {
      this.items.forEach(i => {
        this.response[i.id] = '-99';
      })
    } else {
      this.response = '-99'
    }
    this.$emit('responseChanged', {id: this.qid, response: this.response, question: this.text, items: null});
  },
  methods: {
    getValue(event) {
      if (event.target.value === '' || event.target.value === null) {
        return '-99'
      } else {
        return event.target.value;
      }
    },

    /**
     * Handles input changes by updating the local `response` object
     * and emitting a `responseChanged` event to the parent component.
     * If the value of the input is "" or null, uses "-99" as response value.
     *
     * @param {Event} event - The input event triggered by user interaction.
     * The target element must have a `name` and `value` attribute.
     *
     * @emits responseChanged - Emits an object containing the updated response and related question metadata.
     *
     * @returns {void}
     */
    responseChanged(event) {
      if (this.options.multi_item_response) {
        this.response[event.target.name] = this.getValue(event);
      } else {
        this.response = this.getValue(event)
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
.oq-input {
  width: 80%;
}
.invalid-email {
  border: 2px solid #c51c00 !important;
  border-radius: 3px;
}
.hint-invalid-input {
  color: #c51c00;
  display: none;
}
.open-question-textarea {
	resize: none;
	width: 100%;
	min-height: 150px;
	border-radius: 3px;
	border: 1px solid gray;
	padding: 10px;
	font-size: 0.9rem;
}

.input-row {
  padding: 15px 10px;
  border-bottom: 1px solid #cdcdcd;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

@media (min-width: 769px) {
  .oq-input {
    width: 50%;
  }
}
</style>