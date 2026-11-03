import { defineComponent, h } from "vue";
import { mount } from "@vue/test-utils";
import { describe, it, expect, vi } from "vitest";

import { useScrollHandler } from "@questionnaire/composables/useScrollHandler";

describe("useScrollHandler", () => {
  it("removes the exact 'resize' listener it registered, on unmount", () => {
    const addSpy = vi.spyOn(window, "addEventListener");
    const removeSpy = vi.spyOn(window, "removeEventListener");

    const TestComponent = defineComponent({
      setup() {
        useScrollHandler();
        return () => h("div");
      },
    });
    const wrapper = mount(TestComponent);

    const registeredHandler = addSpy.mock.calls.find(
      ([type]) => type === "resize"
    )?.[1];
    expect(registeredHandler).toBeDefined();

    wrapper.unmount();

    const removedHandler = removeSpy.mock.calls.find(
      ([type]) => type === "resize"
    )?.[1];
    expect(removedHandler).toBe(registeredHandler);

    addSpy.mockRestore();
    removeSpy.mockRestore();
  });
});
