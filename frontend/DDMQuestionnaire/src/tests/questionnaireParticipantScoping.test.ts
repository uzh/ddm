import { mount } from "@vue/test-utils";
import { describe, it, expect, beforeAll, beforeEach, vi } from "vitest";
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

// jsdom doesn't implement scrollIntoView.
Element.prototype.scrollIntoView = vi.fn();

const questionnaireConfig = [
  {
    question: "question-1",
    type: "open",
    page: 1,
    index: 1,
    text: "<p>What's on your mind?</p>",
    requirement_level: REQUIREMENT_LEVELS.NOT_REQUIRED,
    items: [],
    scale: [],
    options: { input_type: "text", display: "small", multi_item_response: false },
  },
];

function mountApp(participantId?: string) {
  return mount(QuestionnaireApp, {
    global: { plugins: [i18n], directives },
    props: {
      questionnaireConfig,
      filterConfig: { "question-1": [] },
      staticVariables: [],
      actionUrl: "https://some.url/questionnaire/",
      language: "en",
      participantId,
    },
  });
}

describe("per-participant scoping of the locally cached draft", () => {
  beforeAll(() => {
    document.documentElement.scrollTo = vi.fn();
  });

  beforeEach(() => {
    localStorage.clear();
  });

  it("does not let a different participant inherit a previous participant's unsubmitted draft", async () => {
    const wrapperA = mountApp("participant-aaa");
    const inputA = wrapperA.find('input[name="question-1"]');
    await inputA.setValue("Participant A's private answer");
    await inputA.trigger("change");
    wrapperA.unmount();

    // A different participant, same browser/localStorage, same questionnaire.
    const wrapperB = mountApp("participant-bbb");
    const inputB = wrapperB.find('input[name="question-1"]');

    expect(inputB.element.value).toBe("");
  });

  it("still restores the same participant's own cached draft on a later visit", async () => {
    const wrapperFirstVisit = mountApp("participant-aaa");
    const input = wrapperFirstVisit.find('input[name="question-1"]');
    await input.setValue("Still working on this");
    await input.trigger("change");
    wrapperFirstVisit.unmount();

    // Same participant, e.g. after a reload.
    const wrapperSecondVisit = mountApp("participant-aaa");
    const restoredInput = wrapperSecondVisit.find('input[name="question-1"]');

    expect(restoredInput.element.value).toBe("Still working on this");
  });

  it("keys the persisted responses and current-page caches by participant id", async () => {
    const wrapper = mountApp("participant-ccc");
    const input = wrapper.find('input[name="question-1"]');
    await input.setValue("some answer");
    await input.trigger("change");

    expect(localStorage.getItem("questionnaire-responses:participant-ccc")).not.toBeNull();
    expect(localStorage.getItem("questionnaire-responses:participant-other")).toBeNull();
  });
});
