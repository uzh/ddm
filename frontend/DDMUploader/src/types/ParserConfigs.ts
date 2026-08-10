export type JSONParserConfig = {
  format: "json";
  extraction_root: string;
  nested_loop_path: string;
  array_join_separator: string;
}

export type CSVParserConfig = {
  format: "csv";
  delimiter: string;
}

export type TXTParserConfig = {
  format: "txt";
  record_separator: string;
  field_separator: string;
  kv_separator: string;
  skip_header_lines: number;
  skip_footer_lines: number;
  ignore_blank_lines: boolean;
  trim_whitespace: boolean;
}
