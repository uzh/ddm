/**
 * Recursively finds the next visible `.question-app-container` element
 * that comes after the given DOM element.
 *
 * @param {HTMLElement} element - The starting DOM element to begin the search from.
 * @returns {HTMLElement|null} The next visible `.question-app-container` element,
 *                              or `null` if none is found.
 */
export function getNextQuestionBody(element) {
  let questionBody = element.closest('.question-app-container');
  let nextQuestionBody = questionBody.nextElementSibling;

  if (nextQuestionBody) {
    let isVisible = window.getComputedStyle(nextQuestionBody).display !== 'none';
    if (isVisible) {
      return nextQuestionBody;
    } else {
      return getNextQuestionBody(nextQuestionBody);
    }
  } else {
    return null;
  }
}

/**
 * Gets the height of the last `.question-text` element
 * that appears before (or inside) the `.question-body`
 * container that wraps the given element.
 *
 * @param {HTMLElement} el - The starting element to search upward from.
 * @returns {number|null} The height in pixels of the `.question-text` element,
 *                        or `null` if no `.question-body` container is found.
 */
export function getHeightOfLastQuestionTextBefore(el) {
  let questionBody = el.closest('.question-body');

  if (!questionBody) {
      return null;
  }
  const questionText = questionBody.querySelector('.question-text');
  return questionText ? questionText.offsetHeight : 0;
}

/**
 * Scrolls to the next visible response row or question block.
 *
 * If the current response row has a sibling, it scrolls to that.
 * If not, it scrolls to the next `.question-app-container` block.
 * If none are found, it scrolls to the bottom of the page.
 *
 * @param {Event} event - The triggering DOM event (e.g. from a key or button).
 */
export function scrollToNext(event) {
  const currentRow = event.target.closest('div.response-row');
  if (currentRow) {
    const nextRow = currentRow.nextElementSibling;
    if (nextRow) {
      const stickyHeight = getHeightOfLastQuestionTextBefore(currentRow);
      const nextRowTop = nextRow.getBoundingClientRect().top + window.scrollY;
      const adjustedPosition = nextRowTop - stickyHeight;
      window.scrollTo({ top: adjustedPosition, behavior: 'smooth' });

    } else if (nextRow === null) {
      // Scroll to next question if there is no next row.
      let nextQuestionBody = getNextQuestionBody(currentRow);
      if (nextQuestionBody) {
        const nextQuestionTop = nextQuestionBody.getBoundingClientRect().top + window.scrollY;
        window.scrollTo({ top: nextQuestionTop, behavior: 'smooth' });
      } else {
        window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
      }
    }
  }
}

/**
 * Adds 'main-scale-first' and 'main-scale-last' classes
 * to the first and last element with class 'main-scale'
 * in a container.
 * Needed to correctly style rounded borders of main scales.
 *
 * @param {string} containerSelector - a query selector for the container in which the scale is positioned.
 */
export function updateMainScaleClasses(containerSelector) {
  const containers = document.querySelectorAll(containerSelector);
  containers.forEach(container => {
    const mainScales = container.querySelectorAll('.main-scale');

    if (mainScales.length > 0) {
      // Remove old classes in case of re-renders
      mainScales.forEach(el => {
        el.classList.remove("main-scale-first", "main-scale-last");
      });

      // Add class to first .main-scale
      mainScales[0].classList.add("main-scale-first");

      // Add class to last .main-scale (if different from first)
      if (mainScales.length > 1) {
        mainScales[mainScales.length - 1].classList.add("main-scale-last");
      }
    }
  });
}

/**
 * Highlights the most visible `.response-row` element in the viewport by setting its opacity to `1`,
 * while dimming all others by setting their opacity to `0.3`.
 *
 * - If `this.shouldScroll` is false, all rows remain fully opaque.
 * - Visibility is determined based on the row's bounding rectangle and its position relative to
 *   the viewport and any sticky `.question-text` content.
 *
 * @param {boolean} shouldScroll - Whether scroll-based row highlighting should be applied.
 * @returns {void}
 */
export function updateMostVisibleRow(shouldScroll) {
  let responseRows = Array.from(document.querySelectorAll('.response-row'));
  let mostVisibleRow = null;
  let minDistance = Infinity;

  if (!shouldScroll) {
    responseRows.forEach(row => row.style.opacity = "1");
    return
  }

  responseRows.forEach(row => {
    let rect = row.getBoundingClientRect();
    let questionHeight = getHeightOfLastQuestionTextBefore(row)
    let distance = Math.abs(rect.top);

    // Check if row is visible in viewport
    if (rect.bottom > 0 && rect.top < window.innerHeight && rect.top >= (questionHeight * 0.25)) {
      if (distance < minDistance) {
        minDistance = distance;
        mostVisibleRow = row;
      }
    }
  });

  // Reset opacity for all rows
  responseRows.forEach(row => row.style.opacity = "0.3");

  // Set the most visible row to full opacity
  if (mostVisibleRow) {
    mostVisibleRow.style.opacity = "1";
  }
}