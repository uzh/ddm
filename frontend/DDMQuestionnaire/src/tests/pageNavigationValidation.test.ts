import { mount } from "@vue/test-utils";
import { describe, it, expect, beforeAll, vi } from "vitest";
import { i18n } from "@questionnaire/tests/testUtils";

import { onlyDigits, validEmail, validLength, validValue } from "@questionnaire/directives/formDirectives";
import { REQUIREMENT_LEVELS } from "@questionnaire/types/questionnaire";
import QuestionnaireApp from "../components/QuestionnaireApp.vue";

const directives = {
  "only-digits": onlyDigits,
  "valid-email": validEmail,
  "valid-length": validLength,
  "valid-value": validValue,
};

const wait = () => new Promise(resolve => setTimeout(resolve, 1000));

// jsdom doesn't implement scrollIntoView.
Element.prototype.scrollIntoView = vi.fn();

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
        requirement_level: REQUIREMENT_LEVELS.NOT_REQUIRED,
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
        requirement_level: REQUIREMENT_LEVELS.NOT_REQUIRED,
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
        requirement_level: REQUIREMENT_LEVELS.NOT_REQUIRED,
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
        requirement_level: REQUIREMENT_LEVELS.NOT_REQUIRED,
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
        requirement_level: REQUIREMENT_LEVELS.NOT_REQUIRED,
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
        requirement_level: REQUIREMENT_LEVELS.NOT_REQUIRED,
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

describe("required-field soft check resets per page", () => {
  beforeAll(() => {
    document.documentElement.scrollTo = vi.fn();
  });

  it("re-checks required fields on each new page instead of only once per session", async () => {
    const wrapper = mountApp([
      {
        question: "question-1",
        type: "open",
        page: 1,
        index: 1,
        text: "<p>Required on page 1</p>",
        requirement_level: REQUIREMENT_LEVELS.SOFT,
        items: [],
        scale: [],
        options: { input_type: "text", display: "small", multi_item_response: false },
      },
      {
        question: "question-2",
        type: "open",
        page: 2,
        index: 1,
        text: "<p>Required on page 2</p>",
        requirement_level: REQUIREMENT_LEVELS.SOFT,
        items: [],
        scale: [],
        options: { input_type: "text", display: "small", multi_item_response: false },
      },
      {
        question: "question-3",
        type: "transition",
        page: 3,
        index: 1,
        text: "<p>done</p>",
        requirement_level: REQUIREMENT_LEVELS.NOT_REQUIRED,
        items: [],
        scale: [],
        options: {},
      },
    ]);

    // Page 1, first click: blocked, hint shown for the missing required field.
    await wrapper.find("#next-page-btn").trigger("click");
    await wait();
    expect(wrapper.find("[data-page-index='1']").element.style.display).not.toBe("none");
    expect(wrapper.find("#required-hint-question-1").classes()).toContain("show");

    // Page 1, second click: soft check already shown once, advances regardless.
    await wrapper.find("#next-page-btn").trigger("click");
    await wait();
    expect(wrapper.find("[data-page-index='1']").element.style.display).toBe("none");
    expect(wrapper.find("[data-page-index='2']").element.style.display).not.toBe("none");

    // Page 2, first click: must be checked independently of page 1 - blocked.
    await wrapper.find("#next-page-btn").trigger("click");
    await wait();
    expect(wrapper.find("[data-page-index='2']").element.style.display).not.toBe("none");
    expect(wrapper.find("[data-page-index='3']").element.style.display).toBe("none");
    expect(wrapper.find("#required-hint-question-2").classes()).toContain("show");

    // Page 2, second click: advances.
    await wrapper.find("#next-page-btn").trigger("click");
    await wait();
    expect(wrapper.find("[data-page-index='2']").element.style.display).toBe("none");
    expect(wrapper.find("[data-page-index='3']").element.style.display).not.toBe("none");
  });
});

describe("hard-required field", () => {
  beforeAll(() => {
    document.documentElement.scrollTo = vi.fn();
  });

  function mountHardRequired() {
    return mountApp([
      {
        question: "question-1",
        type: "open",
        page: 1,
        index: 1,
        text: "<p>Hard required</p>",
        requirement_level: REQUIREMENT_LEVELS.HARD,
        items: [],
        scale: [],
        options: { input_type: "text", display: "small", multi_item_response: false },
      },
      {
        question: "question-2",
        type: "transition",
        page: 2,
        index: 1,
        text: "<p>done</p>",
        requirement_level: REQUIREMENT_LEVELS.NOT_REQUIRED,
        items: [],
        scale: [],
        options: {},
      },
    ]);
  }

  it("keeps blocking on every click while empty, unlike a soft-required field", async () => {
    const wrapper = mountHardRequired();

    // First click: blocked, hint shown.
    await wrapper.find("#next-page-btn").trigger("click");
    await wait();
    expect(wrapper.find("[data-page-index='1']").element.style.display).not.toBe("none");
    expect(wrapper.find("#required-hint-question-1").classes()).toContain("show");

    // Second click, still empty: a soft-required field would advance here; hard-required must not.
    await wrapper.find("#next-page-btn").trigger("click");
    await wait();
    expect(wrapper.find("[data-page-index='1']").element.style.display).not.toBe("none");

    // Third click, still empty: keeps blocking indefinitely.
    await wrapper.find("#next-page-btn").trigger("click");
    await wait();
    expect(wrapper.find("[data-page-index='1']").element.style.display).not.toBe("none");
  });

  it("allows navigation once the hard-required field is filled in", async () => {
    const wrapper = mountHardRequired();

    // Get blocked once first.
    await wrapper.find("#next-page-btn").trigger("click");
    await wait();
    expect(wrapper.find("[data-page-index='1']").element.style.display).not.toBe("none");

    // Fill in the field, then try again.
    const input = wrapper.find('input[name="question-1"]');
    await input.setValue("some answer");
    await input.trigger("change");
    await wrapper.find("#next-page-btn").trigger("click");
    await wait();

    expect(wrapper.find("[data-page-index='1']").element.style.display).toBe("none");
    expect(wrapper.find("[data-page-index='2']").element.style.display).not.toBe("none");
  });
});

describe("mixed soft- and hard-required fields on the same page", () => {
  beforeAll(() => {
    document.documentElement.scrollTo = vi.fn();
  });

  it("clears the soft-required hint and border once answered, even while a hard-required field is still blocking", async () => {
    const wrapper = mountApp([
      {
        question: "question-1",
        type: "open",
        page: 1,
        index: 1,
        text: "<p>Soft required</p>",
        requirement_level: REQUIREMENT_LEVELS.SOFT,
        items: [],
        scale: [],
        options: { input_type: "text", display: "small", multi_item_response: false },
      },
      {
        question: "question-2",
        type: "open",
        page: 1,
        index: 2,
        text: "<p>Hard required</p>",
        requirement_level: REQUIREMENT_LEVELS.HARD,
        items: [],
        scale: [],
        options: { input_type: "text", display: "small", multi_item_response: false },
      },
    ]);

    // First click: both empty, both flagged.
    await wrapper.find("#next-page-btn").trigger("click");
    await wait();
    expect(wrapper.find("#required-hint-question-1").classes()).toContain("show");
    expect(wrapper.find("#answer-question-1").classes()).toContain("required-but-missing");
    expect(wrapper.find("#required-hint-question-2").classes()).toContain("show");
    expect(wrapper.find("#answer-question-2").classes()).toContain("required-but-missing");

    // Answer only the soft-required field; hard-required stays empty.
    const softInput = wrapper.find('input[name="question-1"]');
    await softInput.setValue("some answer");
    await softInput.trigger("change");
    await wrapper.find("#next-page-btn").trigger("click");
    await wait();

    // Still blocked overall (hard-required missing), but the now-answered
    // soft-required question's marks must be cleared.
    expect(wrapper.find("[data-page-index='1']").element.style.display).not.toBe("none");
    expect(wrapper.find("#required-hint-question-1").classes()).not.toContain("show");
    expect(wrapper.find("#answer-question-1").classes()).not.toContain("required-but-missing");
    expect(wrapper.find("#required-hint-question-2").classes()).toContain("show");
    expect(wrapper.find("#answer-question-2").classes()).toContain("required-but-missing");
  });
});

describe("scrolling on next-page click", () => {
  beforeAll(() => {
    document.documentElement.scrollTo = vi.fn();
  });

  it("scrolls to the first missing required hint, not the top, when blocked", async () => {
    const wrapper = mountApp([
      {
        question: "question-1",
        type: "open",
        page: 1,
        index: 1,
        text: "<p>First required</p>",
        requirement_level: REQUIREMENT_LEVELS.SOFT,
        items: [],
        scale: [],
        options: { input_type: "text", display: "small", multi_item_response: false },
      },
      {
        question: "question-2",
        type: "open",
        page: 1,
        index: 2,
        text: "<p>Second required</p>",
        requirement_level: REQUIREMENT_LEVELS.SOFT,
        items: [],
        scale: [],
        options: { input_type: "text", display: "small", multi_item_response: false },
      },
    ]);

    const firstHint = wrapper.find("#required-hint-question-1").element as HTMLElement;
    const secondHint = wrapper.find("#required-hint-question-2").element as HTMLElement;
    const firstHintScroll = vi.spyOn(firstHint, "scrollIntoView").mockImplementation(() => {});
    const secondHintScroll = vi.spyOn(secondHint, "scrollIntoView").mockImplementation(() => {});
    const topScroll = vi.spyOn(document.documentElement, "scrollTo");

    await wrapper.find("#next-page-btn").trigger("click");
    await wait();

    expect(firstHintScroll).toHaveBeenCalled();
    expect(secondHintScroll).not.toHaveBeenCalled();
    expect(topScroll).not.toHaveBeenCalled();
  });

  it("scrolls to the top (not a hint) when navigation succeeds", async () => {
    const wrapper = mountApp([
      {
        question: "question-1",
        type: "transition",
        page: 1,
        index: 1,
        text: "<p>done</p>",
        requirement_level: REQUIREMENT_LEVELS.NOT_REQUIRED,
        items: [],
        scale: [],
        options: {},
      },
      {
        question: "question-2",
        type: "transition",
        page: 2,
        index: 1,
        text: "<p>done</p>",
        requirement_level: REQUIREMENT_LEVELS.NOT_REQUIRED,
        items: [],
        scale: [],
        options: {},
      },
    ]);

    const topScroll = vi.spyOn(document.documentElement, "scrollTo");

    await wrapper.find("#next-page-btn").trigger("click");
    await wait();

    expect(topScroll).toHaveBeenCalled();
  });

  it("scrolls to the first invalid length/value field when blocked by bounds alone (no missing required field)", async () => {
    const wrapper = mountApp([
      {
        question: "question-1",
        type: "open",
        page: 1,
        index: 1,
        text: "<p>Enter a number</p>",
        requirement_level: REQUIREMENT_LEVELS.NOT_REQUIRED,
        items: [],
        scale: [],
        options: { input_type: "numbers", min_number_value: 5, max_number_value: 10, multi_item_response: false },
      },
    ]);

    const input = wrapper.find('input[name="question-1"]');
    await input.setValue("2"); // below the configured minimum
    await input.trigger("change");

    const inputScroll = vi.spyOn(input.element as HTMLElement, "scrollIntoView").mockImplementation(() => {});
    const topScroll = vi.spyOn(document.documentElement, "scrollTo");

    await wrapper.find("#next-page-btn").trigger("click");
    await wait();

    expect(inputScroll).toHaveBeenCalled();
    expect(topScroll).not.toHaveBeenCalled();
  });

  it("scrolls to whichever issue is topmost on the page, regardless of check type", async () => {
    // An invalid-length field above a missing required field: the
    // length issue is topmost, even though `checkRequired` runs before
    // `validateResponses` internally - scrolling must follow DOM order,
    // not which check happened to run first.
    const wrapper = mountApp([
      {
        question: "question-1",
        type: "open",
        page: 1,
        index: 1,
        text: "<p>Needs at least 5 characters</p>",
        requirement_level: REQUIREMENT_LEVELS.NOT_REQUIRED,
        items: [],
        scale: [],
        options: { input_type: "text", display: "small", min_input_length: 5, multi_item_response: false },
      },
      {
        question: "question-2",
        type: "open",
        page: 1,
        index: 2,
        text: "<p>Required</p>",
        requirement_level: REQUIREMENT_LEVELS.SOFT,
        items: [],
        scale: [],
        options: { input_type: "text", display: "small", multi_item_response: false },
      },
    ]);

    const lengthInput = wrapper.find('input[name="question-1"]');
    await lengthInput.setValue("ab"); // too short
    await lengthInput.trigger("change");

    const lengthScroll = vi.spyOn(lengthInput.element as HTMLElement, "scrollIntoView").mockImplementation(() => {});
    const requiredHintEl = wrapper.find("#required-hint-question-2").element as HTMLElement;
    const requiredScroll = vi.spyOn(requiredHintEl, "scrollIntoView").mockImplementation(() => {});

    await wrapper.find("#next-page-btn").trigger("click");
    await wait();

    expect(lengthScroll).toHaveBeenCalled();
    expect(requiredScroll).not.toHaveBeenCalled();
  });
});

describe("required hint on multi-item open questions", () => {
  beforeAll(() => {
    document.documentElement.scrollTo = vi.fn();
  });

  it("shows the required hint and border for a missing item, and clears them once answered", async () => {
    const wrapper = mountApp([
      {
        question: "question-1",
        type: "open",
        page: 1,
        index: 1,
        text: "<p>Enter text for each item</p>",
        requirement_level: REQUIREMENT_LEVELS.SOFT,
        items: [
          { id: "item-1", index: 1, label: "First", value: 1, randomize: false },
          { id: "item-2", index: 2, label: "Second", value: 2, randomize: false },
        ],
        scale: [],
        options: { input_type: "text", display: "small", multi_item_response: true },
      },
    ]);

    await wrapper.find("#next-page-btn").trigger("click");
    await wait();

    expect(wrapper.find("#required-hint-item-1").classes()).toContain("show");
    expect(wrapper.find("#answer-item-1").classes()).toContain("required-but-missing");
    expect(wrapper.find("#required-hint-item-2").classes()).toContain("show");
    expect(wrapper.find("#answer-item-2").classes()).toContain("required-but-missing");

    const item1 = wrapper.find('input[name="item-1"]');
    const item2 = wrapper.find('input[name="item-2"]');
    await item1.setValue("answer one");
    await item1.trigger("change");
    await item2.setValue("answer two");
    await item2.trigger("change");

    await wrapper.find("#next-page-btn").trigger("click");
    await wait();

    expect(wrapper.find("#required-hint-item-1").classes()).not.toContain("show");
    expect(wrapper.find("#answer-item-1").classes()).not.toContain("required-but-missing");
    expect(wrapper.find("#required-hint-item-2").classes()).not.toContain("show");
    expect(wrapper.find("#answer-item-2").classes()).not.toContain("required-but-missing");
  });
});
