/**
 * Recursively finds the next visible `.question-app-container` element
 * that comes after the given DOM element.
 *
 * @param element - The starting DOM element to begin the search from.
 * @returns The next visible `.question-app-container` element, or `null` if none is found.
 */
function getNextQuestionBody(element: HTMLElement): HTMLElement | null {
  const questionBody = element.closest('.question-app-container') as HTMLElement | null;
  const nextQuestionBody = questionBody?.nextElementSibling as HTMLElement | null;

  if (nextQuestionBody) {
    const isVisible = window.getComputedStyle(nextQuestionBody).display !== 'none';
    return isVisible ? nextQuestionBody : getNextQuestionBody(nextQuestionBody);
  }

  return null;
}

/**
 * Gets the height of the last `.question-text` element
 * that appears before (or inside) the `.question-body` container that wraps the given element.
 *
 * @param el - The starting element to search upward from.
 * @returns The height in pixels of the `.question-text` element, or `0` if not found.
 */
export function getHeightOfLastQuestionTextBefore(el: HTMLElement): number {
  const questionBody = el.closest('.question-body');
  if (!questionBody) return 0;

  const questionText = questionBody.querySelector('.question-text') as HTMLElement | null;
  return questionText ? questionText.offsetHeight : 0;
}

/**
 * Scrolls to the next visible response row or question block.
 *
 * If the current response row has a sibling, it scrolls to that.
 * If not, it scrolls to the next `.question-app-container` block.
 * If none are found, it scrolls to the bottom of the page.
 *
 * @param event - The triggering DOM event (e.g. from a key or button).
 */
export function scrollToNext(event: Event): void {
  const currentRow = (event.target as HTMLElement).closest('div.response-row') as HTMLElement | null;

  if (!currentRow) return;

  const nextRow = currentRow.nextElementSibling as HTMLElement | null;

  if (nextRow) {
    const stickyHeight = getHeightOfLastQuestionTextBefore(currentRow);
    const nextRowTop = nextRow.getBoundingClientRect().top + window.scrollY;
    const adjustedPosition = nextRowTop - stickyHeight;
    window.scrollTo({ top: adjustedPosition, behavior: 'smooth' });
  } else {
    const nextQuestionBody = getNextQuestionBody(currentRow);
    if (nextQuestionBody) {
      const nextQuestionTop = nextQuestionBody.getBoundingClientRect().top + window.scrollY;
      window.scrollTo({ top: nextQuestionTop, behavior: 'smooth' });
    } else {
      window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
    }
  }
}

/**
 * Adds 'main-scale-first' and 'main-scale-last' classes
 * to the first and last element with class 'main-scale' in a container.
 *
 * @param containerSelector - A query selector for the container in which the scale is positioned.
 */
export function updateMainScaleClasses(containerSelector: string): void {
  const containers = document.querySelectorAll<HTMLElement>(containerSelector);
  containers.forEach(container => {
    const mainScales = container.querySelectorAll<HTMLElement>('.main-scale');

    mainScales.forEach(el => el.classList.remove("main-scale-first", "main-scale-last"));

    if (mainScales.length > 0) {
      mainScales[0].classList.add("main-scale-first");
      if (mainScales.length > 1) {
        mainScales[mainScales.length - 1].classList.add("main-scale-last");
      }
    }
  });
}
