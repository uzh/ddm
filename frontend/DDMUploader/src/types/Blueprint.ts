import {ExtractionRule} from "@uploader/types/ExtractionRule";
import {BlueprintFilePath} from "@uploader/types/BlueprintFilePath";

export type Blueprint = {
  id: number;
  name: string;
  description: string;
  format: string;
  json_extraction_root: string;
  expected_fields: any[];
  exp_fields_regex_matching: boolean;
  fields_to_extract: any[];
  file_paths: BlueprintFilePath[];
  csv_delimiter: string;
  extraction_rules: ExtractionRule[];
}
