import type {ExtractionStates} from "@uploader/types/ExtractionStates";

export type BlueprintPostData = {
  consent: boolean,
  extractedData: any[],
  status: ExtractionStates
}

export type PostData = Record<number, BlueprintPostData>
