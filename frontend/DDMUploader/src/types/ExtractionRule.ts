export type ExtractionRule = {
  id: number;
  field: string;
  comparison_operator: string | null;
  comparison_value: string | null;
  replacement_value: string | null;
}
