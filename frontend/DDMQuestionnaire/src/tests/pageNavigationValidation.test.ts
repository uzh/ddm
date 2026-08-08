import { mount } from "@vue/test-utils";
import { describe, it, expect, beforeAll, vi } from "vitest";
import { i18n } from "@questionnaire/tests/testUtils";

import { onlyDigits, validEmail, validLength, validValue } from "@questionnaire/directives/formDirectives";
import QuestionnaireApp from "../components/QuestionnaireApp.vue";

const directives = {
  "only-digits": onlyDigits,
  "valid-email": validEmail,
  "valid-length": validLength,
  "valid-value": validValue,
};

const wait = () => new Promise(resolve => setTimeout(resolve, 1000));

function mountApp(questionnaireConfig: unknown[]) {
  const entries: [string, never[]][] = [];
  (questionnaireConfig as { question: string; items?: { id: string }[] }[]).forEach(q => {
    entries.push([q.question, []]);
    (q.items ?? []).forEach(item => entries.push([item.id, []]));
  });
  const filterConfig = Object.fromEntries(entries);
  return mount(QuestionnaireApp, {
    global: { plugins: [i18n], directives },
    props: {
      questionnaireConfig,
      filterConfig,
      staticVariables: [],
      actionUrl: "https://some.url",
      language: "en",
    },
  });
}

describe("page navigation with open question length/value bounds", () => {
  beforeAll(() => {
    document.documentElement.scrollTo = vi.fn();
  });

  it("blocks navigation on an out-of-range number, then allows it once fixed", async () => {
    const wrapper = mountApp([
      {
        question: "question-1",
        type: "open",
        page: 1,
        index: 1,
        text: "<p>Enter a number</p>",
        required: false,
        items: [],
        scale: [],
        options: { input_type: "numbers", min_number_value: 5, max_number_value: 10, multi_item_response: false },
      },
      {
        question: "question-2",
        type: "transition",
        page: 2,
        index: 1,
        text: "<p>done</p>",
        required: false,
        items: [],
        scale: [],
        options: {},
      },
    ]);

    const input = wrapper.find('input[name="question-1"]');

    // Below the configured minimum.
    await input.setValue("2");
    await input.trigger("change");
    await wrapper.find("#next-page-btn").trigger("click");
    await wait();

    expect(wrapper.find("[data-page-index='1']").element.style.display).not.toBe("none");
    expect(input.classes()).toContain("invalid-value");

    // Within bounds.
    await input.setValue("7");
    await input.trigger("change");
    await wrapper.find("#next-page-btn").trigger("click");
    await wait();

    expect(wrapper.find("[data-page-index='1']").element.style.display).toBe("none");
    expect(wrapper.find("[data-page-index='2']").element.style.display).not.toBe("none");
  });

  it("does not block navigation on an unanswered (empty) bounded field", async () => {
    const wrapper = mountApp([
      {
        question: "question-1",
        type: "open",
        page: 1,
        index: 1,
        text: "<p>Optionally enter text</p>",
        required: false,
        items: [],
        scale: [],
        options: { input_type: "text", display: "small", min_input_length: 5, multi_item_response: false },
      },
      {
        question: "question-2",
        type: "transition",
        page: 2,
        index: 1,
        text: "<p>done</p>",
        required: false,
        items: [],
        scale: [],
        options: {},
      },
    ]);

    await wrapper.find("#next-page-btn").trigger("click");
    await wait();

    expect(wrapper.find("[data-page-index='1']").element.style.display).toBe("none");
    expect(wrapper.find("[data-page-index='2']").element.style.display).not.toBe("none");
  });

  it("blocks navigation when only one item of a multi-item question is out of bounds", async () => {
    const wrapper = mountApp([
      {
        question: "question-1",
        type: "open",
        page: 1,
        index: 1,
        text: "<p>Enter text for each item</p>",
        required: false,
        items: [
          { id: "item-1", index: 1, label: "First", value: 1, randomize: false },
          { id: "item-2", index: 2, label: "Second", value: 2, randomize: false },
        ],
        scale: [],
        options: { input_type: "text", display: "small", min_input_length: 5, multi_item_response: true },
      },
      {
        question: "question-2",
        type: "transition",
        page: 2,
        index: 1,
        text: "<p>done</p>",
        required: false,
        items: [],
        scale: [],
        options: {},
      },
    ]);

    const item1 = wrapper.find('input[name="item-1"]');
    const item2 = wrapper.find('input[name="item-2"]');

    await item1.setValue("ab"); // too short
    await item1.trigger("change");
    await item2.setValue("abcdef"); // valid
    await item2.trigger("change");

    await wrapper.find("#next-page-btn").trigger("click");
    await wait();

    expect(wrapper.find("[data-page-index='1']").element.style.display).not.toBe("none");
    expect(item1.classes()).toContain("invalid-length");
    expect(item2.classes()).not.toContain("invalid-length");

    await item1.setValue("abcdef"); // fix it
    await item1.trigger("change");
    await wrapper.find("#next-page-btn").trigger("click");
    await wait();

    expect(wrapper.find("[data-page-index='1']").element.style.display).toBe("none");
    expect(wrapper.find("[data-page-index='2']").element.style.display).not.toBe("none");
  });
});
