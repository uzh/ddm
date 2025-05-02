import {Blueprint} from "@uploader/types/Blueprint";
import {Instruction} from "@uploader/types/Instruction";

export type UploaderConfig = {
  uploader_id: number;
  upload_type: string;
  name: string;
  combined_consent: boolean;
  blueprints: Blueprint[];
  instructions: Instruction[];
}
