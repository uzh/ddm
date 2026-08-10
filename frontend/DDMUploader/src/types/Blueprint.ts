import {ExtractionRule} from "@uploader/types/ExtractionRule";
import {BlueprintFilePath} from "@uploader/types/BlueprintFilePath";
import {ExtractionField} from "@uploader/types/ExtractionField";
import {CSVParserConfig, JSONParserConfig, TXTParserConfig} from "@uploader/types/ParserConfigs";

export type Blueprint = {
  id: number;
  name: string;
  description: string;
  format: string;
  expected_fields: string[];
  exp_fields_regex_matching: boolean;
  nested_expected_fields: string[];
  nested_exp_fields_regex_matching: boolean;
  fields_to_extract: string[];
  extraction_fields: ExtractionField[];
  file_paths: BlueprintFilePath[];
  parser_config: JSONParserConfig | CSVParserConfig | TXTParserConfig;
  extraction_rules: ExtractionRule[];
  is_backup: boolean;
  backup_ids: number[];
}
