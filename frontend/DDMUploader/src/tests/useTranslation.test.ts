import { defineComponent, h } from 'vue';
import { mount } from '@vue/test-utils';
import { createI18n } from 'vue-i18n';
import { describe, it, expect, beforeEach } from 'vitest';
import { useTranslation, setCustomTranslations } from '@uploader/composables/useTranslation';

const messages = {
  en: {
    greeting: 'Hello {name}',
    farewell: 'Goodbye',
    nested: { key: 'Nested {value}' },
  },
};

function mountWithTranslation() {
  const i18n = createI18n({ legacy: false, locale: 'en', fallbackLocale: 'en', messages });
  const Component = defineComponent({
    setup() {
      const { t, te } = useTranslation();
      return { t, te };
    },
    render() {
      return h('div');
    },
  });
  return mount(Component, { global: { plugins: [i18n] } });
}

describe('useTranslation', () => {
  beforeEach(() => {
    setCustomTranslations(undefined);
  });

  it('falls back to the base (precompiled) message when no custom override exists', () => {
    const wrapper = mountWithTranslation();
    expect(wrapper.vm.t('greeting', { name: 'Alice' })).toBe('Hello Alice');
    expect(wrapper.vm.t('farewell')).toBe('Goodbye');
  });

  it('uses a custom override and interpolates {param} placeholders itself when present', () => {
    setCustomTranslations({ en: { greeting: 'Hi there {name}!' } });
    const wrapper = mountWithTranslation();

    expect(wrapper.vm.t('greeting', { name: 'Bob' })).toBe('Hi there Bob!');
    // Keys without an override still fall through to the base message.
    expect(wrapper.vm.t('farewell')).toBe('Goodbye');
  });

  it('resolves nested dot-path keys in custom overrides', () => {
    setCustomTranslations({ en: { nested: { key: 'Custom {value}' } } });
    const wrapper = mountWithTranslation();

    expect(wrapper.vm.t('nested.key', { value: 42 })).toBe('Custom 42');
  });

  it('leaves an unmatched placeholder untouched instead of throwing', () => {
    setCustomTranslations({ en: { greeting: 'Hi {name}, from {unknownParam}' } });
    const wrapper = mountWithTranslation();

    expect(wrapper.vm.t('greeting', { name: 'Cara' })).toBe('Hi Cara, from {unknownParam}');
  });

  it('te() reports a key as existing if it has a custom override, even if absent from the base messages', () => {
    setCustomTranslations({ en: { 'brand-new-key': 'Something new' } });
    const wrapper = mountWithTranslation();

    expect(wrapper.vm.te('brand-new-key')).toBe(true);
    expect(wrapper.vm.te('does-not-exist-anywhere')).toBe(false);
    expect(wrapper.vm.te('farewell')).toBe(true);
  });
});
