import { EntryGroup } from "@uploader/utils/entryGroup";

export interface ExtractionFieldLayout {
  isGrouped: boolean;
  groups: EntryGroup[];
  rootFieldKeys: string[];
  nestedColumns: Map<string, string>;
}
