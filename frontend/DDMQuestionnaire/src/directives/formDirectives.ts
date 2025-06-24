import { Directive } from 'vue';

export const onlyDigits: Directive<HTMLInputElement> = {
  mounted(el) {
    el.addEventListener('input', () => {
      el.value = el.value.replace(/\D/g, '');
    });
  }
};

export const validEmail: Directive<HTMLInputElement> = {
  mounted(el) {
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$/;

    el.addEventListener('blur', () => {
      const hint = el.nextElementSibling;
      const isValid = emailRegex.test(el.value);

      if (hint instanceof HTMLElement) {
        el.classList.toggle('invalid-email', !isValid);
        if (hint?.classList.contains('hint-invalid-input')) {
          hint.style.display = isValid ? 'none' : 'block';
        }
      }
    });

    el.addEventListener('focus', () => {
      const hint = el.nextElementSibling;

      if (hint instanceof HTMLElement) {
        if (hint?.classList.contains('hint-invalid-input')) {
          hint.style.display = 'none';
        }
      }
    });
  }
};
