import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import { createI18n } from 'vue-i18n';
import ConsentQuestion from '@uploader/components/ConsentQuestion.vue';
import en from '@uploader/locales/en.json';

const i18n = createI18n({
  legacy: false,
  locale: 'en',
  fallbackLocale: 'en',
  messages: { en },
});

function mountCombined(componentId: number) {
  return mount(ConsentQuestion, {
    global: { plugins: [i18n] },
    props: {
      combinedConsent: true,
      blueprint: null,
      blueprintId: null,
      componentId,
    },
  });
}

describe('ConsentQuestion', () => {
  it('two combined-consent instances for different Uploaders get different ids/names', () => {
    const first = mountCombined(1);
    const second = mountCombined(2);

    const firstAgreeInput = first.find('input[type="radio"]');
    const secondAgreeInput = second.find('input[type="radio"]');

    expect(firstAgreeInput.attributes('id')).not.toBe(secondAgreeInput.attributes('id'));
    expect(firstAgreeInput.attributes('name')).not.toBe(secondAgreeInput.attributes('name'));
    expect(firstAgreeInput.attributes('id')).toBe('donate-agree-combined-1');
    expect(secondAgreeInput.attributes('id')).toBe('donate-agree-combined-2');
  });

  it('label click actually activates its own input (not the other Uploader\'s)', () => {
    const first = mountCombined(1);
    const second = mountCombined(2);

    const secondAgreeLabel = second.find('label');
    expect(secondAgreeLabel.attributes('for')).toBe(second.find('input[type="radio"]').attributes('id'));
    // The two instances' label/input pairs never share an id, so a browser
    // can't route instance 2's label click to instance 1's input.
    expect(secondAgreeLabel.attributes('for')).not.toBe(first.find('input[type="radio"]').attributes('id'));
  });

  it('individual consent (real blueprintId) is unaffected by the componentId fallback', () => {
    const wrapper = mount(ConsentQuestion, {
      global: { plugins: [i18n] },
      props: {
        combinedConsent: false,
        blueprint: null,
        blueprintId: 42,
        componentId: 7,
      },
    });

    const agreeInput = wrapper.find('input[type="radio"]');
    expect(agreeInput.attributes('id')).toBe('donate-agree-42');
  });
});
