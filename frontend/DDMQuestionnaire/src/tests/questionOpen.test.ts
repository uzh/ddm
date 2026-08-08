import { mount } from "@vue/test-utils";
import { describe, it, expect } from "vitest";
import { i18n } from "@questionnaire/tests/testUtils";

import { onlyDigits, validEmail, validLength, validValue } from "@questionnaire/directives/formDirectives";
import { MISSING_VALUE } from "@questionnaire/constants/missings";
import QuestionOpen from "@questionnaire/components/questions/QuestionOpen.vue";

const directives = {
  "only-digits": onlyDigits,
  "valid-email": validEmail,
  "valid-length": validLength,
  "valid-value": validValue,
};

function mountQuestion(props: Record<string, unknown>) {
  return mount(QuestionOpen, {
    global: { plugins: [i18n], directives },
    props: {
      qid: "question-1",
      text: "Some question",
      items: [],
      hideObjectDict: {},
      responses: {},
      ...props,
    },
  });
}

function descriptiveHint(wrapper: ReturnType<typeof mountQuestion>) {
  return wrapper.find("p.input-hint:not(.hint-invalid-input)");
}

// For numbers-type questions, the generic "only numbers allowed" hint and
// the min/max value hint are both plain `.input-hint` paragraphs; the value
// hint is always rendered last.
function lastDescriptiveHint(wrapper: ReturnType<typeof mountQuestion>) {
  const hints = wrapper.findAll("p.input-hint:not(.hint-invalid-input)");
  return hints[hints.length - 1];
}

describe("QuestionOpen length hints (text input)", () => {
  it("shows only the min-length hint when only a minimum is configured", () => {
    const wrapper = mountQuestion({
      options: { input_type: "text", display: "small", min_input_length: 5, max_input_length: null },
      responses: { "question-1": MISSING_VALUE },
    });
    expect(descriptiveHint(wrapper).text()).toBe("The input must be at least 5 characters long.");
  });

  it("shows only the max-length hint when only a maximum is configured", () => {
    const wrapper = mountQuestion({
      options: { input_type: "text", display: "small", min_input_length: null, max_input_length: 8 },
      responses: { "question-1": MISSING_VALUE },
    });
    expect(descriptiveHint(wrapper).text()).toBe("The input cannot exceed 8 characters.");
  });

  it("shows the combined hint when both bounds are configured", () => {
    const wrapper = mountQuestion({
      options: { input_type: "text", display: "small", min_input_length: 5, max_input_length: 8 },
      responses: { "question-1": MISSING_VALUE },
    });
    expect(descriptiveHint(wrapper).text()).toBe("The input must be between 5 and 8 characters long.");
  });

  it("renders no descriptive hint when neither bound is configured", () => {
    const wrapper = mountQuestion({
      options: { input_type: "text", display: "small", min_input_length: null, max_input_length: null },
      responses: { "question-1": MISSING_VALUE },
    });
    expect(descriptiveHint(wrapper).exists()).toBe(false);
  });

  it("binds minlength/maxlength attributes from options", () => {
    const wrapper = mountQuestion({
      options: { input_type: "text", display: "small", min_input_length: 5, max_input_length: null },
      responses: { "question-1": MISSING_VALUE },
    });
    const input = wrapper.find("input");
    expect(input.attributes("minlength")).toBe("5");
    expect(input.attributes("maxlength")).toBeUndefined();
  });
});

describe("QuestionOpen value hints (numbers input)", () => {
  it("shows the combined value hint and binds min/max attributes", () => {
    const wrapper = mountQuestion({
      options: { input_type: "numbers", display: "small", min_number_value: 1, max_number_value: 10 },
      responses: { "question-1": MISSING_VALUE },
    });
    expect(lastDescriptiveHint(wrapper).text()).toBe("The input must be between 1 and 10.");

    const input = wrapper.find("input");
    expect(input.attributes("min")).toBe("1");
    expect(input.attributes("max")).toBe("10");
  });
});

describe("QuestionOpen multi-item mode", () => {
  it("keeps invalid-length state scoped to the specific item", async () => {
    const wrapper = mountQuestion({
      options: {
        input_type: "text",
        display: "small",
        multi_item_response: true,
        min_input_length: 5,
      },
      items: [
        { id: "item-1", value: 1, label: "Item 1" },
        { id: "item-2", value: 2, label: "Item 2" },
      ],
      hideObjectDict: { "item-1": false, "item-2": false },
      responses: { "item-1": MISSING_VALUE, "item-2": MISSING_VALUE },
    });

    const item1Input = wrapper.find('[name="item-1"]');
    const item2Input = wrapper.find('[name="item-2"]');

    await item1Input.setValue("ab"); // too short
    await item1Input.trigger("blur");
    await item2Input.setValue("abcdef"); // valid length
    await item2Input.trigger("blur");

    expect(item1Input.classes()).toContain("invalid-length");
    expect(item2Input.classes()).not.toContain("invalid-length");
  });
});
