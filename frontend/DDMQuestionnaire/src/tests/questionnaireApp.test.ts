import { mount } from "@vue/test-utils";
import { describe, it, expect } from "vitest";
import { i18n } from "@questionnaire/tests/testUtils";

import QuestionnaireApp from "../components/QuestionnaireApp.vue";

const questionnaireConfigAsString = JSON.stringify(
  [
    {
      "question": "question-1",
      "type": "matrix",
      "page": 1,
      "index": 1,
      "text": "<p>test</p>",
      "required": false,
      "items": [
        {"id": "item-1", "index": 1, "label": "some label", "label_alt": "", "value": 1, "randomize": false},
        {"id": "item-2", "index": 2, "label": "some label", "label_alt": "", "value": 2, "randomize": false}
      ],
      "scale": [
        {"id": 1, "index": 1, "input_label": "1", "heading_label": "1", "value": 1, "secondary_point": false},
        {"id": 2, "index": 2, "input_label": "2", "heading_label": "2", "value": 2, "secondary_point": false},
        {"id": 3, "index": 3, "input_label": "3", "heading_label": "3", "value": 3, "secondary_point": false}
      ],
      "options": { "show_scale_headings": false }
    },
    {
      "question": "question-2",
      "type": "matrix",
      "page": 1,
      "index": 2,
      "text": "<p>test</p>",
      "required": false,
      "items": [
        {"id": "item-3", "index": 1, "label": "some label", "label_alt": "", "value": 1, "randomize": false},
        {"id": "item-4", "index": 2, "label": "some label", "label_alt": "", "value": 2, "randomize": false}
      ],
      "scale": [
        {"id": 4, "index": 1, "input_label": "1", "heading_label": "1", "value": 1, "secondary_point": false},
        {"id": 5, "index": 2, "input_label": "2", "heading_label": "2", "value": 2, "secondary_point": false}
      ],
      "options": { "show_scale_headings": false }
    },
    {
      "question": "question-3",
      "type": "semantic_diff",
      "page": 2,
      "index": 1,
      "text": "<p>test</p>",
      "required": false,
      "items": [
        {"id": "item-5", "index": 1, "label": "some label", "label_alt": "", "value": 1, "randomize": false},
        {"id": "item-6", "index": 2, "label": "some label", "label_alt": "", "value": 2, "randomize": false},
      ],
      "scale": [
        {"id": 6, "index": 1, "input_label": "1", "heading_label": "1", "value": 1, "secondary_point": false},
        {"id": 7, "index": 2, "input_label": "2", "heading_label": "2", "value": 2, "secondary_point": false },
      ],
      "options": {}
    },
    {
      "question": "question-4",
      "type": "transition",
      "page": 3,
      "index": 3,
      "text": "<p>test</p>",
      "required": false,
      "items": [],
      "scale": [],
      "options": {}
    }
  ]
);
const filterConfigAsString = JSON.stringify(
  {
    "question-1": [],
    "item-1": [],
    "item-2": [],
    "question-2": [
      {
        "index": 1,
        "combinator": null,
        "condition_operator": "==",
        "condition_value": "2",
        "target": "question-2",
        "source": "item-1"
      }
    ],
    "item-3": [
      {
        "index": 1,
        "combinator": null,
        "condition_operator": "==",
        "condition_value": "1",
        "target": "item-3",
        "source": "item-1"
      },
      {
        "index": 2,
        "combinator": "OR",
        "condition_operator": "==",
        "condition_value": "3",
        "target": "item-3",
        "source": "item-1"
      }
    ],
    "item-4": [
      {
        "index": 1,
        "combinator": null,
        "condition_operator": "==",
        "condition_value": "3",
        "target": "item-4",
        "source": "item-1"
      }
    ],
    "question-3": [
      {
        "index": 1,
        "combinator": null,
        "condition_operator": "==",
        "condition_value": "1",
        "target": "question-3",
        "source": "item-1"
      }
    ],
    "item-5": [],
    "item-6": [],
    "question-4": []
  }
);
const actionUrl = "https://some.url"
const language = "en"

describe("QuestionnaireApp", () => {
  beforeAll(() => {
    document.documentElement.scrollTo = vi.fn();
  });

  const wrapper = mount(QuestionnaireApp, {
    global: {
      plugins: [i18n]
    },
    props: {
      questionnaireConfigAsString: questionnaireConfigAsString,
      filterConfigAsString: filterConfigAsString,
      actionUrl: actionUrl,
      language: language
    }
  })

  it("displays the correct questions", () => {
    expect(wrapper.find("[data-question-id=question-1]").isVisible()).toBe(true);
    expect(wrapper.find("[data-question-id=question-2]").isVisible()).toBe(true);
    expect(wrapper.find("#answer-item-1").isVisible()).toBe(true);
    expect(wrapper.find("#answer-item-2").isVisible()).toBe(true);
    expect(wrapper.find("#answer-item-3").isVisible()).toBe(true);
    expect(wrapper.find("#answer-item-4").isVisible()).toBe(true);

    expect(wrapper.find("[data-question-id=question-3]").isVisible()).toBe(false);
    expect(wrapper.find("#answer-item-5").isVisible()).toBe(false);
    expect(wrapper.find("#answer-item-6").isVisible()).toBe(false);
    expect(wrapper.find("[data-question-id=question-4]").isVisible()).toBe(false);
  })

  it("hides item when filtered", async() => {
    // Ensure item is visible.
    expect(wrapper.find("#answer-item-3").isVisible()).toBe(true);
    // Select value = 1.
    await wrapper.find("#question-1-item-1-1").trigger("change");
    await new Promise(resolve => setTimeout(resolve, 1000));
    // Ensure that item is filtered.
    expect(wrapper.find("#answer-item-3").element.style.display).toBe('none');
  })

  it("hides question when filtered", async() => {
    // Ensure question is visible.
    expect(wrapper.find("[data-question-id=question-2]").element.style.display).not.toBe('none');
    // Select value = 2.
    await wrapper.find("#question-1-item-1-2").trigger("change");
    await new Promise(resolve => setTimeout(resolve, 1000));
    // Ensure that question is filtered.
    expect(wrapper.find("[data-question-id=question-2]").element.style.display).toBe('none');
  })

  it("hides question when all items are filtered", async() => {
    // Select value = 3.
    await wrapper.find("#question-1-item-1-3").trigger("change");
    await new Promise(resolve => setTimeout(resolve, 1000));
    // Ensure that question is filtered.
    expect(wrapper.find("#answer-item-3").element.style.display).toBe('none');
    expect(wrapper.find("#answer-item-4").element.style.display).toBe('none');
    expect(wrapper.find("[data-question-id=question-2]").element.style.display).toBe('none');
  })

  it("skips page when all questions are hidden", async() => {
    // Select value 1.
    await wrapper.find("#question-1-item-1-1").trigger("change");
    await new Promise(resolve => setTimeout(resolve, 1000));
    // Click on next page.
    await wrapper.find("#next-page-btn").trigger("click");
    await new Promise(resolve => setTimeout(resolve, 1000));
    // Check that questionnaire skips page 2 and displays page 3.
    expect(wrapper.find("[data-page-index='1']").element.style.display).toBe('none');
    expect(wrapper.find("[data-page-index='2']").element.style.display).toBe('none');
    expect(wrapper.find("[data-question-id=question-4]").element.style.display).not.toBe('none');
  })

})
