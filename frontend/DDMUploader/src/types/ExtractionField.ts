export const EXTRACTION_FIELD_SCOPES = {
  ROOT: 'root',
  NESTED: 'warn',
}

export type ExtractionFieldScope = typeof EXTRACTION_FIELD_SCOPES[keyof typeof EXTRACTION_FIELD_SCOPES];

export type ExtractionField = {
  id: number;
  scope: ExtractionFieldScope;
  expected_name: string;
  match_regex: boolean;
  keep_in_donation: boolean;
  alias: string | null;
}
