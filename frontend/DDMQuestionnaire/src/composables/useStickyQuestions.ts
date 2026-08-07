import { ref, reactive, onMounted, onUnmounted, nextTick, watch, type Ref } from 'vue'
import type { QuestionConfig } from '@questionnaire/types/questionnaire'

const STICKY_TOP_OFFSET = 12; // keep in sync with the CSS `top` value on .question-body.is-sticky .question-text
const STICKY_MAX_VIEWPORT_WIDTH = 768;
const STICKY_TYPES = ['matrix', 'semantic_diff'];

export function useStickyQuestions(
  questionMap: Record<string, QuestionConfig>,
  currentPage: Ref<number>,
  hideObjectDict: Ref<Record<string, boolean>>
) {
  const questionDivs = ref<(HTMLElement | null)[]>([]);
  const isSticky = reactive<Record<string, boolean>>({});

  function computeStickiness() {
    const viewportHeight = window.innerHeight - STICKY_TOP_OFFSET;
    const viewportTooWide = window.innerWidth > STICKY_MAX_VIEWPORT_WIDTH;

    questionDivs.value.forEach((el) => {
      if (!el) return;
      const qid = el.dataset.questionId;
      const question = qid ? questionMap[qid] : undefined;

      if (!question || !STICKY_TYPES.includes(question.type)) {
        if (qid) isSticky[qid] = false;
        return;
      }

      if (viewportTooWide) {
        const blockHeight = el.getBoundingClientRect().height;
        isSticky[qid] = blockHeight > viewportHeight;
      } else {
        isSticky[qid] = true;
      }
    });
  }

  onMounted(async () => {
    await nextTick();
    computeStickiness();
    window.addEventListener('resize', computeStickiness);
  });

  onUnmounted(() => {
    window.removeEventListener('resize', computeStickiness);
  });

  watch(currentPage, async () => {
    await nextTick();
    computeStickiness();
  });

  watch(hideObjectDict, async () => {
    await nextTick();
    computeStickiness();
  }, { deep: true });

  return { questionDivs, isSticky };
}
