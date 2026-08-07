import { MISSING_VALUE } from '@questionnaire/constants/missings';
import type { QuestionnaireConfig, QuestionConfig, Responses } from '@questionnaire/types/questionnaire';

/**
 * Builds a mapping from each question ID to its associated item IDs.
 *
 * Iterates over the questionnaire configuration and creates a dictionary where
 * each key is a `question_id`, and the value is an array of `item_id`s belonging to that question.
 * If a question has no items, the value will be an empty array.
 *
 * @param questionnaireConfig - The full questionnaire structure containing questions and optional items.
 * @returns A map of question IDs to arrays of their corresponding item IDs.
 */
export function initializeQuestionItemMap(questionnaireConfig: QuestionnaireConfig): Record<string, string[]> {
 const questionItemMap: Record<string, string[]> = {};
 questionnaireConfig.forEach((q) => {
   questionItemMap[q.question] = q.items?.map((i) => i.id) ?? [];
 });
 return questionItemMap;
}

/**
 * Initializes the response object based on the received questionnaire configuration.
 *
 * Returns a flat map of response placeholders, with keys for both question IDs
 * and item IDs (if present). All values are initialized to the sentinel string '-99',
 * representing unanswered or uninitialized state.
 *
 * @param questionnaireConfig - The full questionnaire structure containing questions and items.
 * @returns A Record mapping each question and item ID to '-99'.
 */
export function initializeResponses(questionnaireConfig: QuestionnaireConfig): Responses {
 const responses: Responses = {};
 questionnaireConfig.forEach((q) => initializeQuestionResponse(q, responses));
 return responses;
}

function initializeQuestionResponse(q: QuestionConfig, responses: Responses): void {
 switch (q.type) {
   case 'single_choice':
     responses[q.question] = MISSING_VALUE;
     break;
   case 'transition':
     break;
   case 'open':
     if (q.options?.multi_item_response) {
       q.items?.forEach((i) => { responses[i.id] = MISSING_VALUE; });
     } else {
       responses[q.question] = MISSING_VALUE;
     }
     break;
   case 'multi_choice':
     q.items?.forEach((i) => { responses[i.id] = 0; });
     break;
   default:
     q.items?.forEach((i) => { responses[i.id] = MISSING_VALUE; });
 }
}
