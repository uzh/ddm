import { EXTRACTION_STATES } from "@uploader/utils/stateCatalog";

export type ExtractionStates = typeof EXTRACTION_STATES[keyof typeof EXTRACTION_STATES];

export type BlueprintDetailState = {
  state: ExtractionStates,
  i18nState: string,
  errorsToDisplay: any[],
}

export type BlueprintExtractionStates = Record<number, BlueprintDetailState>;
