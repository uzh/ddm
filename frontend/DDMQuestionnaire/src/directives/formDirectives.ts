import { Directive } from 'vue';

export const onlyDigits: Directive<HTMLInputElement> = {
  mounted(el) {
    el.addEventListener('input', () => {
      el.value = el.value.replace(/\D/g, '');
    });
  }
};

/**
 * Finds the hint element dedicated to one validation concern (e.g. email
 * format, length, value range) for a given input.
 *
 * Looked up by class within the input's parent element rather than via
 * `nextElementSibling`, so multiple validation directives can sit on the
 * same input without fighting over a single shared sibling.
 */
function findHint(el: HTMLElement, hintClass: string): HTMLElement | null {
  return el.parentElement?.querySelector(`:scope > .${hintClass}`) ?? null;
}

function toggleHint(hint: HTMLElement | null, isValid: boolean) {
  if (hint) {
    hint.style.display = isValid ? 'none' : 'block';
  }
}

export const validEmail: Directive<HTMLInputElement> = {
  mounted(el) {
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

    el.addEventListener('blur', () => {
      const isValid = emailRegex.test(el.value);
      el.classList.toggle('invalid-email', !isValid);
      toggleHint(findHint(el, 'hint-invalid-email'), isValid);
    });

    el.addEventListener('focus', () => {
      toggleHint(findHint(el, 'hint-invalid-email'), true);
    });
  }
};

/**
 * Validates a text-like input against min/max character length, toggling
 * an `.invalid-length` class on the input and its dedicated
 * `.hint-invalid-length` hint, following the same pattern as `validEmail`.
 *
 * Reads bounds from the element's own `minlength`/`maxlength` attributes
 * (set via Vue's `:minlength`/`:maxlength` bindings).
 */
export const validLength: Directive<HTMLInputElement> = {
  mounted(el) {
    function checkLength() {
      const min = el.minLength; // -1 if not set
      const max = el.maxLength; // -1 if not set
      const length = el.value.length;

      const isValid =
        (min < 0 || length >= min) &&
        (max < 0 || length <= max);

      el.classList.toggle('invalid-length', !isValid);
      toggleHint(findHint(el, 'hint-invalid-length'), isValid);
    }

    el.addEventListener('blur', checkLength);

    el.addEventListener('focus', () => {
      toggleHint(findHint(el, 'hint-invalid-length'), true);
    });
  }
};

/**
 * Validates a number input against min/max value, toggling an
 * `.invalid-value` class on the input and its dedicated
 * `.hint-invalid-value` hint, following the same pattern as `validEmail`.
 *
 * Reads bounds from the element's own `min`/`max` attributes (set via Vue's
 * `:min`/`:max` bindings).
 */
export const validValue: Directive<HTMLInputElement> = {
  mounted(el) {
    function checkValue() {
      const min = el.min !== '' ? Number(el.min) : null;
      const max = el.max !== '' ? Number(el.max) : null;

      // An empty field has no value to be out of range; leave it to
      // required-field validation instead.
      let isValid = true;
      if (el.value !== '') {
        const value = Number(el.value);
        isValid = (min === null || value >= min) && (max === null || value <= max);
      }

      el.classList.toggle('invalid-value', !isValid);
      toggleHint(findHint(el, 'hint-invalid-value'), isValid);
    }

    el.addEventListener('blur', checkValue);

    el.addEventListener('focus', () => {
      toggleHint(findHint(el, 'hint-invalid-value'), true);
    });
  }
};
