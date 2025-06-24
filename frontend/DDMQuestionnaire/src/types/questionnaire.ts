// A single selectable or input item in a question.
export interface Item {
  id: string;  // Must be of form 'item-<unique-item-id>'
  value: number;
  label: string;
  label_alt?: string;
}

// A scale point used in matrix questions or semantic differentials.
export interface ScalePoint {
  value: number;
  input_label: string;
  heading_label?: string;
  secondary_point?: boolean;
}

// Options that affect how a question is rendered.
export interface QuestionOptions {
  input_type?: 'text' | 'numbers' | 'email';
  display?: 'small' | 'large';
  max_input_length?: number | null;
  multi_item_response?: boolean;
  show_scale_headings?: boolean;
}

// The configuration for one particular question.
export interface QuestionConfig {
  question: string;  // Must be of form 'question-<unique-question-id>'
  page: number;
  type: string;
  text: string;
  required?: boolean;
  items?: Item[];
  scale?: ScalePoint[];
  options?: QuestionOptions;
}

// The entire parsed questionnaire config.
export type QuestionnaireConfig = QuestionConfig[];

// A single rule within the filter logic.
export interface FilterCondition {
  source: string;
  condition_value: any;
  condition_operator: string;
  combinator: 'AND' | 'OR';
}

// The entire parsed filter config. The key must be "question-<question_id>" or "item-<item_id>".
export type FilterConfig = Record<string, FilterCondition[]>;

// An array holding the recorded responses. The key must be "question-<question_id>" or "item-<item_id>".
export type Responses = Record<string, string | number>;


export interface ResponseEvent {
  id: string;
  response: any;
  question: string;
  items?: any[];
}
