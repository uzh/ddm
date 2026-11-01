import { mount } from "@vue/test-utils";
import { describe, it, expect, beforeAll, beforeEach, vi } from "vitest";
import { i18n } from "@questionnaire/tests/testUtils";
import { REQUIREMENT_LEVELS } from "@questionnaire/types/questionnaire";

import QuestionnaireApp from "../components/QuestionnaireApp.vue";

const wait = () => new Promise(resolve => setTimeout(resolve, 1000));

// jsdom doesn't implement scrollIntoView or full navigation.
Element.prototype.scrollIntoView = vi.fn();

const actionUrl = "https://some.url/questionnaire/";
const participantId = "participant-aaa";
const cacheKey = `questionnaire-responses:${participantId}`;

const questionnaireConfig = [
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
];

function mountApp() {
  return mount(QuestionnaireApp, {
    global: { plugins: [i18n] },
    props: {
      questionnaireConfig,
      filterConfig: { "question-1": [] },
      staticVariables: [],
      actionUrl,
      language: "en",
      participantId,
    },
  });
}

describe("final questionnaire submission: cache clearing and retry", () => {
  beforeAll(() => {
    document.documentElement.scrollTo = vi.fn();
  });

  beforeEach(() => {
    localStorage.clear();
  });

  // Seeds the persisted response cache *after* mount (component-initiated
  // loads already happened), so we can tell whether submitData() cleared it.
  function seedCache() {
    localStorage.setItem(cacheKey, JSON.stringify({
      version: "irrelevant-for-this-test",
      expiresAt: Date.now() + 1000,
      value: { "question-1": "some response" },
    }));
  }

  it("clears the local cache once the backend confirms a successful submission", async () => {
    vi.stubGlobal("fetch", vi.fn(() =>
      Promise.resolve({ redirected: true, url: "https://some.url/debriefing/", status: 200 })
    ));

    const wrapper = mountApp();
    seedCache();
    await wrapper.find("#next-page-btn").trigger("click");
    await wait();

    expect(fetch).toHaveBeenCalledTimes(1);
    expect(localStorage.getItem(cacheKey)).toBeNull();
  });

  it("does not clear the local cache and shows a retry hint when the submission fails", async () => {
    vi.stubGlobal("fetch", vi.fn(() => Promise.reject(new Error("network error"))));

    const wrapper = mountApp();
    seedCache();
    await wrapper.find("#next-page-btn").trigger("click");
    await wait();

    expect(fetch).toHaveBeenCalledTimes(1);
    expect(localStorage.getItem(cacheKey)).not.toBeNull();
    expect(wrapper.find("#submit-failed-hint").exists()).toBe(true);
  });

  it("does not clear the local cache when the backend responds without confirming the submission", async () => {
    vi.stubGlobal("fetch", vi.fn(() =>
      Promise.resolve({ redirected: false, url: actionUrl, status: 500 })
    ));

    const wrapper = mountApp();
    seedCache();
    await wrapper.find("#next-page-btn").trigger("click");
    await wait();

    expect(fetch).toHaveBeenCalledTimes(1);
    expect(localStorage.getItem(cacheKey)).not.toBeNull();
    expect(wrapper.find("#submit-failed-hint").exists()).toBe(true);
  });

  it("allows retrying after a failed submission, and clears the cache once the retry succeeds", async () => {
    const fetchMock = vi.fn()
      .mockImplementationOnce(() => Promise.reject(new Error("network error")))
      .mockImplementationOnce(() => Promise.resolve({
        redirected: true, url: "https://some.url/debriefing/", status: 200,
      }));
    vi.stubGlobal("fetch", fetchMock);

    const wrapper = mountApp();
    seedCache();

    await wrapper.find("#next-page-btn").trigger("click");
    await wait();
    expect(fetch).toHaveBeenCalledTimes(1);
    expect(localStorage.getItem(cacheKey)).not.toBeNull();

    // Retry via the same button.
    await wrapper.find("#next-page-btn").trigger("click");
    await wait();

    expect(fetch).toHaveBeenCalledTimes(2);
    expect(localStorage.getItem(cacheKey)).toBeNull();
  });
});
