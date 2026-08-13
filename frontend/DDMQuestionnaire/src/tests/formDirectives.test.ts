import { defineComponent } from "vue";
import { mount } from "@vue/test-utils";
import { describe, it, expect } from "vitest";

import { validEmail, validLength, validValue } from "@questionnaire/directives/formDirectives";

function hintDisplay(wrapper: ReturnType<typeof mount>, hintClass: string): string {
  return wrapper.find(`.${hintClass}`).classes().includes("show") ? "block" : "none";
}

function mountLengthInput(attrs: string) {
  const Component = defineComponent({
    directives: { validLength },
    template: `
      <div>
        <input v-valid-length type="text" ${attrs} />
        <p class="hint-invalid-input hint-invalid-length"></p>
      </div>
    `,
  });
  return mount(Component);
}

function mountValueInput(attrs: string) {
  const Component = defineComponent({
    directives: { validValue },
    template: `
      <div>
        <input v-valid-value type="text" ${attrs} />
        <p class="hint-invalid-input hint-invalid-value"></p>
      </div>
    `,
  });
  return mount(Component);
}

describe("validLength directive", () => {
  it("flags a too-short value on blur", async () => {
    const wrapper = mountLengthInput('minlength="5"');
    const input = wrapper.find("input");
    await input.setValue("ab");
    await input.trigger("blur");

    expect(input.classes()).toContain("invalid-length");
    expect(hintDisplay(wrapper, "hint-invalid-length")).toBe("block");
  });

  it("flags a too-long value on blur", async () => {
    const wrapper = mountLengthInput('maxlength="3"');
    const input = wrapper.find("input");
    await input.setValue("abcd");
    await input.trigger("blur");

    expect(input.classes()).toContain("invalid-length");
    expect(hintDisplay(wrapper, "hint-invalid-length")).toBe("block");
  });

  it("accepts a value within bounds", async () => {
    const wrapper = mountLengthInput('minlength="2" maxlength="5"');
    const input = wrapper.find("input");
    await input.setValue("abc");
    await input.trigger("blur");

    expect(input.classes()).not.toContain("invalid-length");
    expect(hintDisplay(wrapper, "hint-invalid-length")).toBe("none");
  });

  it("re-hides the hint on focus", async () => {
    const wrapper = mountLengthInput('minlength="5"');
    const input = wrapper.find("input");
    await input.setValue("ab");
    await input.trigger("blur");
    expect(hintDisplay(wrapper, "hint-invalid-length")).toBe("block");

    await input.trigger("focus");
    expect(hintDisplay(wrapper, "hint-invalid-length")).toBe("none");
  });
});

describe("validValue directive", () => {
  it("flags a below-minimum value on blur", async () => {
    const wrapper = mountValueInput('min="5" max="10"');
    const input = wrapper.find("input");
    await input.setValue("2");
    await input.trigger("blur");

    expect(input.classes()).toContain("invalid-value");
    expect(hintDisplay(wrapper, "hint-invalid-value")).toBe("block");
  });

  it("flags an above-maximum value on blur", async () => {
    const wrapper = mountValueInput('min="5" max="10"');
    const input = wrapper.find("input");
    await input.setValue("99");
    await input.trigger("blur");

    expect(input.classes()).toContain("invalid-value");
    expect(hintDisplay(wrapper, "hint-invalid-value")).toBe("block");
  });

  it("accepts a value within bounds", async () => {
    const wrapper = mountValueInput('min="5" max="10"');
    const input = wrapper.find("input");
    await input.setValue("7");
    await input.trigger("blur");

    expect(input.classes()).not.toContain("invalid-value");
    expect(hintDisplay(wrapper, "hint-invalid-value")).toBe("none");
  });

  it("does not flag an empty value", async () => {
    const wrapper = mountValueInput('min="5" max="10"');
    const input = wrapper.find("input");
    await input.setValue("");
    await input.trigger("blur");

    expect(input.classes()).not.toContain("invalid-value");
    expect(hintDisplay(wrapper, "hint-invalid-value")).toBe("none");
  });

  it("works on a type=text input, since the browser's range validity does not apply there", async () => {
    const wrapper = mountValueInput('min="5" max="10"');
    const input = wrapper.find("input");
    expect(input.element.type).toBe("text");

    await input.setValue("2");
    await input.trigger("blur");
    expect(input.classes()).toContain("invalid-value");
  });
});

describe("validLength and validEmail on the same input", () => {
  function mountEmailInput(attrs: string) {
    const Component = defineComponent({
      directives: { validEmail, validLength },
      template: `
        <div>
          <input v-valid-email v-valid-length type="email" ${attrs} />
          <p class="hint-invalid-input hint-invalid-email"></p>
          <p class="hint-invalid-input hint-invalid-length"></p>
        </div>
      `,
    });
    return mount(Component);
  }

  it("only shows the length hint when just the length check fails", async () => {
    const wrapper = mountEmailInput('minlength="10"');
    const input = wrapper.find("input");
    await input.setValue("a@b.co"); // valid email format, too short
    await input.trigger("blur");

    expect(input.classes()).not.toContain("invalid-email");
    expect(hintDisplay(wrapper, "hint-invalid-email")).toBe("none");
    expect(input.classes()).toContain("invalid-length");
    expect(hintDisplay(wrapper, "hint-invalid-length")).toBe("block");
  });

  it("only shows the email hint when just the format check fails", async () => {
    const wrapper = mountEmailInput('minlength="3"');
    const input = wrapper.find("input");
    await input.setValue("not-an-email"); // long enough, invalid format
    await input.trigger("blur");

    expect(input.classes()).toContain("invalid-email");
    expect(hintDisplay(wrapper, "hint-invalid-email")).toBe("block");
    expect(input.classes()).not.toContain("invalid-length");
    expect(hintDisplay(wrapper, "hint-invalid-length")).toBe("none");
  });
});
