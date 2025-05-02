import {ExtractionRule} from "@uploader/types/ExtractionRule";

export type Blueprint = {
  id: number;
  name: string;
  description: string;
  format: string;
  json_extraction_root: string;
  expected_fields: any[];
  exp_fields_regex_matching: boolean;
  fields_to_extract: any[];
  regex_path: string;
  csv_delimiter: string;
  extraction_rules: ExtractionRule[];
}
