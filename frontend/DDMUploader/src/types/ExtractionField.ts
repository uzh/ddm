export type ExtractionField = {
  id: number;
  expected_name: string;
  match_regex: boolean;
  keep_in_donation: boolean;
  alias: string | null;
}
