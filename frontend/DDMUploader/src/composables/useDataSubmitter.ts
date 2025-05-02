import JSZip from "jszip";
import {ref, Ref} from "vue";
import {UploaderOutcome} from "@uploader/types/UploaderOutcome";
import {PostData} from "@uploader/types/PostData";

/**
 * Composable: useDataSubmitter
 *
 * Handles the preparation and submission of extracted blueprint data to the server.
 * Gathers data from all uploaders, compresses it into a ZIP file, and submits it
 * via a form POST request.
 *
 * Features:
 * - Collects data and consent information from all uploader outcomes
 * - Compresses data into a ZIP archive for efficient transfer
 * - Handles form submission and redirects
 *
 * @param uploaderOutcomes - Reactive reference to uploader outcomes containing extraction data
 * @param postUrl - Server endpoint URL for data submission
 *
 * @returns {Object} An object containing:
 *   - submitting: Reactive boolean indicating whether submission is in progress
 *   - submitDonation: Function to trigger the data submission process
 *
 * Usage:
 * ```
 * const { submitting, submitDonation } = useDataSubmitter(uploaderOutcomes, '/api/submit');
 *
 * // Show loading UI when submitting
 * watch(submitting, (value) => {
 *   showLoadingOverlay(value);
 * });
 *
 * // Trigger submission
 * submitDonation();
 * ```
 */
export function useDataSubmitter(
  uploaderOutcomes: Ref<Record<number, UploaderOutcome>>,
  postUrl: string
) {
  const submitting: Ref<boolean> = ref(false);

  /**
   * Gathers and formats data from all uploader outcomes for submission.
   *
   * Extracts data from each blueprint in each uploader, organizing it by
   * blueprint ID with associated consent and status information.
   * If consent for blueprint is false, extractedData is replaced with an empty array ([]).
   *
   * @returns A structured object mapping blueprint IDs to their data, consent, and status
   */
  function gatherPostData(): PostData {
    const postData: PostData = {};

    for (const uploader of Object.values(uploaderOutcomes.value)) {
      if (!uploader.extractionOutcome) continue;

      for (const blueprint of Object.values(uploader.extractionOutcome)) {
        let extractedData: any[] = [];
        if (uploader.consentMap[blueprint.blueprintId] === true) {
          extractedData = blueprint.extractedData;
        }

        postData[blueprint.blueprintId] = {
          consent: uploader.consentMap[blueprint.blueprintId],
          extractedData: extractedData,
          status: uploader.blueprintStates[blueprint.blueprintId].state
        }
      }
    }
    return postData;
  }

  /**
   * Creates a compressed ZIP file containing the provided data.
   *
   * @param data - The data to compress (will be JSON stringified)
   * @param filename - Name of the file within the ZIP archive
   * @returns A Blob containing the compressed ZIP file
   */
  async function createZip(data: PostData, filename: string): Promise<Blob> {
    const zip = new JSZip();
    zip.file(filename, JSON.stringify(data));

    return await zip.generateAsync({
      type: "blob",
      compression: "DEFLATE",
      compressionOptions: {level: 5}
    });
  }

  /**
   * Submits the gathered data to the server.
   *
   * This function:
   * 1. Sets the submitting state to true
   * 2. Gathers and formats the data from uploader outcomes
   * 3. Compresses the data into a ZIP file
   * 4. Appends the data to a form
   * 5. Submits the form to the server
   * 6. Handles redirects from the server response
   *
   * @returns A promise that resolves to true if submission was successful, false otherwise
   */
  async function submitDonation(): Promise<boolean> {
    // Show submission overlay.
    submitting.value = true;

    // Get data.
    const postData: PostData = gatherPostData();
    if (Object.keys(postData).length === 0) {
      console.warn("No data to submit");
      return false;
    }

    const dataBlob: Blob = await createZip(postData, "data_donation.json");

    // Add data to form.
    const formElement = document.getElementById("uploader-form") as HTMLFormElement | null;
    if (!formElement) {
      console.error("Form element not found");
      return false;
    }
    const formData = new FormData(formElement);
    formData.append("post_data", dataBlob);

    // Send data to server
    try {
      const response = await fetch(postUrl, {
        method: "POST",
        body: formData,
      });

      if (response.redirected) {
        window.location.href = response.url;
      }
      return true
    } catch (error) {
      console.error("Error during data submission to server:", error);
    } finally {
      submitting.value = false;
    }
  }

  return {
    submitting,
    submitDonation
  }
}
