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

const wait = () => new Promise(resolve => setTimeout(resolve, 1000));

// jsdom doesn't implement scrollIntoView.
Element.prototype.scrollIntoView = vi.fn();

const actionUrl = "https://some.url/questionnaire/";
const progressUrl = "https://some.url/questionnaire/progress/";

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
      actionUrl,
      progressUrl,
      language: "en",
    },
  });
}

describe("in-progress response saving on page advance", () => {
  beforeAll(() => {
    document.documentElement.scrollTo = vi.fn();
  });

  beforeEach(() => {
    vi.stubGlobal(
      "fetch",
      vi.fn(() => Promise.resolve(new Response(JSON.stringify({ status: "ok" }), { status: 200 })))
    );
  });

  it("posts to progressUrl (not actionUrl) when advancing to a non-final page", async () => {
    const wrapper = mountApp([
      {
        question: "question-1",
        type: "transition",
        page: 1,
        index: 1,
        text: "<p>page one</p>",
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
        text: "<p>page two</p>",
        requirement_level: REQUIREMENT_LEVELS.NOT_REQUIRED,
        items: [],
        scale: [],
        options: {},
      },
    ]);

    await wrapper.find("#next-page-btn").trigger("click");
    await wait();

    expect(fetch).toHaveBeenCalledTimes(1);
    expect(fetch).toHaveBeenCalledWith(progressUrl, expect.objectContaining({ method: "POST" }));
  });

  it("posts to actionUrl (not progressUrl) on the final page, and does not also fire a progress save", async () => {
    const wrapper = mountApp([
      {
        question: "question-1",
        type: "transition",
        page: 1,
        index: 1,
        text: "<p>only page</p>",
        requirement_level: REQUIREMENT_LEVELS.NOT_REQUIRED,
        items: [],
        scale: [],
        options: {},
      },
    ]);

    await wrapper.find("#next-page-btn").trigger("click");
    await wait();

    expect(fetch).toHaveBeenCalledTimes(1);
    expect(fetch).toHaveBeenCalledWith(actionUrl, expect.objectContaining({ method: "POST" }));
  });

  it("does not call fetch when navigation is blocked by a missing hard-required field", async () => {
    const wrapper = mountApp([
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
        text: "<p>page two</p>",
        requirement_level: REQUIREMENT_LEVELS.NOT_REQUIRED,
        items: [],
        scale: [],
        options: {},
      },
    ]);

    await wrapper.find("#next-page-btn").trigger("click");
    await wait();

    expect(fetch).not.toHaveBeenCalled();
  });

  it("does not affect page rendering when progressUrl is not provided", async () => {
    const wrapper = mount(QuestionnaireApp, {
      global: { plugins: [i18n] },
      props: {
        questionnaireConfig: [
          {
            question: "question-1",
            type: "transition",
            page: 1,
            index: 1,
            text: "<p>page one</p>",
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
            text: "<p>page two</p>",
            requirement_level: REQUIREMENT_LEVELS.NOT_REQUIRED,
            items: [],
            scale: [],
            options: {},
          },
        ],
        filterConfig: { "question-1": [], "question-2": [] },
        staticVariables: [],
        actionUrl,
        language: "en",
      },
    });

    await wrapper.find("#next-page-btn").trigger("click");
    await wait();

    expect(fetch).not.toHaveBeenCalled();
    expect(wrapper.find("[data-page-index='1']").element.style.display).toBe("none");
    expect(wrapper.find("[data-page-index='2']").element.style.display).not.toBe("none");
  });
});
