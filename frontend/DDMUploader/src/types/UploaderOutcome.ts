import type {BlueprintExtractionStates, ExtractionStates} from "@uploader/types/ExtractionStates";
import {BlueprintExtractionOutcome} from "@uploader/classes/BlueprintExtractionOutcome";

export type UploaderOutcome = {
  uploaderName: string;
  blueprintNames: Record<number, string>;
  consentMap: Record<number, boolean>,
  uploaderState: ExtractionStates,
  blueprintStates: BlueprintExtractionStates,
  extractionOutcome: Record<number, BlueprintExtractionOutcome>,
}