from typing import Annotated, Literal

from pydantic import BaseModel, Field, TypeAdapter


class JSONParserConfig(BaseModel):
    format: Literal["json"] = "json"
    extraction_root: str = ""
    nested_loop_path: str = ""
    array_join_separator: str = "\n"


class CSVParserConfig(BaseModel):
    format: Literal["csv"] = "csv"
    delimiter: str = ""


class TXTParserConfig(BaseModel):
    format: Literal["txt"] = "txt"
    record_separator: str = "\n\n"
    field_separator: str = "\n"
    kv_separator: str = ":"
    skip_header_lines: int = 0
    skip_footer_lines: int = 0
    ignore_blank_lines: bool = True
    trim_whitespace: bool = True


FileParserConfig = Annotated[
    CSVParserConfig | JSONParserConfig | TXTParserConfig, Field(discriminator="format")
]
FileParserConfigAdapter = TypeAdapter(FileParserConfig)
