export type ExtractionRule = {
  id: number;
  field: string;
  regex_field: boolean;
  comparison_operator: string | null;
  comparison_value: string | null;
  replacement_value: string | null;
}
