/*
 * ATTENTION: An "eval-source-map" devtool has been used.
 * This devtool is neither made for production nor for readable output files.
 * It uses "eval()" calls to create a separate source file with attached SourceMaps in the browser devtools.
 * If you are trying to read the output file, select a different devtool (https://webpack.js.org/configuration/devtool/)
 * or disable the default devtool with "devtool: false".
 * If you are looking for production-ready output files, see mode: "production" (https://webpack.js.org/configuration/mode/).
 */
/******/ (function() { // webpackBootstrap
/******/ 	var __webpack_modules__ = ({

/***/ "./node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!./node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./src/QuestionnaireApp.vue?vue&type=script&lang=js":
/*!***************************************************************************************************************************************************************************************!*\
  !*** ./node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!./node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./src/QuestionnaireApp.vue?vue&type=script&lang=js ***!
  \***************************************************************************************************************************************************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var _components_SingleChoiceQuestion_vue__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./components/SingleChoiceQuestion.vue */ \"./src/components/SingleChoiceQuestion.vue\");\n/* harmony import */ var _components_MultiChoiceQuestion_vue__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./components/MultiChoiceQuestion.vue */ \"./src/components/MultiChoiceQuestion.vue\");\n/* harmony import */ var _components_OpenQuestion__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./components/OpenQuestion */ \"./src/components/OpenQuestion.vue\");\n/* harmony import */ var _components_MatrixQuestion__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./components/MatrixQuestion */ \"./src/components/MatrixQuestion.vue\");\n/* harmony import */ var _components_SemanticDifferential__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ./components/SemanticDifferential */ \"./src/components/SemanticDifferential.vue\");\n/* harmony import */ var _components_TransitionQuestion__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ./components/TransitionQuestion */ \"./src/components/TransitionQuestion.vue\");\n\n\n\n\n\n\n/* harmony default export */ __webpack_exports__[\"default\"] = ({\n  name: 'QApp',\n  components: {\n    SingleChoiceQuestion: _components_SingleChoiceQuestion_vue__WEBPACK_IMPORTED_MODULE_0__[\"default\"],\n    MultiChoiceQuestion: _components_MultiChoiceQuestion_vue__WEBPACK_IMPORTED_MODULE_1__[\"default\"],\n    OpenQuestion: _components_OpenQuestion__WEBPACK_IMPORTED_MODULE_2__[\"default\"],\n    MatrixQuestion: _components_MatrixQuestion__WEBPACK_IMPORTED_MODULE_3__[\"default\"],\n    SemanticDifferential: _components_SemanticDifferential__WEBPACK_IMPORTED_MODULE_4__[\"default\"],\n    TransitionQuestion: _components_TransitionQuestion__WEBPACK_IMPORTED_MODULE_5__[\"default\"]\n  },\n  props: {\n    qconfig: String,\n    actionurl: String\n  },\n\n  data() {\n    return {\n      q_config: JSON.parse(this.qconfig),\n      answers: {},\n      curr_index: 1,\n      max_index: 1\n    };\n  },\n\n  created() {\n    this.setMaxIndex();\n  },\n\n  methods: {\n    updateAnswers(e) {\n      this.answers[e.id] = e.answers;\n    },\n\n    setMaxIndex() {\n      let indices = [];\n      this.q_config.forEach(q => indices.push(q.index));\n      this.max_index = Math.max(...indices);\n    },\n\n    next() {\n      if (this.curr_index == this.max_index) {\n        this.submitData();\n      } else {\n        this.curr_index += 1;\n      }\n    },\n\n    submitData() {\n      let form = new FormData();\n      form.append(\"post_data\", JSON.stringify(this.answers));\n      let csrf = document.querySelector(\"input[name='csrfmiddlewaretoken']\");\n      form.append(\"csrfmiddlewaretoken\", csrf.value);\n      fetch(this.actionurl, {\n        method: \"POST\",\n        body: form\n      }).then(response => {\n        console.log(response);\n\n        if (response.redirected) {\n          window.location.href = response.url;\n        }\n      }).catch(err => {\n        console.info(err);\n      });\n    }\n\n  }\n});//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi9ub2RlX21vZHVsZXMvYmFiZWwtbG9hZGVyL2xpYi9pbmRleC5qcz8/Y2xvbmVkUnVsZVNldC00MC51c2VbMF0hLi9ub2RlX21vZHVsZXMvdnVlLWxvYWRlci9kaXN0L2luZGV4LmpzPz9ydWxlU2V0WzBdLnVzZVswXSEuL3NyYy9RdWVzdGlvbm5haXJlQXBwLnZ1ZT92dWUmdHlwZT1zY3JpcHQmbGFuZz1qcy5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7O0FBaUZBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUVBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQU5BO0FBUUE7QUFDQTtBQUNBO0FBRkE7O0FBSUE7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBSkE7QUFNQTs7QUFDQTtBQUNBO0FBQ0E7O0FBQ0E7QUFDQTtBQUNBO0FBQ0E7O0FBQ0E7QUFDQTtBQUNBO0FBR0E7QUFDQTs7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTs7QUFDQTtBQUNBO0FBQ0E7QUFFQTtBQUNBO0FBRUE7QUFBQTtBQUFBO0FBQUE7QUFFQTs7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUVBO0FBQ0E7QUFDQTs7QUFuQ0E7QUF6QkEiLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly92dWVfZnJvbnRlbmQvLi9zcmMvUXVlc3Rpb25uYWlyZUFwcC52dWU/MGM5ZCJdLCJzb3VyY2VzQ29udGVudCI6WyI8dGVtcGxhdGU+XHJcbiAgPHRlbXBsYXRlIHYtZm9yPVwiKHF1ZXN0aW9uLCBpZCkgaW4gcV9jb25maWdcIiA6a2V5PVwiaWRcIj5cclxuICAgIDxkaXYgdi1zaG93PVwiY3Vycl9pbmRleCA9PSBxdWVzdGlvbi5pbmRleFwiPlxyXG5cclxuICAgICAgPHRlbXBsYXRlIHYtaWY9XCJxdWVzdGlvbi50eXBlID09ICdzaW5nbGVfY2hvaWNlJ1wiPlxyXG4gICAgICAgIDxTaW5nbGVDaG9pY2VRdWVzdGlvblxyXG4gICAgICAgICAgICA6cWlkPVwicXVlc3Rpb24ucXVlc3Rpb25cIlxyXG4gICAgICAgICAgICA6dGV4dD1cInF1ZXN0aW9uLnRleHRcIlxyXG4gICAgICAgICAgICA6aXRlbXM9XCJxdWVzdGlvbi5pdGVtc1wiXHJcbiAgICAgICAgICAgIEBhbnN3ZXJDaGFuZ2VkPVwidXBkYXRlQW5zd2Vyc1wiXHJcbiAgICAgICAgICAgIGNsYXNzPVwicXVlc3Rpb24tY29udGFpbmVyXCJcclxuICAgICAgICA+PC9TaW5nbGVDaG9pY2VRdWVzdGlvbj5cclxuICAgICAgPC90ZW1wbGF0ZT5cclxuXHJcbiAgICAgIDx0ZW1wbGF0ZSB2LWlmPVwicXVlc3Rpb24udHlwZSA9PSAnbXVsdGlfY2hvaWNlJ1wiPlxyXG4gICAgICAgIDxNdWx0aUNob2ljZVF1ZXN0aW9uXHJcbiAgICAgICAgICAgIDpxaWQ9XCJxdWVzdGlvbi5xdWVzdGlvblwiXHJcbiAgICAgICAgICAgIDp0ZXh0PVwicXVlc3Rpb24udGV4dFwiXHJcbiAgICAgICAgICAgIDppdGVtcz1cInF1ZXN0aW9uLml0ZW1zXCJcclxuICAgICAgICAgICAgQGFuc3dlckNoYW5nZWQ9XCJ1cGRhdGVBbnN3ZXJzXCJcclxuICAgICAgICAgICAgY2xhc3M9XCJxdWVzdGlvbi1jb250YWluZXJcIlxyXG4gICAgICAgID48L011bHRpQ2hvaWNlUXVlc3Rpb24+XHJcbiAgICAgIDwvdGVtcGxhdGU+XHJcblxyXG4gICAgICA8dGVtcGxhdGUgdi1pZj1cInF1ZXN0aW9uLnR5cGUgPT0gJ29wZW4nXCI+XHJcbiAgICAgICAgPE9wZW5RdWVzdGlvblxyXG4gICAgICAgICAgICA6cWlkPVwicXVlc3Rpb24ucXVlc3Rpb25cIlxyXG4gICAgICAgICAgICA6dGV4dD1cInF1ZXN0aW9uLnRleHRcIlxyXG4gICAgICAgICAgICA6b3B0aW9ucz1cInF1ZXN0aW9uLm9wdGlvbnNcIlxyXG4gICAgICAgICAgICBAYW5zd2VyQ2hhbmdlZD1cInVwZGF0ZUFuc3dlcnNcIlxyXG4gICAgICAgICAgICBjbGFzcz1cInF1ZXN0aW9uLWNvbnRhaW5lclwiXHJcbiAgICAgICAgPjwvT3BlblF1ZXN0aW9uPlxyXG4gICAgICA8L3RlbXBsYXRlPlxyXG5cclxuICAgICAgPHRlbXBsYXRlIHYtaWY9XCJxdWVzdGlvbi50eXBlID09ICdtYXRyaXgnXCI+XHJcbiAgICAgICAgPE1hdHJpeFF1ZXN0aW9uXHJcbiAgICAgICAgICAgIDpxaWQ9XCJxdWVzdGlvbi5xdWVzdGlvblwiXHJcbiAgICAgICAgICAgIDp0ZXh0PVwicXVlc3Rpb24udGV4dFwiXHJcbiAgICAgICAgICAgIDppdGVtcz1cInF1ZXN0aW9uLml0ZW1zXCJcclxuICAgICAgICAgICAgOnNjYWxlPVwicXVlc3Rpb24uc2NhbGVcIlxyXG4gICAgICAgICAgICBAYW5zd2VyQ2hhbmdlZD1cInVwZGF0ZUFuc3dlcnNcIlxyXG4gICAgICAgICAgICBjbGFzcz1cInF1ZXN0aW9uLWNvbnRhaW5lclwiXHJcbiAgICAgICAgPjwvTWF0cml4UXVlc3Rpb24+XHJcbiAgICAgIDwvdGVtcGxhdGU+XHJcblxyXG4gICAgICA8dGVtcGxhdGUgdi1pZj1cInF1ZXN0aW9uLnR5cGUgPT0gJ3NlbWFudGljX2RpZmYnXCI+XHJcbiAgICAgICAgPFNlbWFudGljRGlmZmVyZW50aWFsXHJcbiAgICAgICAgICAgIDpxaWQ9XCJxdWVzdGlvbi5xdWVzdGlvblwiXHJcbiAgICAgICAgICAgIDp0ZXh0PVwicXVlc3Rpb24udGV4dFwiXHJcbiAgICAgICAgICAgIDppdGVtcz1cInF1ZXN0aW9uLml0ZW1zXCJcclxuICAgICAgICAgICAgOnNjYWxlPVwicXVlc3Rpb24uc2NhbGVcIlxyXG4gICAgICAgICAgICBAYW5zd2VyQ2hhbmdlZD1cInVwZGF0ZUFuc3dlcnNcIlxyXG4gICAgICAgICAgICBjbGFzcz1cInF1ZXN0aW9uLWNvbnRhaW5lclwiXHJcbiAgICAgICAgPjwvU2VtYW50aWNEaWZmZXJlbnRpYWw+XHJcbiAgICAgIDwvdGVtcGxhdGU+XHJcblxyXG4gICAgICA8dGVtcGxhdGUgdi1pZj1cInF1ZXN0aW9uLnR5cGUgPT0gJ3RyYW5zaXRpb24nXCI+XHJcbiAgICAgICAgPFRyYW5zaXRpb25RdWVzdGlvblxyXG4gICAgICAgICAgICA6dGV4dD1cInF1ZXN0aW9uLnRleHRcIlxyXG4gICAgICAgICAgICBAYW5zd2VyQ2hhbmdlZD1cInVwZGF0ZUFuc3dlcnNcIlxyXG4gICAgICAgICAgICBjbGFzcz1cInF1ZXN0aW9uLWNvbnRhaW5lclwiXHJcbiAgICAgICAgPjwvVHJhbnNpdGlvblF1ZXN0aW9uPlxyXG4gICAgICA8L3RlbXBsYXRlPlxyXG5cclxuICAgIDwvZGl2PlxyXG5cclxuICA8L3RlbXBsYXRlPlxyXG5cclxuICA8ZGl2IGNsYXNzPVwicm93XCI+XHJcbiAgICA8ZGl2IGNsYXNzPVwiY29sXCI+XHJcbiAgICAgIDxidXR0b25cclxuICAgICAgICAgIGNsYXNzPVwiZmxvdy1idG5cIlxyXG4gICAgICAgICAgdHlwZT1cImJ1dHRvblwiXHJcbiAgICAgICAgICBAY2xpY2s9XCJuZXh0XCJcclxuICAgICAgPldlaXRlciZuYnNwOyZuYnNwOyYjODI1MDs8L2J1dHRvbj5cclxuICAgIDwvZGl2PlxyXG4gIDwvZGl2PlxyXG5cclxuPC90ZW1wbGF0ZT5cclxuXHJcbjxzY3JpcHQ+XHJcbmltcG9ydCBTaW5nbGVDaG9pY2VRdWVzdGlvbiBmcm9tIFwiLi9jb21wb25lbnRzL1NpbmdsZUNob2ljZVF1ZXN0aW9uLnZ1ZVwiO1xyXG5pbXBvcnQgTXVsdGlDaG9pY2VRdWVzdGlvbiBmcm9tIFwiLi9jb21wb25lbnRzL011bHRpQ2hvaWNlUXVlc3Rpb24udnVlXCI7XHJcbmltcG9ydCBPcGVuUXVlc3Rpb24gZnJvbSBcIi4vY29tcG9uZW50cy9PcGVuUXVlc3Rpb25cIjtcclxuaW1wb3J0IE1hdHJpeFF1ZXN0aW9uIGZyb20gXCIuL2NvbXBvbmVudHMvTWF0cml4UXVlc3Rpb25cIjtcclxuaW1wb3J0IFNlbWFudGljRGlmZmVyZW50aWFsIGZyb20gXCIuL2NvbXBvbmVudHMvU2VtYW50aWNEaWZmZXJlbnRpYWxcIjtcclxuaW1wb3J0IFRyYW5zaXRpb25RdWVzdGlvbiBmcm9tIFwiLi9jb21wb25lbnRzL1RyYW5zaXRpb25RdWVzdGlvblwiO1xyXG5cclxuZXhwb3J0IGRlZmF1bHQge1xyXG4gIG5hbWU6ICdRQXBwJyxcclxuICBjb21wb25lbnRzOiB7XHJcbiAgICBTaW5nbGVDaG9pY2VRdWVzdGlvbixcclxuICAgIE11bHRpQ2hvaWNlUXVlc3Rpb24sXHJcbiAgICBPcGVuUXVlc3Rpb24sXHJcbiAgICBNYXRyaXhRdWVzdGlvbixcclxuICAgIFNlbWFudGljRGlmZmVyZW50aWFsLFxyXG4gICAgVHJhbnNpdGlvblF1ZXN0aW9uXHJcbiAgfSxcclxuICBwcm9wczoge1xyXG4gICAgcWNvbmZpZzogU3RyaW5nLFxyXG4gICAgYWN0aW9udXJsOiBTdHJpbmcsXHJcbiAgfSxcclxuICBkYXRhKCkge1xyXG4gICAgcmV0dXJuIHtcclxuICAgICAgcV9jb25maWc6IEpTT04ucGFyc2UodGhpcy5xY29uZmlnKSxcclxuICAgICAgYW5zd2Vyczoge30sXHJcbiAgICAgIGN1cnJfaW5kZXg6IDEsXHJcbiAgICAgIG1heF9pbmRleDogMVxyXG4gICAgfVxyXG4gIH0sXHJcbiAgY3JlYXRlZCgpIHtcclxuICAgIHRoaXMuc2V0TWF4SW5kZXgoKTtcclxuICB9LFxyXG4gIG1ldGhvZHM6IHtcclxuICAgIHVwZGF0ZUFuc3dlcnMoZSkge1xyXG4gICAgICB0aGlzLmFuc3dlcnNbZS5pZF0gPSBlLmFuc3dlcnM7XHJcbiAgICB9LFxyXG4gICAgc2V0TWF4SW5kZXgoKSB7XHJcbiAgICAgIGxldCBpbmRpY2VzID0gW107XHJcbiAgICAgIHRoaXMucV9jb25maWcuZm9yRWFjaChxID0+XHJcbiAgICAgICAgICBpbmRpY2VzLnB1c2gocS5pbmRleClcclxuICAgICAgKVxyXG4gICAgICB0aGlzLm1heF9pbmRleCA9IE1hdGgubWF4KC4uLmluZGljZXMpO1xyXG4gICAgfSxcclxuICAgIG5leHQoKSB7XHJcbiAgICAgIGlmICh0aGlzLmN1cnJfaW5kZXggPT0gdGhpcy5tYXhfaW5kZXgpIHtcclxuICAgICAgICB0aGlzLnN1Ym1pdERhdGEoKTtcclxuICAgICAgfSBlbHNlIHtcclxuICAgICAgICB0aGlzLmN1cnJfaW5kZXggKz0gMTtcclxuICAgICAgfVxyXG4gICAgfSxcclxuICAgIHN1Ym1pdERhdGEoKSB7XHJcbiAgICAgIGxldCBmb3JtID0gbmV3IEZvcm1EYXRhKClcclxuICAgICAgZm9ybS5hcHBlbmQoXCJwb3N0X2RhdGFcIiwgSlNPTi5zdHJpbmdpZnkodGhpcy5hbnN3ZXJzKSk7XHJcblxyXG4gICAgICBsZXQgY3NyZiA9IGRvY3VtZW50LnF1ZXJ5U2VsZWN0b3IoXCJpbnB1dFtuYW1lPSdjc3JmbWlkZGxld2FyZXRva2VuJ11cIik7XHJcbiAgICAgIGZvcm0uYXBwZW5kKFwiY3NyZm1pZGRsZXdhcmV0b2tlblwiLCBjc3JmLnZhbHVlKTtcclxuXHJcbiAgICAgIGZldGNoKHRoaXMuYWN0aW9udXJsLCB7bWV0aG9kOiBcIlBPU1RcIiwgYm9keTogZm9ybX0pXHJcbiAgICAgICAgICAudGhlbihyZXNwb25zZSA9PiB7XHJcbiAgICAgICAgICAgIGNvbnNvbGUubG9nKHJlc3BvbnNlKVxyXG4gICAgICAgICAgICBpZiAocmVzcG9uc2UucmVkaXJlY3RlZCkge1xyXG4gICAgICAgICAgICAgIHdpbmRvdy5sb2NhdGlvbi5ocmVmID0gcmVzcG9uc2UudXJsO1xyXG4gICAgICAgICAgICB9XHJcbiAgICAgICAgICB9KVxyXG4gICAgICAgICAgLmNhdGNoKGVyciA9PiB7XHJcbiAgICAgICAgICAgIGNvbnNvbGUuaW5mbyhlcnIpO1xyXG4gICAgICAgICAgfSk7XHJcbiAgICB9XHJcbiAgfVxyXG59XHJcbjwvc2NyaXB0PlxyXG5cclxuPHN0eWxlPlxyXG4jcWFwcCB7XHJcbiAgZm9udC1mYW1pbHk6IEF2ZW5pciwgSGVsdmV0aWNhLCBBcmlhbCwgc2Fucy1zZXJpZjtcclxuICAtd2Via2l0LWZvbnQtc21vb3RoaW5nOiBhbnRpYWxpYXNlZDtcclxuICAtbW96LW9zeC1mb250LXNtb290aGluZzogZ3JheXNjYWxlO1xyXG4gIHRleHQtYWxpZ246IGxlZnQ7XHJcbn1cclxuLnF1ZXN0aW9uLWNvbnRhaW5lciB7XHJcbiAgbWFyZ2luLWJvdHRvbTogNTBweDtcclxufVxyXG48L3N0eWxlPlxyXG4iXSwibmFtZXMiOltdLCJzb3VyY2VSb290IjoiIn0=\n//# sourceURL=webpack-internal:///./node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!./node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./src/QuestionnaireApp.vue?vue&type=script&lang=js\n");

/***/ }),

/***/ "./node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!./node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./src/components/MatrixQuestion.vue?vue&type=script&lang=js":
/*!************************************************************************************************************************************************************************************************!*\
  !*** ./node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!./node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./src/components/MatrixQuestion.vue?vue&type=script&lang=js ***!
  \************************************************************************************************************************************************************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony default export */ __webpack_exports__[\"default\"] = ({\n  name: 'SingleChoiceQuestion',\n  props: ['qid', 'text', 'items', 'scale'],\n  emits: ['answerChanged'],\n  data: function () {\n    return {\n      answer: {}\n    };\n  },\n\n  created() {\n    this.items.forEach(i => {\n      this.answer[i.id] = -99;\n    });\n    this.$emit('answerChanged', {\n      id: this.qid,\n      answers: this.answer\n    });\n  },\n\n  methods: {\n    answerChanged(event) {\n      this.answer[event.target.name] = event.target.value;\n      this.$emit('answerChanged', {\n        id: this.qid,\n        answers: this.answer\n      });\n    }\n\n  }\n});//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi9ub2RlX21vZHVsZXMvYmFiZWwtbG9hZGVyL2xpYi9pbmRleC5qcz8/Y2xvbmVkUnVsZVNldC00MC51c2VbMF0hLi9ub2RlX21vZHVsZXMvdnVlLWxvYWRlci9kaXN0L2luZGV4LmpzPz9ydWxlU2V0WzBdLnVzZVswXSEuL3NyYy9jb21wb25lbnRzL01hdHJpeFF1ZXN0aW9uLnZ1ZT92dWUmdHlwZT1zY3JpcHQmbGFuZz1qcy5qcyIsIm1hcHBpbmdzIjoiO0FBNEJBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBREE7QUFHQTs7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQUE7QUFBQTtBQUFBO0FBQ0E7O0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFBQTtBQUFBO0FBQUE7QUFDQTs7QUFKQTtBQWZBIiwic291cmNlcyI6WyJ3ZWJwYWNrOi8vdnVlX2Zyb250ZW5kLy4vc3JjL2NvbXBvbmVudHMvTWF0cml4UXVlc3Rpb24udnVlPzA1ZmYiXSwic291cmNlc0NvbnRlbnQiOlsiPHRlbXBsYXRlPlxyXG4gIDxkaXY+XHJcblxyXG4gICAgPGRpdiBjbGFzcz1cInN1cnF1ZXN0LXF1ZXN0aW9uLXRleHRcIiB2LWh0bWw9XCJ0ZXh0XCI+PC9kaXY+XHJcblxyXG4gICAgPHRhYmxlIGNsYXNzPVwibXEtdGFibGVcIj5cclxuICAgICAgPHRoZWFkIGNsYXNzPVwibXEtaGVhZGVyXCI+XHJcbiAgICAgIDx0cj5cclxuICAgICAgICA8dGg+PC90aD5cclxuICAgICAgICA8dGggdi1mb3I9XCIocG9pbnQsIGlkKSBpbiBzY2FsZVwiIDprZXk9XCJpZFwiPnt7IHBvaW50LmxhYmVsIH19PC90aD5cclxuICAgICAgPC90cj5cclxuICAgICAgPC90aGVhZD5cclxuICAgICAgPHRib2R5PlxyXG4gICAgICA8dGVtcGxhdGUgdi1mb3I9XCIoaXRlbSwgaWQpIGluIGl0ZW1zXCIgOmtleT1cImlkXCI+XHJcbiAgICAgICAgPHRyPlxyXG4gICAgICAgICAgPHRkIGNsYXNzPVwibXEtdGFibGUtdGQtaXRlbVwiPnt7IGl0ZW0ubGFiZWwgfX08L3RkPlxyXG4gICAgICAgICAgPHRkIHYtZm9yPVwiKHBvaW50LCBpZCkgaW4gc2NhbGVcIiA6a2V5PVwiaWRcIiBjbGFzcz1cIm1xLXRhYmxlLXRkLWlucHV0XCI+XHJcbiAgICAgICAgICAgIDxsYWJlbD48aW5wdXQgdHlwZT1cInJhZGlvXCIgOm5hbWU9XCJpdGVtLmlkXCIgOnZhbHVlPVwicG9pbnQudmFsdWVcIiBAY2hhbmdlPVwiYW5zd2VyQ2hhbmdlZCgkZXZlbnQpXCI+PC9sYWJlbD5cclxuICAgICAgICAgIDwvdGQ+XHJcbiAgICAgICAgPC90cj5cclxuICAgICAgPC90ZW1wbGF0ZT5cclxuICAgICAgPC90Ym9keT5cclxuICAgIDwvdGFibGU+XHJcblxyXG4gIDwvZGl2PlxyXG48L3RlbXBsYXRlPlxyXG5cclxuPHNjcmlwdD5cclxuZXhwb3J0IGRlZmF1bHQge1xyXG4gIG5hbWU6ICdTaW5nbGVDaG9pY2VRdWVzdGlvbicsXHJcbiAgcHJvcHM6IFsncWlkJywgJ3RleHQnLCAnaXRlbXMnLCAnc2NhbGUnXSxcclxuICBlbWl0czogWydhbnN3ZXJDaGFuZ2VkJ10sXHJcbiAgZGF0YTogZnVuY3Rpb24oKSB7XHJcbiAgICByZXR1cm4ge1xyXG4gICAgICBhbnN3ZXI6IHt9XHJcbiAgICB9XHJcbiAgfSxcclxuICBjcmVhdGVkKCkge1xyXG4gICAgdGhpcy5pdGVtcy5mb3JFYWNoKGkgPT4ge1xyXG4gICAgICB0aGlzLmFuc3dlcltpLmlkXSA9IC05OTtcclxuICAgIH0pXHJcbiAgICB0aGlzLiRlbWl0KCdhbnN3ZXJDaGFuZ2VkJywge2lkOiB0aGlzLnFpZCwgYW5zd2VyczogdGhpcy5hbnN3ZXJ9KTtcclxuICB9LFxyXG4gIG1ldGhvZHM6IHtcclxuICAgIGFuc3dlckNoYW5nZWQoZXZlbnQpIHtcclxuICAgICAgdGhpcy5hbnN3ZXJbZXZlbnQudGFyZ2V0Lm5hbWVdID0gZXZlbnQudGFyZ2V0LnZhbHVlO1xyXG4gICAgICB0aGlzLiRlbWl0KCdhbnN3ZXJDaGFuZ2VkJywge2lkOiB0aGlzLnFpZCwgYW5zd2VyczogdGhpcy5hbnN3ZXJ9KTtcclxuICAgIH1cclxuICB9XHJcbn1cclxuPC9zY3JpcHQ+XHJcblxyXG48c3R5bGUgc2NvcGVkPlxyXG5cclxuPC9zdHlsZT4iXSwibmFtZXMiOltdLCJzb3VyY2VSb290IjoiIn0=\n//# sourceURL=webpack-internal:///./node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!./node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./src/components/MatrixQuestion.vue?vue&type=script&lang=js\n");

/***/ }),

/***/ "./node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!./node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./src/components/MultiChoiceQuestion.vue?vue&type=script&lang=js":
/*!*****************************************************************************************************************************************************************************************************!*\
  !*** ./node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!./node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./src/components/MultiChoiceQuestion.vue?vue&type=script&lang=js ***!
  \*****************************************************************************************************************************************************************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony default export */ __webpack_exports__[\"default\"] = ({\n  name: 'MultiChoiceQuestion',\n  props: ['qid', 'text', 'items'],\n  emits: ['answerChanged'],\n  data: function () {\n    return {\n      answer: {}\n    };\n  },\n\n  created() {\n    this.items.forEach(i => {\n      this.answer[i.id] = false;\n    });\n    this.$emit('answerChanged', {\n      id: this.qid,\n      answers: this.answer\n    });\n  },\n\n  methods: {\n    answerChanged(event) {\n      this.answer[event.target.name] = event.target.checked;\n      this.$emit('answerChanged', {\n        id: this.qid,\n        answers: this.answer\n      });\n    }\n\n  }\n});//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi9ub2RlX21vZHVsZXMvYmFiZWwtbG9hZGVyL2xpYi9pbmRleC5qcz8/Y2xvbmVkUnVsZVNldC00MC51c2VbMF0hLi9ub2RlX21vZHVsZXMvdnVlLWxvYWRlci9kaXN0L2luZGV4LmpzPz9ydWxlU2V0WzBdLnVzZVswXSEuL3NyYy9jb21wb25lbnRzL011bHRpQ2hvaWNlUXVlc3Rpb24udnVlP3Z1ZSZ0eXBlPXNjcmlwdCZsYW5nPWpzLmpzIiwibWFwcGluZ3MiOiI7QUFlQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQURBO0FBR0E7O0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUFBO0FBQUE7QUFBQTtBQUNBOztBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQUE7QUFBQTtBQUFBO0FBQ0E7O0FBSkE7QUFmQSIsInNvdXJjZXMiOlsid2VicGFjazovL3Z1ZV9mcm9udGVuZC8uL3NyYy9jb21wb25lbnRzL011bHRpQ2hvaWNlUXVlc3Rpb24udnVlPzAwODgiXSwic291cmNlc0NvbnRlbnQiOlsiPHRlbXBsYXRlPlxyXG4gIDxkaXY+XHJcbiAgICA8ZGl2IGNsYXNzPVwic3VycXVlc3QtcXVlc3Rpb24tdGV4dFwiIHYtaHRtbD1cInRleHRcIj48L2Rpdj5cclxuICAgIDxkaXYgdi1mb3I9XCIoaXRlbSwgaWQpIGluIGl0ZW1zXCIgOmtleT1cImlkXCIgY2xhc3M9XCJzdXJxdWVzdC1ncS1yZXNwb25zZSBzdXJxdWVzdC1jcS1yZXNwb25zZVwiPlxyXG4gICAgICA8ZGl2IGNsYXNzPVwic3VycXVlc3QtY2hvaWNlLWl0ZW0gZm9ybS1jaGVja1wiPlxyXG4gICAgICAgIDxsYWJlbCBjbGFzcz1cImZvcm0tY2hlY2stbGFiZWwgcmItY2ItbGFiZWxcIj5cclxuICAgICAgICAgIDxpbnB1dCBjbGFzcz1cImZvcm0tY2hlY2staW5wdXRcIiB0eXBlPVwiY2hlY2tib3hcIiA6bmFtZT1cIml0ZW0uaWRcIiA6dmFsdWU9XCJpdGVtLnZhbHVlXCIgQGNoYW5nZT1cImFuc3dlckNoYW5nZWQoJGV2ZW50KVwiPlxyXG4gICAgICAgICAge3sgaXRlbS5sYWJlbCB9fVxyXG4gICAgICAgIDwvbGFiZWw+XHJcbiAgICAgIDwvZGl2PlxyXG4gICAgPC9kaXY+XHJcbiAgPC9kaXY+XHJcbjwvdGVtcGxhdGU+XHJcblxyXG48c2NyaXB0PlxyXG5leHBvcnQgZGVmYXVsdCB7XHJcbiAgbmFtZTogJ011bHRpQ2hvaWNlUXVlc3Rpb24nLFxyXG4gIHByb3BzOiBbJ3FpZCcsICd0ZXh0JywgJ2l0ZW1zJ10sXHJcbiAgZW1pdHM6IFsnYW5zd2VyQ2hhbmdlZCddLFxyXG4gIGRhdGE6IGZ1bmN0aW9uKCkge1xyXG4gICAgcmV0dXJuIHtcclxuICAgICAgYW5zd2VyOiB7fVxyXG4gICAgfVxyXG4gIH0sXHJcbiAgY3JlYXRlZCgpIHtcclxuICAgIHRoaXMuaXRlbXMuZm9yRWFjaChpID0+IHtcclxuICAgICAgdGhpcy5hbnN3ZXJbaS5pZF0gPSBmYWxzZTtcclxuICAgIH0pXHJcbiAgICB0aGlzLiRlbWl0KCdhbnN3ZXJDaGFuZ2VkJywge2lkOiB0aGlzLnFpZCwgYW5zd2VyczogdGhpcy5hbnN3ZXJ9KTtcclxuICB9LFxyXG4gIG1ldGhvZHM6IHtcclxuICAgIGFuc3dlckNoYW5nZWQoZXZlbnQpIHtcclxuICAgICAgdGhpcy5hbnN3ZXJbZXZlbnQudGFyZ2V0Lm5hbWVdID0gZXZlbnQudGFyZ2V0LmNoZWNrZWQ7XHJcbiAgICAgIHRoaXMuJGVtaXQoJ2Fuc3dlckNoYW5nZWQnLCB7aWQ6IHRoaXMucWlkLCBhbnN3ZXJzOiB0aGlzLmFuc3dlcn0pO1xyXG4gICAgfVxyXG4gIH1cclxufVxyXG48L3NjcmlwdD5cclxuXHJcbjxzdHlsZSBzY29wZWQ+XHJcblxyXG48L3N0eWxlPiJdLCJuYW1lcyI6W10sInNvdXJjZVJvb3QiOiIifQ==\n//# sourceURL=webpack-internal:///./node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!./node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./src/components/MultiChoiceQuestion.vue?vue&type=script&lang=js\n");

/***/ }),

/***/ "./node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!./node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./src/components/OpenQuestion.vue?vue&type=script&lang=js":
/*!**********************************************************************************************************************************************************************************************!*\
  !*** ./node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!./node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./src/components/OpenQuestion.vue?vue&type=script&lang=js ***!
  \**********************************************************************************************************************************************************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony default export */ __webpack_exports__[\"default\"] = ({\n  name: 'OpenQuestion',\n  props: ['qid', 'text', 'options'],\n  emits: ['answerChanged'],\n  data: function () {\n    return {\n      answer: '-99'\n    };\n  },\n\n  created() {\n    this.$emit('answerChanged', {\n      id: this.qid,\n      answers: this.answer\n    });\n  },\n\n  methods: {\n    answerChanged(event) {\n      this.answer = event.target.value;\n      this.$emit('answerChanged', {\n        id: this.qid,\n        answers: this.answer\n      });\n    }\n\n  }\n});//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi9ub2RlX21vZHVsZXMvYmFiZWwtbG9hZGVyL2xpYi9pbmRleC5qcz8/Y2xvbmVkUnVsZVNldC00MC51c2VbMF0hLi9ub2RlX21vZHVsZXMvdnVlLWxvYWRlci9kaXN0L2luZGV4LmpzPz9ydWxlU2V0WzBdLnVzZVswXSEuL3NyYy9jb21wb25lbnRzL09wZW5RdWVzdGlvbi52dWU/dnVlJnR5cGU9c2NyaXB0Jmxhbmc9anMuanMiLCJtYXBwaW5ncyI6IjtBQVdBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBREE7QUFHQTs7QUFDQTtBQUNBO0FBQUE7QUFBQTtBQUFBO0FBQ0E7O0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFBQTtBQUFBO0FBQUE7QUFDQTs7QUFKQTtBQVpBIiwic291cmNlcyI6WyJ3ZWJwYWNrOi8vdnVlX2Zyb250ZW5kLy4vc3JjL2NvbXBvbmVudHMvT3BlblF1ZXN0aW9uLnZ1ZT83NTQ1Il0sInNvdXJjZXNDb250ZW50IjpbIjx0ZW1wbGF0ZT5cclxuICA8ZGl2PlxyXG4gICAgPGRpdiBjbGFzcz1cInN1cnF1ZXN0LXF1ZXN0aW9uLXRleHRcIiB2LWh0bWw9XCJ0ZXh0XCI+PC9kaXY+XHJcbiAgICA8ZGl2IGNsYXNzPVwic3VycXVlc3QtZ3EtcmVzcG9uc2VcIj5cclxuICAgICAgPGlucHV0IGNsYXNzPVwic3VycXVlc3Qtb3EtdGV4dGxpbmVcIiB2LWlmPVwib3B0aW9ucy5kaXNwbGF5ID09ICdzbWFsbCdcIiB0eXBlPVwidGV4dFwiIDpuYW1lPVwicWlkXCIgQGNoYW5nZT1cImFuc3dlckNoYW5nZWQoJGV2ZW50KVwiPlxyXG4gICAgICA8dGV4dGFyZWEgY2xhc3M9XCJzdXJxdWVzdC1vcS10ZXh0YXJlYVwiIHYtaWY9XCJvcHRpb25zLmRpc3BsYXkgPT0gJ2xhcmdlJ1wiIHR5cGU9XCJ0ZXh0XCIgOm5hbWU9XCJxaWRcIiBAY2hhbmdlPVwiYW5zd2VyQ2hhbmdlZCgkZXZlbnQpXCI+PC90ZXh0YXJlYT5cclxuICAgIDwvZGl2PlxyXG4gIDwvZGl2PlxyXG48L3RlbXBsYXRlPlxyXG5cclxuPHNjcmlwdD5cclxuZXhwb3J0IGRlZmF1bHQge1xyXG4gIG5hbWU6ICdPcGVuUXVlc3Rpb24nLFxyXG4gIHByb3BzOiBbJ3FpZCcsICd0ZXh0JywgJ29wdGlvbnMnXSxcclxuICBlbWl0czogWydhbnN3ZXJDaGFuZ2VkJ10sXHJcbiAgZGF0YTogZnVuY3Rpb24oKSB7XHJcbiAgICByZXR1cm4ge1xyXG4gICAgICBhbnN3ZXI6ICctOTknXHJcbiAgICB9XHJcbiAgfSxcclxuICBjcmVhdGVkKCkge1xyXG4gICAgdGhpcy4kZW1pdCgnYW5zd2VyQ2hhbmdlZCcsIHtpZDogdGhpcy5xaWQsIGFuc3dlcnM6IHRoaXMuYW5zd2VyfSk7XHJcbiAgfSxcclxuICBtZXRob2RzOiB7XHJcbiAgICBhbnN3ZXJDaGFuZ2VkKGV2ZW50KSB7XHJcbiAgICAgIHRoaXMuYW5zd2VyID0gZXZlbnQudGFyZ2V0LnZhbHVlO1xyXG4gICAgICB0aGlzLiRlbWl0KCdhbnN3ZXJDaGFuZ2VkJywge2lkOiB0aGlzLnFpZCwgYW5zd2VyczogdGhpcy5hbnN3ZXJ9KTtcclxuICAgIH1cclxuICB9XHJcbn1cclxuPC9zY3JpcHQ+XHJcblxyXG48c3R5bGUgc2NvcGVkPlxyXG5cclxuPC9zdHlsZT4iXSwibmFtZXMiOltdLCJzb3VyY2VSb290IjoiIn0=\n//# sourceURL=webpack-internal:///./node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!./node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./src/components/OpenQuestion.vue?vue&type=script&lang=js\n");

/***/ }),

/***/ "./node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!./node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./src/components/SemanticDifferential.vue?vue&type=script&lang=js":
/*!******************************************************************************************************************************************************************************************************!*\
  !*** ./node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!./node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./src/components/SemanticDifferential.vue?vue&type=script&lang=js ***!
  \******************************************************************************************************************************************************************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony default export */ __webpack_exports__[\"default\"] = ({\n  name: 'SingleChoiceQuestion',\n  props: ['qid', 'text', 'items', 'scale'],\n  emits: ['answerChanged'],\n  data: function () {\n    return {\n      answer: {}\n    };\n  },\n\n  created() {\n    this.items.forEach(i => {\n      this.answer[i.id] = -99;\n    });\n    this.$emit('answerChanged', {\n      id: this.qid,\n      answers: this.answer\n    });\n  },\n\n  methods: {\n    answerChanged(event) {\n      this.answer[event.target.name] = event.target.value;\n      this.$emit('answerChanged', {\n        id: this.qid,\n        answers: this.answer\n      });\n    }\n\n  }\n});//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi9ub2RlX21vZHVsZXMvYmFiZWwtbG9hZGVyL2xpYi9pbmRleC5qcz8/Y2xvbmVkUnVsZVNldC00MC51c2VbMF0hLi9ub2RlX21vZHVsZXMvdnVlLWxvYWRlci9kaXN0L2luZGV4LmpzPz9ydWxlU2V0WzBdLnVzZVswXSEuL3NyYy9jb21wb25lbnRzL1NlbWFudGljRGlmZmVyZW50aWFsLnZ1ZT92dWUmdHlwZT1zY3JpcHQmbGFuZz1qcy5qcyIsIm1hcHBpbmdzIjoiO0FBOEJBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBREE7QUFHQTs7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQUE7QUFBQTtBQUFBO0FBQ0E7O0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFBQTtBQUFBO0FBQUE7QUFDQTs7QUFKQTtBQWZBIiwic291cmNlcyI6WyJ3ZWJwYWNrOi8vdnVlX2Zyb250ZW5kLy4vc3JjL2NvbXBvbmVudHMvU2VtYW50aWNEaWZmZXJlbnRpYWwudnVlPzQxNTYiXSwic291cmNlc0NvbnRlbnQiOlsiPHRlbXBsYXRlPlxyXG4gIDxkaXY+XHJcblxyXG4gICAgPGRpdiBjbGFzcz1cInN1cnF1ZXN0LXF1ZXN0aW9uLXRleHRcIiB2LWh0bWw9XCJ0ZXh0XCI+PC9kaXY+XHJcblxyXG4gICAgPGRpdiBjbGFzcz1cInN1cnF1ZXN0LWdxLXJlc3BvbnNlXCI+XHJcbiAgICAgIDx0YWJsZSBjbGFzcz1cImRxLXRhYmxlXCI+XHJcbiAgICAgICAgPHRoZWFkPlxyXG4gICAgICAgIDx0cj5cclxuICAgICAgICAgIDx0aD48L3RoPlxyXG4gICAgICAgICAgPHRoIHYtZm9yPVwiKHBvaW50LCBpZCkgaW4gc2NhbGVcIiA6a2V5PVwiaWRcIj57eyBwb2ludC5sYWJlbCB9fTwvdGg+XHJcbiAgICAgICAgICA8dGg+PC90aD5cclxuICAgICAgICA8L3RyPlxyXG4gICAgICAgIDwvdGhlYWQ+XHJcbiAgICAgICAgPHRib2R5PlxyXG4gICAgICAgIDx0ciB2LWZvcj1cIihpdGVtLCBpZCkgaW4gaXRlbXNcIiA6a2V5PVwiaWRcIj5cclxuICAgICAgICAgIDx0ZCBjbGFzcz1cIm1xLXRhYmxlLXRkLWl0ZW0gZHEtdGFibGUtdGQtaXRlbS1sZWZ0XCI+e3sgaXRlbS5sYWJlbCB9fTwvdGQ+XHJcbiAgICAgICAgICA8dGQgdi1mb3I9XCIocG9pbnQsIGlkKSBpbiBzY2FsZVwiIDprZXk9XCJpZFwiIGNsYXNzPVwiZHEtdGFibGUtdGQtaW5wdXRcIj5cclxuICAgICAgICAgICAgPGxhYmVsPjxpbnB1dCB0eXBlPVwicmFkaW9cIiA6bmFtZT1cIml0ZW0uaWRcIiA6dmFsdWU9XCJwb2ludC52YWx1ZVwiIEBjaGFuZ2U9XCJhbnN3ZXJDaGFuZ2VkKCRldmVudClcIj48L2xhYmVsPlxyXG4gICAgICAgICAgPC90ZD5cclxuICAgICAgICAgIDx0ZCBjbGFzcz1cIm1xLXRhYmxlLXRkLWl0ZW0gZHEtdGFibGUtdGQtaXRlbS1yaWdodFwiPnt7IGl0ZW0ubGFiZWxfYWx0IH19PC90ZD5cclxuICAgICAgICA8L3RyPlxyXG4gICAgICAgIDwvdGJvZHk+XHJcbiAgICAgIDwvdGFibGU+XHJcbiAgICA8L2Rpdj5cclxuXHJcbiAgPC9kaXY+XHJcbjwvdGVtcGxhdGU+XHJcblxyXG48c2NyaXB0PlxyXG5leHBvcnQgZGVmYXVsdCB7XHJcbiAgbmFtZTogJ1NpbmdsZUNob2ljZVF1ZXN0aW9uJyxcclxuICBwcm9wczogWydxaWQnLCAndGV4dCcsICdpdGVtcycsICdzY2FsZSddLFxyXG4gIGVtaXRzOiBbJ2Fuc3dlckNoYW5nZWQnXSxcclxuICBkYXRhOiBmdW5jdGlvbigpIHtcclxuICAgIHJldHVybiB7XHJcbiAgICAgIGFuc3dlcjoge31cclxuICAgIH1cclxuICB9LFxyXG4gIGNyZWF0ZWQoKSB7XHJcbiAgICB0aGlzLml0ZW1zLmZvckVhY2goaSA9PiB7XHJcbiAgICAgIHRoaXMuYW5zd2VyW2kuaWRdID0gLTk5O1xyXG4gICAgfSlcclxuICAgIHRoaXMuJGVtaXQoJ2Fuc3dlckNoYW5nZWQnLCB7aWQ6IHRoaXMucWlkLCBhbnN3ZXJzOiB0aGlzLmFuc3dlcn0pO1xyXG4gIH0sXHJcbiAgbWV0aG9kczoge1xyXG4gICAgYW5zd2VyQ2hhbmdlZChldmVudCkge1xyXG4gICAgICB0aGlzLmFuc3dlcltldmVudC50YXJnZXQubmFtZV0gPSBldmVudC50YXJnZXQudmFsdWU7XHJcbiAgICAgIHRoaXMuJGVtaXQoJ2Fuc3dlckNoYW5nZWQnLCB7aWQ6IHRoaXMucWlkLCBhbnN3ZXJzOiB0aGlzLmFuc3dlcn0pO1xyXG4gICAgfVxyXG4gIH1cclxufVxyXG48L3NjcmlwdD5cclxuXHJcbjxzdHlsZSBzY29wZWQ+XHJcblxyXG48L3N0eWxlPiJdLCJuYW1lcyI6W10sInNvdXJjZVJvb3QiOiIifQ==\n//# sourceURL=webpack-internal:///./node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!./node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./src/components/SemanticDifferential.vue?vue&type=script&lang=js\n");

/***/ }),

/***/ "./node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!./node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./src/components/SingleChoiceQuestion.vue?vue&type=script&lang=js":
/*!******************************************************************************************************************************************************************************************************!*\
  !*** ./node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!./node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./src/components/SingleChoiceQuestion.vue?vue&type=script&lang=js ***!
  \******************************************************************************************************************************************************************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony default export */ __webpack_exports__[\"default\"] = ({\n  name: 'SingleChoiceQuestion',\n  props: ['qid', 'text', 'items'],\n  emits: ['answerChanged'],\n  data: function () {\n    return {\n      answer: ''\n    };\n  },\n\n  created() {\n    this.answer = -99;\n    this.$emit('answerChanged', {\n      id: this.qid,\n      answers: this.answer\n    });\n  },\n\n  methods: {\n    answerChanged(event) {\n      this.answer = event.target.value;\n      this.$emit('answerChanged', {\n        id: this.qid,\n        answers: this.answer\n      });\n    }\n\n  }\n});//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi9ub2RlX21vZHVsZXMvYmFiZWwtbG9hZGVyL2xpYi9pbmRleC5qcz8/Y2xvbmVkUnVsZVNldC00MC51c2VbMF0hLi9ub2RlX21vZHVsZXMvdnVlLWxvYWRlci9kaXN0L2luZGV4LmpzPz9ydWxlU2V0WzBdLnVzZVswXSEuL3NyYy9jb21wb25lbnRzL1NpbmdsZUNob2ljZVF1ZXN0aW9uLnZ1ZT92dWUmdHlwZT1zY3JpcHQmbGFuZz1qcy5qcyIsIm1hcHBpbmdzIjoiO0FBeUJBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBREE7QUFHQTs7QUFDQTtBQUNBO0FBQ0E7QUFBQTtBQUFBO0FBQUE7QUFDQTs7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUFBO0FBQUE7QUFBQTtBQUNBOztBQUpBO0FBYkEiLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly92dWVfZnJvbnRlbmQvLi9zcmMvY29tcG9uZW50cy9TaW5nbGVDaG9pY2VRdWVzdGlvbi52dWU/MmExZCJdLCJzb3VyY2VzQ29udGVudCI6WyI8dGVtcGxhdGU+XHJcbiAgPGRpdj5cclxuICAgIDxkaXYgY2xhc3M9XCJzdXJxdWVzdC1xdWVzdGlvbi10ZXh0XCIgdi1odG1sPVwidGV4dFwiPjwvZGl2PlxyXG4gICAgPGRpdiBjbGFzcz1cInN1cnF1ZXN0LWdxLXJlc3BvbnNlIHN1cnF1ZXN0LWNxLXJlc3BvbnNlXCI+XHJcbiAgICAgIDxkaXYgdi1mb3I9XCIoaXRlbSwgaWQpIGluIGl0ZW1zXCIgOmtleT1cImlkXCIgY2xhc3M9XCJzdXJxdWVzdC1jaG9pY2UtaXRlbSBmb3JtLWNoZWNrXCI+XHJcbiAgICAgICAgPGxhYmVsIGNsYXNzPVwiZm9ybS1jaGVjay1sYWJlbCByYi1jYi1sYWJlbFwiPlxyXG4gICAgICAgICAgPGlucHV0IGNsYXNzPVwiZm9ybS1jaGVjay1pbnB1dFwiIHR5cGU9XCJyYWRpb1wiIDpkYXRhaWQ9XCJxaWRcIiA6bmFtZT1cIidxLScgKyBxaWRcIiA6dmFsdWU9XCJpdGVtLnZhbHVlXCIgQGNoYW5nZT1cImFuc3dlckNoYW5nZWQoJGV2ZW50KVwiPlxyXG4gICAgICAgICAge3sgaXRlbS5sYWJlbCB9fVxyXG4gICAgICAgIDwvbGFiZWw+XHJcbiAgICAgIDwvZGl2PlxyXG4gICAgPC9kaXY+XHJcbiAgPC9kaXY+XHJcblxyXG4gIDwhLS0gQWRkaXRpb25hbCBkaXNwbGF5IG9wdGlvbiBhcyBkcm9wZG93biBzZWxlY3Q6XHJcbiAgPGRpdj5cclxuICAgIDxkaXYgOnJlZl9mb3I9XCJxaWRcIj57eyB0ZXh0IH19PC9kaXY+XHJcbiAgICA8c2VsZWN0IDppZD1cInFpZFwiIDpuYW1lPVwicWlkXCIgY2xhc3M9XCJmb3JtLWNvbnRyb2xcIiBAY2hhbmdlPVwiYW5zd2VyQ2hhbmdlZCgkZXZlbnQpXCI+XHJcbiAgICAgIDxvcHRpb24gc2VsZWN0ZWQgZGlzYWJsZWQ+Q2hvb3NlPC9vcHRpb24+XHJcbiAgICAgIDxvcHRpb24gdi1mb3I9XCIoaXRlbSwgaWQpIGluIGl0ZW1zXCIgOmtleT1cImlkXCIgOnZhbHVlPVwiaXRlbS52YWx1ZVwiPnt7IGl0ZW0ubGFiZWwgfX08L29wdGlvbj5cclxuICAgIDwvc2VsZWN0PlxyXG4gIDwvZGl2PlxyXG4gIC0tPlxyXG48L3RlbXBsYXRlPlxyXG5cclxuPHNjcmlwdD5cclxuZXhwb3J0IGRlZmF1bHQge1xyXG4gIG5hbWU6ICdTaW5nbGVDaG9pY2VRdWVzdGlvbicsXHJcbiAgcHJvcHM6IFsncWlkJywgJ3RleHQnLCAnaXRlbXMnXSxcclxuICBlbWl0czogWydhbnN3ZXJDaGFuZ2VkJ10sXHJcbiAgZGF0YTogZnVuY3Rpb24oKSB7XHJcbiAgICByZXR1cm4ge1xyXG4gICAgICBhbnN3ZXI6ICcnXHJcbiAgICB9XHJcbiAgfSxcclxuICBjcmVhdGVkKCkge1xyXG4gICAgdGhpcy5hbnN3ZXIgPSAtOTk7XHJcbiAgICB0aGlzLiRlbWl0KCdhbnN3ZXJDaGFuZ2VkJywge2lkOiB0aGlzLnFpZCwgYW5zd2VyczogdGhpcy5hbnN3ZXJ9KTtcclxuICB9LFxyXG4gIG1ldGhvZHM6IHtcclxuICAgIGFuc3dlckNoYW5nZWQoZXZlbnQpIHtcclxuICAgICAgdGhpcy5hbnN3ZXIgPSBldmVudC50YXJnZXQudmFsdWU7XHJcbiAgICAgIHRoaXMuJGVtaXQoJ2Fuc3dlckNoYW5nZWQnLCB7aWQ6IHRoaXMucWlkLCBhbnN3ZXJzOiB0aGlzLmFuc3dlcn0pO1xyXG4gICAgfVxyXG4gIH1cclxufVxyXG48L3NjcmlwdD5cclxuXHJcbjxzdHlsZSBzY29wZWQ+XHJcblxyXG48L3N0eWxlPiJdLCJuYW1lcyI6W10sInNvdXJjZVJvb3QiOiIifQ==\n//# sourceURL=webpack-internal:///./node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!./node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./src/components/SingleChoiceQuestion.vue?vue&type=script&lang=js\n");

/***/ }),

/***/ "./node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!./node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./src/components/TransitionQuestion.vue?vue&type=script&lang=js":
/*!****************************************************************************************************************************************************************************************************!*\
  !*** ./node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!./node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./src/components/TransitionQuestion.vue?vue&type=script&lang=js ***!
  \****************************************************************************************************************************************************************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony default export */ __webpack_exports__[\"default\"] = ({\n  name: \"TransitionQuestion\",\n  props: ['text']\n});//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi9ub2RlX21vZHVsZXMvYmFiZWwtbG9hZGVyL2xpYi9pbmRleC5qcz8/Y2xvbmVkUnVsZVNldC00MC51c2VbMF0hLi9ub2RlX21vZHVsZXMvdnVlLWxvYWRlci9kaXN0L2luZGV4LmpzPz9ydWxlU2V0WzBdLnVzZVswXSEuL3NyYy9jb21wb25lbnRzL1RyYW5zaXRpb25RdWVzdGlvbi52dWU/dnVlJnR5cGU9c2NyaXB0Jmxhbmc9anMuanMiLCJtYXBwaW5ncyI6IjtBQU9BO0FBQ0E7QUFDQTtBQUZBIiwic291cmNlcyI6WyJ3ZWJwYWNrOi8vdnVlX2Zyb250ZW5kLy4vc3JjL2NvbXBvbmVudHMvVHJhbnNpdGlvblF1ZXN0aW9uLnZ1ZT8wMTllIl0sInNvdXJjZXNDb250ZW50IjpbIjx0ZW1wbGF0ZT5cclxuICA8ZGl2PlxyXG4gICAgPGRpdiBjbGFzcz1cInN1cnF1ZXN0LXF1ZXN0aW9uLXRleHRcIiB2LWh0bWw9XCJ0ZXh0XCI+PC9kaXY+XHJcbiAgPC9kaXY+XHJcbjwvdGVtcGxhdGU+XHJcblxyXG48c2NyaXB0PlxyXG5leHBvcnQgZGVmYXVsdCB7XHJcbiAgbmFtZTogXCJUcmFuc2l0aW9uUXVlc3Rpb25cIixcclxuICBwcm9wczogWyd0ZXh0J10sXHJcbn1cclxuPC9zY3JpcHQ+XHJcblxyXG48c3R5bGUgc2NvcGVkPlxyXG5cclxuPC9zdHlsZT4iXSwibmFtZXMiOltdLCJzb3VyY2VSb290IjoiIn0=\n//# sourceURL=webpack-internal:///./node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!./node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./src/components/TransitionQuestion.vue?vue&type=script&lang=js\n");

/***/ }),

/***/ "./node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!./node_modules/vue-loader/dist/templateLoader.js??ruleSet[1].rules[3]!./node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./src/QuestionnaireApp.vue?vue&type=template&id=2f351a77":
/*!*******************************************************************************************************************************************************************************************************************************************************************!*\
  !*** ./node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!./node_modules/vue-loader/dist/templateLoader.js??ruleSet[1].rules[3]!./node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./src/QuestionnaireApp.vue?vue&type=template&id=2f351a77 ***!
  \*******************************************************************************************************************************************************************************************************************************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   \"render\": function() { return /* binding */ render; }\n/* harmony export */ });\n/* harmony import */ var vue__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! vue */ \"./node_modules/vue/dist/vue.esm-bundler.js\");\n\nconst _hoisted_1 = {\n  class: \"row\"\n};\nconst _hoisted_2 = {\n  class: \"col\"\n};\nfunction render(_ctx, _cache, $props, $setup, $data, $options) {\n  const _component_SingleChoiceQuestion = (0,vue__WEBPACK_IMPORTED_MODULE_0__.resolveComponent)(\"SingleChoiceQuestion\");\n\n  const _component_MultiChoiceQuestion = (0,vue__WEBPACK_IMPORTED_MODULE_0__.resolveComponent)(\"MultiChoiceQuestion\");\n\n  const _component_OpenQuestion = (0,vue__WEBPACK_IMPORTED_MODULE_0__.resolveComponent)(\"OpenQuestion\");\n\n  const _component_MatrixQuestion = (0,vue__WEBPACK_IMPORTED_MODULE_0__.resolveComponent)(\"MatrixQuestion\");\n\n  const _component_SemanticDifferential = (0,vue__WEBPACK_IMPORTED_MODULE_0__.resolveComponent)(\"SemanticDifferential\");\n\n  const _component_TransitionQuestion = (0,vue__WEBPACK_IMPORTED_MODULE_0__.resolveComponent)(\"TransitionQuestion\");\n\n  return (0,vue__WEBPACK_IMPORTED_MODULE_0__.openBlock)(), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementBlock)(vue__WEBPACK_IMPORTED_MODULE_0__.Fragment, null, [((0,vue__WEBPACK_IMPORTED_MODULE_0__.openBlock)(true), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementBlock)(vue__WEBPACK_IMPORTED_MODULE_0__.Fragment, null, (0,vue__WEBPACK_IMPORTED_MODULE_0__.renderList)($data.q_config, (question, id) => {\n    return (0,vue__WEBPACK_IMPORTED_MODULE_0__.withDirectives)(((0,vue__WEBPACK_IMPORTED_MODULE_0__.openBlock)(), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementBlock)(\"div\", {\n      key: id\n    }, [question.type == 'single_choice' ? ((0,vue__WEBPACK_IMPORTED_MODULE_0__.openBlock)(), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createBlock)(_component_SingleChoiceQuestion, {\n      key: 0,\n      qid: question.question,\n      text: question.text,\n      items: question.items,\n      onAnswerChanged: $options.updateAnswers,\n      class: \"question-container\"\n    }, null, 8\n    /* PROPS */\n    , [\"qid\", \"text\", \"items\", \"onAnswerChanged\"])) : (0,vue__WEBPACK_IMPORTED_MODULE_0__.createCommentVNode)(\"v-if\", true), question.type == 'multi_choice' ? ((0,vue__WEBPACK_IMPORTED_MODULE_0__.openBlock)(), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createBlock)(_component_MultiChoiceQuestion, {\n      key: 1,\n      qid: question.question,\n      text: question.text,\n      items: question.items,\n      onAnswerChanged: $options.updateAnswers,\n      class: \"question-container\"\n    }, null, 8\n    /* PROPS */\n    , [\"qid\", \"text\", \"items\", \"onAnswerChanged\"])) : (0,vue__WEBPACK_IMPORTED_MODULE_0__.createCommentVNode)(\"v-if\", true), question.type == 'open' ? ((0,vue__WEBPACK_IMPORTED_MODULE_0__.openBlock)(), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createBlock)(_component_OpenQuestion, {\n      key: 2,\n      qid: question.question,\n      text: question.text,\n      options: question.options,\n      onAnswerChanged: $options.updateAnswers,\n      class: \"question-container\"\n    }, null, 8\n    /* PROPS */\n    , [\"qid\", \"text\", \"options\", \"onAnswerChanged\"])) : (0,vue__WEBPACK_IMPORTED_MODULE_0__.createCommentVNode)(\"v-if\", true), question.type == 'matrix' ? ((0,vue__WEBPACK_IMPORTED_MODULE_0__.openBlock)(), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createBlock)(_component_MatrixQuestion, {\n      key: 3,\n      qid: question.question,\n      text: question.text,\n      items: question.items,\n      scale: question.scale,\n      onAnswerChanged: $options.updateAnswers,\n      class: \"question-container\"\n    }, null, 8\n    /* PROPS */\n    , [\"qid\", \"text\", \"items\", \"scale\", \"onAnswerChanged\"])) : (0,vue__WEBPACK_IMPORTED_MODULE_0__.createCommentVNode)(\"v-if\", true), question.type == 'semantic_diff' ? ((0,vue__WEBPACK_IMPORTED_MODULE_0__.openBlock)(), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createBlock)(_component_SemanticDifferential, {\n      key: 4,\n      qid: question.question,\n      text: question.text,\n      items: question.items,\n      scale: question.scale,\n      onAnswerChanged: $options.updateAnswers,\n      class: \"question-container\"\n    }, null, 8\n    /* PROPS */\n    , [\"qid\", \"text\", \"items\", \"scale\", \"onAnswerChanged\"])) : (0,vue__WEBPACK_IMPORTED_MODULE_0__.createCommentVNode)(\"v-if\", true), question.type == 'transition' ? ((0,vue__WEBPACK_IMPORTED_MODULE_0__.openBlock)(), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createBlock)(_component_TransitionQuestion, {\n      key: 5,\n      text: question.text,\n      onAnswerChanged: $options.updateAnswers,\n      class: \"question-container\"\n    }, null, 8\n    /* PROPS */\n    , [\"text\", \"onAnswerChanged\"])) : (0,vue__WEBPACK_IMPORTED_MODULE_0__.createCommentVNode)(\"v-if\", true)], 512\n    /* NEED_PATCH */\n    )), [[vue__WEBPACK_IMPORTED_MODULE_0__.vShow, $data.curr_index == question.index]]);\n  }), 128\n  /* KEYED_FRAGMENT */\n  )), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementVNode)(\"div\", _hoisted_1, [(0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementVNode)(\"div\", _hoisted_2, [(0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementVNode)(\"button\", {\n    class: \"flow-btn\",\n    type: \"button\",\n    onClick: _cache[0] || (_cache[0] = (...args) => $options.next && $options.next(...args))\n  }, \"Weiter  ›\")])])], 64\n  /* STABLE_FRAGMENT */\n  );\n}//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi9ub2RlX21vZHVsZXMvYmFiZWwtbG9hZGVyL2xpYi9pbmRleC5qcz8/Y2xvbmVkUnVsZVNldC00MC51c2VbMF0hLi9ub2RlX21vZHVsZXMvdnVlLWxvYWRlci9kaXN0L3RlbXBsYXRlTG9hZGVyLmpzPz9ydWxlU2V0WzFdLnJ1bGVzWzNdIS4vbm9kZV9tb2R1bGVzL3Z1ZS1sb2FkZXIvZGlzdC9pbmRleC5qcz8/cnVsZVNldFswXS51c2VbMF0hLi9zcmMvUXVlc3Rpb25uYWlyZUFwcC52dWU/dnVlJnR5cGU9dGVtcGxhdGUmaWQ9MmYzNTFhNzcuanMiLCJtYXBwaW5ncyI6Ijs7Ozs7OztBQW9FQTs7O0FBQ0E7Ozs7Ozs7Ozs7Ozs7OztBQXBFQTtBQUNBO0FBOERBO0FBQUE7QUFyREE7QUFMQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7O0FBTkE7QUFnQkE7QUFMQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7O0FBTkE7QUFnQkE7QUFMQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7O0FBTkE7QUFpQkE7QUFOQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTs7QUFQQTtBQWtCQTtBQU5BO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBOztBQVBBO0FBZUE7QUFIQTtBQUNBO0FBQ0E7QUFDQTs7QUFKQTs7QUF2REE7QUFnRUE7O0FBakVBO0FBc0VBO0FBQ0E7QUFDQTtBQUNBIiwic291cmNlcyI6WyJ3ZWJwYWNrOi8vdnVlX2Zyb250ZW5kLy4vc3JjL1F1ZXN0aW9ubmFpcmVBcHAudnVlPzBjOWQiXSwic291cmNlc0NvbnRlbnQiOlsiPHRlbXBsYXRlPlxyXG4gIDx0ZW1wbGF0ZSB2LWZvcj1cIihxdWVzdGlvbiwgaWQpIGluIHFfY29uZmlnXCIgOmtleT1cImlkXCI+XHJcbiAgICA8ZGl2IHYtc2hvdz1cImN1cnJfaW5kZXggPT0gcXVlc3Rpb24uaW5kZXhcIj5cclxuXHJcbiAgICAgIDx0ZW1wbGF0ZSB2LWlmPVwicXVlc3Rpb24udHlwZSA9PSAnc2luZ2xlX2Nob2ljZSdcIj5cclxuICAgICAgICA8U2luZ2xlQ2hvaWNlUXVlc3Rpb25cclxuICAgICAgICAgICAgOnFpZD1cInF1ZXN0aW9uLnF1ZXN0aW9uXCJcclxuICAgICAgICAgICAgOnRleHQ9XCJxdWVzdGlvbi50ZXh0XCJcclxuICAgICAgICAgICAgOml0ZW1zPVwicXVlc3Rpb24uaXRlbXNcIlxyXG4gICAgICAgICAgICBAYW5zd2VyQ2hhbmdlZD1cInVwZGF0ZUFuc3dlcnNcIlxyXG4gICAgICAgICAgICBjbGFzcz1cInF1ZXN0aW9uLWNvbnRhaW5lclwiXHJcbiAgICAgICAgPjwvU2luZ2xlQ2hvaWNlUXVlc3Rpb24+XHJcbiAgICAgIDwvdGVtcGxhdGU+XHJcblxyXG4gICAgICA8dGVtcGxhdGUgdi1pZj1cInF1ZXN0aW9uLnR5cGUgPT0gJ211bHRpX2Nob2ljZSdcIj5cclxuICAgICAgICA8TXVsdGlDaG9pY2VRdWVzdGlvblxyXG4gICAgICAgICAgICA6cWlkPVwicXVlc3Rpb24ucXVlc3Rpb25cIlxyXG4gICAgICAgICAgICA6dGV4dD1cInF1ZXN0aW9uLnRleHRcIlxyXG4gICAgICAgICAgICA6aXRlbXM9XCJxdWVzdGlvbi5pdGVtc1wiXHJcbiAgICAgICAgICAgIEBhbnN3ZXJDaGFuZ2VkPVwidXBkYXRlQW5zd2Vyc1wiXHJcbiAgICAgICAgICAgIGNsYXNzPVwicXVlc3Rpb24tY29udGFpbmVyXCJcclxuICAgICAgICA+PC9NdWx0aUNob2ljZVF1ZXN0aW9uPlxyXG4gICAgICA8L3RlbXBsYXRlPlxyXG5cclxuICAgICAgPHRlbXBsYXRlIHYtaWY9XCJxdWVzdGlvbi50eXBlID09ICdvcGVuJ1wiPlxyXG4gICAgICAgIDxPcGVuUXVlc3Rpb25cclxuICAgICAgICAgICAgOnFpZD1cInF1ZXN0aW9uLnF1ZXN0aW9uXCJcclxuICAgICAgICAgICAgOnRleHQ9XCJxdWVzdGlvbi50ZXh0XCJcclxuICAgICAgICAgICAgOm9wdGlvbnM9XCJxdWVzdGlvbi5vcHRpb25zXCJcclxuICAgICAgICAgICAgQGFuc3dlckNoYW5nZWQ9XCJ1cGRhdGVBbnN3ZXJzXCJcclxuICAgICAgICAgICAgY2xhc3M9XCJxdWVzdGlvbi1jb250YWluZXJcIlxyXG4gICAgICAgID48L09wZW5RdWVzdGlvbj5cclxuICAgICAgPC90ZW1wbGF0ZT5cclxuXHJcbiAgICAgIDx0ZW1wbGF0ZSB2LWlmPVwicXVlc3Rpb24udHlwZSA9PSAnbWF0cml4J1wiPlxyXG4gICAgICAgIDxNYXRyaXhRdWVzdGlvblxyXG4gICAgICAgICAgICA6cWlkPVwicXVlc3Rpb24ucXVlc3Rpb25cIlxyXG4gICAgICAgICAgICA6dGV4dD1cInF1ZXN0aW9uLnRleHRcIlxyXG4gICAgICAgICAgICA6aXRlbXM9XCJxdWVzdGlvbi5pdGVtc1wiXHJcbiAgICAgICAgICAgIDpzY2FsZT1cInF1ZXN0aW9uLnNjYWxlXCJcclxuICAgICAgICAgICAgQGFuc3dlckNoYW5nZWQ9XCJ1cGRhdGVBbnN3ZXJzXCJcclxuICAgICAgICAgICAgY2xhc3M9XCJxdWVzdGlvbi1jb250YWluZXJcIlxyXG4gICAgICAgID48L01hdHJpeFF1ZXN0aW9uPlxyXG4gICAgICA8L3RlbXBsYXRlPlxyXG5cclxuICAgICAgPHRlbXBsYXRlIHYtaWY9XCJxdWVzdGlvbi50eXBlID09ICdzZW1hbnRpY19kaWZmJ1wiPlxyXG4gICAgICAgIDxTZW1hbnRpY0RpZmZlcmVudGlhbFxyXG4gICAgICAgICAgICA6cWlkPVwicXVlc3Rpb24ucXVlc3Rpb25cIlxyXG4gICAgICAgICAgICA6dGV4dD1cInF1ZXN0aW9uLnRleHRcIlxyXG4gICAgICAgICAgICA6aXRlbXM9XCJxdWVzdGlvbi5pdGVtc1wiXHJcbiAgICAgICAgICAgIDpzY2FsZT1cInF1ZXN0aW9uLnNjYWxlXCJcclxuICAgICAgICAgICAgQGFuc3dlckNoYW5nZWQ9XCJ1cGRhdGVBbnN3ZXJzXCJcclxuICAgICAgICAgICAgY2xhc3M9XCJxdWVzdGlvbi1jb250YWluZXJcIlxyXG4gICAgICAgID48L1NlbWFudGljRGlmZmVyZW50aWFsPlxyXG4gICAgICA8L3RlbXBsYXRlPlxyXG5cclxuICAgICAgPHRlbXBsYXRlIHYtaWY9XCJxdWVzdGlvbi50eXBlID09ICd0cmFuc2l0aW9uJ1wiPlxyXG4gICAgICAgIDxUcmFuc2l0aW9uUXVlc3Rpb25cclxuICAgICAgICAgICAgOnRleHQ9XCJxdWVzdGlvbi50ZXh0XCJcclxuICAgICAgICAgICAgQGFuc3dlckNoYW5nZWQ9XCJ1cGRhdGVBbnN3ZXJzXCJcclxuICAgICAgICAgICAgY2xhc3M9XCJxdWVzdGlvbi1jb250YWluZXJcIlxyXG4gICAgICAgID48L1RyYW5zaXRpb25RdWVzdGlvbj5cclxuICAgICAgPC90ZW1wbGF0ZT5cclxuXHJcbiAgICA8L2Rpdj5cclxuXHJcbiAgPC90ZW1wbGF0ZT5cclxuXHJcbiAgPGRpdiBjbGFzcz1cInJvd1wiPlxyXG4gICAgPGRpdiBjbGFzcz1cImNvbFwiPlxyXG4gICAgICA8YnV0dG9uXHJcbiAgICAgICAgICBjbGFzcz1cImZsb3ctYnRuXCJcclxuICAgICAgICAgIHR5cGU9XCJidXR0b25cIlxyXG4gICAgICAgICAgQGNsaWNrPVwibmV4dFwiXHJcbiAgICAgID5XZWl0ZXImbmJzcDsmbmJzcDsmIzgyNTA7PC9idXR0b24+XHJcbiAgICA8L2Rpdj5cclxuICA8L2Rpdj5cclxuXHJcbjwvdGVtcGxhdGU+XHJcblxyXG48c2NyaXB0PlxyXG5pbXBvcnQgU2luZ2xlQ2hvaWNlUXVlc3Rpb24gZnJvbSBcIi4vY29tcG9uZW50cy9TaW5nbGVDaG9pY2VRdWVzdGlvbi52dWVcIjtcclxuaW1wb3J0IE11bHRpQ2hvaWNlUXVlc3Rpb24gZnJvbSBcIi4vY29tcG9uZW50cy9NdWx0aUNob2ljZVF1ZXN0aW9uLnZ1ZVwiO1xyXG5pbXBvcnQgT3BlblF1ZXN0aW9uIGZyb20gXCIuL2NvbXBvbmVudHMvT3BlblF1ZXN0aW9uXCI7XHJcbmltcG9ydCBNYXRyaXhRdWVzdGlvbiBmcm9tIFwiLi9jb21wb25lbnRzL01hdHJpeFF1ZXN0aW9uXCI7XHJcbmltcG9ydCBTZW1hbnRpY0RpZmZlcmVudGlhbCBmcm9tIFwiLi9jb21wb25lbnRzL1NlbWFudGljRGlmZmVyZW50aWFsXCI7XHJcbmltcG9ydCBUcmFuc2l0aW9uUXVlc3Rpb24gZnJvbSBcIi4vY29tcG9uZW50cy9UcmFuc2l0aW9uUXVlc3Rpb25cIjtcclxuXHJcbmV4cG9ydCBkZWZhdWx0IHtcclxuICBuYW1lOiAnUUFwcCcsXHJcbiAgY29tcG9uZW50czoge1xyXG4gICAgU2luZ2xlQ2hvaWNlUXVlc3Rpb24sXHJcbiAgICBNdWx0aUNob2ljZVF1ZXN0aW9uLFxyXG4gICAgT3BlblF1ZXN0aW9uLFxyXG4gICAgTWF0cml4UXVlc3Rpb24sXHJcbiAgICBTZW1hbnRpY0RpZmZlcmVudGlhbCxcclxuICAgIFRyYW5zaXRpb25RdWVzdGlvblxyXG4gIH0sXHJcbiAgcHJvcHM6IHtcclxuICAgIHFjb25maWc6IFN0cmluZyxcclxuICAgIGFjdGlvbnVybDogU3RyaW5nLFxyXG4gIH0sXHJcbiAgZGF0YSgpIHtcclxuICAgIHJldHVybiB7XHJcbiAgICAgIHFfY29uZmlnOiBKU09OLnBhcnNlKHRoaXMucWNvbmZpZyksXHJcbiAgICAgIGFuc3dlcnM6IHt9LFxyXG4gICAgICBjdXJyX2luZGV4OiAxLFxyXG4gICAgICBtYXhfaW5kZXg6IDFcclxuICAgIH1cclxuICB9LFxyXG4gIGNyZWF0ZWQoKSB7XHJcbiAgICB0aGlzLnNldE1heEluZGV4KCk7XHJcbiAgfSxcclxuICBtZXRob2RzOiB7XHJcbiAgICB1cGRhdGVBbnN3ZXJzKGUpIHtcclxuICAgICAgdGhpcy5hbnN3ZXJzW2UuaWRdID0gZS5hbnN3ZXJzO1xyXG4gICAgfSxcclxuICAgIHNldE1heEluZGV4KCkge1xyXG4gICAgICBsZXQgaW5kaWNlcyA9IFtdO1xyXG4gICAgICB0aGlzLnFfY29uZmlnLmZvckVhY2gocSA9PlxyXG4gICAgICAgICAgaW5kaWNlcy5wdXNoKHEuaW5kZXgpXHJcbiAgICAgIClcclxuICAgICAgdGhpcy5tYXhfaW5kZXggPSBNYXRoLm1heCguLi5pbmRpY2VzKTtcclxuICAgIH0sXHJcbiAgICBuZXh0KCkge1xyXG4gICAgICBpZiAodGhpcy5jdXJyX2luZGV4ID09IHRoaXMubWF4X2luZGV4KSB7XHJcbiAgICAgICAgdGhpcy5zdWJtaXREYXRhKCk7XHJcbiAgICAgIH0gZWxzZSB7XHJcbiAgICAgICAgdGhpcy5jdXJyX2luZGV4ICs9IDE7XHJcbiAgICAgIH1cclxuICAgIH0sXHJcbiAgICBzdWJtaXREYXRhKCkge1xyXG4gICAgICBsZXQgZm9ybSA9IG5ldyBGb3JtRGF0YSgpXHJcbiAgICAgIGZvcm0uYXBwZW5kKFwicG9zdF9kYXRhXCIsIEpTT04uc3RyaW5naWZ5KHRoaXMuYW5zd2VycykpO1xyXG5cclxuICAgICAgbGV0IGNzcmYgPSBkb2N1bWVudC5xdWVyeVNlbGVjdG9yKFwiaW5wdXRbbmFtZT0nY3NyZm1pZGRsZXdhcmV0b2tlbiddXCIpO1xyXG4gICAgICBmb3JtLmFwcGVuZChcImNzcmZtaWRkbGV3YXJldG9rZW5cIiwgY3NyZi52YWx1ZSk7XHJcblxyXG4gICAgICBmZXRjaCh0aGlzLmFjdGlvbnVybCwge21ldGhvZDogXCJQT1NUXCIsIGJvZHk6IGZvcm19KVxyXG4gICAgICAgICAgLnRoZW4ocmVzcG9uc2UgPT4ge1xyXG4gICAgICAgICAgICBjb25zb2xlLmxvZyhyZXNwb25zZSlcclxuICAgICAgICAgICAgaWYgKHJlc3BvbnNlLnJlZGlyZWN0ZWQpIHtcclxuICAgICAgICAgICAgICB3aW5kb3cubG9jYXRpb24uaHJlZiA9IHJlc3BvbnNlLnVybDtcclxuICAgICAgICAgICAgfVxyXG4gICAgICAgICAgfSlcclxuICAgICAgICAgIC5jYXRjaChlcnIgPT4ge1xyXG4gICAgICAgICAgICBjb25zb2xlLmluZm8oZXJyKTtcclxuICAgICAgICAgIH0pO1xyXG4gICAgfVxyXG4gIH1cclxufVxyXG48L3NjcmlwdD5cclxuXHJcbjxzdHlsZT5cclxuI3FhcHAge1xyXG4gIGZvbnQtZmFtaWx5OiBBdmVuaXIsIEhlbHZldGljYSwgQXJpYWwsIHNhbnMtc2VyaWY7XHJcbiAgLXdlYmtpdC1mb250LXNtb290aGluZzogYW50aWFsaWFzZWQ7XHJcbiAgLW1vei1vc3gtZm9udC1zbW9vdGhpbmc6IGdyYXlzY2FsZTtcclxuICB0ZXh0LWFsaWduOiBsZWZ0O1xyXG59XHJcbi5xdWVzdGlvbi1jb250YWluZXIge1xyXG4gIG1hcmdpbi1ib3R0b206IDUwcHg7XHJcbn1cclxuPC9zdHlsZT5cclxuIl0sIm5hbWVzIjpbXSwic291cmNlUm9vdCI6IiJ9\n//# sourceURL=webpack-internal:///./node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!./node_modules/vue-loader/dist/templateLoader.js??ruleSet[1].rules[3]!./node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./src/QuestionnaireApp.vue?vue&type=template&id=2f351a77\n");

/***/ }),

/***/ "./node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!./node_modules/vue-loader/dist/templateLoader.js??ruleSet[1].rules[3]!./node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./src/components/MatrixQuestion.vue?vue&type=template&id=5831b977":
/*!****************************************************************************************************************************************************************************************************************************************************************************!*\
  !*** ./node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!./node_modules/vue-loader/dist/templateLoader.js??ruleSet[1].rules[3]!./node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./src/components/MatrixQuestion.vue?vue&type=template&id=5831b977 ***!
  \****************************************************************************************************************************************************************************************************************************************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   \"render\": function() { return /* binding */ render; }\n/* harmony export */ });\n/* harmony import */ var vue__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! vue */ \"./node_modules/vue/dist/vue.esm-bundler.js\");\n\nconst _hoisted_1 = [\"innerHTML\"];\nconst _hoisted_2 = {\n  class: \"mq-table\"\n};\nconst _hoisted_3 = {\n  class: \"mq-header\"\n};\n\nconst _hoisted_4 = /*#__PURE__*/(0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementVNode)(\"th\", null, null, -1\n/* HOISTED */\n);\n\nconst _hoisted_5 = {\n  class: \"mq-table-td-item\"\n};\nconst _hoisted_6 = [\"name\", \"value\"];\nfunction render(_ctx, _cache, $props, $setup, $data, $options) {\n  return (0,vue__WEBPACK_IMPORTED_MODULE_0__.openBlock)(), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementBlock)(\"div\", null, [(0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementVNode)(\"div\", {\n    class: \"surquest-question-text\",\n    innerHTML: $props.text\n  }, null, 8\n  /* PROPS */\n  , _hoisted_1), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementVNode)(\"table\", _hoisted_2, [(0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementVNode)(\"thead\", _hoisted_3, [(0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementVNode)(\"tr\", null, [_hoisted_4, ((0,vue__WEBPACK_IMPORTED_MODULE_0__.openBlock)(true), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementBlock)(vue__WEBPACK_IMPORTED_MODULE_0__.Fragment, null, (0,vue__WEBPACK_IMPORTED_MODULE_0__.renderList)($props.scale, (point, id) => {\n    return (0,vue__WEBPACK_IMPORTED_MODULE_0__.openBlock)(), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementBlock)(\"th\", {\n      key: id\n    }, (0,vue__WEBPACK_IMPORTED_MODULE_0__.toDisplayString)(point.label), 1\n    /* TEXT */\n    );\n  }), 128\n  /* KEYED_FRAGMENT */\n  ))])]), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementVNode)(\"tbody\", null, [((0,vue__WEBPACK_IMPORTED_MODULE_0__.openBlock)(true), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementBlock)(vue__WEBPACK_IMPORTED_MODULE_0__.Fragment, null, (0,vue__WEBPACK_IMPORTED_MODULE_0__.renderList)($props.items, (item, id) => {\n    return (0,vue__WEBPACK_IMPORTED_MODULE_0__.openBlock)(), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementBlock)(\"tr\", {\n      key: id\n    }, [(0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementVNode)(\"td\", _hoisted_5, (0,vue__WEBPACK_IMPORTED_MODULE_0__.toDisplayString)(item.label), 1\n    /* TEXT */\n    ), ((0,vue__WEBPACK_IMPORTED_MODULE_0__.openBlock)(true), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementBlock)(vue__WEBPACK_IMPORTED_MODULE_0__.Fragment, null, (0,vue__WEBPACK_IMPORTED_MODULE_0__.renderList)($props.scale, (point, id) => {\n      return (0,vue__WEBPACK_IMPORTED_MODULE_0__.openBlock)(), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementBlock)(\"td\", {\n        key: id,\n        class: \"mq-table-td-input\"\n      }, [(0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementVNode)(\"label\", null, [(0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementVNode)(\"input\", {\n        type: \"radio\",\n        name: item.id,\n        value: point.value,\n        onChange: _cache[0] || (_cache[0] = $event => $options.answerChanged($event))\n      }, null, 40\n      /* PROPS, HYDRATE_EVENTS */\n      , _hoisted_6)])]);\n    }), 128\n    /* KEYED_FRAGMENT */\n    ))]);\n  }), 128\n  /* KEYED_FRAGMENT */\n  ))])])]);\n}//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi9ub2RlX21vZHVsZXMvYmFiZWwtbG9hZGVyL2xpYi9pbmRleC5qcz8/Y2xvbmVkUnVsZVNldC00MC51c2VbMF0hLi9ub2RlX21vZHVsZXMvdnVlLWxvYWRlci9kaXN0L3RlbXBsYXRlTG9hZGVyLmpzPz9ydWxlU2V0WzFdLnJ1bGVzWzNdIS4vbm9kZV9tb2R1bGVzL3Z1ZS1sb2FkZXIvZGlzdC9pbmRleC5qcz8/cnVsZVNldFswXS51c2VbMF0hLi9zcmMvY29tcG9uZW50cy9NYXRyaXhRdWVzdGlvbi52dWU/dnVlJnR5cGU9dGVtcGxhdGUmaWQ9NTgzMWI5NzcuanMiLCJtYXBwaW5ncyI6Ijs7Ozs7Ozs7QUFLQTs7O0FBQ0E7OztBQUVBO0FBQUE7QUFBQTs7O0FBT0E7Ozs7QUFkQTtBQUVBO0FBQUE7QUFBQTs7QUFBQTtBQU1BO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTs7QUFBQTtBQUtBO0FBS0E7QUFBQTtBQUpBO0FBQUE7QUFDQTtBQUFBO0FBQUE7QUFFQTtBQURBO0FBQUE7QUFBQTtBQUFBO0FBQUE7O0FBQUE7QUFDQTs7QUFGQTtBQUlBOztBQVBBIiwic291cmNlcyI6WyJ3ZWJwYWNrOi8vdnVlX2Zyb250ZW5kLy4vc3JjL2NvbXBvbmVudHMvTWF0cml4UXVlc3Rpb24udnVlPzA1ZmYiXSwic291cmNlc0NvbnRlbnQiOlsiPHRlbXBsYXRlPlxyXG4gIDxkaXY+XHJcblxyXG4gICAgPGRpdiBjbGFzcz1cInN1cnF1ZXN0LXF1ZXN0aW9uLXRleHRcIiB2LWh0bWw9XCJ0ZXh0XCI+PC9kaXY+XHJcblxyXG4gICAgPHRhYmxlIGNsYXNzPVwibXEtdGFibGVcIj5cclxuICAgICAgPHRoZWFkIGNsYXNzPVwibXEtaGVhZGVyXCI+XHJcbiAgICAgIDx0cj5cclxuICAgICAgICA8dGg+PC90aD5cclxuICAgICAgICA8dGggdi1mb3I9XCIocG9pbnQsIGlkKSBpbiBzY2FsZVwiIDprZXk9XCJpZFwiPnt7IHBvaW50LmxhYmVsIH19PC90aD5cclxuICAgICAgPC90cj5cclxuICAgICAgPC90aGVhZD5cclxuICAgICAgPHRib2R5PlxyXG4gICAgICA8dGVtcGxhdGUgdi1mb3I9XCIoaXRlbSwgaWQpIGluIGl0ZW1zXCIgOmtleT1cImlkXCI+XHJcbiAgICAgICAgPHRyPlxyXG4gICAgICAgICAgPHRkIGNsYXNzPVwibXEtdGFibGUtdGQtaXRlbVwiPnt7IGl0ZW0ubGFiZWwgfX08L3RkPlxyXG4gICAgICAgICAgPHRkIHYtZm9yPVwiKHBvaW50LCBpZCkgaW4gc2NhbGVcIiA6a2V5PVwiaWRcIiBjbGFzcz1cIm1xLXRhYmxlLXRkLWlucHV0XCI+XHJcbiAgICAgICAgICAgIDxsYWJlbD48aW5wdXQgdHlwZT1cInJhZGlvXCIgOm5hbWU9XCJpdGVtLmlkXCIgOnZhbHVlPVwicG9pbnQudmFsdWVcIiBAY2hhbmdlPVwiYW5zd2VyQ2hhbmdlZCgkZXZlbnQpXCI+PC9sYWJlbD5cclxuICAgICAgICAgIDwvdGQ+XHJcbiAgICAgICAgPC90cj5cclxuICAgICAgPC90ZW1wbGF0ZT5cclxuICAgICAgPC90Ym9keT5cclxuICAgIDwvdGFibGU+XHJcblxyXG4gIDwvZGl2PlxyXG48L3RlbXBsYXRlPlxyXG5cclxuPHNjcmlwdD5cclxuZXhwb3J0IGRlZmF1bHQge1xyXG4gIG5hbWU6ICdTaW5nbGVDaG9pY2VRdWVzdGlvbicsXHJcbiAgcHJvcHM6IFsncWlkJywgJ3RleHQnLCAnaXRlbXMnLCAnc2NhbGUnXSxcclxuICBlbWl0czogWydhbnN3ZXJDaGFuZ2VkJ10sXHJcbiAgZGF0YTogZnVuY3Rpb24oKSB7XHJcbiAgICByZXR1cm4ge1xyXG4gICAgICBhbnN3ZXI6IHt9XHJcbiAgICB9XHJcbiAgfSxcclxuICBjcmVhdGVkKCkge1xyXG4gICAgdGhpcy5pdGVtcy5mb3JFYWNoKGkgPT4ge1xyXG4gICAgICB0aGlzLmFuc3dlcltpLmlkXSA9IC05OTtcclxuICAgIH0pXHJcbiAgICB0aGlzLiRlbWl0KCdhbnN3ZXJDaGFuZ2VkJywge2lkOiB0aGlzLnFpZCwgYW5zd2VyczogdGhpcy5hbnN3ZXJ9KTtcclxuICB9LFxyXG4gIG1ldGhvZHM6IHtcclxuICAgIGFuc3dlckNoYW5nZWQoZXZlbnQpIHtcclxuICAgICAgdGhpcy5hbnN3ZXJbZXZlbnQudGFyZ2V0Lm5hbWVdID0gZXZlbnQudGFyZ2V0LnZhbHVlO1xyXG4gICAgICB0aGlzLiRlbWl0KCdhbnN3ZXJDaGFuZ2VkJywge2lkOiB0aGlzLnFpZCwgYW5zd2VyczogdGhpcy5hbnN3ZXJ9KTtcclxuICAgIH1cclxuICB9XHJcbn1cclxuPC9zY3JpcHQ+XHJcblxyXG48c3R5bGUgc2NvcGVkPlxyXG5cclxuPC9zdHlsZT4iXSwibmFtZXMiOltdLCJzb3VyY2VSb290IjoiIn0=\n//# sourceURL=webpack-internal:///./node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!./node_modules/vue-loader/dist/templateLoader.js??ruleSet[1].rules[3]!./node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./src/components/MatrixQuestion.vue?vue&type=template&id=5831b977\n");

/***/ }),

/***/ "./node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!./node_modules/vue-loader/dist/templateLoader.js??ruleSet[1].rules[3]!./node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./src/components/MultiChoiceQuestion.vue?vue&type=template&id=0bba8c40":
/*!*********************************************************************************************************************************************************************************************************************************************************************************!*\
  !*** ./node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!./node_modules/vue-loader/dist/templateLoader.js??ruleSet[1].rules[3]!./node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./src/components/MultiChoiceQuestion.vue?vue&type=template&id=0bba8c40 ***!
  \*********************************************************************************************************************************************************************************************************************************************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   \"render\": function() { return /* binding */ render; }\n/* harmony export */ });\n/* harmony import */ var vue__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! vue */ \"./node_modules/vue/dist/vue.esm-bundler.js\");\n\nconst _hoisted_1 = [\"innerHTML\"];\nconst _hoisted_2 = {\n  class: \"surquest-choice-item form-check\"\n};\nconst _hoisted_3 = {\n  class: \"form-check-label rb-cb-label\"\n};\nconst _hoisted_4 = [\"name\", \"value\"];\nfunction render(_ctx, _cache, $props, $setup, $data, $options) {\n  return (0,vue__WEBPACK_IMPORTED_MODULE_0__.openBlock)(), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementBlock)(\"div\", null, [(0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementVNode)(\"div\", {\n    class: \"surquest-question-text\",\n    innerHTML: $props.text\n  }, null, 8\n  /* PROPS */\n  , _hoisted_1), ((0,vue__WEBPACK_IMPORTED_MODULE_0__.openBlock)(true), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementBlock)(vue__WEBPACK_IMPORTED_MODULE_0__.Fragment, null, (0,vue__WEBPACK_IMPORTED_MODULE_0__.renderList)($props.items, (item, id) => {\n    return (0,vue__WEBPACK_IMPORTED_MODULE_0__.openBlock)(), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementBlock)(\"div\", {\n      key: id,\n      class: \"surquest-gq-response surquest-cq-response\"\n    }, [(0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementVNode)(\"div\", _hoisted_2, [(0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementVNode)(\"label\", _hoisted_3, [(0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementVNode)(\"input\", {\n      class: \"form-check-input\",\n      type: \"checkbox\",\n      name: item.id,\n      value: item.value,\n      onChange: _cache[0] || (_cache[0] = $event => $options.answerChanged($event))\n    }, null, 40\n    /* PROPS, HYDRATE_EVENTS */\n    , _hoisted_4), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createTextVNode)(\" \" + (0,vue__WEBPACK_IMPORTED_MODULE_0__.toDisplayString)(item.label), 1\n    /* TEXT */\n    )])])]);\n  }), 128\n  /* KEYED_FRAGMENT */\n  ))]);\n}//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi9ub2RlX21vZHVsZXMvYmFiZWwtbG9hZGVyL2xpYi9pbmRleC5qcz8/Y2xvbmVkUnVsZVNldC00MC51c2VbMF0hLi9ub2RlX21vZHVsZXMvdnVlLWxvYWRlci9kaXN0L3RlbXBsYXRlTG9hZGVyLmpzPz9ydWxlU2V0WzFdLnJ1bGVzWzNdIS4vbm9kZV9tb2R1bGVzL3Z1ZS1sb2FkZXIvZGlzdC9pbmRleC5qcz8/cnVsZVNldFswXS51c2VbMF0hLi9zcmMvY29tcG9uZW50cy9NdWx0aUNob2ljZVF1ZXN0aW9uLnZ1ZT92dWUmdHlwZT10ZW1wbGF0ZSZpZD0wYmJhOGM0MC5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7OztBQUlBOzs7QUFDQTs7OztBQUpBO0FBQ0E7QUFBQTtBQUFBOztBQUFBO0FBQ0E7QUFBQTtBQUFBO0FBT0E7QUFKQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7O0FBQUE7QUFDQTtBQUNBO0FBRUE7O0FBUEEiLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly92dWVfZnJvbnRlbmQvLi9zcmMvY29tcG9uZW50cy9NdWx0aUNob2ljZVF1ZXN0aW9uLnZ1ZT8wMDg4Il0sInNvdXJjZXNDb250ZW50IjpbIjx0ZW1wbGF0ZT5cclxuICA8ZGl2PlxyXG4gICAgPGRpdiBjbGFzcz1cInN1cnF1ZXN0LXF1ZXN0aW9uLXRleHRcIiB2LWh0bWw9XCJ0ZXh0XCI+PC9kaXY+XHJcbiAgICA8ZGl2IHYtZm9yPVwiKGl0ZW0sIGlkKSBpbiBpdGVtc1wiIDprZXk9XCJpZFwiIGNsYXNzPVwic3VycXVlc3QtZ3EtcmVzcG9uc2Ugc3VycXVlc3QtY3EtcmVzcG9uc2VcIj5cclxuICAgICAgPGRpdiBjbGFzcz1cInN1cnF1ZXN0LWNob2ljZS1pdGVtIGZvcm0tY2hlY2tcIj5cclxuICAgICAgICA8bGFiZWwgY2xhc3M9XCJmb3JtLWNoZWNrLWxhYmVsIHJiLWNiLWxhYmVsXCI+XHJcbiAgICAgICAgICA8aW5wdXQgY2xhc3M9XCJmb3JtLWNoZWNrLWlucHV0XCIgdHlwZT1cImNoZWNrYm94XCIgOm5hbWU9XCJpdGVtLmlkXCIgOnZhbHVlPVwiaXRlbS52YWx1ZVwiIEBjaGFuZ2U9XCJhbnN3ZXJDaGFuZ2VkKCRldmVudClcIj5cclxuICAgICAgICAgIHt7IGl0ZW0ubGFiZWwgfX1cclxuICAgICAgICA8L2xhYmVsPlxyXG4gICAgICA8L2Rpdj5cclxuICAgIDwvZGl2PlxyXG4gIDwvZGl2PlxyXG48L3RlbXBsYXRlPlxyXG5cclxuPHNjcmlwdD5cclxuZXhwb3J0IGRlZmF1bHQge1xyXG4gIG5hbWU6ICdNdWx0aUNob2ljZVF1ZXN0aW9uJyxcclxuICBwcm9wczogWydxaWQnLCAndGV4dCcsICdpdGVtcyddLFxyXG4gIGVtaXRzOiBbJ2Fuc3dlckNoYW5nZWQnXSxcclxuICBkYXRhOiBmdW5jdGlvbigpIHtcclxuICAgIHJldHVybiB7XHJcbiAgICAgIGFuc3dlcjoge31cclxuICAgIH1cclxuICB9LFxyXG4gIGNyZWF0ZWQoKSB7XHJcbiAgICB0aGlzLml0ZW1zLmZvckVhY2goaSA9PiB7XHJcbiAgICAgIHRoaXMuYW5zd2VyW2kuaWRdID0gZmFsc2U7XHJcbiAgICB9KVxyXG4gICAgdGhpcy4kZW1pdCgnYW5zd2VyQ2hhbmdlZCcsIHtpZDogdGhpcy5xaWQsIGFuc3dlcnM6IHRoaXMuYW5zd2VyfSk7XHJcbiAgfSxcclxuICBtZXRob2RzOiB7XHJcbiAgICBhbnN3ZXJDaGFuZ2VkKGV2ZW50KSB7XHJcbiAgICAgIHRoaXMuYW5zd2VyW2V2ZW50LnRhcmdldC5uYW1lXSA9IGV2ZW50LnRhcmdldC5jaGVja2VkO1xyXG4gICAgICB0aGlzLiRlbWl0KCdhbnN3ZXJDaGFuZ2VkJywge2lkOiB0aGlzLnFpZCwgYW5zd2VyczogdGhpcy5hbnN3ZXJ9KTtcclxuICAgIH1cclxuICB9XHJcbn1cclxuPC9zY3JpcHQ+XHJcblxyXG48c3R5bGUgc2NvcGVkPlxyXG5cclxuPC9zdHlsZT4iXSwibmFtZXMiOltdLCJzb3VyY2VSb290IjoiIn0=\n//# sourceURL=webpack-internal:///./node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!./node_modules/vue-loader/dist/templateLoader.js??ruleSet[1].rules[3]!./node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./src/components/MultiChoiceQuestion.vue?vue&type=template&id=0bba8c40\n");

/***/ }),

/***/ "./node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!./node_modules/vue-loader/dist/templateLoader.js??ruleSet[1].rules[3]!./node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./src/components/OpenQuestion.vue?vue&type=template&id=0e43c880":
/*!**************************************************************************************************************************************************************************************************************************************************************************!*\
  !*** ./node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!./node_modules/vue-loader/dist/templateLoader.js??ruleSet[1].rules[3]!./node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./src/components/OpenQuestion.vue?vue&type=template&id=0e43c880 ***!
  \**************************************************************************************************************************************************************************************************************************************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   \"render\": function() { return /* binding */ render; }\n/* harmony export */ });\n/* harmony import */ var vue__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! vue */ \"./node_modules/vue/dist/vue.esm-bundler.js\");\n\nconst _hoisted_1 = [\"innerHTML\"];\nconst _hoisted_2 = {\n  class: \"surquest-gq-response\"\n};\nconst _hoisted_3 = [\"name\"];\nconst _hoisted_4 = [\"name\"];\nfunction render(_ctx, _cache, $props, $setup, $data, $options) {\n  return (0,vue__WEBPACK_IMPORTED_MODULE_0__.openBlock)(), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementBlock)(\"div\", null, [(0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementVNode)(\"div\", {\n    class: \"surquest-question-text\",\n    innerHTML: $props.text\n  }, null, 8\n  /* PROPS */\n  , _hoisted_1), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementVNode)(\"div\", _hoisted_2, [$props.options.display == 'small' ? ((0,vue__WEBPACK_IMPORTED_MODULE_0__.openBlock)(), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementBlock)(\"input\", {\n    key: 0,\n    class: \"surquest-oq-textline\",\n    type: \"text\",\n    name: $props.qid,\n    onChange: _cache[0] || (_cache[0] = $event => $options.answerChanged($event))\n  }, null, 40\n  /* PROPS, HYDRATE_EVENTS */\n  , _hoisted_3)) : (0,vue__WEBPACK_IMPORTED_MODULE_0__.createCommentVNode)(\"v-if\", true), $props.options.display == 'large' ? ((0,vue__WEBPACK_IMPORTED_MODULE_0__.openBlock)(), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementBlock)(\"textarea\", {\n    key: 1,\n    class: \"surquest-oq-textarea\",\n    type: \"text\",\n    name: $props.qid,\n    onChange: _cache[1] || (_cache[1] = $event => $options.answerChanged($event))\n  }, null, 40\n  /* PROPS, HYDRATE_EVENTS */\n  , _hoisted_4)) : (0,vue__WEBPACK_IMPORTED_MODULE_0__.createCommentVNode)(\"v-if\", true)])]);\n}//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi9ub2RlX21vZHVsZXMvYmFiZWwtbG9hZGVyL2xpYi9pbmRleC5qcz8/Y2xvbmVkUnVsZVNldC00MC51c2VbMF0hLi9ub2RlX21vZHVsZXMvdnVlLWxvYWRlci9kaXN0L3RlbXBsYXRlTG9hZGVyLmpzPz9ydWxlU2V0WzFdLnJ1bGVzWzNdIS4vbm9kZV9tb2R1bGVzL3Z1ZS1sb2FkZXIvZGlzdC9pbmRleC5qcz8/cnVsZVNldFswXS51c2VbMF0hLi9zcmMvY29tcG9uZW50cy9PcGVuUXVlc3Rpb24udnVlP3Z1ZSZ0eXBlPXRlbXBsYXRlJmlkPTBlNDNjODgwLmpzIiwibWFwcGluZ3MiOiI7Ozs7Ozs7O0FBR0E7Ozs7O0FBRkE7QUFDQTtBQUFBO0FBQUE7O0FBQUE7QUFFQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7O0FBQUE7QUFDQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7O0FBQUEiLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly92dWVfZnJvbnRlbmQvLi9zcmMvY29tcG9uZW50cy9PcGVuUXVlc3Rpb24udnVlPzc1NDUiXSwic291cmNlc0NvbnRlbnQiOlsiPHRlbXBsYXRlPlxyXG4gIDxkaXY+XHJcbiAgICA8ZGl2IGNsYXNzPVwic3VycXVlc3QtcXVlc3Rpb24tdGV4dFwiIHYtaHRtbD1cInRleHRcIj48L2Rpdj5cclxuICAgIDxkaXYgY2xhc3M9XCJzdXJxdWVzdC1ncS1yZXNwb25zZVwiPlxyXG4gICAgICA8aW5wdXQgY2xhc3M9XCJzdXJxdWVzdC1vcS10ZXh0bGluZVwiIHYtaWY9XCJvcHRpb25zLmRpc3BsYXkgPT0gJ3NtYWxsJ1wiIHR5cGU9XCJ0ZXh0XCIgOm5hbWU9XCJxaWRcIiBAY2hhbmdlPVwiYW5zd2VyQ2hhbmdlZCgkZXZlbnQpXCI+XHJcbiAgICAgIDx0ZXh0YXJlYSBjbGFzcz1cInN1cnF1ZXN0LW9xLXRleHRhcmVhXCIgdi1pZj1cIm9wdGlvbnMuZGlzcGxheSA9PSAnbGFyZ2UnXCIgdHlwZT1cInRleHRcIiA6bmFtZT1cInFpZFwiIEBjaGFuZ2U9XCJhbnN3ZXJDaGFuZ2VkKCRldmVudClcIj48L3RleHRhcmVhPlxyXG4gICAgPC9kaXY+XHJcbiAgPC9kaXY+XHJcbjwvdGVtcGxhdGU+XHJcblxyXG48c2NyaXB0PlxyXG5leHBvcnQgZGVmYXVsdCB7XHJcbiAgbmFtZTogJ09wZW5RdWVzdGlvbicsXHJcbiAgcHJvcHM6IFsncWlkJywgJ3RleHQnLCAnb3B0aW9ucyddLFxyXG4gIGVtaXRzOiBbJ2Fuc3dlckNoYW5nZWQnXSxcclxuICBkYXRhOiBmdW5jdGlvbigpIHtcclxuICAgIHJldHVybiB7XHJcbiAgICAgIGFuc3dlcjogJy05OSdcclxuICAgIH1cclxuICB9LFxyXG4gIGNyZWF0ZWQoKSB7XHJcbiAgICB0aGlzLiRlbWl0KCdhbnN3ZXJDaGFuZ2VkJywge2lkOiB0aGlzLnFpZCwgYW5zd2VyczogdGhpcy5hbnN3ZXJ9KTtcclxuICB9LFxyXG4gIG1ldGhvZHM6IHtcclxuICAgIGFuc3dlckNoYW5nZWQoZXZlbnQpIHtcclxuICAgICAgdGhpcy5hbnN3ZXIgPSBldmVudC50YXJnZXQudmFsdWU7XHJcbiAgICAgIHRoaXMuJGVtaXQoJ2Fuc3dlckNoYW5nZWQnLCB7aWQ6IHRoaXMucWlkLCBhbnN3ZXJzOiB0aGlzLmFuc3dlcn0pO1xyXG4gICAgfVxyXG4gIH1cclxufVxyXG48L3NjcmlwdD5cclxuXHJcbjxzdHlsZSBzY29wZWQ+XHJcblxyXG48L3N0eWxlPiJdLCJuYW1lcyI6W10sInNvdXJjZVJvb3QiOiIifQ==\n//# sourceURL=webpack-internal:///./node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!./node_modules/vue-loader/dist/templateLoader.js??ruleSet[1].rules[3]!./node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./src/components/OpenQuestion.vue?vue&type=template&id=0e43c880\n");

/***/ }),

/***/ "./node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!./node_modules/vue-loader/dist/templateLoader.js??ruleSet[1].rules[3]!./node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./src/components/SemanticDifferential.vue?vue&type=template&id=fdf447de":
/*!**********************************************************************************************************************************************************************************************************************************************************************************!*\
  !*** ./node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!./node_modules/vue-loader/dist/templateLoader.js??ruleSet[1].rules[3]!./node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./src/components/SemanticDifferential.vue?vue&type=template&id=fdf447de ***!
  \**********************************************************************************************************************************************************************************************************************************************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   \"render\": function() { return /* binding */ render; }\n/* harmony export */ });\n/* harmony import */ var vue__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! vue */ \"./node_modules/vue/dist/vue.esm-bundler.js\");\n\nconst _hoisted_1 = [\"innerHTML\"];\nconst _hoisted_2 = {\n  class: \"surquest-gq-response\"\n};\nconst _hoisted_3 = {\n  class: \"dq-table\"\n};\n\nconst _hoisted_4 = /*#__PURE__*/(0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementVNode)(\"th\", null, null, -1\n/* HOISTED */\n);\n\nconst _hoisted_5 = /*#__PURE__*/(0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementVNode)(\"th\", null, null, -1\n/* HOISTED */\n);\n\nconst _hoisted_6 = {\n  class: \"mq-table-td-item dq-table-td-item-left\"\n};\nconst _hoisted_7 = [\"name\", \"value\"];\nconst _hoisted_8 = {\n  class: \"mq-table-td-item dq-table-td-item-right\"\n};\nfunction render(_ctx, _cache, $props, $setup, $data, $options) {\n  return (0,vue__WEBPACK_IMPORTED_MODULE_0__.openBlock)(), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementBlock)(\"div\", null, [(0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementVNode)(\"div\", {\n    class: \"surquest-question-text\",\n    innerHTML: $props.text\n  }, null, 8\n  /* PROPS */\n  , _hoisted_1), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementVNode)(\"div\", _hoisted_2, [(0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementVNode)(\"table\", _hoisted_3, [(0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementVNode)(\"thead\", null, [(0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementVNode)(\"tr\", null, [_hoisted_4, ((0,vue__WEBPACK_IMPORTED_MODULE_0__.openBlock)(true), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementBlock)(vue__WEBPACK_IMPORTED_MODULE_0__.Fragment, null, (0,vue__WEBPACK_IMPORTED_MODULE_0__.renderList)($props.scale, (point, id) => {\n    return (0,vue__WEBPACK_IMPORTED_MODULE_0__.openBlock)(), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementBlock)(\"th\", {\n      key: id\n    }, (0,vue__WEBPACK_IMPORTED_MODULE_0__.toDisplayString)(point.label), 1\n    /* TEXT */\n    );\n  }), 128\n  /* KEYED_FRAGMENT */\n  )), _hoisted_5])]), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementVNode)(\"tbody\", null, [((0,vue__WEBPACK_IMPORTED_MODULE_0__.openBlock)(true), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementBlock)(vue__WEBPACK_IMPORTED_MODULE_0__.Fragment, null, (0,vue__WEBPACK_IMPORTED_MODULE_0__.renderList)($props.items, (item, id) => {\n    return (0,vue__WEBPACK_IMPORTED_MODULE_0__.openBlock)(), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementBlock)(\"tr\", {\n      key: id\n    }, [(0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementVNode)(\"td\", _hoisted_6, (0,vue__WEBPACK_IMPORTED_MODULE_0__.toDisplayString)(item.label), 1\n    /* TEXT */\n    ), ((0,vue__WEBPACK_IMPORTED_MODULE_0__.openBlock)(true), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementBlock)(vue__WEBPACK_IMPORTED_MODULE_0__.Fragment, null, (0,vue__WEBPACK_IMPORTED_MODULE_0__.renderList)($props.scale, (point, id) => {\n      return (0,vue__WEBPACK_IMPORTED_MODULE_0__.openBlock)(), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementBlock)(\"td\", {\n        key: id,\n        class: \"dq-table-td-input\"\n      }, [(0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementVNode)(\"label\", null, [(0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementVNode)(\"input\", {\n        type: \"radio\",\n        name: item.id,\n        value: point.value,\n        onChange: _cache[0] || (_cache[0] = $event => $options.answerChanged($event))\n      }, null, 40\n      /* PROPS, HYDRATE_EVENTS */\n      , _hoisted_7)])]);\n    }), 128\n    /* KEYED_FRAGMENT */\n    )), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementVNode)(\"td\", _hoisted_8, (0,vue__WEBPACK_IMPORTED_MODULE_0__.toDisplayString)(item.label_alt), 1\n    /* TEXT */\n    )]);\n  }), 128\n  /* KEYED_FRAGMENT */\n  ))])])])]);\n}//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi9ub2RlX21vZHVsZXMvYmFiZWwtbG9hZGVyL2xpYi9pbmRleC5qcz8/Y2xvbmVkUnVsZVNldC00MC51c2VbMF0hLi9ub2RlX21vZHVsZXMvdnVlLWxvYWRlci9kaXN0L3RlbXBsYXRlTG9hZGVyLmpzPz9ydWxlU2V0WzFdLnJ1bGVzWzNdIS4vbm9kZV9tb2R1bGVzL3Z1ZS1sb2FkZXIvZGlzdC9pbmRleC5qcz8/cnVsZVNldFswXS51c2VbMF0hLi9zcmMvY29tcG9uZW50cy9TZW1hbnRpY0RpZmZlcmVudGlhbC52dWU/dnVlJnR5cGU9dGVtcGxhdGUmaWQ9ZmRmNDQ3ZGUuanMiLCJtYXBwaW5ncyI6Ijs7Ozs7Ozs7QUFLQTs7O0FBQ0E7OztBQUdBO0FBQUE7QUFBQTs7QUFFQTtBQUFBO0FBQUE7OztBQUtBOzs7O0FBSUE7OztBQW5CQTtBQUVBO0FBQUE7QUFBQTs7QUFBQTtBQU9BO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTs7QUFBQTtBQUtBO0FBQUE7QUFNQTtBQUxBO0FBQUE7QUFDQTtBQUFBO0FBQUE7QUFFQTtBQURBO0FBQUE7QUFBQTtBQUFBO0FBQUE7O0FBQUE7QUFDQTs7QUFGQTtBQUdBO0FBQUE7QUFDQTs7QUFOQSIsInNvdXJjZXMiOlsid2VicGFjazovL3Z1ZV9mcm9udGVuZC8uL3NyYy9jb21wb25lbnRzL1NlbWFudGljRGlmZmVyZW50aWFsLnZ1ZT80MTU2Il0sInNvdXJjZXNDb250ZW50IjpbIjx0ZW1wbGF0ZT5cclxuICA8ZGl2PlxyXG5cclxuICAgIDxkaXYgY2xhc3M9XCJzdXJxdWVzdC1xdWVzdGlvbi10ZXh0XCIgdi1odG1sPVwidGV4dFwiPjwvZGl2PlxyXG5cclxuICAgIDxkaXYgY2xhc3M9XCJzdXJxdWVzdC1ncS1yZXNwb25zZVwiPlxyXG4gICAgICA8dGFibGUgY2xhc3M9XCJkcS10YWJsZVwiPlxyXG4gICAgICAgIDx0aGVhZD5cclxuICAgICAgICA8dHI+XHJcbiAgICAgICAgICA8dGg+PC90aD5cclxuICAgICAgICAgIDx0aCB2LWZvcj1cIihwb2ludCwgaWQpIGluIHNjYWxlXCIgOmtleT1cImlkXCI+e3sgcG9pbnQubGFiZWwgfX08L3RoPlxyXG4gICAgICAgICAgPHRoPjwvdGg+XHJcbiAgICAgICAgPC90cj5cclxuICAgICAgICA8L3RoZWFkPlxyXG4gICAgICAgIDx0Ym9keT5cclxuICAgICAgICA8dHIgdi1mb3I9XCIoaXRlbSwgaWQpIGluIGl0ZW1zXCIgOmtleT1cImlkXCI+XHJcbiAgICAgICAgICA8dGQgY2xhc3M9XCJtcS10YWJsZS10ZC1pdGVtIGRxLXRhYmxlLXRkLWl0ZW0tbGVmdFwiPnt7IGl0ZW0ubGFiZWwgfX08L3RkPlxyXG4gICAgICAgICAgPHRkIHYtZm9yPVwiKHBvaW50LCBpZCkgaW4gc2NhbGVcIiA6a2V5PVwiaWRcIiBjbGFzcz1cImRxLXRhYmxlLXRkLWlucHV0XCI+XHJcbiAgICAgICAgICAgIDxsYWJlbD48aW5wdXQgdHlwZT1cInJhZGlvXCIgOm5hbWU9XCJpdGVtLmlkXCIgOnZhbHVlPVwicG9pbnQudmFsdWVcIiBAY2hhbmdlPVwiYW5zd2VyQ2hhbmdlZCgkZXZlbnQpXCI+PC9sYWJlbD5cclxuICAgICAgICAgIDwvdGQ+XHJcbiAgICAgICAgICA8dGQgY2xhc3M9XCJtcS10YWJsZS10ZC1pdGVtIGRxLXRhYmxlLXRkLWl0ZW0tcmlnaHRcIj57eyBpdGVtLmxhYmVsX2FsdCB9fTwvdGQ+XHJcbiAgICAgICAgPC90cj5cclxuICAgICAgICA8L3Rib2R5PlxyXG4gICAgICA8L3RhYmxlPlxyXG4gICAgPC9kaXY+XHJcblxyXG4gIDwvZGl2PlxyXG48L3RlbXBsYXRlPlxyXG5cclxuPHNjcmlwdD5cclxuZXhwb3J0IGRlZmF1bHQge1xyXG4gIG5hbWU6ICdTaW5nbGVDaG9pY2VRdWVzdGlvbicsXHJcbiAgcHJvcHM6IFsncWlkJywgJ3RleHQnLCAnaXRlbXMnLCAnc2NhbGUnXSxcclxuICBlbWl0czogWydhbnN3ZXJDaGFuZ2VkJ10sXHJcbiAgZGF0YTogZnVuY3Rpb24oKSB7XHJcbiAgICByZXR1cm4ge1xyXG4gICAgICBhbnN3ZXI6IHt9XHJcbiAgICB9XHJcbiAgfSxcclxuICBjcmVhdGVkKCkge1xyXG4gICAgdGhpcy5pdGVtcy5mb3JFYWNoKGkgPT4ge1xyXG4gICAgICB0aGlzLmFuc3dlcltpLmlkXSA9IC05OTtcclxuICAgIH0pXHJcbiAgICB0aGlzLiRlbWl0KCdhbnN3ZXJDaGFuZ2VkJywge2lkOiB0aGlzLnFpZCwgYW5zd2VyczogdGhpcy5hbnN3ZXJ9KTtcclxuICB9LFxyXG4gIG1ldGhvZHM6IHtcclxuICAgIGFuc3dlckNoYW5nZWQoZXZlbnQpIHtcclxuICAgICAgdGhpcy5hbnN3ZXJbZXZlbnQudGFyZ2V0Lm5hbWVdID0gZXZlbnQudGFyZ2V0LnZhbHVlO1xyXG4gICAgICB0aGlzLiRlbWl0KCdhbnN3ZXJDaGFuZ2VkJywge2lkOiB0aGlzLnFpZCwgYW5zd2VyczogdGhpcy5hbnN3ZXJ9KTtcclxuICAgIH1cclxuICB9XHJcbn1cclxuPC9zY3JpcHQ+XHJcblxyXG48c3R5bGUgc2NvcGVkPlxyXG5cclxuPC9zdHlsZT4iXSwibmFtZXMiOltdLCJzb3VyY2VSb290IjoiIn0=\n//# sourceURL=webpack-internal:///./node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!./node_modules/vue-loader/dist/templateLoader.js??ruleSet[1].rules[3]!./node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./src/components/SemanticDifferential.vue?vue&type=template&id=fdf447de\n");

/***/ }),

/***/ "./node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!./node_modules/vue-loader/dist/templateLoader.js??ruleSet[1].rules[3]!./node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./src/components/SingleChoiceQuestion.vue?vue&type=template&id=76d95bbf":
/*!**********************************************************************************************************************************************************************************************************************************************************************************!*\
  !*** ./node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!./node_modules/vue-loader/dist/templateLoader.js??ruleSet[1].rules[3]!./node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./src/components/SingleChoiceQuestion.vue?vue&type=template&id=76d95bbf ***!
  \**********************************************************************************************************************************************************************************************************************************************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   \"render\": function() { return /* binding */ render; }\n/* harmony export */ });\n/* harmony import */ var vue__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! vue */ \"./node_modules/vue/dist/vue.esm-bundler.js\");\n\nconst _hoisted_1 = [\"innerHTML\"];\nconst _hoisted_2 = {\n  class: \"surquest-gq-response surquest-cq-response\"\n};\nconst _hoisted_3 = {\n  class: \"form-check-label rb-cb-label\"\n};\nconst _hoisted_4 = [\"dataid\", \"name\", \"value\"];\nfunction render(_ctx, _cache, $props, $setup, $data, $options) {\n  return (0,vue__WEBPACK_IMPORTED_MODULE_0__.openBlock)(), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementBlock)(vue__WEBPACK_IMPORTED_MODULE_0__.Fragment, null, [(0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementVNode)(\"div\", null, [(0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementVNode)(\"div\", {\n    class: \"surquest-question-text\",\n    innerHTML: $props.text\n  }, null, 8\n  /* PROPS */\n  , _hoisted_1), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementVNode)(\"div\", _hoisted_2, [((0,vue__WEBPACK_IMPORTED_MODULE_0__.openBlock)(true), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementBlock)(vue__WEBPACK_IMPORTED_MODULE_0__.Fragment, null, (0,vue__WEBPACK_IMPORTED_MODULE_0__.renderList)($props.items, (item, id) => {\n    return (0,vue__WEBPACK_IMPORTED_MODULE_0__.openBlock)(), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementBlock)(\"div\", {\n      key: id,\n      class: \"surquest-choice-item form-check\"\n    }, [(0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementVNode)(\"label\", _hoisted_3, [(0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementVNode)(\"input\", {\n      class: \"form-check-input\",\n      type: \"radio\",\n      dataid: $props.qid,\n      name: 'q-' + $props.qid,\n      value: item.value,\n      onChange: _cache[0] || (_cache[0] = $event => $options.answerChanged($event))\n    }, null, 40\n    /* PROPS, HYDRATE_EVENTS */\n    , _hoisted_4), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createTextVNode)(\" \" + (0,vue__WEBPACK_IMPORTED_MODULE_0__.toDisplayString)(item.label), 1\n    /* TEXT */\n    )])]);\n  }), 128\n  /* KEYED_FRAGMENT */\n  ))])]), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createCommentVNode)(\" Additional display option as dropdown select:\\r\\n  <div>\\r\\n    <div :ref_for=\\\"qid\\\">{{ text }}</div>\\r\\n    <select :id=\\\"qid\\\" :name=\\\"qid\\\" class=\\\"form-control\\\" @change=\\\"answerChanged($event)\\\">\\r\\n      <option selected disabled>Choose</option>\\r\\n      <option v-for=\\\"(item, id) in items\\\" :key=\\\"id\\\" :value=\\\"item.value\\\">{{ item.label }}</option>\\r\\n    </select>\\r\\n  </div>\\r\\n  \")], 2112\n  /* STABLE_FRAGMENT, DEV_ROOT_FRAGMENT */\n  );\n}//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi9ub2RlX21vZHVsZXMvYmFiZWwtbG9hZGVyL2xpYi9pbmRleC5qcz8/Y2xvbmVkUnVsZVNldC00MC51c2VbMF0hLi9ub2RlX21vZHVsZXMvdnVlLWxvYWRlci9kaXN0L3RlbXBsYXRlTG9hZGVyLmpzPz9ydWxlU2V0WzFdLnJ1bGVzWzNdIS4vbm9kZV9tb2R1bGVzL3Z1ZS1sb2FkZXIvZGlzdC9pbmRleC5qcz8/cnVsZVNldFswXS51c2VbMF0hLi9zcmMvY29tcG9uZW50cy9TaW5nbGVDaG9pY2VRdWVzdGlvbi52dWU/dnVlJnR5cGU9dGVtcGxhdGUmaWQ9NzZkOTViYmYuanMiLCJtYXBwaW5ncyI6Ijs7Ozs7Ozs7QUFHQTs7O0FBRUE7Ozs7QUFKQTtBQUNBO0FBQUE7QUFBQTs7QUFBQTtBQUVBO0FBQUE7QUFBQTtBQUtBO0FBSEE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7O0FBQUE7QUFDQTtBQUNBO0FBQ0E7O0FBTEEiLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly92dWVfZnJvbnRlbmQvLi9zcmMvY29tcG9uZW50cy9TaW5nbGVDaG9pY2VRdWVzdGlvbi52dWU/MmExZCJdLCJzb3VyY2VzQ29udGVudCI6WyI8dGVtcGxhdGU+XHJcbiAgPGRpdj5cclxuICAgIDxkaXYgY2xhc3M9XCJzdXJxdWVzdC1xdWVzdGlvbi10ZXh0XCIgdi1odG1sPVwidGV4dFwiPjwvZGl2PlxyXG4gICAgPGRpdiBjbGFzcz1cInN1cnF1ZXN0LWdxLXJlc3BvbnNlIHN1cnF1ZXN0LWNxLXJlc3BvbnNlXCI+XHJcbiAgICAgIDxkaXYgdi1mb3I9XCIoaXRlbSwgaWQpIGluIGl0ZW1zXCIgOmtleT1cImlkXCIgY2xhc3M9XCJzdXJxdWVzdC1jaG9pY2UtaXRlbSBmb3JtLWNoZWNrXCI+XHJcbiAgICAgICAgPGxhYmVsIGNsYXNzPVwiZm9ybS1jaGVjay1sYWJlbCByYi1jYi1sYWJlbFwiPlxyXG4gICAgICAgICAgPGlucHV0IGNsYXNzPVwiZm9ybS1jaGVjay1pbnB1dFwiIHR5cGU9XCJyYWRpb1wiIDpkYXRhaWQ9XCJxaWRcIiA6bmFtZT1cIidxLScgKyBxaWRcIiA6dmFsdWU9XCJpdGVtLnZhbHVlXCIgQGNoYW5nZT1cImFuc3dlckNoYW5nZWQoJGV2ZW50KVwiPlxyXG4gICAgICAgICAge3sgaXRlbS5sYWJlbCB9fVxyXG4gICAgICAgIDwvbGFiZWw+XHJcbiAgICAgIDwvZGl2PlxyXG4gICAgPC9kaXY+XHJcbiAgPC9kaXY+XHJcblxyXG4gIDwhLS0gQWRkaXRpb25hbCBkaXNwbGF5IG9wdGlvbiBhcyBkcm9wZG93biBzZWxlY3Q6XHJcbiAgPGRpdj5cclxuICAgIDxkaXYgOnJlZl9mb3I9XCJxaWRcIj57eyB0ZXh0IH19PC9kaXY+XHJcbiAgICA8c2VsZWN0IDppZD1cInFpZFwiIDpuYW1lPVwicWlkXCIgY2xhc3M9XCJmb3JtLWNvbnRyb2xcIiBAY2hhbmdlPVwiYW5zd2VyQ2hhbmdlZCgkZXZlbnQpXCI+XHJcbiAgICAgIDxvcHRpb24gc2VsZWN0ZWQgZGlzYWJsZWQ+Q2hvb3NlPC9vcHRpb24+XHJcbiAgICAgIDxvcHRpb24gdi1mb3I9XCIoaXRlbSwgaWQpIGluIGl0ZW1zXCIgOmtleT1cImlkXCIgOnZhbHVlPVwiaXRlbS52YWx1ZVwiPnt7IGl0ZW0ubGFiZWwgfX08L29wdGlvbj5cclxuICAgIDwvc2VsZWN0PlxyXG4gIDwvZGl2PlxyXG4gIC0tPlxyXG48L3RlbXBsYXRlPlxyXG5cclxuPHNjcmlwdD5cclxuZXhwb3J0IGRlZmF1bHQge1xyXG4gIG5hbWU6ICdTaW5nbGVDaG9pY2VRdWVzdGlvbicsXHJcbiAgcHJvcHM6IFsncWlkJywgJ3RleHQnLCAnaXRlbXMnXSxcclxuICBlbWl0czogWydhbnN3ZXJDaGFuZ2VkJ10sXHJcbiAgZGF0YTogZnVuY3Rpb24oKSB7XHJcbiAgICByZXR1cm4ge1xyXG4gICAgICBhbnN3ZXI6ICcnXHJcbiAgICB9XHJcbiAgfSxcclxuICBjcmVhdGVkKCkge1xyXG4gICAgdGhpcy5hbnN3ZXIgPSAtOTk7XHJcbiAgICB0aGlzLiRlbWl0KCdhbnN3ZXJDaGFuZ2VkJywge2lkOiB0aGlzLnFpZCwgYW5zd2VyczogdGhpcy5hbnN3ZXJ9KTtcclxuICB9LFxyXG4gIG1ldGhvZHM6IHtcclxuICAgIGFuc3dlckNoYW5nZWQoZXZlbnQpIHtcclxuICAgICAgdGhpcy5hbnN3ZXIgPSBldmVudC50YXJnZXQudmFsdWU7XHJcbiAgICAgIHRoaXMuJGVtaXQoJ2Fuc3dlckNoYW5nZWQnLCB7aWQ6IHRoaXMucWlkLCBhbnN3ZXJzOiB0aGlzLmFuc3dlcn0pO1xyXG4gICAgfVxyXG4gIH1cclxufVxyXG48L3NjcmlwdD5cclxuXHJcbjxzdHlsZSBzY29wZWQ+XHJcblxyXG48L3N0eWxlPiJdLCJuYW1lcyI6W10sInNvdXJjZVJvb3QiOiIifQ==\n//# sourceURL=webpack-internal:///./node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!./node_modules/vue-loader/dist/templateLoader.js??ruleSet[1].rules[3]!./node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./src/components/SingleChoiceQuestion.vue?vue&type=template&id=76d95bbf\n");

/***/ }),

/***/ "./node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!./node_modules/vue-loader/dist/templateLoader.js??ruleSet[1].rules[3]!./node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./src/components/TransitionQuestion.vue?vue&type=template&id=43ff75ea":
/*!********************************************************************************************************************************************************************************************************************************************************************************!*\
  !*** ./node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!./node_modules/vue-loader/dist/templateLoader.js??ruleSet[1].rules[3]!./node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./src/components/TransitionQuestion.vue?vue&type=template&id=43ff75ea ***!
  \********************************************************************************************************************************************************************************************************************************************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   \"render\": function() { return /* binding */ render; }\n/* harmony export */ });\n/* harmony import */ var vue__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! vue */ \"./node_modules/vue/dist/vue.esm-bundler.js\");\n\nconst _hoisted_1 = [\"innerHTML\"];\nfunction render(_ctx, _cache, $props, $setup, $data, $options) {\n  return (0,vue__WEBPACK_IMPORTED_MODULE_0__.openBlock)(), (0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementBlock)(\"div\", null, [(0,vue__WEBPACK_IMPORTED_MODULE_0__.createElementVNode)(\"div\", {\n    class: \"surquest-question-text\",\n    innerHTML: $props.text\n  }, null, 8\n  /* PROPS */\n  , _hoisted_1)]);\n}//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi9ub2RlX21vZHVsZXMvYmFiZWwtbG9hZGVyL2xpYi9pbmRleC5qcz8/Y2xvbmVkUnVsZVNldC00MC51c2VbMF0hLi9ub2RlX21vZHVsZXMvdnVlLWxvYWRlci9kaXN0L3RlbXBsYXRlTG9hZGVyLmpzPz9ydWxlU2V0WzFdLnJ1bGVzWzNdIS4vbm9kZV9tb2R1bGVzL3Z1ZS1sb2FkZXIvZGlzdC9pbmRleC5qcz8/cnVsZVNldFswXS51c2VbMF0hLi9zcmMvY29tcG9uZW50cy9UcmFuc2l0aW9uUXVlc3Rpb24udnVlP3Z1ZSZ0eXBlPXRlbXBsYXRlJmlkPTQzZmY3NWVhLmpzIiwibWFwcGluZ3MiOiI7Ozs7Ozs7O0FBQ0E7QUFDQTtBQUFBO0FBQUE7O0FBQUEiLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly92dWVfZnJvbnRlbmQvLi9zcmMvY29tcG9uZW50cy9UcmFuc2l0aW9uUXVlc3Rpb24udnVlPzAxOWUiXSwic291cmNlc0NvbnRlbnQiOlsiPHRlbXBsYXRlPlxyXG4gIDxkaXY+XHJcbiAgICA8ZGl2IGNsYXNzPVwic3VycXVlc3QtcXVlc3Rpb24tdGV4dFwiIHYtaHRtbD1cInRleHRcIj48L2Rpdj5cclxuICA8L2Rpdj5cclxuPC90ZW1wbGF0ZT5cclxuXHJcbjxzY3JpcHQ+XHJcbmV4cG9ydCBkZWZhdWx0IHtcclxuICBuYW1lOiBcIlRyYW5zaXRpb25RdWVzdGlvblwiLFxyXG4gIHByb3BzOiBbJ3RleHQnXSxcclxufVxyXG48L3NjcmlwdD5cclxuXHJcbjxzdHlsZSBzY29wZWQ+XHJcblxyXG48L3N0eWxlPiJdLCJuYW1lcyI6W10sInNvdXJjZVJvb3QiOiIifQ==\n//# sourceURL=webpack-internal:///./node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!./node_modules/vue-loader/dist/templateLoader.js??ruleSet[1].rules[3]!./node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./src/components/TransitionQuestion.vue?vue&type=template&id=43ff75ea\n");

/***/ }),

/***/ "./src/questionnaire.js":
/*!******************************!*\
  !*** ./src/questionnaire.js ***!
  \******************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var vue__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! vue */ \"./node_modules/vue/dist/vue.esm-bundler.js\");\n/* harmony import */ var _QuestionnaireApp_vue__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./QuestionnaireApp.vue */ \"./src/QuestionnaireApp.vue\");\n\n\nconst selector = \"#qapp\";\nconst mountEl = document.querySelector(selector);\n(0,vue__WEBPACK_IMPORTED_MODULE_0__.createApp)(_QuestionnaireApp_vue__WEBPACK_IMPORTED_MODULE_1__[\"default\"], { ...mountEl.dataset\n}).mount('#qapp');//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi9zcmMvcXVlc3Rpb25uYWlyZS5qcy5qcyIsIm1hcHBpbmdzIjoiOzs7QUFBQTtBQUNBO0FBRUE7QUFDQTtBQUVBO0FBQUEiLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly92dWVfZnJvbnRlbmQvLi9zcmMvcXVlc3Rpb25uYWlyZS5qcz9mZDNkIl0sInNvdXJjZXNDb250ZW50IjpbImltcG9ydCB7IGNyZWF0ZUFwcCB9IGZyb20gJ3Z1ZSdcclxuaW1wb3J0IFFBcHAgZnJvbSAnLi9RdWVzdGlvbm5haXJlQXBwLnZ1ZSdcclxuXHJcbmNvbnN0IHNlbGVjdG9yID0gXCIjcWFwcFwiO1xyXG5jb25zdCBtb3VudEVsID0gZG9jdW1lbnQucXVlcnlTZWxlY3RvcihzZWxlY3Rvcik7XHJcblxyXG5jcmVhdGVBcHAoUUFwcCwgey4uLm1vdW50RWwuZGF0YXNldH0pLm1vdW50KCcjcWFwcCcpXHJcbiJdLCJuYW1lcyI6W10sInNvdXJjZVJvb3QiOiIifQ==\n//# sourceURL=webpack-internal:///./src/questionnaire.js\n");

/***/ }),

/***/ "./node_modules/css-loader/dist/cjs.js??clonedRuleSet-12.use[1]!./node_modules/vue-loader/dist/stylePostLoader.js!./node_modules/postcss-loader/dist/cjs.js??clonedRuleSet-12.use[2]!./node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./src/QuestionnaireApp.vue?vue&type=style&index=0&id=2f351a77&lang=css":
/*!*****************************************************************************************************************************************************************************************************************************************************************************************************************************!*\
  !*** ./node_modules/css-loader/dist/cjs.js??clonedRuleSet-12.use[1]!./node_modules/vue-loader/dist/stylePostLoader.js!./node_modules/postcss-loader/dist/cjs.js??clonedRuleSet-12.use[2]!./node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./src/QuestionnaireApp.vue?vue&type=style&index=0&id=2f351a77&lang=css ***!
  \*****************************************************************************************************************************************************************************************************************************************************************************************************************************/
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var _node_modules_css_loader_dist_runtime_noSourceMaps_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../node_modules/css-loader/dist/runtime/noSourceMaps.js */ \"./node_modules/css-loader/dist/runtime/noSourceMaps.js\");\n/* harmony import */ var _node_modules_css_loader_dist_runtime_noSourceMaps_js__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_node_modules_css_loader_dist_runtime_noSourceMaps_js__WEBPACK_IMPORTED_MODULE_0__);\n/* harmony import */ var _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../node_modules/css-loader/dist/runtime/api.js */ \"./node_modules/css-loader/dist/runtime/api.js\");\n/* harmony import */ var _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1__);\n// Imports\n\n\nvar ___CSS_LOADER_EXPORT___ = _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1___default()((_node_modules_css_loader_dist_runtime_noSourceMaps_js__WEBPACK_IMPORTED_MODULE_0___default()));\n// Module\n___CSS_LOADER_EXPORT___.push([module.id, \"\\n#qapp {\\r\\n  font-family: Avenir, Helvetica, Arial, sans-serif;\\r\\n  -webkit-font-smoothing: antialiased;\\r\\n  -moz-osx-font-smoothing: grayscale;\\r\\n  text-align: left;\\n}\\n.question-container {\\r\\n  margin-bottom: 50px;\\n}\\r\\n\", \"\"]);\n// Exports\n/* harmony default export */ __webpack_exports__[\"default\"] = (___CSS_LOADER_EXPORT___);\n//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi9ub2RlX21vZHVsZXMvY3NzLWxvYWRlci9kaXN0L2Nqcy5qcz8/Y2xvbmVkUnVsZVNldC0xMi51c2VbMV0hLi9ub2RlX21vZHVsZXMvdnVlLWxvYWRlci9kaXN0L3N0eWxlUG9zdExvYWRlci5qcyEuL25vZGVfbW9kdWxlcy9wb3N0Y3NzLWxvYWRlci9kaXN0L2Nqcy5qcz8/Y2xvbmVkUnVsZVNldC0xMi51c2VbMl0hLi9ub2RlX21vZHVsZXMvdnVlLWxvYWRlci9kaXN0L2luZGV4LmpzPz9ydWxlU2V0WzBdLnVzZVswXSEuL3NyYy9RdWVzdGlvbm5haXJlQXBwLnZ1ZT92dWUmdHlwZT1zdHlsZSZpbmRleD0wJmlkPTJmMzUxYTc3Jmxhbmc9Y3NzLmpzIiwibWFwcGluZ3MiOiI7Ozs7O0FBQUE7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSIsInNvdXJjZXMiOlsid2VicGFjazovL3Z1ZV9mcm9udGVuZC8uL3NyYy9RdWVzdGlvbm5haXJlQXBwLnZ1ZT83MzE0Il0sInNvdXJjZXNDb250ZW50IjpbIi8vIEltcG9ydHNcbmltcG9ydCBfX19DU1NfTE9BREVSX0FQSV9OT19TT1VSQ0VNQVBfSU1QT1JUX19fIGZyb20gXCIuLi9ub2RlX21vZHVsZXMvY3NzLWxvYWRlci9kaXN0L3J1bnRpbWUvbm9Tb3VyY2VNYXBzLmpzXCI7XG5pbXBvcnQgX19fQ1NTX0xPQURFUl9BUElfSU1QT1JUX19fIGZyb20gXCIuLi9ub2RlX21vZHVsZXMvY3NzLWxvYWRlci9kaXN0L3J1bnRpbWUvYXBpLmpzXCI7XG52YXIgX19fQ1NTX0xPQURFUl9FWFBPUlRfX18gPSBfX19DU1NfTE9BREVSX0FQSV9JTVBPUlRfX18oX19fQ1NTX0xPQURFUl9BUElfTk9fU09VUkNFTUFQX0lNUE9SVF9fXyk7XG4vLyBNb2R1bGVcbl9fX0NTU19MT0FERVJfRVhQT1JUX19fLnB1c2goW21vZHVsZS5pZCwgXCJcXG4jcWFwcCB7XFxyXFxuICBmb250LWZhbWlseTogQXZlbmlyLCBIZWx2ZXRpY2EsIEFyaWFsLCBzYW5zLXNlcmlmO1xcclxcbiAgLXdlYmtpdC1mb250LXNtb290aGluZzogYW50aWFsaWFzZWQ7XFxyXFxuICAtbW96LW9zeC1mb250LXNtb290aGluZzogZ3JheXNjYWxlO1xcclxcbiAgdGV4dC1hbGlnbjogbGVmdDtcXG59XFxuLnF1ZXN0aW9uLWNvbnRhaW5lciB7XFxyXFxuICBtYXJnaW4tYm90dG9tOiA1MHB4O1xcbn1cXHJcXG5cIiwgXCJcIl0pO1xuLy8gRXhwb3J0c1xuZXhwb3J0IGRlZmF1bHQgX19fQ1NTX0xPQURFUl9FWFBPUlRfX187XG4iXSwibmFtZXMiOltdLCJzb3VyY2VSb290IjoiIn0=\n//# sourceURL=webpack-internal:///./node_modules/css-loader/dist/cjs.js??clonedRuleSet-12.use[1]!./node_modules/vue-loader/dist/stylePostLoader.js!./node_modules/postcss-loader/dist/cjs.js??clonedRuleSet-12.use[2]!./node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./src/QuestionnaireApp.vue?vue&type=style&index=0&id=2f351a77&lang=css\n");

/***/ }),

/***/ "./src/QuestionnaireApp.vue":
/*!**********************************!*\
  !*** ./src/QuestionnaireApp.vue ***!
  \**********************************/
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var _QuestionnaireApp_vue_vue_type_template_id_2f351a77__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./QuestionnaireApp.vue?vue&type=template&id=2f351a77 */ \"./src/QuestionnaireApp.vue?vue&type=template&id=2f351a77\");\n/* harmony import */ var _QuestionnaireApp_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./QuestionnaireApp.vue?vue&type=script&lang=js */ \"./src/QuestionnaireApp.vue?vue&type=script&lang=js\");\n/* harmony import */ var _QuestionnaireApp_vue_vue_type_style_index_0_id_2f351a77_lang_css__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./QuestionnaireApp.vue?vue&type=style&index=0&id=2f351a77&lang=css */ \"./src/QuestionnaireApp.vue?vue&type=style&index=0&id=2f351a77&lang=css\");\n/* harmony import */ var C_Files_Arbeit_Projekte_Data_Donation_Lab_Code_DDM_ddm_vue_frontend_node_modules_vue_loader_dist_exportHelper_js__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./node_modules/vue-loader/dist/exportHelper.js */ \"./node_modules/vue-loader/dist/exportHelper.js\");\n\n\n\n\n;\n\n\nconst __exports__ = /*#__PURE__*/(0,C_Files_Arbeit_Projekte_Data_Donation_Lab_Code_DDM_ddm_vue_frontend_node_modules_vue_loader_dist_exportHelper_js__WEBPACK_IMPORTED_MODULE_3__[\"default\"])(_QuestionnaireApp_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_1__[\"default\"], [['render',_QuestionnaireApp_vue_vue_type_template_id_2f351a77__WEBPACK_IMPORTED_MODULE_0__.render],['__file',\"src/QuestionnaireApp.vue\"]])\n/* hot reload */\nif (true) {\n  __exports__.__hmrId = \"2f351a77\"\n  const api = __VUE_HMR_RUNTIME__\n  module.hot.accept()\n  if (!api.createRecord('2f351a77', __exports__)) {\n    api.reload('2f351a77', __exports__)\n  }\n  \n  module.hot.accept(/*! ./QuestionnaireApp.vue?vue&type=template&id=2f351a77 */ \"./src/QuestionnaireApp.vue?vue&type=template&id=2f351a77\", function(__WEBPACK_OUTDATED_DEPENDENCIES__) { /* harmony import */ _QuestionnaireApp_vue_vue_type_template_id_2f351a77__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./QuestionnaireApp.vue?vue&type=template&id=2f351a77 */ \"./src/QuestionnaireApp.vue?vue&type=template&id=2f351a77\");\n(() => {\n    api.rerender('2f351a77', _QuestionnaireApp_vue_vue_type_template_id_2f351a77__WEBPACK_IMPORTED_MODULE_0__.render)\n  })(__WEBPACK_OUTDATED_DEPENDENCIES__); }.bind(this))\n\n}\n\n\n/* harmony default export */ __webpack_exports__[\"default\"] = (__exports__);//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi9zcmMvUXVlc3Rpb25uYWlyZUFwcC52dWUuanMiLCJtYXBwaW5ncyI6Ijs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBIiwic291cmNlcyI6WyJ3ZWJwYWNrOi8vdnVlX2Zyb250ZW5kLy4vc3JjL1F1ZXN0aW9ubmFpcmVBcHAudnVlP2VmOTUiXSwic291cmNlc0NvbnRlbnQiOlsiaW1wb3J0IHsgcmVuZGVyIH0gZnJvbSBcIi4vUXVlc3Rpb25uYWlyZUFwcC52dWU/dnVlJnR5cGU9dGVtcGxhdGUmaWQ9MmYzNTFhNzdcIlxuaW1wb3J0IHNjcmlwdCBmcm9tIFwiLi9RdWVzdGlvbm5haXJlQXBwLnZ1ZT92dWUmdHlwZT1zY3JpcHQmbGFuZz1qc1wiXG5leHBvcnQgKiBmcm9tIFwiLi9RdWVzdGlvbm5haXJlQXBwLnZ1ZT92dWUmdHlwZT1zY3JpcHQmbGFuZz1qc1wiXG5cbmltcG9ydCBcIi4vUXVlc3Rpb25uYWlyZUFwcC52dWU/dnVlJnR5cGU9c3R5bGUmaW5kZXg9MCZpZD0yZjM1MWE3NyZsYW5nPWNzc1wiXG5cbmltcG9ydCBleHBvcnRDb21wb25lbnQgZnJvbSBcIkM6XFxcXEZpbGVzXFxcXEFyYmVpdFxcXFxQcm9qZWt0ZVxcXFxEYXRhIERvbmF0aW9uIExhYlxcXFxDb2RlXFxcXERETVxcXFxkZG1cXFxcdnVlX2Zyb250ZW5kXFxcXG5vZGVfbW9kdWxlc1xcXFx2dWUtbG9hZGVyXFxcXGRpc3RcXFxcZXhwb3J0SGVscGVyLmpzXCJcbmNvbnN0IF9fZXhwb3J0c19fID0gLyojX19QVVJFX18qL2V4cG9ydENvbXBvbmVudChzY3JpcHQsIFtbJ3JlbmRlcicscmVuZGVyXSxbJ19fZmlsZScsXCJzcmMvUXVlc3Rpb25uYWlyZUFwcC52dWVcIl1dKVxuLyogaG90IHJlbG9hZCAqL1xuaWYgKG1vZHVsZS5ob3QpIHtcbiAgX19leHBvcnRzX18uX19obXJJZCA9IFwiMmYzNTFhNzdcIlxuICBjb25zdCBhcGkgPSBfX1ZVRV9ITVJfUlVOVElNRV9fXG4gIG1vZHVsZS5ob3QuYWNjZXB0KClcbiAgaWYgKCFhcGkuY3JlYXRlUmVjb3JkKCcyZjM1MWE3NycsIF9fZXhwb3J0c19fKSkge1xuICAgIGFwaS5yZWxvYWQoJzJmMzUxYTc3JywgX19leHBvcnRzX18pXG4gIH1cbiAgXG4gIG1vZHVsZS5ob3QuYWNjZXB0KFwiLi9RdWVzdGlvbm5haXJlQXBwLnZ1ZT92dWUmdHlwZT10ZW1wbGF0ZSZpZD0yZjM1MWE3N1wiLCAoKSA9PiB7XG4gICAgYXBpLnJlcmVuZGVyKCcyZjM1MWE3NycsIHJlbmRlcilcbiAgfSlcblxufVxuXG5cbmV4cG9ydCBkZWZhdWx0IF9fZXhwb3J0c19fIl0sIm5hbWVzIjpbXSwic291cmNlUm9vdCI6IiJ9\n//# sourceURL=webpack-internal:///./src/QuestionnaireApp.vue\n");

/***/ }),

/***/ "./src/components/MatrixQuestion.vue":
/*!*******************************************!*\
  !*** ./src/components/MatrixQuestion.vue ***!
  \*******************************************/
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var _MatrixQuestion_vue_vue_type_template_id_5831b977__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./MatrixQuestion.vue?vue&type=template&id=5831b977 */ \"./src/components/MatrixQuestion.vue?vue&type=template&id=5831b977\");\n/* harmony import */ var _MatrixQuestion_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./MatrixQuestion.vue?vue&type=script&lang=js */ \"./src/components/MatrixQuestion.vue?vue&type=script&lang=js\");\n/* harmony import */ var C_Files_Arbeit_Projekte_Data_Donation_Lab_Code_DDM_ddm_vue_frontend_node_modules_vue_loader_dist_exportHelper_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./node_modules/vue-loader/dist/exportHelper.js */ \"./node_modules/vue-loader/dist/exportHelper.js\");\n\n\n\n\n;\nconst __exports__ = /*#__PURE__*/(0,C_Files_Arbeit_Projekte_Data_Donation_Lab_Code_DDM_ddm_vue_frontend_node_modules_vue_loader_dist_exportHelper_js__WEBPACK_IMPORTED_MODULE_2__[\"default\"])(_MatrixQuestion_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_1__[\"default\"], [['render',_MatrixQuestion_vue_vue_type_template_id_5831b977__WEBPACK_IMPORTED_MODULE_0__.render],['__file',\"src/components/MatrixQuestion.vue\"]])\n/* hot reload */\nif (true) {\n  __exports__.__hmrId = \"5831b977\"\n  const api = __VUE_HMR_RUNTIME__\n  module.hot.accept()\n  if (!api.createRecord('5831b977', __exports__)) {\n    api.reload('5831b977', __exports__)\n  }\n  \n  module.hot.accept(/*! ./MatrixQuestion.vue?vue&type=template&id=5831b977 */ \"./src/components/MatrixQuestion.vue?vue&type=template&id=5831b977\", function(__WEBPACK_OUTDATED_DEPENDENCIES__) { /* harmony import */ _MatrixQuestion_vue_vue_type_template_id_5831b977__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./MatrixQuestion.vue?vue&type=template&id=5831b977 */ \"./src/components/MatrixQuestion.vue?vue&type=template&id=5831b977\");\n(() => {\n    api.rerender('5831b977', _MatrixQuestion_vue_vue_type_template_id_5831b977__WEBPACK_IMPORTED_MODULE_0__.render)\n  })(__WEBPACK_OUTDATED_DEPENDENCIES__); }.bind(this))\n\n}\n\n\n/* harmony default export */ __webpack_exports__[\"default\"] = (__exports__);//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi9zcmMvY29tcG9uZW50cy9NYXRyaXhRdWVzdGlvbi52dWUuanMiLCJtYXBwaW5ncyI6Ijs7OztBQUFBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQUE7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSIsInNvdXJjZXMiOlsid2VicGFjazovL3Z1ZV9mcm9udGVuZC8uL3NyYy9jb21wb25lbnRzL01hdHJpeFF1ZXN0aW9uLnZ1ZT82YTRiIl0sInNvdXJjZXNDb250ZW50IjpbImltcG9ydCB7IHJlbmRlciB9IGZyb20gXCIuL01hdHJpeFF1ZXN0aW9uLnZ1ZT92dWUmdHlwZT10ZW1wbGF0ZSZpZD01ODMxYjk3N1wiXG5pbXBvcnQgc2NyaXB0IGZyb20gXCIuL01hdHJpeFF1ZXN0aW9uLnZ1ZT92dWUmdHlwZT1zY3JpcHQmbGFuZz1qc1wiXG5leHBvcnQgKiBmcm9tIFwiLi9NYXRyaXhRdWVzdGlvbi52dWU/dnVlJnR5cGU9c2NyaXB0Jmxhbmc9anNcIlxuXG5pbXBvcnQgZXhwb3J0Q29tcG9uZW50IGZyb20gXCJDOlxcXFxGaWxlc1xcXFxBcmJlaXRcXFxcUHJvamVrdGVcXFxcRGF0YSBEb25hdGlvbiBMYWJcXFxcQ29kZVxcXFxERE1cXFxcZGRtXFxcXHZ1ZV9mcm9udGVuZFxcXFxub2RlX21vZHVsZXNcXFxcdnVlLWxvYWRlclxcXFxkaXN0XFxcXGV4cG9ydEhlbHBlci5qc1wiXG5jb25zdCBfX2V4cG9ydHNfXyA9IC8qI19fUFVSRV9fKi9leHBvcnRDb21wb25lbnQoc2NyaXB0LCBbWydyZW5kZXInLHJlbmRlcl0sWydfX2ZpbGUnLFwic3JjL2NvbXBvbmVudHMvTWF0cml4UXVlc3Rpb24udnVlXCJdXSlcbi8qIGhvdCByZWxvYWQgKi9cbmlmIChtb2R1bGUuaG90KSB7XG4gIF9fZXhwb3J0c19fLl9faG1ySWQgPSBcIjU4MzFiOTc3XCJcbiAgY29uc3QgYXBpID0gX19WVUVfSE1SX1JVTlRJTUVfX1xuICBtb2R1bGUuaG90LmFjY2VwdCgpXG4gIGlmICghYXBpLmNyZWF0ZVJlY29yZCgnNTgzMWI5NzcnLCBfX2V4cG9ydHNfXykpIHtcbiAgICBhcGkucmVsb2FkKCc1ODMxYjk3NycsIF9fZXhwb3J0c19fKVxuICB9XG4gIFxuICBtb2R1bGUuaG90LmFjY2VwdChcIi4vTWF0cml4UXVlc3Rpb24udnVlP3Z1ZSZ0eXBlPXRlbXBsYXRlJmlkPTU4MzFiOTc3XCIsICgpID0+IHtcbiAgICBhcGkucmVyZW5kZXIoJzU4MzFiOTc3JywgcmVuZGVyKVxuICB9KVxuXG59XG5cblxuZXhwb3J0IGRlZmF1bHQgX19leHBvcnRzX18iXSwibmFtZXMiOltdLCJzb3VyY2VSb290IjoiIn0=\n//# sourceURL=webpack-internal:///./src/components/MatrixQuestion.vue\n");

/***/ }),

/***/ "./src/components/MultiChoiceQuestion.vue":
/*!************************************************!*\
  !*** ./src/components/MultiChoiceQuestion.vue ***!
  \************************************************/
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var _MultiChoiceQuestion_vue_vue_type_template_id_0bba8c40__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./MultiChoiceQuestion.vue?vue&type=template&id=0bba8c40 */ \"./src/components/MultiChoiceQuestion.vue?vue&type=template&id=0bba8c40\");\n/* harmony import */ var _MultiChoiceQuestion_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./MultiChoiceQuestion.vue?vue&type=script&lang=js */ \"./src/components/MultiChoiceQuestion.vue?vue&type=script&lang=js\");\n/* harmony import */ var C_Files_Arbeit_Projekte_Data_Donation_Lab_Code_DDM_ddm_vue_frontend_node_modules_vue_loader_dist_exportHelper_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./node_modules/vue-loader/dist/exportHelper.js */ \"./node_modules/vue-loader/dist/exportHelper.js\");\n\n\n\n\n;\nconst __exports__ = /*#__PURE__*/(0,C_Files_Arbeit_Projekte_Data_Donation_Lab_Code_DDM_ddm_vue_frontend_node_modules_vue_loader_dist_exportHelper_js__WEBPACK_IMPORTED_MODULE_2__[\"default\"])(_MultiChoiceQuestion_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_1__[\"default\"], [['render',_MultiChoiceQuestion_vue_vue_type_template_id_0bba8c40__WEBPACK_IMPORTED_MODULE_0__.render],['__file',\"src/components/MultiChoiceQuestion.vue\"]])\n/* hot reload */\nif (true) {\n  __exports__.__hmrId = \"0bba8c40\"\n  const api = __VUE_HMR_RUNTIME__\n  module.hot.accept()\n  if (!api.createRecord('0bba8c40', __exports__)) {\n    api.reload('0bba8c40', __exports__)\n  }\n  \n  module.hot.accept(/*! ./MultiChoiceQuestion.vue?vue&type=template&id=0bba8c40 */ \"./src/components/MultiChoiceQuestion.vue?vue&type=template&id=0bba8c40\", function(__WEBPACK_OUTDATED_DEPENDENCIES__) { /* harmony import */ _MultiChoiceQuestion_vue_vue_type_template_id_0bba8c40__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./MultiChoiceQuestion.vue?vue&type=template&id=0bba8c40 */ \"./src/components/MultiChoiceQuestion.vue?vue&type=template&id=0bba8c40\");\n(() => {\n    api.rerender('0bba8c40', _MultiChoiceQuestion_vue_vue_type_template_id_0bba8c40__WEBPACK_IMPORTED_MODULE_0__.render)\n  })(__WEBPACK_OUTDATED_DEPENDENCIES__); }.bind(this))\n\n}\n\n\n/* harmony default export */ __webpack_exports__[\"default\"] = (__exports__);//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi9zcmMvY29tcG9uZW50cy9NdWx0aUNob2ljZVF1ZXN0aW9uLnZ1ZS5qcyIsIm1hcHBpbmdzIjoiOzs7O0FBQUE7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBIiwic291cmNlcyI6WyJ3ZWJwYWNrOi8vdnVlX2Zyb250ZW5kLy4vc3JjL2NvbXBvbmVudHMvTXVsdGlDaG9pY2VRdWVzdGlvbi52dWU/NmM0OCJdLCJzb3VyY2VzQ29udGVudCI6WyJpbXBvcnQgeyByZW5kZXIgfSBmcm9tIFwiLi9NdWx0aUNob2ljZVF1ZXN0aW9uLnZ1ZT92dWUmdHlwZT10ZW1wbGF0ZSZpZD0wYmJhOGM0MFwiXG5pbXBvcnQgc2NyaXB0IGZyb20gXCIuL011bHRpQ2hvaWNlUXVlc3Rpb24udnVlP3Z1ZSZ0eXBlPXNjcmlwdCZsYW5nPWpzXCJcbmV4cG9ydCAqIGZyb20gXCIuL011bHRpQ2hvaWNlUXVlc3Rpb24udnVlP3Z1ZSZ0eXBlPXNjcmlwdCZsYW5nPWpzXCJcblxuaW1wb3J0IGV4cG9ydENvbXBvbmVudCBmcm9tIFwiQzpcXFxcRmlsZXNcXFxcQXJiZWl0XFxcXFByb2pla3RlXFxcXERhdGEgRG9uYXRpb24gTGFiXFxcXENvZGVcXFxcRERNXFxcXGRkbVxcXFx2dWVfZnJvbnRlbmRcXFxcbm9kZV9tb2R1bGVzXFxcXHZ1ZS1sb2FkZXJcXFxcZGlzdFxcXFxleHBvcnRIZWxwZXIuanNcIlxuY29uc3QgX19leHBvcnRzX18gPSAvKiNfX1BVUkVfXyovZXhwb3J0Q29tcG9uZW50KHNjcmlwdCwgW1sncmVuZGVyJyxyZW5kZXJdLFsnX19maWxlJyxcInNyYy9jb21wb25lbnRzL011bHRpQ2hvaWNlUXVlc3Rpb24udnVlXCJdXSlcbi8qIGhvdCByZWxvYWQgKi9cbmlmIChtb2R1bGUuaG90KSB7XG4gIF9fZXhwb3J0c19fLl9faG1ySWQgPSBcIjBiYmE4YzQwXCJcbiAgY29uc3QgYXBpID0gX19WVUVfSE1SX1JVTlRJTUVfX1xuICBtb2R1bGUuaG90LmFjY2VwdCgpXG4gIGlmICghYXBpLmNyZWF0ZVJlY29yZCgnMGJiYThjNDAnLCBfX2V4cG9ydHNfXykpIHtcbiAgICBhcGkucmVsb2FkKCcwYmJhOGM0MCcsIF9fZXhwb3J0c19fKVxuICB9XG4gIFxuICBtb2R1bGUuaG90LmFjY2VwdChcIi4vTXVsdGlDaG9pY2VRdWVzdGlvbi52dWU/dnVlJnR5cGU9dGVtcGxhdGUmaWQ9MGJiYThjNDBcIiwgKCkgPT4ge1xuICAgIGFwaS5yZXJlbmRlcignMGJiYThjNDAnLCByZW5kZXIpXG4gIH0pXG5cbn1cblxuXG5leHBvcnQgZGVmYXVsdCBfX2V4cG9ydHNfXyJdLCJuYW1lcyI6W10sInNvdXJjZVJvb3QiOiIifQ==\n//# sourceURL=webpack-internal:///./src/components/MultiChoiceQuestion.vue\n");

/***/ }),

/***/ "./src/components/OpenQuestion.vue":
/*!*****************************************!*\
  !*** ./src/components/OpenQuestion.vue ***!
  \*****************************************/
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var _OpenQuestion_vue_vue_type_template_id_0e43c880__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./OpenQuestion.vue?vue&type=template&id=0e43c880 */ \"./src/components/OpenQuestion.vue?vue&type=template&id=0e43c880\");\n/* harmony import */ var _OpenQuestion_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./OpenQuestion.vue?vue&type=script&lang=js */ \"./src/components/OpenQuestion.vue?vue&type=script&lang=js\");\n/* harmony import */ var C_Files_Arbeit_Projekte_Data_Donation_Lab_Code_DDM_ddm_vue_frontend_node_modules_vue_loader_dist_exportHelper_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./node_modules/vue-loader/dist/exportHelper.js */ \"./node_modules/vue-loader/dist/exportHelper.js\");\n\n\n\n\n;\nconst __exports__ = /*#__PURE__*/(0,C_Files_Arbeit_Projekte_Data_Donation_Lab_Code_DDM_ddm_vue_frontend_node_modules_vue_loader_dist_exportHelper_js__WEBPACK_IMPORTED_MODULE_2__[\"default\"])(_OpenQuestion_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_1__[\"default\"], [['render',_OpenQuestion_vue_vue_type_template_id_0e43c880__WEBPACK_IMPORTED_MODULE_0__.render],['__file',\"src/components/OpenQuestion.vue\"]])\n/* hot reload */\nif (true) {\n  __exports__.__hmrId = \"0e43c880\"\n  const api = __VUE_HMR_RUNTIME__\n  module.hot.accept()\n  if (!api.createRecord('0e43c880', __exports__)) {\n    api.reload('0e43c880', __exports__)\n  }\n  \n  module.hot.accept(/*! ./OpenQuestion.vue?vue&type=template&id=0e43c880 */ \"./src/components/OpenQuestion.vue?vue&type=template&id=0e43c880\", function(__WEBPACK_OUTDATED_DEPENDENCIES__) { /* harmony import */ _OpenQuestion_vue_vue_type_template_id_0e43c880__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./OpenQuestion.vue?vue&type=template&id=0e43c880 */ \"./src/components/OpenQuestion.vue?vue&type=template&id=0e43c880\");\n(() => {\n    api.rerender('0e43c880', _OpenQuestion_vue_vue_type_template_id_0e43c880__WEBPACK_IMPORTED_MODULE_0__.render)\n  })(__WEBPACK_OUTDATED_DEPENDENCIES__); }.bind(this))\n\n}\n\n\n/* harmony default export */ __webpack_exports__[\"default\"] = (__exports__);//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi9zcmMvY29tcG9uZW50cy9PcGVuUXVlc3Rpb24udnVlLmpzIiwibWFwcGluZ3MiOiI7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUFBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0EiLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly92dWVfZnJvbnRlbmQvLi9zcmMvY29tcG9uZW50cy9PcGVuUXVlc3Rpb24udnVlPzUzMDQiXSwic291cmNlc0NvbnRlbnQiOlsiaW1wb3J0IHsgcmVuZGVyIH0gZnJvbSBcIi4vT3BlblF1ZXN0aW9uLnZ1ZT92dWUmdHlwZT10ZW1wbGF0ZSZpZD0wZTQzYzg4MFwiXG5pbXBvcnQgc2NyaXB0IGZyb20gXCIuL09wZW5RdWVzdGlvbi52dWU/dnVlJnR5cGU9c2NyaXB0Jmxhbmc9anNcIlxuZXhwb3J0ICogZnJvbSBcIi4vT3BlblF1ZXN0aW9uLnZ1ZT92dWUmdHlwZT1zY3JpcHQmbGFuZz1qc1wiXG5cbmltcG9ydCBleHBvcnRDb21wb25lbnQgZnJvbSBcIkM6XFxcXEZpbGVzXFxcXEFyYmVpdFxcXFxQcm9qZWt0ZVxcXFxEYXRhIERvbmF0aW9uIExhYlxcXFxDb2RlXFxcXERETVxcXFxkZG1cXFxcdnVlX2Zyb250ZW5kXFxcXG5vZGVfbW9kdWxlc1xcXFx2dWUtbG9hZGVyXFxcXGRpc3RcXFxcZXhwb3J0SGVscGVyLmpzXCJcbmNvbnN0IF9fZXhwb3J0c19fID0gLyojX19QVVJFX18qL2V4cG9ydENvbXBvbmVudChzY3JpcHQsIFtbJ3JlbmRlcicscmVuZGVyXSxbJ19fZmlsZScsXCJzcmMvY29tcG9uZW50cy9PcGVuUXVlc3Rpb24udnVlXCJdXSlcbi8qIGhvdCByZWxvYWQgKi9cbmlmIChtb2R1bGUuaG90KSB7XG4gIF9fZXhwb3J0c19fLl9faG1ySWQgPSBcIjBlNDNjODgwXCJcbiAgY29uc3QgYXBpID0gX19WVUVfSE1SX1JVTlRJTUVfX1xuICBtb2R1bGUuaG90LmFjY2VwdCgpXG4gIGlmICghYXBpLmNyZWF0ZVJlY29yZCgnMGU0M2M4ODAnLCBfX2V4cG9ydHNfXykpIHtcbiAgICBhcGkucmVsb2FkKCcwZTQzYzg4MCcsIF9fZXhwb3J0c19fKVxuICB9XG4gIFxuICBtb2R1bGUuaG90LmFjY2VwdChcIi4vT3BlblF1ZXN0aW9uLnZ1ZT92dWUmdHlwZT10ZW1wbGF0ZSZpZD0wZTQzYzg4MFwiLCAoKSA9PiB7XG4gICAgYXBpLnJlcmVuZGVyKCcwZTQzYzg4MCcsIHJlbmRlcilcbiAgfSlcblxufVxuXG5cbmV4cG9ydCBkZWZhdWx0IF9fZXhwb3J0c19fIl0sIm5hbWVzIjpbXSwic291cmNlUm9vdCI6IiJ9\n//# sourceURL=webpack-internal:///./src/components/OpenQuestion.vue\n");

/***/ }),

/***/ "./src/components/SemanticDifferential.vue":
/*!*************************************************!*\
  !*** ./src/components/SemanticDifferential.vue ***!
  \*************************************************/
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var _SemanticDifferential_vue_vue_type_template_id_fdf447de__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./SemanticDifferential.vue?vue&type=template&id=fdf447de */ \"./src/components/SemanticDifferential.vue?vue&type=template&id=fdf447de\");\n/* harmony import */ var _SemanticDifferential_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./SemanticDifferential.vue?vue&type=script&lang=js */ \"./src/components/SemanticDifferential.vue?vue&type=script&lang=js\");\n/* harmony import */ var C_Files_Arbeit_Projekte_Data_Donation_Lab_Code_DDM_ddm_vue_frontend_node_modules_vue_loader_dist_exportHelper_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./node_modules/vue-loader/dist/exportHelper.js */ \"./node_modules/vue-loader/dist/exportHelper.js\");\n\n\n\n\n;\nconst __exports__ = /*#__PURE__*/(0,C_Files_Arbeit_Projekte_Data_Donation_Lab_Code_DDM_ddm_vue_frontend_node_modules_vue_loader_dist_exportHelper_js__WEBPACK_IMPORTED_MODULE_2__[\"default\"])(_SemanticDifferential_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_1__[\"default\"], [['render',_SemanticDifferential_vue_vue_type_template_id_fdf447de__WEBPACK_IMPORTED_MODULE_0__.render],['__file',\"src/components/SemanticDifferential.vue\"]])\n/* hot reload */\nif (true) {\n  __exports__.__hmrId = \"fdf447de\"\n  const api = __VUE_HMR_RUNTIME__\n  module.hot.accept()\n  if (!api.createRecord('fdf447de', __exports__)) {\n    api.reload('fdf447de', __exports__)\n  }\n  \n  module.hot.accept(/*! ./SemanticDifferential.vue?vue&type=template&id=fdf447de */ \"./src/components/SemanticDifferential.vue?vue&type=template&id=fdf447de\", function(__WEBPACK_OUTDATED_DEPENDENCIES__) { /* harmony import */ _SemanticDifferential_vue_vue_type_template_id_fdf447de__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./SemanticDifferential.vue?vue&type=template&id=fdf447de */ \"./src/components/SemanticDifferential.vue?vue&type=template&id=fdf447de\");\n(() => {\n    api.rerender('fdf447de', _SemanticDifferential_vue_vue_type_template_id_fdf447de__WEBPACK_IMPORTED_MODULE_0__.render)\n  })(__WEBPACK_OUTDATED_DEPENDENCIES__); }.bind(this))\n\n}\n\n\n/* harmony default export */ __webpack_exports__[\"default\"] = (__exports__);//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi9zcmMvY29tcG9uZW50cy9TZW1hbnRpY0RpZmZlcmVudGlhbC52dWUuanMiLCJtYXBwaW5ncyI6Ijs7OztBQUFBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQUE7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSIsInNvdXJjZXMiOlsid2VicGFjazovL3Z1ZV9mcm9udGVuZC8uL3NyYy9jb21wb25lbnRzL1NlbWFudGljRGlmZmVyZW50aWFsLnZ1ZT8yODFiIl0sInNvdXJjZXNDb250ZW50IjpbImltcG9ydCB7IHJlbmRlciB9IGZyb20gXCIuL1NlbWFudGljRGlmZmVyZW50aWFsLnZ1ZT92dWUmdHlwZT10ZW1wbGF0ZSZpZD1mZGY0NDdkZVwiXG5pbXBvcnQgc2NyaXB0IGZyb20gXCIuL1NlbWFudGljRGlmZmVyZW50aWFsLnZ1ZT92dWUmdHlwZT1zY3JpcHQmbGFuZz1qc1wiXG5leHBvcnQgKiBmcm9tIFwiLi9TZW1hbnRpY0RpZmZlcmVudGlhbC52dWU/dnVlJnR5cGU9c2NyaXB0Jmxhbmc9anNcIlxuXG5pbXBvcnQgZXhwb3J0Q29tcG9uZW50IGZyb20gXCJDOlxcXFxGaWxlc1xcXFxBcmJlaXRcXFxcUHJvamVrdGVcXFxcRGF0YSBEb25hdGlvbiBMYWJcXFxcQ29kZVxcXFxERE1cXFxcZGRtXFxcXHZ1ZV9mcm9udGVuZFxcXFxub2RlX21vZHVsZXNcXFxcdnVlLWxvYWRlclxcXFxkaXN0XFxcXGV4cG9ydEhlbHBlci5qc1wiXG5jb25zdCBfX2V4cG9ydHNfXyA9IC8qI19fUFVSRV9fKi9leHBvcnRDb21wb25lbnQoc2NyaXB0LCBbWydyZW5kZXInLHJlbmRlcl0sWydfX2ZpbGUnLFwic3JjL2NvbXBvbmVudHMvU2VtYW50aWNEaWZmZXJlbnRpYWwudnVlXCJdXSlcbi8qIGhvdCByZWxvYWQgKi9cbmlmIChtb2R1bGUuaG90KSB7XG4gIF9fZXhwb3J0c19fLl9faG1ySWQgPSBcImZkZjQ0N2RlXCJcbiAgY29uc3QgYXBpID0gX19WVUVfSE1SX1JVTlRJTUVfX1xuICBtb2R1bGUuaG90LmFjY2VwdCgpXG4gIGlmICghYXBpLmNyZWF0ZVJlY29yZCgnZmRmNDQ3ZGUnLCBfX2V4cG9ydHNfXykpIHtcbiAgICBhcGkucmVsb2FkKCdmZGY0NDdkZScsIF9fZXhwb3J0c19fKVxuICB9XG4gIFxuICBtb2R1bGUuaG90LmFjY2VwdChcIi4vU2VtYW50aWNEaWZmZXJlbnRpYWwudnVlP3Z1ZSZ0eXBlPXRlbXBsYXRlJmlkPWZkZjQ0N2RlXCIsICgpID0+IHtcbiAgICBhcGkucmVyZW5kZXIoJ2ZkZjQ0N2RlJywgcmVuZGVyKVxuICB9KVxuXG59XG5cblxuZXhwb3J0IGRlZmF1bHQgX19leHBvcnRzX18iXSwibmFtZXMiOltdLCJzb3VyY2VSb290IjoiIn0=\n//# sourceURL=webpack-internal:///./src/components/SemanticDifferential.vue\n");

/***/ }),

/***/ "./src/components/SingleChoiceQuestion.vue":
/*!*************************************************!*\
  !*** ./src/components/SingleChoiceQuestion.vue ***!
  \*************************************************/
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var _SingleChoiceQuestion_vue_vue_type_template_id_76d95bbf__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./SingleChoiceQuestion.vue?vue&type=template&id=76d95bbf */ \"./src/components/SingleChoiceQuestion.vue?vue&type=template&id=76d95bbf\");\n/* harmony import */ var _SingleChoiceQuestion_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./SingleChoiceQuestion.vue?vue&type=script&lang=js */ \"./src/components/SingleChoiceQuestion.vue?vue&type=script&lang=js\");\n/* harmony import */ var C_Files_Arbeit_Projekte_Data_Donation_Lab_Code_DDM_ddm_vue_frontend_node_modules_vue_loader_dist_exportHelper_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./node_modules/vue-loader/dist/exportHelper.js */ \"./node_modules/vue-loader/dist/exportHelper.js\");\n\n\n\n\n;\nconst __exports__ = /*#__PURE__*/(0,C_Files_Arbeit_Projekte_Data_Donation_Lab_Code_DDM_ddm_vue_frontend_node_modules_vue_loader_dist_exportHelper_js__WEBPACK_IMPORTED_MODULE_2__[\"default\"])(_SingleChoiceQuestion_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_1__[\"default\"], [['render',_SingleChoiceQuestion_vue_vue_type_template_id_76d95bbf__WEBPACK_IMPORTED_MODULE_0__.render],['__file',\"src/components/SingleChoiceQuestion.vue\"]])\n/* hot reload */\nif (true) {\n  __exports__.__hmrId = \"76d95bbf\"\n  const api = __VUE_HMR_RUNTIME__\n  module.hot.accept()\n  if (!api.createRecord('76d95bbf', __exports__)) {\n    api.reload('76d95bbf', __exports__)\n  }\n  \n  module.hot.accept(/*! ./SingleChoiceQuestion.vue?vue&type=template&id=76d95bbf */ \"./src/components/SingleChoiceQuestion.vue?vue&type=template&id=76d95bbf\", function(__WEBPACK_OUTDATED_DEPENDENCIES__) { /* harmony import */ _SingleChoiceQuestion_vue_vue_type_template_id_76d95bbf__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./SingleChoiceQuestion.vue?vue&type=template&id=76d95bbf */ \"./src/components/SingleChoiceQuestion.vue?vue&type=template&id=76d95bbf\");\n(() => {\n    api.rerender('76d95bbf', _SingleChoiceQuestion_vue_vue_type_template_id_76d95bbf__WEBPACK_IMPORTED_MODULE_0__.render)\n  })(__WEBPACK_OUTDATED_DEPENDENCIES__); }.bind(this))\n\n}\n\n\n/* harmony default export */ __webpack_exports__[\"default\"] = (__exports__);//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi9zcmMvY29tcG9uZW50cy9TaW5nbGVDaG9pY2VRdWVzdGlvbi52dWUuanMiLCJtYXBwaW5ncyI6Ijs7OztBQUFBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQUE7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSIsInNvdXJjZXMiOlsid2VicGFjazovL3Z1ZV9mcm9udGVuZC8uL3NyYy9jb21wb25lbnRzL1NpbmdsZUNob2ljZVF1ZXN0aW9uLnZ1ZT9lZjMxIl0sInNvdXJjZXNDb250ZW50IjpbImltcG9ydCB7IHJlbmRlciB9IGZyb20gXCIuL1NpbmdsZUNob2ljZVF1ZXN0aW9uLnZ1ZT92dWUmdHlwZT10ZW1wbGF0ZSZpZD03NmQ5NWJiZlwiXG5pbXBvcnQgc2NyaXB0IGZyb20gXCIuL1NpbmdsZUNob2ljZVF1ZXN0aW9uLnZ1ZT92dWUmdHlwZT1zY3JpcHQmbGFuZz1qc1wiXG5leHBvcnQgKiBmcm9tIFwiLi9TaW5nbGVDaG9pY2VRdWVzdGlvbi52dWU/dnVlJnR5cGU9c2NyaXB0Jmxhbmc9anNcIlxuXG5pbXBvcnQgZXhwb3J0Q29tcG9uZW50IGZyb20gXCJDOlxcXFxGaWxlc1xcXFxBcmJlaXRcXFxcUHJvamVrdGVcXFxcRGF0YSBEb25hdGlvbiBMYWJcXFxcQ29kZVxcXFxERE1cXFxcZGRtXFxcXHZ1ZV9mcm9udGVuZFxcXFxub2RlX21vZHVsZXNcXFxcdnVlLWxvYWRlclxcXFxkaXN0XFxcXGV4cG9ydEhlbHBlci5qc1wiXG5jb25zdCBfX2V4cG9ydHNfXyA9IC8qI19fUFVSRV9fKi9leHBvcnRDb21wb25lbnQoc2NyaXB0LCBbWydyZW5kZXInLHJlbmRlcl0sWydfX2ZpbGUnLFwic3JjL2NvbXBvbmVudHMvU2luZ2xlQ2hvaWNlUXVlc3Rpb24udnVlXCJdXSlcbi8qIGhvdCByZWxvYWQgKi9cbmlmIChtb2R1bGUuaG90KSB7XG4gIF9fZXhwb3J0c19fLl9faG1ySWQgPSBcIjc2ZDk1YmJmXCJcbiAgY29uc3QgYXBpID0gX19WVUVfSE1SX1JVTlRJTUVfX1xuICBtb2R1bGUuaG90LmFjY2VwdCgpXG4gIGlmICghYXBpLmNyZWF0ZVJlY29yZCgnNzZkOTViYmYnLCBfX2V4cG9ydHNfXykpIHtcbiAgICBhcGkucmVsb2FkKCc3NmQ5NWJiZicsIF9fZXhwb3J0c19fKVxuICB9XG4gIFxuICBtb2R1bGUuaG90LmFjY2VwdChcIi4vU2luZ2xlQ2hvaWNlUXVlc3Rpb24udnVlP3Z1ZSZ0eXBlPXRlbXBsYXRlJmlkPTc2ZDk1YmJmXCIsICgpID0+IHtcbiAgICBhcGkucmVyZW5kZXIoJzc2ZDk1YmJmJywgcmVuZGVyKVxuICB9KVxuXG59XG5cblxuZXhwb3J0IGRlZmF1bHQgX19leHBvcnRzX18iXSwibmFtZXMiOltdLCJzb3VyY2VSb290IjoiIn0=\n//# sourceURL=webpack-internal:///./src/components/SingleChoiceQuestion.vue\n");

/***/ }),

/***/ "./src/components/TransitionQuestion.vue":
/*!***********************************************!*\
  !*** ./src/components/TransitionQuestion.vue ***!
  \***********************************************/
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var _TransitionQuestion_vue_vue_type_template_id_43ff75ea__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./TransitionQuestion.vue?vue&type=template&id=43ff75ea */ \"./src/components/TransitionQuestion.vue?vue&type=template&id=43ff75ea\");\n/* harmony import */ var _TransitionQuestion_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./TransitionQuestion.vue?vue&type=script&lang=js */ \"./src/components/TransitionQuestion.vue?vue&type=script&lang=js\");\n/* harmony import */ var C_Files_Arbeit_Projekte_Data_Donation_Lab_Code_DDM_ddm_vue_frontend_node_modules_vue_loader_dist_exportHelper_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./node_modules/vue-loader/dist/exportHelper.js */ \"./node_modules/vue-loader/dist/exportHelper.js\");\n\n\n\n\n;\nconst __exports__ = /*#__PURE__*/(0,C_Files_Arbeit_Projekte_Data_Donation_Lab_Code_DDM_ddm_vue_frontend_node_modules_vue_loader_dist_exportHelper_js__WEBPACK_IMPORTED_MODULE_2__[\"default\"])(_TransitionQuestion_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_1__[\"default\"], [['render',_TransitionQuestion_vue_vue_type_template_id_43ff75ea__WEBPACK_IMPORTED_MODULE_0__.render],['__file',\"src/components/TransitionQuestion.vue\"]])\n/* hot reload */\nif (true) {\n  __exports__.__hmrId = \"43ff75ea\"\n  const api = __VUE_HMR_RUNTIME__\n  module.hot.accept()\n  if (!api.createRecord('43ff75ea', __exports__)) {\n    api.reload('43ff75ea', __exports__)\n  }\n  \n  module.hot.accept(/*! ./TransitionQuestion.vue?vue&type=template&id=43ff75ea */ \"./src/components/TransitionQuestion.vue?vue&type=template&id=43ff75ea\", function(__WEBPACK_OUTDATED_DEPENDENCIES__) { /* harmony import */ _TransitionQuestion_vue_vue_type_template_id_43ff75ea__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./TransitionQuestion.vue?vue&type=template&id=43ff75ea */ \"./src/components/TransitionQuestion.vue?vue&type=template&id=43ff75ea\");\n(() => {\n    api.rerender('43ff75ea', _TransitionQuestion_vue_vue_type_template_id_43ff75ea__WEBPACK_IMPORTED_MODULE_0__.render)\n  })(__WEBPACK_OUTDATED_DEPENDENCIES__); }.bind(this))\n\n}\n\n\n/* harmony default export */ __webpack_exports__[\"default\"] = (__exports__);//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi9zcmMvY29tcG9uZW50cy9UcmFuc2l0aW9uUXVlc3Rpb24udnVlLmpzIiwibWFwcGluZ3MiOiI7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUFBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0EiLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly92dWVfZnJvbnRlbmQvLi9zcmMvY29tcG9uZW50cy9UcmFuc2l0aW9uUXVlc3Rpb24udnVlPzVhMTkiXSwic291cmNlc0NvbnRlbnQiOlsiaW1wb3J0IHsgcmVuZGVyIH0gZnJvbSBcIi4vVHJhbnNpdGlvblF1ZXN0aW9uLnZ1ZT92dWUmdHlwZT10ZW1wbGF0ZSZpZD00M2ZmNzVlYVwiXG5pbXBvcnQgc2NyaXB0IGZyb20gXCIuL1RyYW5zaXRpb25RdWVzdGlvbi52dWU/dnVlJnR5cGU9c2NyaXB0Jmxhbmc9anNcIlxuZXhwb3J0ICogZnJvbSBcIi4vVHJhbnNpdGlvblF1ZXN0aW9uLnZ1ZT92dWUmdHlwZT1zY3JpcHQmbGFuZz1qc1wiXG5cbmltcG9ydCBleHBvcnRDb21wb25lbnQgZnJvbSBcIkM6XFxcXEZpbGVzXFxcXEFyYmVpdFxcXFxQcm9qZWt0ZVxcXFxEYXRhIERvbmF0aW9uIExhYlxcXFxDb2RlXFxcXERETVxcXFxkZG1cXFxcdnVlX2Zyb250ZW5kXFxcXG5vZGVfbW9kdWxlc1xcXFx2dWUtbG9hZGVyXFxcXGRpc3RcXFxcZXhwb3J0SGVscGVyLmpzXCJcbmNvbnN0IF9fZXhwb3J0c19fID0gLyojX19QVVJFX18qL2V4cG9ydENvbXBvbmVudChzY3JpcHQsIFtbJ3JlbmRlcicscmVuZGVyXSxbJ19fZmlsZScsXCJzcmMvY29tcG9uZW50cy9UcmFuc2l0aW9uUXVlc3Rpb24udnVlXCJdXSlcbi8qIGhvdCByZWxvYWQgKi9cbmlmIChtb2R1bGUuaG90KSB7XG4gIF9fZXhwb3J0c19fLl9faG1ySWQgPSBcIjQzZmY3NWVhXCJcbiAgY29uc3QgYXBpID0gX19WVUVfSE1SX1JVTlRJTUVfX1xuICBtb2R1bGUuaG90LmFjY2VwdCgpXG4gIGlmICghYXBpLmNyZWF0ZVJlY29yZCgnNDNmZjc1ZWEnLCBfX2V4cG9ydHNfXykpIHtcbiAgICBhcGkucmVsb2FkKCc0M2ZmNzVlYScsIF9fZXhwb3J0c19fKVxuICB9XG4gIFxuICBtb2R1bGUuaG90LmFjY2VwdChcIi4vVHJhbnNpdGlvblF1ZXN0aW9uLnZ1ZT92dWUmdHlwZT10ZW1wbGF0ZSZpZD00M2ZmNzVlYVwiLCAoKSA9PiB7XG4gICAgYXBpLnJlcmVuZGVyKCc0M2ZmNzVlYScsIHJlbmRlcilcbiAgfSlcblxufVxuXG5cbmV4cG9ydCBkZWZhdWx0IF9fZXhwb3J0c19fIl0sIm5hbWVzIjpbXSwic291cmNlUm9vdCI6IiJ9\n//# sourceURL=webpack-internal:///./src/components/TransitionQuestion.vue\n");

/***/ }),

/***/ "./src/QuestionnaireApp.vue?vue&type=script&lang=js":
/*!**********************************************************!*\
  !*** ./src/QuestionnaireApp.vue?vue&type=script&lang=js ***!
  \**********************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   \"default\": function() { return /* reexport safe */ _node_modules_babel_loader_lib_index_js_clonedRuleSet_40_use_0_node_modules_vue_loader_dist_index_js_ruleSet_0_use_0_QuestionnaireApp_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_0__[\"default\"]; }\n/* harmony export */ });\n/* harmony import */ var _node_modules_babel_loader_lib_index_js_clonedRuleSet_40_use_0_node_modules_vue_loader_dist_index_js_ruleSet_0_use_0_QuestionnaireApp_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! -!../node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!../node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./QuestionnaireApp.vue?vue&type=script&lang=js */ \"./node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!./node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./src/QuestionnaireApp.vue?vue&type=script&lang=js\");\n //# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi9zcmMvUXVlc3Rpb25uYWlyZUFwcC52dWU/dnVlJnR5cGU9c2NyaXB0Jmxhbmc9anMuanMiLCJtYXBwaW5ncyI6Ijs7Ozs7QUFBQSIsInNvdXJjZXMiOlsid2VicGFjazovL3Z1ZV9mcm9udGVuZC8uL3NyYy9RdWVzdGlvbm5haXJlQXBwLnZ1ZT85NDRmIl0sInNvdXJjZXNDb250ZW50IjpbImV4cG9ydCB7IGRlZmF1bHQgfSBmcm9tIFwiLSEuLi9ub2RlX21vZHVsZXMvYmFiZWwtbG9hZGVyL2xpYi9pbmRleC5qcz8/Y2xvbmVkUnVsZVNldC00MC51c2VbMF0hLi4vbm9kZV9tb2R1bGVzL3Z1ZS1sb2FkZXIvZGlzdC9pbmRleC5qcz8/cnVsZVNldFswXS51c2VbMF0hLi9RdWVzdGlvbm5haXJlQXBwLnZ1ZT92dWUmdHlwZT1zY3JpcHQmbGFuZz1qc1wiOyBleHBvcnQgKiBmcm9tIFwiLSEuLi9ub2RlX21vZHVsZXMvYmFiZWwtbG9hZGVyL2xpYi9pbmRleC5qcz8/Y2xvbmVkUnVsZVNldC00MC51c2VbMF0hLi4vbm9kZV9tb2R1bGVzL3Z1ZS1sb2FkZXIvZGlzdC9pbmRleC5qcz8/cnVsZVNldFswXS51c2VbMF0hLi9RdWVzdGlvbm5haXJlQXBwLnZ1ZT92dWUmdHlwZT1zY3JpcHQmbGFuZz1qc1wiIl0sIm5hbWVzIjpbXSwic291cmNlUm9vdCI6IiJ9\n//# sourceURL=webpack-internal:///./src/QuestionnaireApp.vue?vue&type=script&lang=js\n");

/***/ }),

/***/ "./src/components/MatrixQuestion.vue?vue&type=script&lang=js":
/*!*******************************************************************!*\
  !*** ./src/components/MatrixQuestion.vue?vue&type=script&lang=js ***!
  \*******************************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   \"default\": function() { return /* reexport safe */ _node_modules_babel_loader_lib_index_js_clonedRuleSet_40_use_0_node_modules_vue_loader_dist_index_js_ruleSet_0_use_0_MatrixQuestion_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_0__[\"default\"]; }\n/* harmony export */ });\n/* harmony import */ var _node_modules_babel_loader_lib_index_js_clonedRuleSet_40_use_0_node_modules_vue_loader_dist_index_js_ruleSet_0_use_0_MatrixQuestion_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! -!../../node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!../../node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./MatrixQuestion.vue?vue&type=script&lang=js */ \"./node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!./node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./src/components/MatrixQuestion.vue?vue&type=script&lang=js\");\n //# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi9zcmMvY29tcG9uZW50cy9NYXRyaXhRdWVzdGlvbi52dWU/dnVlJnR5cGU9c2NyaXB0Jmxhbmc9anMuanMiLCJtYXBwaW5ncyI6Ijs7Ozs7QUFBQSIsInNvdXJjZXMiOlsid2VicGFjazovL3Z1ZV9mcm9udGVuZC8uL3NyYy9jb21wb25lbnRzL01hdHJpeFF1ZXN0aW9uLnZ1ZT84YTU5Il0sInNvdXJjZXNDb250ZW50IjpbImV4cG9ydCB7IGRlZmF1bHQgfSBmcm9tIFwiLSEuLi8uLi9ub2RlX21vZHVsZXMvYmFiZWwtbG9hZGVyL2xpYi9pbmRleC5qcz8/Y2xvbmVkUnVsZVNldC00MC51c2VbMF0hLi4vLi4vbm9kZV9tb2R1bGVzL3Z1ZS1sb2FkZXIvZGlzdC9pbmRleC5qcz8/cnVsZVNldFswXS51c2VbMF0hLi9NYXRyaXhRdWVzdGlvbi52dWU/dnVlJnR5cGU9c2NyaXB0Jmxhbmc9anNcIjsgZXhwb3J0ICogZnJvbSBcIi0hLi4vLi4vbm9kZV9tb2R1bGVzL2JhYmVsLWxvYWRlci9saWIvaW5kZXguanM/P2Nsb25lZFJ1bGVTZXQtNDAudXNlWzBdIS4uLy4uL25vZGVfbW9kdWxlcy92dWUtbG9hZGVyL2Rpc3QvaW5kZXguanM/P3J1bGVTZXRbMF0udXNlWzBdIS4vTWF0cml4UXVlc3Rpb24udnVlP3Z1ZSZ0eXBlPXNjcmlwdCZsYW5nPWpzXCIiXSwibmFtZXMiOltdLCJzb3VyY2VSb290IjoiIn0=\n//# sourceURL=webpack-internal:///./src/components/MatrixQuestion.vue?vue&type=script&lang=js\n");

/***/ }),

/***/ "./src/components/MultiChoiceQuestion.vue?vue&type=script&lang=js":
/*!************************************************************************!*\
  !*** ./src/components/MultiChoiceQuestion.vue?vue&type=script&lang=js ***!
  \************************************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   \"default\": function() { return /* reexport safe */ _node_modules_babel_loader_lib_index_js_clonedRuleSet_40_use_0_node_modules_vue_loader_dist_index_js_ruleSet_0_use_0_MultiChoiceQuestion_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_0__[\"default\"]; }\n/* harmony export */ });\n/* harmony import */ var _node_modules_babel_loader_lib_index_js_clonedRuleSet_40_use_0_node_modules_vue_loader_dist_index_js_ruleSet_0_use_0_MultiChoiceQuestion_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! -!../../node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!../../node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./MultiChoiceQuestion.vue?vue&type=script&lang=js */ \"./node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!./node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./src/components/MultiChoiceQuestion.vue?vue&type=script&lang=js\");\n //# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi9zcmMvY29tcG9uZW50cy9NdWx0aUNob2ljZVF1ZXN0aW9uLnZ1ZT92dWUmdHlwZT1zY3JpcHQmbGFuZz1qcy5qcyIsIm1hcHBpbmdzIjoiOzs7OztBQUFBIiwic291cmNlcyI6WyJ3ZWJwYWNrOi8vdnVlX2Zyb250ZW5kLy4vc3JjL2NvbXBvbmVudHMvTXVsdGlDaG9pY2VRdWVzdGlvbi52dWU/ZDVkZSJdLCJzb3VyY2VzQ29udGVudCI6WyJleHBvcnQgeyBkZWZhdWx0IH0gZnJvbSBcIi0hLi4vLi4vbm9kZV9tb2R1bGVzL2JhYmVsLWxvYWRlci9saWIvaW5kZXguanM/P2Nsb25lZFJ1bGVTZXQtNDAudXNlWzBdIS4uLy4uL25vZGVfbW9kdWxlcy92dWUtbG9hZGVyL2Rpc3QvaW5kZXguanM/P3J1bGVTZXRbMF0udXNlWzBdIS4vTXVsdGlDaG9pY2VRdWVzdGlvbi52dWU/dnVlJnR5cGU9c2NyaXB0Jmxhbmc9anNcIjsgZXhwb3J0ICogZnJvbSBcIi0hLi4vLi4vbm9kZV9tb2R1bGVzL2JhYmVsLWxvYWRlci9saWIvaW5kZXguanM/P2Nsb25lZFJ1bGVTZXQtNDAudXNlWzBdIS4uLy4uL25vZGVfbW9kdWxlcy92dWUtbG9hZGVyL2Rpc3QvaW5kZXguanM/P3J1bGVTZXRbMF0udXNlWzBdIS4vTXVsdGlDaG9pY2VRdWVzdGlvbi52dWU/dnVlJnR5cGU9c2NyaXB0Jmxhbmc9anNcIiJdLCJuYW1lcyI6W10sInNvdXJjZVJvb3QiOiIifQ==\n//# sourceURL=webpack-internal:///./src/components/MultiChoiceQuestion.vue?vue&type=script&lang=js\n");

/***/ }),

/***/ "./src/components/OpenQuestion.vue?vue&type=script&lang=js":
/*!*****************************************************************!*\
  !*** ./src/components/OpenQuestion.vue?vue&type=script&lang=js ***!
  \*****************************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   \"default\": function() { return /* reexport safe */ _node_modules_babel_loader_lib_index_js_clonedRuleSet_40_use_0_node_modules_vue_loader_dist_index_js_ruleSet_0_use_0_OpenQuestion_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_0__[\"default\"]; }\n/* harmony export */ });\n/* harmony import */ var _node_modules_babel_loader_lib_index_js_clonedRuleSet_40_use_0_node_modules_vue_loader_dist_index_js_ruleSet_0_use_0_OpenQuestion_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! -!../../node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!../../node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./OpenQuestion.vue?vue&type=script&lang=js */ \"./node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!./node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./src/components/OpenQuestion.vue?vue&type=script&lang=js\");\n //# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi9zcmMvY29tcG9uZW50cy9PcGVuUXVlc3Rpb24udnVlP3Z1ZSZ0eXBlPXNjcmlwdCZsYW5nPWpzLmpzIiwibWFwcGluZ3MiOiI7Ozs7O0FBQUEiLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly92dWVfZnJvbnRlbmQvLi9zcmMvY29tcG9uZW50cy9PcGVuUXVlc3Rpb24udnVlP2QyY2EiXSwic291cmNlc0NvbnRlbnQiOlsiZXhwb3J0IHsgZGVmYXVsdCB9IGZyb20gXCItIS4uLy4uL25vZGVfbW9kdWxlcy9iYWJlbC1sb2FkZXIvbGliL2luZGV4LmpzPz9jbG9uZWRSdWxlU2V0LTQwLnVzZVswXSEuLi8uLi9ub2RlX21vZHVsZXMvdnVlLWxvYWRlci9kaXN0L2luZGV4LmpzPz9ydWxlU2V0WzBdLnVzZVswXSEuL09wZW5RdWVzdGlvbi52dWU/dnVlJnR5cGU9c2NyaXB0Jmxhbmc9anNcIjsgZXhwb3J0ICogZnJvbSBcIi0hLi4vLi4vbm9kZV9tb2R1bGVzL2JhYmVsLWxvYWRlci9saWIvaW5kZXguanM/P2Nsb25lZFJ1bGVTZXQtNDAudXNlWzBdIS4uLy4uL25vZGVfbW9kdWxlcy92dWUtbG9hZGVyL2Rpc3QvaW5kZXguanM/P3J1bGVTZXRbMF0udXNlWzBdIS4vT3BlblF1ZXN0aW9uLnZ1ZT92dWUmdHlwZT1zY3JpcHQmbGFuZz1qc1wiIl0sIm5hbWVzIjpbXSwic291cmNlUm9vdCI6IiJ9\n//# sourceURL=webpack-internal:///./src/components/OpenQuestion.vue?vue&type=script&lang=js\n");

/***/ }),

/***/ "./src/components/SemanticDifferential.vue?vue&type=script&lang=js":
/*!*************************************************************************!*\
  !*** ./src/components/SemanticDifferential.vue?vue&type=script&lang=js ***!
  \*************************************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   \"default\": function() { return /* reexport safe */ _node_modules_babel_loader_lib_index_js_clonedRuleSet_40_use_0_node_modules_vue_loader_dist_index_js_ruleSet_0_use_0_SemanticDifferential_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_0__[\"default\"]; }\n/* harmony export */ });\n/* harmony import */ var _node_modules_babel_loader_lib_index_js_clonedRuleSet_40_use_0_node_modules_vue_loader_dist_index_js_ruleSet_0_use_0_SemanticDifferential_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! -!../../node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!../../node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./SemanticDifferential.vue?vue&type=script&lang=js */ \"./node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!./node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./src/components/SemanticDifferential.vue?vue&type=script&lang=js\");\n //# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi9zcmMvY29tcG9uZW50cy9TZW1hbnRpY0RpZmZlcmVudGlhbC52dWU/dnVlJnR5cGU9c2NyaXB0Jmxhbmc9anMuanMiLCJtYXBwaW5ncyI6Ijs7Ozs7QUFBQSIsInNvdXJjZXMiOlsid2VicGFjazovL3Z1ZV9mcm9udGVuZC8uL3NyYy9jb21wb25lbnRzL1NlbWFudGljRGlmZmVyZW50aWFsLnZ1ZT85OWJjIl0sInNvdXJjZXNDb250ZW50IjpbImV4cG9ydCB7IGRlZmF1bHQgfSBmcm9tIFwiLSEuLi8uLi9ub2RlX21vZHVsZXMvYmFiZWwtbG9hZGVyL2xpYi9pbmRleC5qcz8/Y2xvbmVkUnVsZVNldC00MC51c2VbMF0hLi4vLi4vbm9kZV9tb2R1bGVzL3Z1ZS1sb2FkZXIvZGlzdC9pbmRleC5qcz8/cnVsZVNldFswXS51c2VbMF0hLi9TZW1hbnRpY0RpZmZlcmVudGlhbC52dWU/dnVlJnR5cGU9c2NyaXB0Jmxhbmc9anNcIjsgZXhwb3J0ICogZnJvbSBcIi0hLi4vLi4vbm9kZV9tb2R1bGVzL2JhYmVsLWxvYWRlci9saWIvaW5kZXguanM/P2Nsb25lZFJ1bGVTZXQtNDAudXNlWzBdIS4uLy4uL25vZGVfbW9kdWxlcy92dWUtbG9hZGVyL2Rpc3QvaW5kZXguanM/P3J1bGVTZXRbMF0udXNlWzBdIS4vU2VtYW50aWNEaWZmZXJlbnRpYWwudnVlP3Z1ZSZ0eXBlPXNjcmlwdCZsYW5nPWpzXCIiXSwibmFtZXMiOltdLCJzb3VyY2VSb290IjoiIn0=\n//# sourceURL=webpack-internal:///./src/components/SemanticDifferential.vue?vue&type=script&lang=js\n");

/***/ }),

/***/ "./src/components/SingleChoiceQuestion.vue?vue&type=script&lang=js":
/*!*************************************************************************!*\
  !*** ./src/components/SingleChoiceQuestion.vue?vue&type=script&lang=js ***!
  \*************************************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   \"default\": function() { return /* reexport safe */ _node_modules_babel_loader_lib_index_js_clonedRuleSet_40_use_0_node_modules_vue_loader_dist_index_js_ruleSet_0_use_0_SingleChoiceQuestion_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_0__[\"default\"]; }\n/* harmony export */ });\n/* harmony import */ var _node_modules_babel_loader_lib_index_js_clonedRuleSet_40_use_0_node_modules_vue_loader_dist_index_js_ruleSet_0_use_0_SingleChoiceQuestion_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! -!../../node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!../../node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./SingleChoiceQuestion.vue?vue&type=script&lang=js */ \"./node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!./node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./src/components/SingleChoiceQuestion.vue?vue&type=script&lang=js\");\n //# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi9zcmMvY29tcG9uZW50cy9TaW5nbGVDaG9pY2VRdWVzdGlvbi52dWU/dnVlJnR5cGU9c2NyaXB0Jmxhbmc9anMuanMiLCJtYXBwaW5ncyI6Ijs7Ozs7QUFBQSIsInNvdXJjZXMiOlsid2VicGFjazovL3Z1ZV9mcm9udGVuZC8uL3NyYy9jb21wb25lbnRzL1NpbmdsZUNob2ljZVF1ZXN0aW9uLnZ1ZT82NmVmIl0sInNvdXJjZXNDb250ZW50IjpbImV4cG9ydCB7IGRlZmF1bHQgfSBmcm9tIFwiLSEuLi8uLi9ub2RlX21vZHVsZXMvYmFiZWwtbG9hZGVyL2xpYi9pbmRleC5qcz8/Y2xvbmVkUnVsZVNldC00MC51c2VbMF0hLi4vLi4vbm9kZV9tb2R1bGVzL3Z1ZS1sb2FkZXIvZGlzdC9pbmRleC5qcz8/cnVsZVNldFswXS51c2VbMF0hLi9TaW5nbGVDaG9pY2VRdWVzdGlvbi52dWU/dnVlJnR5cGU9c2NyaXB0Jmxhbmc9anNcIjsgZXhwb3J0ICogZnJvbSBcIi0hLi4vLi4vbm9kZV9tb2R1bGVzL2JhYmVsLWxvYWRlci9saWIvaW5kZXguanM/P2Nsb25lZFJ1bGVTZXQtNDAudXNlWzBdIS4uLy4uL25vZGVfbW9kdWxlcy92dWUtbG9hZGVyL2Rpc3QvaW5kZXguanM/P3J1bGVTZXRbMF0udXNlWzBdIS4vU2luZ2xlQ2hvaWNlUXVlc3Rpb24udnVlP3Z1ZSZ0eXBlPXNjcmlwdCZsYW5nPWpzXCIiXSwibmFtZXMiOltdLCJzb3VyY2VSb290IjoiIn0=\n//# sourceURL=webpack-internal:///./src/components/SingleChoiceQuestion.vue?vue&type=script&lang=js\n");

/***/ }),

/***/ "./src/components/TransitionQuestion.vue?vue&type=script&lang=js":
/*!***********************************************************************!*\
  !*** ./src/components/TransitionQuestion.vue?vue&type=script&lang=js ***!
  \***********************************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   \"default\": function() { return /* reexport safe */ _node_modules_babel_loader_lib_index_js_clonedRuleSet_40_use_0_node_modules_vue_loader_dist_index_js_ruleSet_0_use_0_TransitionQuestion_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_0__[\"default\"]; }\n/* harmony export */ });\n/* harmony import */ var _node_modules_babel_loader_lib_index_js_clonedRuleSet_40_use_0_node_modules_vue_loader_dist_index_js_ruleSet_0_use_0_TransitionQuestion_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! -!../../node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!../../node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./TransitionQuestion.vue?vue&type=script&lang=js */ \"./node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!./node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./src/components/TransitionQuestion.vue?vue&type=script&lang=js\");\n //# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi9zcmMvY29tcG9uZW50cy9UcmFuc2l0aW9uUXVlc3Rpb24udnVlP3Z1ZSZ0eXBlPXNjcmlwdCZsYW5nPWpzLmpzIiwibWFwcGluZ3MiOiI7Ozs7O0FBQUEiLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly92dWVfZnJvbnRlbmQvLi9zcmMvY29tcG9uZW50cy9UcmFuc2l0aW9uUXVlc3Rpb24udnVlPzlhYmYiXSwic291cmNlc0NvbnRlbnQiOlsiZXhwb3J0IHsgZGVmYXVsdCB9IGZyb20gXCItIS4uLy4uL25vZGVfbW9kdWxlcy9iYWJlbC1sb2FkZXIvbGliL2luZGV4LmpzPz9jbG9uZWRSdWxlU2V0LTQwLnVzZVswXSEuLi8uLi9ub2RlX21vZHVsZXMvdnVlLWxvYWRlci9kaXN0L2luZGV4LmpzPz9ydWxlU2V0WzBdLnVzZVswXSEuL1RyYW5zaXRpb25RdWVzdGlvbi52dWU/dnVlJnR5cGU9c2NyaXB0Jmxhbmc9anNcIjsgZXhwb3J0ICogZnJvbSBcIi0hLi4vLi4vbm9kZV9tb2R1bGVzL2JhYmVsLWxvYWRlci9saWIvaW5kZXguanM/P2Nsb25lZFJ1bGVTZXQtNDAudXNlWzBdIS4uLy4uL25vZGVfbW9kdWxlcy92dWUtbG9hZGVyL2Rpc3QvaW5kZXguanM/P3J1bGVTZXRbMF0udXNlWzBdIS4vVHJhbnNpdGlvblF1ZXN0aW9uLnZ1ZT92dWUmdHlwZT1zY3JpcHQmbGFuZz1qc1wiIl0sIm5hbWVzIjpbXSwic291cmNlUm9vdCI6IiJ9\n//# sourceURL=webpack-internal:///./src/components/TransitionQuestion.vue?vue&type=script&lang=js\n");

/***/ }),

/***/ "./src/QuestionnaireApp.vue?vue&type=template&id=2f351a77":
/*!****************************************************************!*\
  !*** ./src/QuestionnaireApp.vue?vue&type=template&id=2f351a77 ***!
  \****************************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "render": function() { return /* reexport safe */ _node_modules_babel_loader_lib_index_js_clonedRuleSet_40_use_0_node_modules_vue_loader_dist_templateLoader_js_ruleSet_1_rules_3_node_modules_vue_loader_dist_index_js_ruleSet_0_use_0_QuestionnaireApp_vue_vue_type_template_id_2f351a77__WEBPACK_IMPORTED_MODULE_0__.render; }
/* harmony export */ });
/* harmony import */ var _node_modules_babel_loader_lib_index_js_clonedRuleSet_40_use_0_node_modules_vue_loader_dist_templateLoader_js_ruleSet_1_rules_3_node_modules_vue_loader_dist_index_js_ruleSet_0_use_0_QuestionnaireApp_vue_vue_type_template_id_2f351a77__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! -!../node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!../node_modules/vue-loader/dist/templateLoader.js??ruleSet[1].rules[3]!../node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./QuestionnaireApp.vue?vue&type=template&id=2f351a77 */ "./node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!./node_modules/vue-loader/dist/templateLoader.js??ruleSet[1].rules[3]!./node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./src/QuestionnaireApp.vue?vue&type=template&id=2f351a77");


/***/ }),

/***/ "./src/components/MatrixQuestion.vue?vue&type=template&id=5831b977":
/*!*************************************************************************!*\
  !*** ./src/components/MatrixQuestion.vue?vue&type=template&id=5831b977 ***!
  \*************************************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "render": function() { return /* reexport safe */ _node_modules_babel_loader_lib_index_js_clonedRuleSet_40_use_0_node_modules_vue_loader_dist_templateLoader_js_ruleSet_1_rules_3_node_modules_vue_loader_dist_index_js_ruleSet_0_use_0_MatrixQuestion_vue_vue_type_template_id_5831b977__WEBPACK_IMPORTED_MODULE_0__.render; }
/* harmony export */ });
/* harmony import */ var _node_modules_babel_loader_lib_index_js_clonedRuleSet_40_use_0_node_modules_vue_loader_dist_templateLoader_js_ruleSet_1_rules_3_node_modules_vue_loader_dist_index_js_ruleSet_0_use_0_MatrixQuestion_vue_vue_type_template_id_5831b977__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! -!../../node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!../../node_modules/vue-loader/dist/templateLoader.js??ruleSet[1].rules[3]!../../node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./MatrixQuestion.vue?vue&type=template&id=5831b977 */ "./node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!./node_modules/vue-loader/dist/templateLoader.js??ruleSet[1].rules[3]!./node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./src/components/MatrixQuestion.vue?vue&type=template&id=5831b977");


/***/ }),

/***/ "./src/components/MultiChoiceQuestion.vue?vue&type=template&id=0bba8c40":
/*!******************************************************************************!*\
  !*** ./src/components/MultiChoiceQuestion.vue?vue&type=template&id=0bba8c40 ***!
  \******************************************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "render": function() { return /* reexport safe */ _node_modules_babel_loader_lib_index_js_clonedRuleSet_40_use_0_node_modules_vue_loader_dist_templateLoader_js_ruleSet_1_rules_3_node_modules_vue_loader_dist_index_js_ruleSet_0_use_0_MultiChoiceQuestion_vue_vue_type_template_id_0bba8c40__WEBPACK_IMPORTED_MODULE_0__.render; }
/* harmony export */ });
/* harmony import */ var _node_modules_babel_loader_lib_index_js_clonedRuleSet_40_use_0_node_modules_vue_loader_dist_templateLoader_js_ruleSet_1_rules_3_node_modules_vue_loader_dist_index_js_ruleSet_0_use_0_MultiChoiceQuestion_vue_vue_type_template_id_0bba8c40__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! -!../../node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!../../node_modules/vue-loader/dist/templateLoader.js??ruleSet[1].rules[3]!../../node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./MultiChoiceQuestion.vue?vue&type=template&id=0bba8c40 */ "./node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!./node_modules/vue-loader/dist/templateLoader.js??ruleSet[1].rules[3]!./node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./src/components/MultiChoiceQuestion.vue?vue&type=template&id=0bba8c40");


/***/ }),

/***/ "./src/components/OpenQuestion.vue?vue&type=template&id=0e43c880":
/*!***********************************************************************!*\
  !*** ./src/components/OpenQuestion.vue?vue&type=template&id=0e43c880 ***!
  \***********************************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "render": function() { return /* reexport safe */ _node_modules_babel_loader_lib_index_js_clonedRuleSet_40_use_0_node_modules_vue_loader_dist_templateLoader_js_ruleSet_1_rules_3_node_modules_vue_loader_dist_index_js_ruleSet_0_use_0_OpenQuestion_vue_vue_type_template_id_0e43c880__WEBPACK_IMPORTED_MODULE_0__.render; }
/* harmony export */ });
/* harmony import */ var _node_modules_babel_loader_lib_index_js_clonedRuleSet_40_use_0_node_modules_vue_loader_dist_templateLoader_js_ruleSet_1_rules_3_node_modules_vue_loader_dist_index_js_ruleSet_0_use_0_OpenQuestion_vue_vue_type_template_id_0e43c880__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! -!../../node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!../../node_modules/vue-loader/dist/templateLoader.js??ruleSet[1].rules[3]!../../node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./OpenQuestion.vue?vue&type=template&id=0e43c880 */ "./node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!./node_modules/vue-loader/dist/templateLoader.js??ruleSet[1].rules[3]!./node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./src/components/OpenQuestion.vue?vue&type=template&id=0e43c880");


/***/ }),

/***/ "./src/components/SemanticDifferential.vue?vue&type=template&id=fdf447de":
/*!*******************************************************************************!*\
  !*** ./src/components/SemanticDifferential.vue?vue&type=template&id=fdf447de ***!
  \*******************************************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "render": function() { return /* reexport safe */ _node_modules_babel_loader_lib_index_js_clonedRuleSet_40_use_0_node_modules_vue_loader_dist_templateLoader_js_ruleSet_1_rules_3_node_modules_vue_loader_dist_index_js_ruleSet_0_use_0_SemanticDifferential_vue_vue_type_template_id_fdf447de__WEBPACK_IMPORTED_MODULE_0__.render; }
/* harmony export */ });
/* harmony import */ var _node_modules_babel_loader_lib_index_js_clonedRuleSet_40_use_0_node_modules_vue_loader_dist_templateLoader_js_ruleSet_1_rules_3_node_modules_vue_loader_dist_index_js_ruleSet_0_use_0_SemanticDifferential_vue_vue_type_template_id_fdf447de__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! -!../../node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!../../node_modules/vue-loader/dist/templateLoader.js??ruleSet[1].rules[3]!../../node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./SemanticDifferential.vue?vue&type=template&id=fdf447de */ "./node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!./node_modules/vue-loader/dist/templateLoader.js??ruleSet[1].rules[3]!./node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./src/components/SemanticDifferential.vue?vue&type=template&id=fdf447de");


/***/ }),

/***/ "./src/components/SingleChoiceQuestion.vue?vue&type=template&id=76d95bbf":
/*!*******************************************************************************!*\
  !*** ./src/components/SingleChoiceQuestion.vue?vue&type=template&id=76d95bbf ***!
  \*******************************************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "render": function() { return /* reexport safe */ _node_modules_babel_loader_lib_index_js_clonedRuleSet_40_use_0_node_modules_vue_loader_dist_templateLoader_js_ruleSet_1_rules_3_node_modules_vue_loader_dist_index_js_ruleSet_0_use_0_SingleChoiceQuestion_vue_vue_type_template_id_76d95bbf__WEBPACK_IMPORTED_MODULE_0__.render; }
/* harmony export */ });
/* harmony import */ var _node_modules_babel_loader_lib_index_js_clonedRuleSet_40_use_0_node_modules_vue_loader_dist_templateLoader_js_ruleSet_1_rules_3_node_modules_vue_loader_dist_index_js_ruleSet_0_use_0_SingleChoiceQuestion_vue_vue_type_template_id_76d95bbf__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! -!../../node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!../../node_modules/vue-loader/dist/templateLoader.js??ruleSet[1].rules[3]!../../node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./SingleChoiceQuestion.vue?vue&type=template&id=76d95bbf */ "./node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!./node_modules/vue-loader/dist/templateLoader.js??ruleSet[1].rules[3]!./node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./src/components/SingleChoiceQuestion.vue?vue&type=template&id=76d95bbf");


/***/ }),

/***/ "./src/components/TransitionQuestion.vue?vue&type=template&id=43ff75ea":
/*!*****************************************************************************!*\
  !*** ./src/components/TransitionQuestion.vue?vue&type=template&id=43ff75ea ***!
  \*****************************************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "render": function() { return /* reexport safe */ _node_modules_babel_loader_lib_index_js_clonedRuleSet_40_use_0_node_modules_vue_loader_dist_templateLoader_js_ruleSet_1_rules_3_node_modules_vue_loader_dist_index_js_ruleSet_0_use_0_TransitionQuestion_vue_vue_type_template_id_43ff75ea__WEBPACK_IMPORTED_MODULE_0__.render; }
/* harmony export */ });
/* harmony import */ var _node_modules_babel_loader_lib_index_js_clonedRuleSet_40_use_0_node_modules_vue_loader_dist_templateLoader_js_ruleSet_1_rules_3_node_modules_vue_loader_dist_index_js_ruleSet_0_use_0_TransitionQuestion_vue_vue_type_template_id_43ff75ea__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! -!../../node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!../../node_modules/vue-loader/dist/templateLoader.js??ruleSet[1].rules[3]!../../node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./TransitionQuestion.vue?vue&type=template&id=43ff75ea */ "./node_modules/babel-loader/lib/index.js??clonedRuleSet-40.use[0]!./node_modules/vue-loader/dist/templateLoader.js??ruleSet[1].rules[3]!./node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./src/components/TransitionQuestion.vue?vue&type=template&id=43ff75ea");


/***/ }),

/***/ "./src/QuestionnaireApp.vue?vue&type=style&index=0&id=2f351a77&lang=css":
/*!******************************************************************************!*\
  !*** ./src/QuestionnaireApp.vue?vue&type=style&index=0&id=2f351a77&lang=css ***!
  \******************************************************************************/
/***/ (function(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony import */ var _node_modules_vue_style_loader_index_js_clonedRuleSet_12_use_0_node_modules_css_loader_dist_cjs_js_clonedRuleSet_12_use_1_node_modules_vue_loader_dist_stylePostLoader_js_node_modules_postcss_loader_dist_cjs_js_clonedRuleSet_12_use_2_node_modules_vue_loader_dist_index_js_ruleSet_0_use_0_QuestionnaireApp_vue_vue_type_style_index_0_id_2f351a77_lang_css__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! -!../node_modules/vue-style-loader/index.js??clonedRuleSet-12.use[0]!../node_modules/css-loader/dist/cjs.js??clonedRuleSet-12.use[1]!../node_modules/vue-loader/dist/stylePostLoader.js!../node_modules/postcss-loader/dist/cjs.js??clonedRuleSet-12.use[2]!../node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./QuestionnaireApp.vue?vue&type=style&index=0&id=2f351a77&lang=css */ "./node_modules/vue-style-loader/index.js??clonedRuleSet-12.use[0]!./node_modules/css-loader/dist/cjs.js??clonedRuleSet-12.use[1]!./node_modules/vue-loader/dist/stylePostLoader.js!./node_modules/postcss-loader/dist/cjs.js??clonedRuleSet-12.use[2]!./node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./src/QuestionnaireApp.vue?vue&type=style&index=0&id=2f351a77&lang=css");
/* harmony import */ var _node_modules_vue_style_loader_index_js_clonedRuleSet_12_use_0_node_modules_css_loader_dist_cjs_js_clonedRuleSet_12_use_1_node_modules_vue_loader_dist_stylePostLoader_js_node_modules_postcss_loader_dist_cjs_js_clonedRuleSet_12_use_2_node_modules_vue_loader_dist_index_js_ruleSet_0_use_0_QuestionnaireApp_vue_vue_type_style_index_0_id_2f351a77_lang_css__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_node_modules_vue_style_loader_index_js_clonedRuleSet_12_use_0_node_modules_css_loader_dist_cjs_js_clonedRuleSet_12_use_1_node_modules_vue_loader_dist_stylePostLoader_js_node_modules_postcss_loader_dist_cjs_js_clonedRuleSet_12_use_2_node_modules_vue_loader_dist_index_js_ruleSet_0_use_0_QuestionnaireApp_vue_vue_type_style_index_0_id_2f351a77_lang_css__WEBPACK_IMPORTED_MODULE_0__);
/* harmony reexport (unknown) */ var __WEBPACK_REEXPORT_OBJECT__ = {};
/* harmony reexport (unknown) */ for(var __WEBPACK_IMPORT_KEY__ in _node_modules_vue_style_loader_index_js_clonedRuleSet_12_use_0_node_modules_css_loader_dist_cjs_js_clonedRuleSet_12_use_1_node_modules_vue_loader_dist_stylePostLoader_js_node_modules_postcss_loader_dist_cjs_js_clonedRuleSet_12_use_2_node_modules_vue_loader_dist_index_js_ruleSet_0_use_0_QuestionnaireApp_vue_vue_type_style_index_0_id_2f351a77_lang_css__WEBPACK_IMPORTED_MODULE_0__) if(__WEBPACK_IMPORT_KEY__ !== "default") __WEBPACK_REEXPORT_OBJECT__[__WEBPACK_IMPORT_KEY__] = function(key) { return _node_modules_vue_style_loader_index_js_clonedRuleSet_12_use_0_node_modules_css_loader_dist_cjs_js_clonedRuleSet_12_use_1_node_modules_vue_loader_dist_stylePostLoader_js_node_modules_postcss_loader_dist_cjs_js_clonedRuleSet_12_use_2_node_modules_vue_loader_dist_index_js_ruleSet_0_use_0_QuestionnaireApp_vue_vue_type_style_index_0_id_2f351a77_lang_css__WEBPACK_IMPORTED_MODULE_0__[key]; }.bind(0, __WEBPACK_IMPORT_KEY__)
/* harmony reexport (unknown) */ __webpack_require__.d(__webpack_exports__, __WEBPACK_REEXPORT_OBJECT__);


/***/ }),

/***/ "./node_modules/vue-style-loader/index.js??clonedRuleSet-12.use[0]!./node_modules/css-loader/dist/cjs.js??clonedRuleSet-12.use[1]!./node_modules/vue-loader/dist/stylePostLoader.js!./node_modules/postcss-loader/dist/cjs.js??clonedRuleSet-12.use[2]!./node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./src/QuestionnaireApp.vue?vue&type=style&index=0&id=2f351a77&lang=css":
/*!***********************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************!*\
  !*** ./node_modules/vue-style-loader/index.js??clonedRuleSet-12.use[0]!./node_modules/css-loader/dist/cjs.js??clonedRuleSet-12.use[1]!./node_modules/vue-loader/dist/stylePostLoader.js!./node_modules/postcss-loader/dist/cjs.js??clonedRuleSet-12.use[2]!./node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./src/QuestionnaireApp.vue?vue&type=style&index=0&id=2f351a77&lang=css ***!
  \***********************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************/
/***/ (function(module, __unused_webpack_exports, __webpack_require__) {

eval("// style-loader: Adds some css to the DOM by adding a <style> tag\n\n// load the styles\nvar content = __webpack_require__(/*! !!../node_modules/css-loader/dist/cjs.js??clonedRuleSet-12.use[1]!../node_modules/vue-loader/dist/stylePostLoader.js!../node_modules/postcss-loader/dist/cjs.js??clonedRuleSet-12.use[2]!../node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./QuestionnaireApp.vue?vue&type=style&index=0&id=2f351a77&lang=css */ \"./node_modules/css-loader/dist/cjs.js??clonedRuleSet-12.use[1]!./node_modules/vue-loader/dist/stylePostLoader.js!./node_modules/postcss-loader/dist/cjs.js??clonedRuleSet-12.use[2]!./node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./src/QuestionnaireApp.vue?vue&type=style&index=0&id=2f351a77&lang=css\");\nif(content.__esModule) content = content.default;\nif(typeof content === 'string') content = [[module.id, content, '']];\nif(content.locals) module.exports = content.locals;\n// add the styles to the DOM\nvar add = (__webpack_require__(/*! !../node_modules/vue-style-loader/lib/addStylesClient.js */ \"./node_modules/vue-style-loader/lib/addStylesClient.js\")[\"default\"])\nvar update = add(\"a035baf8\", content, false, {\"sourceMap\":false,\"shadowMode\":false});\n// Hot Module Replacement\nif(true) {\n // When the styles change, update the <style> tags\n if(!content.locals) {\n   module.hot.accept(/*! !!../node_modules/css-loader/dist/cjs.js??clonedRuleSet-12.use[1]!../node_modules/vue-loader/dist/stylePostLoader.js!../node_modules/postcss-loader/dist/cjs.js??clonedRuleSet-12.use[2]!../node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./QuestionnaireApp.vue?vue&type=style&index=0&id=2f351a77&lang=css */ \"./node_modules/css-loader/dist/cjs.js??clonedRuleSet-12.use[1]!./node_modules/vue-loader/dist/stylePostLoader.js!./node_modules/postcss-loader/dist/cjs.js??clonedRuleSet-12.use[2]!./node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./src/QuestionnaireApp.vue?vue&type=style&index=0&id=2f351a77&lang=css\", function() {\n     var newContent = __webpack_require__(/*! !!../node_modules/css-loader/dist/cjs.js??clonedRuleSet-12.use[1]!../node_modules/vue-loader/dist/stylePostLoader.js!../node_modules/postcss-loader/dist/cjs.js??clonedRuleSet-12.use[2]!../node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./QuestionnaireApp.vue?vue&type=style&index=0&id=2f351a77&lang=css */ \"./node_modules/css-loader/dist/cjs.js??clonedRuleSet-12.use[1]!./node_modules/vue-loader/dist/stylePostLoader.js!./node_modules/postcss-loader/dist/cjs.js??clonedRuleSet-12.use[2]!./node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./src/QuestionnaireApp.vue?vue&type=style&index=0&id=2f351a77&lang=css\");\n     if(newContent.__esModule) newContent = newContent.default;\n     if(typeof newContent === 'string') newContent = [[module.id, newContent, '']];\n     update(newContent);\n   });\n }\n // When the module is disposed, remove the <style> tags\n module.hot.dispose(function() { update(); });\n}//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi9ub2RlX21vZHVsZXMvdnVlLXN0eWxlLWxvYWRlci9pbmRleC5qcz8/Y2xvbmVkUnVsZVNldC0xMi51c2VbMF0hLi9ub2RlX21vZHVsZXMvY3NzLWxvYWRlci9kaXN0L2Nqcy5qcz8/Y2xvbmVkUnVsZVNldC0xMi51c2VbMV0hLi9ub2RlX21vZHVsZXMvdnVlLWxvYWRlci9kaXN0L3N0eWxlUG9zdExvYWRlci5qcyEuL25vZGVfbW9kdWxlcy9wb3N0Y3NzLWxvYWRlci9kaXN0L2Nqcy5qcz8/Y2xvbmVkUnVsZVNldC0xMi51c2VbMl0hLi9ub2RlX21vZHVsZXMvdnVlLWxvYWRlci9kaXN0L2luZGV4LmpzPz9ydWxlU2V0WzBdLnVzZVswXSEuL3NyYy9RdWVzdGlvbm5haXJlQXBwLnZ1ZT92dWUmdHlwZT1zdHlsZSZpbmRleD0wJmlkPTJmMzUxYTc3Jmxhbmc9Y3NzLmpzIiwibWFwcGluZ3MiOiJBQUFBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSIsInNvdXJjZXMiOlsid2VicGFjazovL3Z1ZV9mcm9udGVuZC8uL3NyYy9RdWVzdGlvbm5haXJlQXBwLnZ1ZT84ODZiIl0sInNvdXJjZXNDb250ZW50IjpbIi8vIHN0eWxlLWxvYWRlcjogQWRkcyBzb21lIGNzcyB0byB0aGUgRE9NIGJ5IGFkZGluZyBhIDxzdHlsZT4gdGFnXG5cbi8vIGxvYWQgdGhlIHN0eWxlc1xudmFyIGNvbnRlbnQgPSByZXF1aXJlKFwiISEuLi9ub2RlX21vZHVsZXMvY3NzLWxvYWRlci9kaXN0L2Nqcy5qcz8/Y2xvbmVkUnVsZVNldC0xMi51c2VbMV0hLi4vbm9kZV9tb2R1bGVzL3Z1ZS1sb2FkZXIvZGlzdC9zdHlsZVBvc3RMb2FkZXIuanMhLi4vbm9kZV9tb2R1bGVzL3Bvc3Rjc3MtbG9hZGVyL2Rpc3QvY2pzLmpzPz9jbG9uZWRSdWxlU2V0LTEyLnVzZVsyXSEuLi9ub2RlX21vZHVsZXMvdnVlLWxvYWRlci9kaXN0L2luZGV4LmpzPz9ydWxlU2V0WzBdLnVzZVswXSEuL1F1ZXN0aW9ubmFpcmVBcHAudnVlP3Z1ZSZ0eXBlPXN0eWxlJmluZGV4PTAmaWQ9MmYzNTFhNzcmbGFuZz1jc3NcIik7XG5pZihjb250ZW50Ll9fZXNNb2R1bGUpIGNvbnRlbnQgPSBjb250ZW50LmRlZmF1bHQ7XG5pZih0eXBlb2YgY29udGVudCA9PT0gJ3N0cmluZycpIGNvbnRlbnQgPSBbW21vZHVsZS5pZCwgY29udGVudCwgJyddXTtcbmlmKGNvbnRlbnQubG9jYWxzKSBtb2R1bGUuZXhwb3J0cyA9IGNvbnRlbnQubG9jYWxzO1xuLy8gYWRkIHRoZSBzdHlsZXMgdG8gdGhlIERPTVxudmFyIGFkZCA9IHJlcXVpcmUoXCIhLi4vbm9kZV9tb2R1bGVzL3Z1ZS1zdHlsZS1sb2FkZXIvbGliL2FkZFN0eWxlc0NsaWVudC5qc1wiKS5kZWZhdWx0XG52YXIgdXBkYXRlID0gYWRkKFwiYTAzNWJhZjhcIiwgY29udGVudCwgZmFsc2UsIHtcInNvdXJjZU1hcFwiOmZhbHNlLFwic2hhZG93TW9kZVwiOmZhbHNlfSk7XG4vLyBIb3QgTW9kdWxlIFJlcGxhY2VtZW50XG5pZihtb2R1bGUuaG90KSB7XG4gLy8gV2hlbiB0aGUgc3R5bGVzIGNoYW5nZSwgdXBkYXRlIHRoZSA8c3R5bGU+IHRhZ3NcbiBpZighY29udGVudC5sb2NhbHMpIHtcbiAgIG1vZHVsZS5ob3QuYWNjZXB0KFwiISEuLi9ub2RlX21vZHVsZXMvY3NzLWxvYWRlci9kaXN0L2Nqcy5qcz8/Y2xvbmVkUnVsZVNldC0xMi51c2VbMV0hLi4vbm9kZV9tb2R1bGVzL3Z1ZS1sb2FkZXIvZGlzdC9zdHlsZVBvc3RMb2FkZXIuanMhLi4vbm9kZV9tb2R1bGVzL3Bvc3Rjc3MtbG9hZGVyL2Rpc3QvY2pzLmpzPz9jbG9uZWRSdWxlU2V0LTEyLnVzZVsyXSEuLi9ub2RlX21vZHVsZXMvdnVlLWxvYWRlci9kaXN0L2luZGV4LmpzPz9ydWxlU2V0WzBdLnVzZVswXSEuL1F1ZXN0aW9ubmFpcmVBcHAudnVlP3Z1ZSZ0eXBlPXN0eWxlJmluZGV4PTAmaWQ9MmYzNTFhNzcmbGFuZz1jc3NcIiwgZnVuY3Rpb24oKSB7XG4gICAgIHZhciBuZXdDb250ZW50ID0gcmVxdWlyZShcIiEhLi4vbm9kZV9tb2R1bGVzL2Nzcy1sb2FkZXIvZGlzdC9janMuanM/P2Nsb25lZFJ1bGVTZXQtMTIudXNlWzFdIS4uL25vZGVfbW9kdWxlcy92dWUtbG9hZGVyL2Rpc3Qvc3R5bGVQb3N0TG9hZGVyLmpzIS4uL25vZGVfbW9kdWxlcy9wb3N0Y3NzLWxvYWRlci9kaXN0L2Nqcy5qcz8/Y2xvbmVkUnVsZVNldC0xMi51c2VbMl0hLi4vbm9kZV9tb2R1bGVzL3Z1ZS1sb2FkZXIvZGlzdC9pbmRleC5qcz8/cnVsZVNldFswXS51c2VbMF0hLi9RdWVzdGlvbm5haXJlQXBwLnZ1ZT92dWUmdHlwZT1zdHlsZSZpbmRleD0wJmlkPTJmMzUxYTc3Jmxhbmc9Y3NzXCIpO1xuICAgICBpZihuZXdDb250ZW50Ll9fZXNNb2R1bGUpIG5ld0NvbnRlbnQgPSBuZXdDb250ZW50LmRlZmF1bHQ7XG4gICAgIGlmKHR5cGVvZiBuZXdDb250ZW50ID09PSAnc3RyaW5nJykgbmV3Q29udGVudCA9IFtbbW9kdWxlLmlkLCBuZXdDb250ZW50LCAnJ11dO1xuICAgICB1cGRhdGUobmV3Q29udGVudCk7XG4gICB9KTtcbiB9XG4gLy8gV2hlbiB0aGUgbW9kdWxlIGlzIGRpc3Bvc2VkLCByZW1vdmUgdGhlIDxzdHlsZT4gdGFnc1xuIG1vZHVsZS5ob3QuZGlzcG9zZShmdW5jdGlvbigpIHsgdXBkYXRlKCk7IH0pO1xufSJdLCJuYW1lcyI6W10sInNvdXJjZVJvb3QiOiIifQ==\n//# sourceURL=webpack-internal:///./node_modules/vue-style-loader/index.js??clonedRuleSet-12.use[0]!./node_modules/css-loader/dist/cjs.js??clonedRuleSet-12.use[1]!./node_modules/vue-loader/dist/stylePostLoader.js!./node_modules/postcss-loader/dist/cjs.js??clonedRuleSet-12.use[2]!./node_modules/vue-loader/dist/index.js??ruleSet[0].use[0]!./src/QuestionnaireApp.vue?vue&type=style&index=0&id=2f351a77&lang=css\n");

/***/ })

/******/ 	});
/************************************************************************/
/******/ 	// The module cache
/******/ 	var __webpack_module_cache__ = {};
/******/ 	
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/ 		// Check if module is in cache
/******/ 		var cachedModule = __webpack_module_cache__[moduleId];
/******/ 		if (cachedModule !== undefined) {
/******/ 			if (cachedModule.error !== undefined) throw cachedModule.error;
/******/ 			return cachedModule.exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = __webpack_module_cache__[moduleId] = {
/******/ 			id: moduleId,
/******/ 			// no module.loaded needed
/******/ 			exports: {}
/******/ 		};
/******/ 	
/******/ 		// Execute the module function
/******/ 		try {
/******/ 			var execOptions = { id: moduleId, module: module, factory: __webpack_modules__[moduleId], require: __webpack_require__ };
/******/ 			__webpack_require__.i.forEach(function(handler) { handler(execOptions); });
/******/ 			module = execOptions.module;
/******/ 			execOptions.factory.call(module.exports, module, module.exports, execOptions.require);
/******/ 		} catch(e) {
/******/ 			module.error = e;
/******/ 			throw e;
/******/ 		}
/******/ 	
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/ 	
/******/ 	// expose the modules object (__webpack_modules__)
/******/ 	__webpack_require__.m = __webpack_modules__;
/******/ 	
/******/ 	// expose the module cache
/******/ 	__webpack_require__.c = __webpack_module_cache__;
/******/ 	
/******/ 	// expose the module execution interceptor
/******/ 	__webpack_require__.i = [];
/******/ 	
/************************************************************************/
/******/ 	/* webpack/runtime/chunk loaded */
/******/ 	!function() {
/******/ 		var deferred = [];
/******/ 		__webpack_require__.O = function(result, chunkIds, fn, priority) {
/******/ 			if(chunkIds) {
/******/ 				priority = priority || 0;
/******/ 				for(var i = deferred.length; i > 0 && deferred[i - 1][2] > priority; i--) deferred[i] = deferred[i - 1];
/******/ 				deferred[i] = [chunkIds, fn, priority];
/******/ 				return;
/******/ 			}
/******/ 			var notFulfilled = Infinity;
/******/ 			for (var i = 0; i < deferred.length; i++) {
/******/ 				var chunkIds = deferred[i][0];
/******/ 				var fn = deferred[i][1];
/******/ 				var priority = deferred[i][2];
/******/ 				var fulfilled = true;
/******/ 				for (var j = 0; j < chunkIds.length; j++) {
/******/ 					if ((priority & 1 === 0 || notFulfilled >= priority) && Object.keys(__webpack_require__.O).every(function(key) { return __webpack_require__.O[key](chunkIds[j]); })) {
/******/ 						chunkIds.splice(j--, 1);
/******/ 					} else {
/******/ 						fulfilled = false;
/******/ 						if(priority < notFulfilled) notFulfilled = priority;
/******/ 					}
/******/ 				}
/******/ 				if(fulfilled) {
/******/ 					deferred.splice(i--, 1)
/******/ 					var r = fn();
/******/ 					if (r !== undefined) result = r;
/******/ 				}
/******/ 			}
/******/ 			return result;
/******/ 		};
/******/ 	}();
/******/ 	
/******/ 	/* webpack/runtime/compat get default export */
/******/ 	!function() {
/******/ 		// getDefaultExport function for compatibility with non-harmony modules
/******/ 		__webpack_require__.n = function(module) {
/******/ 			var getter = module && module.__esModule ?
/******/ 				function() { return module['default']; } :
/******/ 				function() { return module; };
/******/ 			__webpack_require__.d(getter, { a: getter });
/******/ 			return getter;
/******/ 		};
/******/ 	}();
/******/ 	
/******/ 	/* webpack/runtime/define property getters */
/******/ 	!function() {
/******/ 		// define getter functions for harmony exports
/******/ 		__webpack_require__.d = function(exports, definition) {
/******/ 			for(var key in definition) {
/******/ 				if(__webpack_require__.o(definition, key) && !__webpack_require__.o(exports, key)) {
/******/ 					Object.defineProperty(exports, key, { enumerable: true, get: definition[key] });
/******/ 				}
/******/ 			}
/******/ 		};
/******/ 	}();
/******/ 	
/******/ 	/* webpack/runtime/get javascript update chunk filename */
/******/ 	!function() {
/******/ 		// This function allow to reference all chunks
/******/ 		__webpack_require__.hu = function(chunkId) {
/******/ 			// return url for filenames based on template
/******/ 			return "" + chunkId + "." + __webpack_require__.h() + ".hot-update.js";
/******/ 		};
/******/ 	}();
/******/ 	
/******/ 	/* webpack/runtime/get update manifest filename */
/******/ 	!function() {
/******/ 		__webpack_require__.hmrF = function() { return "vue_questionnaire." + __webpack_require__.h() + ".hot-update.json"; };
/******/ 	}();
/******/ 	
/******/ 	/* webpack/runtime/getFullHash */
/******/ 	!function() {
/******/ 		__webpack_require__.h = function() { return "b1c9c38606f1b824"; }
/******/ 	}();
/******/ 	
/******/ 	/* webpack/runtime/global */
/******/ 	!function() {
/******/ 		__webpack_require__.g = (function() {
/******/ 			if (typeof globalThis === 'object') return globalThis;
/******/ 			try {
/******/ 				return this || new Function('return this')();
/******/ 			} catch (e) {
/******/ 				if (typeof window === 'object') return window;
/******/ 			}
/******/ 		})();
/******/ 	}();
/******/ 	
/******/ 	/* webpack/runtime/hasOwnProperty shorthand */
/******/ 	!function() {
/******/ 		__webpack_require__.o = function(obj, prop) { return Object.prototype.hasOwnProperty.call(obj, prop); }
/******/ 	}();
/******/ 	
/******/ 	/* webpack/runtime/load script */
/******/ 	!function() {
/******/ 		var inProgress = {};
/******/ 		var dataWebpackPrefix = "vue_frontend:";
/******/ 		// loadScript function to load a script via script tag
/******/ 		__webpack_require__.l = function(url, done, key, chunkId) {
/******/ 			if(inProgress[url]) { inProgress[url].push(done); return; }
/******/ 			var script, needAttach;
/******/ 			if(key !== undefined) {
/******/ 				var scripts = document.getElementsByTagName("script");
/******/ 				for(var i = 0; i < scripts.length; i++) {
/******/ 					var s = scripts[i];
/******/ 					if(s.getAttribute("src") == url || s.getAttribute("data-webpack") == dataWebpackPrefix + key) { script = s; break; }
/******/ 				}
/******/ 			}
/******/ 			if(!script) {
/******/ 				needAttach = true;
/******/ 				script = document.createElement('script');
/******/ 		
/******/ 				script.charset = 'utf-8';
/******/ 				script.timeout = 120;
/******/ 				if (__webpack_require__.nc) {
/******/ 					script.setAttribute("nonce", __webpack_require__.nc);
/******/ 				}
/******/ 				script.setAttribute("data-webpack", dataWebpackPrefix + key);
/******/ 				script.src = url;
/******/ 			}
/******/ 			inProgress[url] = [done];
/******/ 			var onScriptComplete = function(prev, event) {
/******/ 				// avoid mem leaks in IE.
/******/ 				script.onerror = script.onload = null;
/******/ 				clearTimeout(timeout);
/******/ 				var doneFns = inProgress[url];
/******/ 				delete inProgress[url];
/******/ 				script.parentNode && script.parentNode.removeChild(script);
/******/ 				doneFns && doneFns.forEach(function(fn) { return fn(event); });
/******/ 				if(prev) return prev(event);
/******/ 			}
/******/ 			;
/******/ 			var timeout = setTimeout(onScriptComplete.bind(null, undefined, { type: 'timeout', target: script }), 120000);
/******/ 			script.onerror = onScriptComplete.bind(null, script.onerror);
/******/ 			script.onload = onScriptComplete.bind(null, script.onload);
/******/ 			needAttach && document.head.appendChild(script);
/******/ 		};
/******/ 	}();
/******/ 	
/******/ 	/* webpack/runtime/make namespace object */
/******/ 	!function() {
/******/ 		// define __esModule on exports
/******/ 		__webpack_require__.r = function(exports) {
/******/ 			if(typeof Symbol !== 'undefined' && Symbol.toStringTag) {
/******/ 				Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });
/******/ 			}
/******/ 			Object.defineProperty(exports, '__esModule', { value: true });
/******/ 		};
/******/ 	}();
/******/ 	
/******/ 	/* webpack/runtime/hot module replacement */
/******/ 	!function() {
/******/ 		var currentModuleData = {};
/******/ 		var installedModules = __webpack_require__.c;
/******/ 		
/******/ 		// module and require creation
/******/ 		var currentChildModule;
/******/ 		var currentParents = [];
/******/ 		
/******/ 		// status
/******/ 		var registeredStatusHandlers = [];
/******/ 		var currentStatus = "idle";
/******/ 		
/******/ 		// while downloading
/******/ 		var blockingPromises = 0;
/******/ 		var blockingPromisesWaiting = [];
/******/ 		
/******/ 		// The update info
/******/ 		var currentUpdateApplyHandlers;
/******/ 		var queuedInvalidatedModules;
/******/ 		
/******/ 		// eslint-disable-next-line no-unused-vars
/******/ 		__webpack_require__.hmrD = currentModuleData;
/******/ 		
/******/ 		__webpack_require__.i.push(function (options) {
/******/ 			var module = options.module;
/******/ 			var require = createRequire(options.require, options.id);
/******/ 			module.hot = createModuleHotObject(options.id, module);
/******/ 			module.parents = currentParents;
/******/ 			module.children = [];
/******/ 			currentParents = [];
/******/ 			options.require = require;
/******/ 		});
/******/ 		
/******/ 		__webpack_require__.hmrC = {};
/******/ 		__webpack_require__.hmrI = {};
/******/ 		
/******/ 		function createRequire(require, moduleId) {
/******/ 			var me = installedModules[moduleId];
/******/ 			if (!me) return require;
/******/ 			var fn = function (request) {
/******/ 				if (me.hot.active) {
/******/ 					if (installedModules[request]) {
/******/ 						var parents = installedModules[request].parents;
/******/ 						if (parents.indexOf(moduleId) === -1) {
/******/ 							parents.push(moduleId);
/******/ 						}
/******/ 					} else {
/******/ 						currentParents = [moduleId];
/******/ 						currentChildModule = request;
/******/ 					}
/******/ 					if (me.children.indexOf(request) === -1) {
/******/ 						me.children.push(request);
/******/ 					}
/******/ 				} else {
/******/ 					console.warn(
/******/ 						"[HMR] unexpected require(" +
/******/ 							request +
/******/ 							") from disposed module " +
/******/ 							moduleId
/******/ 					);
/******/ 					currentParents = [];
/******/ 				}
/******/ 				return require(request);
/******/ 			};
/******/ 			var createPropertyDescriptor = function (name) {
/******/ 				return {
/******/ 					configurable: true,
/******/ 					enumerable: true,
/******/ 					get: function () {
/******/ 						return require[name];
/******/ 					},
/******/ 					set: function (value) {
/******/ 						require[name] = value;
/******/ 					}
/******/ 				};
/******/ 			};
/******/ 			for (var name in require) {
/******/ 				if (Object.prototype.hasOwnProperty.call(require, name) && name !== "e") {
/******/ 					Object.defineProperty(fn, name, createPropertyDescriptor(name));
/******/ 				}
/******/ 			}
/******/ 			fn.e = function (chunkId) {
/******/ 				return trackBlockingPromise(require.e(chunkId));
/******/ 			};
/******/ 			return fn;
/******/ 		}
/******/ 		
/******/ 		function createModuleHotObject(moduleId, me) {
/******/ 			var _main = currentChildModule !== moduleId;
/******/ 			var hot = {
/******/ 				// private stuff
/******/ 				_acceptedDependencies: {},
/******/ 				_acceptedErrorHandlers: {},
/******/ 				_declinedDependencies: {},
/******/ 				_selfAccepted: false,
/******/ 				_selfDeclined: false,
/******/ 				_selfInvalidated: false,
/******/ 				_disposeHandlers: [],
/******/ 				_main: _main,
/******/ 				_requireSelf: function () {
/******/ 					currentParents = me.parents.slice();
/******/ 					currentChildModule = _main ? undefined : moduleId;
/******/ 					__webpack_require__(moduleId);
/******/ 				},
/******/ 		
/******/ 				// Module API
/******/ 				active: true,
/******/ 				accept: function (dep, callback, errorHandler) {
/******/ 					if (dep === undefined) hot._selfAccepted = true;
/******/ 					else if (typeof dep === "function") hot._selfAccepted = dep;
/******/ 					else if (typeof dep === "object" && dep !== null) {
/******/ 						for (var i = 0; i < dep.length; i++) {
/******/ 							hot._acceptedDependencies[dep[i]] = callback || function () {};
/******/ 							hot._acceptedErrorHandlers[dep[i]] = errorHandler;
/******/ 						}
/******/ 					} else {
/******/ 						hot._acceptedDependencies[dep] = callback || function () {};
/******/ 						hot._acceptedErrorHandlers[dep] = errorHandler;
/******/ 					}
/******/ 				},
/******/ 				decline: function (dep) {
/******/ 					if (dep === undefined) hot._selfDeclined = true;
/******/ 					else if (typeof dep === "object" && dep !== null)
/******/ 						for (var i = 0; i < dep.length; i++)
/******/ 							hot._declinedDependencies[dep[i]] = true;
/******/ 					else hot._declinedDependencies[dep] = true;
/******/ 				},
/******/ 				dispose: function (callback) {
/******/ 					hot._disposeHandlers.push(callback);
/******/ 				},
/******/ 				addDisposeHandler: function (callback) {
/******/ 					hot._disposeHandlers.push(callback);
/******/ 				},
/******/ 				removeDisposeHandler: function (callback) {
/******/ 					var idx = hot._disposeHandlers.indexOf(callback);
/******/ 					if (idx >= 0) hot._disposeHandlers.splice(idx, 1);
/******/ 				},
/******/ 				invalidate: function () {
/******/ 					this._selfInvalidated = true;
/******/ 					switch (currentStatus) {
/******/ 						case "idle":
/******/ 							currentUpdateApplyHandlers = [];
/******/ 							Object.keys(__webpack_require__.hmrI).forEach(function (key) {
/******/ 								__webpack_require__.hmrI[key](
/******/ 									moduleId,
/******/ 									currentUpdateApplyHandlers
/******/ 								);
/******/ 							});
/******/ 							setStatus("ready");
/******/ 							break;
/******/ 						case "ready":
/******/ 							Object.keys(__webpack_require__.hmrI).forEach(function (key) {
/******/ 								__webpack_require__.hmrI[key](
/******/ 									moduleId,
/******/ 									currentUpdateApplyHandlers
/******/ 								);
/******/ 							});
/******/ 							break;
/******/ 						case "prepare":
/******/ 						case "check":
/******/ 						case "dispose":
/******/ 						case "apply":
/******/ 							(queuedInvalidatedModules = queuedInvalidatedModules || []).push(
/******/ 								moduleId
/******/ 							);
/******/ 							break;
/******/ 						default:
/******/ 							// ignore requests in error states
/******/ 							break;
/******/ 					}
/******/ 				},
/******/ 		
/******/ 				// Management API
/******/ 				check: hotCheck,
/******/ 				apply: hotApply,
/******/ 				status: function (l) {
/******/ 					if (!l) return currentStatus;
/******/ 					registeredStatusHandlers.push(l);
/******/ 				},
/******/ 				addStatusHandler: function (l) {
/******/ 					registeredStatusHandlers.push(l);
/******/ 				},
/******/ 				removeStatusHandler: function (l) {
/******/ 					var idx = registeredStatusHandlers.indexOf(l);
/******/ 					if (idx >= 0) registeredStatusHandlers.splice(idx, 1);
/******/ 				},
/******/ 		
/******/ 				//inherit from previous dispose call
/******/ 				data: currentModuleData[moduleId]
/******/ 			};
/******/ 			currentChildModule = undefined;
/******/ 			return hot;
/******/ 		}
/******/ 		
/******/ 		function setStatus(newStatus) {
/******/ 			currentStatus = newStatus;
/******/ 			var results = [];
/******/ 		
/******/ 			for (var i = 0; i < registeredStatusHandlers.length; i++)
/******/ 				results[i] = registeredStatusHandlers[i].call(null, newStatus);
/******/ 		
/******/ 			return Promise.all(results);
/******/ 		}
/******/ 		
/******/ 		function unblock() {
/******/ 			if (--blockingPromises === 0) {
/******/ 				setStatus("ready").then(function () {
/******/ 					if (blockingPromises === 0) {
/******/ 						var list = blockingPromisesWaiting;
/******/ 						blockingPromisesWaiting = [];
/******/ 						for (var i = 0; i < list.length; i++) {
/******/ 							list[i]();
/******/ 						}
/******/ 					}
/******/ 				});
/******/ 			}
/******/ 		}
/******/ 		
/******/ 		function trackBlockingPromise(promise) {
/******/ 			switch (currentStatus) {
/******/ 				case "ready":
/******/ 					setStatus("prepare");
/******/ 				/* fallthrough */
/******/ 				case "prepare":
/******/ 					blockingPromises++;
/******/ 					promise.then(unblock, unblock);
/******/ 					return promise;
/******/ 				default:
/******/ 					return promise;
/******/ 			}
/******/ 		}
/******/ 		
/******/ 		function waitForBlockingPromises(fn) {
/******/ 			if (blockingPromises === 0) return fn();
/******/ 			return new Promise(function (resolve) {
/******/ 				blockingPromisesWaiting.push(function () {
/******/ 					resolve(fn());
/******/ 				});
/******/ 			});
/******/ 		}
/******/ 		
/******/ 		function hotCheck(applyOnUpdate) {
/******/ 			if (currentStatus !== "idle") {
/******/ 				throw new Error("check() is only allowed in idle status");
/******/ 			}
/******/ 			return setStatus("check")
/******/ 				.then(__webpack_require__.hmrM)
/******/ 				.then(function (update) {
/******/ 					if (!update) {
/******/ 						return setStatus(applyInvalidatedModules() ? "ready" : "idle").then(
/******/ 							function () {
/******/ 								return null;
/******/ 							}
/******/ 						);
/******/ 					}
/******/ 		
/******/ 					return setStatus("prepare").then(function () {
/******/ 						var updatedModules = [];
/******/ 						currentUpdateApplyHandlers = [];
/******/ 		
/******/ 						return Promise.all(
/******/ 							Object.keys(__webpack_require__.hmrC).reduce(function (
/******/ 								promises,
/******/ 								key
/******/ 							) {
/******/ 								__webpack_require__.hmrC[key](
/******/ 									update.c,
/******/ 									update.r,
/******/ 									update.m,
/******/ 									promises,
/******/ 									currentUpdateApplyHandlers,
/******/ 									updatedModules
/******/ 								);
/******/ 								return promises;
/******/ 							},
/******/ 							[])
/******/ 						).then(function () {
/******/ 							return waitForBlockingPromises(function () {
/******/ 								if (applyOnUpdate) {
/******/ 									return internalApply(applyOnUpdate);
/******/ 								} else {
/******/ 									return setStatus("ready").then(function () {
/******/ 										return updatedModules;
/******/ 									});
/******/ 								}
/******/ 							});
/******/ 						});
/******/ 					});
/******/ 				});
/******/ 		}
/******/ 		
/******/ 		function hotApply(options) {
/******/ 			if (currentStatus !== "ready") {
/******/ 				return Promise.resolve().then(function () {
/******/ 					throw new Error(
/******/ 						"apply() is only allowed in ready status (state: " +
/******/ 							currentStatus +
/******/ 							")"
/******/ 					);
/******/ 				});
/******/ 			}
/******/ 			return internalApply(options);
/******/ 		}
/******/ 		
/******/ 		function internalApply(options) {
/******/ 			options = options || {};
/******/ 		
/******/ 			applyInvalidatedModules();
/******/ 		
/******/ 			var results = currentUpdateApplyHandlers.map(function (handler) {
/******/ 				return handler(options);
/******/ 			});
/******/ 			currentUpdateApplyHandlers = undefined;
/******/ 		
/******/ 			var errors = results
/******/ 				.map(function (r) {
/******/ 					return r.error;
/******/ 				})
/******/ 				.filter(Boolean);
/******/ 		
/******/ 			if (errors.length > 0) {
/******/ 				return setStatus("abort").then(function () {
/******/ 					throw errors[0];
/******/ 				});
/******/ 			}
/******/ 		
/******/ 			// Now in "dispose" phase
/******/ 			var disposePromise = setStatus("dispose");
/******/ 		
/******/ 			results.forEach(function (result) {
/******/ 				if (result.dispose) result.dispose();
/******/ 			});
/******/ 		
/******/ 			// Now in "apply" phase
/******/ 			var applyPromise = setStatus("apply");
/******/ 		
/******/ 			var error;
/******/ 			var reportError = function (err) {
/******/ 				if (!error) error = err;
/******/ 			};
/******/ 		
/******/ 			var outdatedModules = [];
/******/ 			results.forEach(function (result) {
/******/ 				if (result.apply) {
/******/ 					var modules = result.apply(reportError);
/******/ 					if (modules) {
/******/ 						for (var i = 0; i < modules.length; i++) {
/******/ 							outdatedModules.push(modules[i]);
/******/ 						}
/******/ 					}
/******/ 				}
/******/ 			});
/******/ 		
/******/ 			return Promise.all([disposePromise, applyPromise]).then(function () {
/******/ 				// handle errors in accept handlers and self accepted module load
/******/ 				if (error) {
/******/ 					return setStatus("fail").then(function () {
/******/ 						throw error;
/******/ 					});
/******/ 				}
/******/ 		
/******/ 				if (queuedInvalidatedModules) {
/******/ 					return internalApply(options).then(function (list) {
/******/ 						outdatedModules.forEach(function (moduleId) {
/******/ 							if (list.indexOf(moduleId) < 0) list.push(moduleId);
/******/ 						});
/******/ 						return list;
/******/ 					});
/******/ 				}
/******/ 		
/******/ 				return setStatus("idle").then(function () {
/******/ 					return outdatedModules;
/******/ 				});
/******/ 			});
/******/ 		}
/******/ 		
/******/ 		function applyInvalidatedModules() {
/******/ 			if (queuedInvalidatedModules) {
/******/ 				if (!currentUpdateApplyHandlers) currentUpdateApplyHandlers = [];
/******/ 				Object.keys(__webpack_require__.hmrI).forEach(function (key) {
/******/ 					queuedInvalidatedModules.forEach(function (moduleId) {
/******/ 						__webpack_require__.hmrI[key](
/******/ 							moduleId,
/******/ 							currentUpdateApplyHandlers
/******/ 						);
/******/ 					});
/******/ 				});
/******/ 				queuedInvalidatedModules = undefined;
/******/ 				return true;
/******/ 			}
/******/ 		}
/******/ 	}();
/******/ 	
/******/ 	/* webpack/runtime/publicPath */
/******/ 	!function() {
/******/ 		__webpack_require__.p = "/static/ddm/vue/";
/******/ 	}();
/******/ 	
/******/ 	/* webpack/runtime/jsonp chunk loading */
/******/ 	!function() {
/******/ 		// no baseURI
/******/ 		
/******/ 		// object to store loaded and loading chunks
/******/ 		// undefined = chunk not loaded, null = chunk preloaded/prefetched
/******/ 		// [resolve, reject, Promise] = chunk loading, 0 = chunk loaded
/******/ 		var installedChunks = __webpack_require__.hmrS_jsonp = __webpack_require__.hmrS_jsonp || {
/******/ 			"vue_questionnaire": 0
/******/ 		};
/******/ 		
/******/ 		// no chunk on demand loading
/******/ 		
/******/ 		// no prefetching
/******/ 		
/******/ 		// no preloaded
/******/ 		
/******/ 		var currentUpdatedModulesList;
/******/ 		var waitingUpdateResolves = {};
/******/ 		function loadUpdateChunk(chunkId, updatedModulesList) {
/******/ 			currentUpdatedModulesList = updatedModulesList;
/******/ 			return new Promise(function(resolve, reject) {
/******/ 				waitingUpdateResolves[chunkId] = resolve;
/******/ 				// start update chunk loading
/******/ 				var url = __webpack_require__.p + __webpack_require__.hu(chunkId);
/******/ 				// create error before stack unwound to get useful stacktrace later
/******/ 				var error = new Error();
/******/ 				var loadingEnded = function(event) {
/******/ 					if(waitingUpdateResolves[chunkId]) {
/******/ 						waitingUpdateResolves[chunkId] = undefined
/******/ 						var errorType = event && (event.type === 'load' ? 'missing' : event.type);
/******/ 						var realSrc = event && event.target && event.target.src;
/******/ 						error.message = 'Loading hot update chunk ' + chunkId + ' failed.\n(' + errorType + ': ' + realSrc + ')';
/******/ 						error.name = 'ChunkLoadError';
/******/ 						error.type = errorType;
/******/ 						error.request = realSrc;
/******/ 						reject(error);
/******/ 					}
/******/ 				};
/******/ 				__webpack_require__.l(url, loadingEnded);
/******/ 			});
/******/ 		}
/******/ 		
/******/ 		(typeof self !== 'undefined' ? self : this)["webpackHotUpdatevue_frontend"] = function(chunkId, moreModules, runtime) {
/******/ 			for(var moduleId in moreModules) {
/******/ 				if(__webpack_require__.o(moreModules, moduleId)) {
/******/ 					currentUpdate[moduleId] = moreModules[moduleId];
/******/ 					if(currentUpdatedModulesList) currentUpdatedModulesList.push(moduleId);
/******/ 				}
/******/ 			}
/******/ 			if(runtime) currentUpdateRuntime.push(runtime);
/******/ 			if(waitingUpdateResolves[chunkId]) {
/******/ 				waitingUpdateResolves[chunkId]();
/******/ 				waitingUpdateResolves[chunkId] = undefined;
/******/ 			}
/******/ 		};
/******/ 		
/******/ 		var currentUpdateChunks;
/******/ 		var currentUpdate;
/******/ 		var currentUpdateRemovedChunks;
/******/ 		var currentUpdateRuntime;
/******/ 		function applyHandler(options) {
/******/ 			if (__webpack_require__.f) delete __webpack_require__.f.jsonpHmr;
/******/ 			currentUpdateChunks = undefined;
/******/ 			function getAffectedModuleEffects(updateModuleId) {
/******/ 				var outdatedModules = [updateModuleId];
/******/ 				var outdatedDependencies = {};
/******/ 		
/******/ 				var queue = outdatedModules.map(function (id) {
/******/ 					return {
/******/ 						chain: [id],
/******/ 						id: id
/******/ 					};
/******/ 				});
/******/ 				while (queue.length > 0) {
/******/ 					var queueItem = queue.pop();
/******/ 					var moduleId = queueItem.id;
/******/ 					var chain = queueItem.chain;
/******/ 					var module = __webpack_require__.c[moduleId];
/******/ 					if (
/******/ 						!module ||
/******/ 						(module.hot._selfAccepted && !module.hot._selfInvalidated)
/******/ 					)
/******/ 						continue;
/******/ 					if (module.hot._selfDeclined) {
/******/ 						return {
/******/ 							type: "self-declined",
/******/ 							chain: chain,
/******/ 							moduleId: moduleId
/******/ 						};
/******/ 					}
/******/ 					if (module.hot._main) {
/******/ 						return {
/******/ 							type: "unaccepted",
/******/ 							chain: chain,
/******/ 							moduleId: moduleId
/******/ 						};
/******/ 					}
/******/ 					for (var i = 0; i < module.parents.length; i++) {
/******/ 						var parentId = module.parents[i];
/******/ 						var parent = __webpack_require__.c[parentId];
/******/ 						if (!parent) continue;
/******/ 						if (parent.hot._declinedDependencies[moduleId]) {
/******/ 							return {
/******/ 								type: "declined",
/******/ 								chain: chain.concat([parentId]),
/******/ 								moduleId: moduleId,
/******/ 								parentId: parentId
/******/ 							};
/******/ 						}
/******/ 						if (outdatedModules.indexOf(parentId) !== -1) continue;
/******/ 						if (parent.hot._acceptedDependencies[moduleId]) {
/******/ 							if (!outdatedDependencies[parentId])
/******/ 								outdatedDependencies[parentId] = [];
/******/ 							addAllToSet(outdatedDependencies[parentId], [moduleId]);
/******/ 							continue;
/******/ 						}
/******/ 						delete outdatedDependencies[parentId];
/******/ 						outdatedModules.push(parentId);
/******/ 						queue.push({
/******/ 							chain: chain.concat([parentId]),
/******/ 							id: parentId
/******/ 						});
/******/ 					}
/******/ 				}
/******/ 		
/******/ 				return {
/******/ 					type: "accepted",
/******/ 					moduleId: updateModuleId,
/******/ 					outdatedModules: outdatedModules,
/******/ 					outdatedDependencies: outdatedDependencies
/******/ 				};
/******/ 			}
/******/ 		
/******/ 			function addAllToSet(a, b) {
/******/ 				for (var i = 0; i < b.length; i++) {
/******/ 					var item = b[i];
/******/ 					if (a.indexOf(item) === -1) a.push(item);
/******/ 				}
/******/ 			}
/******/ 		
/******/ 			// at begin all updates modules are outdated
/******/ 			// the "outdated" status can propagate to parents if they don't accept the children
/******/ 			var outdatedDependencies = {};
/******/ 			var outdatedModules = [];
/******/ 			var appliedUpdate = {};
/******/ 		
/******/ 			var warnUnexpectedRequire = function warnUnexpectedRequire(module) {
/******/ 				console.warn(
/******/ 					"[HMR] unexpected require(" + module.id + ") to disposed module"
/******/ 				);
/******/ 			};
/******/ 		
/******/ 			for (var moduleId in currentUpdate) {
/******/ 				if (__webpack_require__.o(currentUpdate, moduleId)) {
/******/ 					var newModuleFactory = currentUpdate[moduleId];
/******/ 					/** @type {TODO} */
/******/ 					var result;
/******/ 					if (newModuleFactory) {
/******/ 						result = getAffectedModuleEffects(moduleId);
/******/ 					} else {
/******/ 						result = {
/******/ 							type: "disposed",
/******/ 							moduleId: moduleId
/******/ 						};
/******/ 					}
/******/ 					/** @type {Error|false} */
/******/ 					var abortError = false;
/******/ 					var doApply = false;
/******/ 					var doDispose = false;
/******/ 					var chainInfo = "";
/******/ 					if (result.chain) {
/******/ 						chainInfo = "\nUpdate propagation: " + result.chain.join(" -> ");
/******/ 					}
/******/ 					switch (result.type) {
/******/ 						case "self-declined":
/******/ 							if (options.onDeclined) options.onDeclined(result);
/******/ 							if (!options.ignoreDeclined)
/******/ 								abortError = new Error(
/******/ 									"Aborted because of self decline: " +
/******/ 										result.moduleId +
/******/ 										chainInfo
/******/ 								);
/******/ 							break;
/******/ 						case "declined":
/******/ 							if (options.onDeclined) options.onDeclined(result);
/******/ 							if (!options.ignoreDeclined)
/******/ 								abortError = new Error(
/******/ 									"Aborted because of declined dependency: " +
/******/ 										result.moduleId +
/******/ 										" in " +
/******/ 										result.parentId +
/******/ 										chainInfo
/******/ 								);
/******/ 							break;
/******/ 						case "unaccepted":
/******/ 							if (options.onUnaccepted) options.onUnaccepted(result);
/******/ 							if (!options.ignoreUnaccepted)
/******/ 								abortError = new Error(
/******/ 									"Aborted because " + moduleId + " is not accepted" + chainInfo
/******/ 								);
/******/ 							break;
/******/ 						case "accepted":
/******/ 							if (options.onAccepted) options.onAccepted(result);
/******/ 							doApply = true;
/******/ 							break;
/******/ 						case "disposed":
/******/ 							if (options.onDisposed) options.onDisposed(result);
/******/ 							doDispose = true;
/******/ 							break;
/******/ 						default:
/******/ 							throw new Error("Unexception type " + result.type);
/******/ 					}
/******/ 					if (abortError) {
/******/ 						return {
/******/ 							error: abortError
/******/ 						};
/******/ 					}
/******/ 					if (doApply) {
/******/ 						appliedUpdate[moduleId] = newModuleFactory;
/******/ 						addAllToSet(outdatedModules, result.outdatedModules);
/******/ 						for (moduleId in result.outdatedDependencies) {
/******/ 							if (__webpack_require__.o(result.outdatedDependencies, moduleId)) {
/******/ 								if (!outdatedDependencies[moduleId])
/******/ 									outdatedDependencies[moduleId] = [];
/******/ 								addAllToSet(
/******/ 									outdatedDependencies[moduleId],
/******/ 									result.outdatedDependencies[moduleId]
/******/ 								);
/******/ 							}
/******/ 						}
/******/ 					}
/******/ 					if (doDispose) {
/******/ 						addAllToSet(outdatedModules, [result.moduleId]);
/******/ 						appliedUpdate[moduleId] = warnUnexpectedRequire;
/******/ 					}
/******/ 				}
/******/ 			}
/******/ 			currentUpdate = undefined;
/******/ 		
/******/ 			// Store self accepted outdated modules to require them later by the module system
/******/ 			var outdatedSelfAcceptedModules = [];
/******/ 			for (var j = 0; j < outdatedModules.length; j++) {
/******/ 				var outdatedModuleId = outdatedModules[j];
/******/ 				var module = __webpack_require__.c[outdatedModuleId];
/******/ 				if (
/******/ 					module &&
/******/ 					(module.hot._selfAccepted || module.hot._main) &&
/******/ 					// removed self-accepted modules should not be required
/******/ 					appliedUpdate[outdatedModuleId] !== warnUnexpectedRequire &&
/******/ 					// when called invalidate self-accepting is not possible
/******/ 					!module.hot._selfInvalidated
/******/ 				) {
/******/ 					outdatedSelfAcceptedModules.push({
/******/ 						module: outdatedModuleId,
/******/ 						require: module.hot._requireSelf,
/******/ 						errorHandler: module.hot._selfAccepted
/******/ 					});
/******/ 				}
/******/ 			}
/******/ 		
/******/ 			var moduleOutdatedDependencies;
/******/ 		
/******/ 			return {
/******/ 				dispose: function () {
/******/ 					currentUpdateRemovedChunks.forEach(function (chunkId) {
/******/ 						delete installedChunks[chunkId];
/******/ 					});
/******/ 					currentUpdateRemovedChunks = undefined;
/******/ 		
/******/ 					var idx;
/******/ 					var queue = outdatedModules.slice();
/******/ 					while (queue.length > 0) {
/******/ 						var moduleId = queue.pop();
/******/ 						var module = __webpack_require__.c[moduleId];
/******/ 						if (!module) continue;
/******/ 		
/******/ 						var data = {};
/******/ 		
/******/ 						// Call dispose handlers
/******/ 						var disposeHandlers = module.hot._disposeHandlers;
/******/ 						for (j = 0; j < disposeHandlers.length; j++) {
/******/ 							disposeHandlers[j].call(null, data);
/******/ 						}
/******/ 						__webpack_require__.hmrD[moduleId] = data;
/******/ 		
/******/ 						// disable module (this disables requires from this module)
/******/ 						module.hot.active = false;
/******/ 		
/******/ 						// remove module from cache
/******/ 						delete __webpack_require__.c[moduleId];
/******/ 		
/******/ 						// when disposing there is no need to call dispose handler
/******/ 						delete outdatedDependencies[moduleId];
/******/ 		
/******/ 						// remove "parents" references from all children
/******/ 						for (j = 0; j < module.children.length; j++) {
/******/ 							var child = __webpack_require__.c[module.children[j]];
/******/ 							if (!child) continue;
/******/ 							idx = child.parents.indexOf(moduleId);
/******/ 							if (idx >= 0) {
/******/ 								child.parents.splice(idx, 1);
/******/ 							}
/******/ 						}
/******/ 					}
/******/ 		
/******/ 					// remove outdated dependency from module children
/******/ 					var dependency;
/******/ 					for (var outdatedModuleId in outdatedDependencies) {
/******/ 						if (__webpack_require__.o(outdatedDependencies, outdatedModuleId)) {
/******/ 							module = __webpack_require__.c[outdatedModuleId];
/******/ 							if (module) {
/******/ 								moduleOutdatedDependencies =
/******/ 									outdatedDependencies[outdatedModuleId];
/******/ 								for (j = 0; j < moduleOutdatedDependencies.length; j++) {
/******/ 									dependency = moduleOutdatedDependencies[j];
/******/ 									idx = module.children.indexOf(dependency);
/******/ 									if (idx >= 0) module.children.splice(idx, 1);
/******/ 								}
/******/ 							}
/******/ 						}
/******/ 					}
/******/ 				},
/******/ 				apply: function (reportError) {
/******/ 					// insert new code
/******/ 					for (var updateModuleId in appliedUpdate) {
/******/ 						if (__webpack_require__.o(appliedUpdate, updateModuleId)) {
/******/ 							__webpack_require__.m[updateModuleId] = appliedUpdate[updateModuleId];
/******/ 						}
/******/ 					}
/******/ 		
/******/ 					// run new runtime modules
/******/ 					for (var i = 0; i < currentUpdateRuntime.length; i++) {
/******/ 						currentUpdateRuntime[i](__webpack_require__);
/******/ 					}
/******/ 		
/******/ 					// call accept handlers
/******/ 					for (var outdatedModuleId in outdatedDependencies) {
/******/ 						if (__webpack_require__.o(outdatedDependencies, outdatedModuleId)) {
/******/ 							var module = __webpack_require__.c[outdatedModuleId];
/******/ 							if (module) {
/******/ 								moduleOutdatedDependencies =
/******/ 									outdatedDependencies[outdatedModuleId];
/******/ 								var callbacks = [];
/******/ 								var errorHandlers = [];
/******/ 								var dependenciesForCallbacks = [];
/******/ 								for (var j = 0; j < moduleOutdatedDependencies.length; j++) {
/******/ 									var dependency = moduleOutdatedDependencies[j];
/******/ 									var acceptCallback =
/******/ 										module.hot._acceptedDependencies[dependency];
/******/ 									var errorHandler =
/******/ 										module.hot._acceptedErrorHandlers[dependency];
/******/ 									if (acceptCallback) {
/******/ 										if (callbacks.indexOf(acceptCallback) !== -1) continue;
/******/ 										callbacks.push(acceptCallback);
/******/ 										errorHandlers.push(errorHandler);
/******/ 										dependenciesForCallbacks.push(dependency);
/******/ 									}
/******/ 								}
/******/ 								for (var k = 0; k < callbacks.length; k++) {
/******/ 									try {
/******/ 										callbacks[k].call(null, moduleOutdatedDependencies);
/******/ 									} catch (err) {
/******/ 										if (typeof errorHandlers[k] === "function") {
/******/ 											try {
/******/ 												errorHandlers[k](err, {
/******/ 													moduleId: outdatedModuleId,
/******/ 													dependencyId: dependenciesForCallbacks[k]
/******/ 												});
/******/ 											} catch (err2) {
/******/ 												if (options.onErrored) {
/******/ 													options.onErrored({
/******/ 														type: "accept-error-handler-errored",
/******/ 														moduleId: outdatedModuleId,
/******/ 														dependencyId: dependenciesForCallbacks[k],
/******/ 														error: err2,
/******/ 														originalError: err
/******/ 													});
/******/ 												}
/******/ 												if (!options.ignoreErrored) {
/******/ 													reportError(err2);
/******/ 													reportError(err);
/******/ 												}
/******/ 											}
/******/ 										} else {
/******/ 											if (options.onErrored) {
/******/ 												options.onErrored({
/******/ 													type: "accept-errored",
/******/ 													moduleId: outdatedModuleId,
/******/ 													dependencyId: dependenciesForCallbacks[k],
/******/ 													error: err
/******/ 												});
/******/ 											}
/******/ 											if (!options.ignoreErrored) {
/******/ 												reportError(err);
/******/ 											}
/******/ 										}
/******/ 									}
/******/ 								}
/******/ 							}
/******/ 						}
/******/ 					}
/******/ 		
/******/ 					// Load self accepted modules
/******/ 					for (var o = 0; o < outdatedSelfAcceptedModules.length; o++) {
/******/ 						var item = outdatedSelfAcceptedModules[o];
/******/ 						var moduleId = item.module;
/******/ 						try {
/******/ 							item.require(moduleId);
/******/ 						} catch (err) {
/******/ 							if (typeof item.errorHandler === "function") {
/******/ 								try {
/******/ 									item.errorHandler(err, {
/******/ 										moduleId: moduleId,
/******/ 										module: __webpack_require__.c[moduleId]
/******/ 									});
/******/ 								} catch (err2) {
/******/ 									if (options.onErrored) {
/******/ 										options.onErrored({
/******/ 											type: "self-accept-error-handler-errored",
/******/ 											moduleId: moduleId,
/******/ 											error: err2,
/******/ 											originalError: err
/******/ 										});
/******/ 									}
/******/ 									if (!options.ignoreErrored) {
/******/ 										reportError(err2);
/******/ 										reportError(err);
/******/ 									}
/******/ 								}
/******/ 							} else {
/******/ 								if (options.onErrored) {
/******/ 									options.onErrored({
/******/ 										type: "self-accept-errored",
/******/ 										moduleId: moduleId,
/******/ 										error: err
/******/ 									});
/******/ 								}
/******/ 								if (!options.ignoreErrored) {
/******/ 									reportError(err);
/******/ 								}
/******/ 							}
/******/ 						}
/******/ 					}
/******/ 		
/******/ 					return outdatedModules;
/******/ 				}
/******/ 			};
/******/ 		}
/******/ 		__webpack_require__.hmrI.jsonp = function (moduleId, applyHandlers) {
/******/ 			if (!currentUpdate) {
/******/ 				currentUpdate = {};
/******/ 				currentUpdateRuntime = [];
/******/ 				currentUpdateRemovedChunks = [];
/******/ 				applyHandlers.push(applyHandler);
/******/ 			}
/******/ 			if (!__webpack_require__.o(currentUpdate, moduleId)) {
/******/ 				currentUpdate[moduleId] = __webpack_require__.m[moduleId];
/******/ 			}
/******/ 		};
/******/ 		__webpack_require__.hmrC.jsonp = function (
/******/ 			chunkIds,
/******/ 			removedChunks,
/******/ 			removedModules,
/******/ 			promises,
/******/ 			applyHandlers,
/******/ 			updatedModulesList
/******/ 		) {
/******/ 			applyHandlers.push(applyHandler);
/******/ 			currentUpdateChunks = {};
/******/ 			currentUpdateRemovedChunks = removedChunks;
/******/ 			currentUpdate = removedModules.reduce(function (obj, key) {
/******/ 				obj[key] = false;
/******/ 				return obj;
/******/ 			}, {});
/******/ 			currentUpdateRuntime = [];
/******/ 			chunkIds.forEach(function (chunkId) {
/******/ 				if (
/******/ 					__webpack_require__.o(installedChunks, chunkId) &&
/******/ 					installedChunks[chunkId] !== undefined
/******/ 				) {
/******/ 					promises.push(loadUpdateChunk(chunkId, updatedModulesList));
/******/ 					currentUpdateChunks[chunkId] = true;
/******/ 				} else {
/******/ 					currentUpdateChunks[chunkId] = false;
/******/ 				}
/******/ 			});
/******/ 			if (__webpack_require__.f) {
/******/ 				__webpack_require__.f.jsonpHmr = function (chunkId, promises) {
/******/ 					if (
/******/ 						currentUpdateChunks &&
/******/ 						__webpack_require__.o(currentUpdateChunks, chunkId) &&
/******/ 						!currentUpdateChunks[chunkId]
/******/ 					) {
/******/ 						promises.push(loadUpdateChunk(chunkId));
/******/ 						currentUpdateChunks[chunkId] = true;
/******/ 					}
/******/ 				};
/******/ 			}
/******/ 		};
/******/ 		
/******/ 		__webpack_require__.hmrM = function() {
/******/ 			if (typeof fetch === "undefined") throw new Error("No browser support: need fetch API");
/******/ 			return fetch(__webpack_require__.p + __webpack_require__.hmrF()).then(function(response) {
/******/ 				if(response.status === 404) return; // no update available
/******/ 				if(!response.ok) throw new Error("Failed to fetch update manifest " + response.statusText);
/******/ 				return response.json();
/******/ 			});
/******/ 		};
/******/ 		
/******/ 		__webpack_require__.O.j = function(chunkId) { return installedChunks[chunkId] === 0; };
/******/ 		
/******/ 		// install a JSONP callback for chunk loading
/******/ 		var webpackJsonpCallback = function(parentChunkLoadingFunction, data) {
/******/ 			var chunkIds = data[0];
/******/ 			var moreModules = data[1];
/******/ 			var runtime = data[2];
/******/ 			// add "moreModules" to the modules object,
/******/ 			// then flag all "chunkIds" as loaded and fire callback
/******/ 			var moduleId, chunkId, i = 0;
/******/ 			if(chunkIds.some(function(id) { return installedChunks[id] !== 0; })) {
/******/ 				for(moduleId in moreModules) {
/******/ 					if(__webpack_require__.o(moreModules, moduleId)) {
/******/ 						__webpack_require__.m[moduleId] = moreModules[moduleId];
/******/ 					}
/******/ 				}
/******/ 				if(runtime) var result = runtime(__webpack_require__);
/******/ 			}
/******/ 			if(parentChunkLoadingFunction) parentChunkLoadingFunction(data);
/******/ 			for(;i < chunkIds.length; i++) {
/******/ 				chunkId = chunkIds[i];
/******/ 				if(__webpack_require__.o(installedChunks, chunkId) && installedChunks[chunkId]) {
/******/ 					installedChunks[chunkId][0]();
/******/ 				}
/******/ 				installedChunks[chunkId] = 0;
/******/ 			}
/******/ 			return __webpack_require__.O(result);
/******/ 		}
/******/ 		
/******/ 		var chunkLoadingGlobal = (typeof self !== 'undefined' ? self : this)["webpackChunkvue_frontend"] = (typeof self !== 'undefined' ? self : this)["webpackChunkvue_frontend"] || [];
/******/ 		chunkLoadingGlobal.forEach(webpackJsonpCallback.bind(null, 0));
/******/ 		chunkLoadingGlobal.push = webpackJsonpCallback.bind(null, chunkLoadingGlobal.push.bind(chunkLoadingGlobal));
/******/ 	}();
/******/ 	
/************************************************************************/
/******/ 	
/******/ 	// module cache are used so entry inlining is disabled
/******/ 	// startup
/******/ 	// Load entry module and return exports
/******/ 	__webpack_require__.O(undefined, ["chunk-vendors"], function() { return __webpack_require__("./node_modules/whatwg-fetch/fetch.js"); })
/******/ 	__webpack_require__.O(undefined, ["chunk-vendors"], function() { return __webpack_require__("./node_modules/webpack-dev-server/client/index.js?protocol=ws&hostname=localhost&port=8080&pathname=%2Fws&logging=none&reconnect=10"); })
/******/ 	__webpack_require__.O(undefined, ["chunk-vendors"], function() { return __webpack_require__("./node_modules/webpack/hot/dev-server.js"); })
/******/ 	var __webpack_exports__ = __webpack_require__.O(undefined, ["chunk-vendors"], function() { return __webpack_require__("./src/questionnaire.js"); })
/******/ 	__webpack_exports__ = __webpack_require__.O(__webpack_exports__);
/******/ 	
/******/ })()
;