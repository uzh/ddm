<i18n src="../translations/file_uploader.json"></i18n>

<template>

  <div class="mb-5">
    <div class="float-left pt-2 ps-2 rounded-top">
      <div class="col-sm">
        <h4 class="fw-bold">{{ name }}</h4>
      </div>
    </div>

    <div class="uploader-container">
    <!-- INSTRUCTIONS -->
    <div v-if="instructions.length" class="accordion" :id="'ul-acc-'+componentId">
      <div class="accordion-body border-bottom">
        <div class="row align-items-center">
          <div class="col-auto ul-status-icon"><i class="bi bi-signpost"></i></div>
          <div class="col-auto"><h5>{{ $t('instructions') }}</h5></div>
          <div class="col accordion-header" :id="'acc-instr-head-'+componentId">
            <button class="accordion-button" type="button" data-bs-toggle="collapse" :data-bs-target="'#acc-instr-body-'+componentId" aria-expanded="true" :aria-controls="'acc-instr-body-'+componentId">
            </button>
          </div>
        </div>

        <div :id="'acc-instr-body-'+componentId" class="accordion-collapse collapse show" aria-labelledby="headingOne" :data-bs-parent="'#ul-acc-'+componentId">
          <div class="accordion-body ps-0 pe-0">
            <DonationInstructions :instructions="instructions" :component-id="componentId"></DonationInstructions>
          </div>
        </div>

      </div>
    </div>

    <!-- DATA UPLOAD -->
    <div class="accordion-body border-bottom">
      <div class="row align-items-center" style="height: 100px;">

        <!-- Upload pending -->
        <template v-if="uploadStatus === 'pending'">
          <div class="col-auto ul-status-icon"><i class="bi bi-upload"></i></div>

          <div class="col-auto ul-status-description">
            <h5 v-if="!uploadAttempts">{{ $t('upload-file') }}:</h5>
            <p v-else-if="uploadAttempts">{{ $t('upload-different-file') }}:</p>
          </div>

          <div class="col ul-status-message">
            <label class="select-file-btn">

              <input v-if="expectsZip"
                     :name="'ul-' + componentId"
                     accept=".zip,application/zip,application/x-zip-compressed,multipart/x-zip"
                     type="file"
                     @change="processFile"
                     class="d-none">
              <input v-else-if="blueprints[0].format === 'json'"
                     :name="'ul-' + componentId"
                     accept=".json,application/json"
                     type="file"
                     @change="processFile"
                     class="d-none">
              <input v-else-if="blueprints[0].format === 'csv'"
                     :name="'ul-' + componentId"
                     accept=".csv,text/csv"
                     type="file"
                     @change="processFile"
                     class="d-none">

              {{ $t('choose-file') }}
            </label>
          </div>
        </template>

        <!-- Upload in progress -->
        <template v-else-if="uploadStatus === 'processing'">
          <div class="col-auto ul-status-icon">
            <div class="clearfix">
              <p><span class="spinner-border float-right me-3" role="status"><span class="sr-only"></span></span></p>
            </div>
          </div>

          <div class="col ul-status-description">
            <p>{{ $t('file-is-being-uploaded') }}</p>
          </div>

          <div class="col ul-status-message"></div>
        </template>

        <!-- Upload successful -->
        <template v-else-if="uploadStatus === 'success'">
          <div class="col-auto ul-status-icon"><i class="bi bi-file-check"></i></div>

          <div class="col ul-status-description">
            <h5 class="text-success fw-bold">{{ $t('upload-success') }}</h5>
          </div>
        </template>

        <!-- Upload partial -->
        <template v-else-if="uploadStatus === 'partial'">
          <div class="col-auto ul-status-icon"><i class="bi bi-exclamation-diamond text-orange"></i></div>

          <div class="col-auto ul-status-description">
            <p class="fw-bold">{{ $t('partial-upload-status') }}</p>
            <p><a @click="uploadStatus = 'pending'" class="upload-other">{{ $t('choose-different-file') }}</a></p>
          </div>

          <div class="col ul-status-message">
            <p>{{ $t('partial-upload-message') }}</p>
          </div>
        </template>

        <!-- Upload failed -->
        <template v-else-if="uploadStatus === 'failed'">
          <div class="col-auto ul-status-icon"><i class="bi bi-x-octagon text-danger"></i></div>

          <div class="col-auto ul-status-description">
            <p class="fw-bold">{{ $t('upload-failed') }}</p>
            <p><a @click="uploadStatus = 'pending'" class="upload-other">{{ $t('choose-different-file') }}</a></p>
          </div>

          <div class="col ul-status-message">
            <ul class="text-danger">
              <li v-for="error in generalErrors" :key="error">{{ error }}</li>
            </ul>
          </div>
        </template>

      </div>
      </div>
      <!-- UPLOAD FEEDBACK -->

      <div class="accordion-body">
        <div class="row align-items-center">
          <div class="col extraction-information-container">
            <div class="col">
              <template v-if="uploadStatus === 'pending'">
                <h6>{{ $t('data-extraction-intro') }}</h6>
              </template>
              <template v-else>
                <h6 class="fw-bold">{{ $t('extracted-data-intro') }}</h6>
              </template>
            </div>
          </div>
        </div>
      </div>

      <div class="accordion-body">
      <div class="container ul-feedback-container ps-2 pe-2">
        <div class="row">
          <div class="col extraction-information-container">
            <template v-for="bp in blueprints" :key="bp">
            <div class="ul-status row align-items-start pt-2 pb-2"
                 :class="{ 'ul-success': blueprintData[bp.id.toString()].status === 'success', 'ul-failed': blueprintData[bp.id.toString()].status === 'failed'}">

              <!-- Pending -->
              <template v-if="blueprintData[bp.id.toString()].status === 'pending'">
                <div class="col w-small bp-ul-icon"><i class="bi bi-file-earmark-fill text-grey"></i></div>
                <div class="col">
                  <div class="col bp-description pb-2">{{ bp.name }}</div>
                  <div class="col bp-ul-status">{{ bp.description }}</div>
                </div>
              </template>

              <!-- Success -->
              <template v-if="blueprintData[bp.id.toString()].status === 'success'">
                <div class="row">
                  <div class="col w-small bp-ul-icon"><i class="bi bi-file-earmark-check-fill text-success"></i></div>
                  <div class="col">
                    <div class="col bp-description pb-2">{{ bp.name }}</div>
                    <div class="col bp-ul-status">{{ bp.description }}</div>
                  </div>
                </div>

                <div class="row pe-0">
                  <div class="col feedback-col pe-0">
                    <div>
                      {{ $t('extracted-data') }}
                    </div>
                    <div class="data-donation-container pb-3 pt-3 fs-09">
                      <div :id="'donation-container-'+bp.id.toString()" class="ul-data-container ul-data-condensed bg-white">
                        <div class="data-donation-table">
                          <table :id="'ul-result-' + bp.id.toString()" class="table table-sm">
                            <thead>
                            <tr>
                              <th v-for="value in blueprintData[bp.id.toString()].extracted_fields.values()" :key="value">{{ value }}</th>
                            </tr>
                            </thead>
                            <tbody>
                            <tr v-for="row in blueprintData[bp.id.toString()].extracted_data.slice(blueprintData[bp.id.toString()].fb_pos_lower, blueprintData[bp.id.toString()].fb_pos_upper)" :key="row">
                              <template v-for="key in blueprintData[bp.id.toString()].extracted_fields.keys()" :key="key">
                                <td v-if="key in row" :key="row">{{ row[key] }}</td>
                                <td v-else>–</td>
                              </template>
                            </tr>

                            </tbody>
                          </table>
                        </div>
                        <div class="data-table-navigation">
                          <div class="pb-2">
                            <a class="btn btn-pagination btn-sm me-2 btn-active" v-if="blueprintData[bp.id.toString()].fb_pos_lower > 9" v-on:click="updateFbPos(bp.id.toString(), 'down')" >{{ $t('previous-page') }}</a>
                            <span class="btn-pagination btn-sm me-2 btn-light text-muted user-select-none btn-muted" v-if="blueprintData[bp.id.toString()].fb_pos_lower <= 9">{{ $t('previous-page') }}</span>
                            <a class="btn btn-pagination btn-sm btn-active" v-if="blueprintData[bp.id.toString()].fb_pos_upper < blueprintData[bp.id.toString()].extracted_data.length" v-on:click="updateFbPos(bp.id.toString(), 'up')" >{{ $t('next-page') }}</a>
                            <span class="btn-pagination btn-sm btn-light text-muted user-select-none btn-muted" v-if="blueprintData[bp.id.toString()].fb_pos_upper >= blueprintData[bp.id.toString()].extracted_data.length">{{ $t('next-page') }}</span>
                          </div>

                          <div class="pb-3">
                            <p class="pb-3">
                              {{ $t('extraction-disclaimer', { lower: blueprintData[bp.id.toString()].fb_pos_lower + 1, upper: blueprintData[bp.id.toString()].fb_pos_upper, total: blueprintData[bp.id.toString()].extracted_data.length }) }}
                            </p>
                          </div>
                        </div>
                      </div>
                      <div>

                      </div>
                      <div :id="'expansion-control-'+bp.id.toString()" class="ul-data-expansion-control control-condensed">
                        <a class="fw-bold"
                           :id="'collapse-toggle-'+bp.id.toString()"
                           v-on:click="showHideData(bp.id.toString())">
                          <span :id="'donation-container-'+ bp.id.toString() + '-toggle-label'">{{ $t('show-extracted-data') }}</span>
                        </a>
                      </div>
                    </div>
                  </div>
                </div>

                <template v-if="this.combinedConsent === false">
                <div class="row pe-0">
                  <div class="col feedback-col pb-5 pt-1 pe-0">
                    <p class="fw-bold">{{ $t('donation-question') }}</p>
                      <div class="consent-question-container">

                        <div class="btn-group" role="group" aria-label="Basic radio toggle button group">
                          <input type="radio"
                                 class="btn-check"
                                 :id="'donate-agree-'+bp.id.toString()"
                                 :name="'agreement-'+bp.id.toString()"
                                 value="true"
                                 autocomplete="off"
                                 v-model="blueprintData[bp.id.toString()].consent"
                                 @change="emitToParent"
                                 required>
                          <label :class="{ 'selected-donate-agree': blueprintData[bp.id.toString()].consent === 'true' }"
                                 :for="'donate-agree-'+bp.id.toString()"
                                 class="form-check-label rb-cb-label btn btn-light donation-btn shadow-none">
                            {{ $t('donation-agree') }}
                          </label>

                          <input type="radio"
                                 class="btn-check"
                                 :id="'donate-disagree-'+bp.id.toString()"
                                 :name="'agreement-'+bp.id.toString()"
                                 value="false"
                                 autocomplete="off"
                                 v-model="blueprintData[bp.id.toString()].consent"
                                 @change="emitToParent">
                          <label :class="{ 'selected-donate-disagree': blueprintData[bp.id.toString()].consent === 'false' }"
                                 :for="'donate-disagree-'+bp.id.toString()"
                                 class="form-check-label rb-cb-label btn btn-light donation-btn shadow-none">
                            {{ $t('donation-disagree') }}
                          </label>
                        </div>
                      </div>
                  </div>
                </div>
                </template>

              </template>

              <!-- Nothing Extracted -->
              <template v-if="blueprintData[bp.id.toString()].status === 'nothing extracted'">
                <div class="col w-small bp-ul-icon"><i class="bi bi-file-earmark-x-fill text-grey"></i></div>
                <div class="col-4 bp-description">{{ bp.name }}</div>
                <div class="col bp-ul-status">
                  <template v-if="blueprintData[bp.id.toString()].errors.length">
                    <p v-for="e in blueprintData[bp.id.toString()].errors" :key="e">{{ e }}</p>
                  </template>
                  <p v-else>{{ $t('extraction-failed') }}</p>
                </div>
                <div class="col-auto bp-ul-data"></div>
                <div class="col-auto bp-ul-consent"></div>
              </template>

              <!-- Failed -->
              <template v-if="blueprintData[bp.id.toString()].status === 'failed'">
                <div class="col w-small bp-ul-icon"><i class="bi bi-file-earmark-x-fill text-danger"></i></div>
                <div class="col-4 bp-description">{{ bp.name }}</div>
                <div class="col bp-ul-status">
                  <template v-if="blueprintData[bp.id.toString()].errors.length">
                    <p v-for="e in blueprintData[bp.id.toString()].errors" :key="e">{{ e }}</p>
                  </template>
                  <p v-else>{{ $t('extraction-failed') }}</p>
                </div>
                <div class="col-auto bp-ul-data"></div>
                <div class="col-auto bp-ul-consent"></div>
              </template>

            </div>

            </template>
          </div>
        </div>
      </div>

        <template v-if="this.combinedConsent === true && (uploadStatus === 'success' || uploadStatus === 'partial')">
          <div class="row mt-5 pe-0">
            <div class="col feedback-col pb-5 pt-1 pe-0">
              <p class="fw-bold">{{ $t('donation-question') }}</p>
              <div class="consent-question-container">

                <div class="btn-group" role="group" aria-label="Basic radio toggle button group">
                  <input type="radio"
                         class="btn-check"
                         id="combined-donate-agree"
                         value="true"
                         autocomplete="off"
                         v-model="combinedDonation"
                         @change="emitToParent"
                         required>
                  <label :class="{ 'selected-donate-agree': combinedDonation === 'true' }"
                         class="form-check-label rb-cb-label btn btn-light donation-btn shadow-none"
                         for="combined-donate-agree">
                    {{ $t('donation-agree') }}
                  </label>

                  <input type="radio"
                         class="btn-check"
                         id="combined-donate-disagree"
                         value="false"
                         autocomplete="off"
                         v-model="combinedDonation"
                         @change="emitToParent">
                  <label :class="{ 'selected-donate-disagree': combinedDonation === 'false' }"
                         class="form-check-label rb-cb-label btn btn-light donation-btn shadow-none"
                         for="combined-donate-disagree">
                    {{ $t('donation-disagree') }}
                  </label>
                </div>

              </div>
            </div>
          </div>
        </template>
    </div>
  </div>
  </div>

  <div class="default-modal" id="ulInfoModal" ref="ulInfoModal" style="display: none">
    <div class="modal-body d-flex flex-row align-items-center pt-5">

      <div class="ps-2 pe-3 ul-status-icon"><i id="ul-modal-info-icon" class="bi bi-file-check"></i></div>

      <div class="ul-status-description">
        <h4>{{ this.ulModalInfoTitle }}</h4>
        <p id="ul-modal-info-msg" class="pb-2" v-html="this.ulModalInfoMsg"></p>
        <div v-if="uploadStatus === 'failed'">
          <ul class="text-danger pb-3">
            <li v-for="error in generalErrors" :key="error">{{ error }}</li>
          </ul>
        </div>
      </div>

    </div>
    <div class="modal-footer">
      <button class="ddm-btn" type="button" id="closeUlInfoModal" @click="closeUlInfoModal">OK</button>
    </div>
  </div>

  <div class="modal-backdrop" ref="modalBackdrop" style="display: none"></div>

</template>

<script>
import JSZip from "jszip";
import DonationInstructions from "./DonationInstructions";
import axios from "axios";
import Papa from 'papaparse';
import {
  regexDeleteMatch,
  regexReplaceMatch,
  regexDeleteRow,
  valueIsEqual,
  valueIsNotEqual,
  valueIsSmallerOrEqual,
  valueIsGreaterOrEqual,
  valueIsSmaller,
  valueIsGreater
} from '../utils/FileUploaderExtractionFunctions'


export default {
  name: 'ProcessFile',
  components: {DonationInstructions},
  props: {
    expectsZip: Boolean,
    blueprints: Array,
    instructions: Array,
    componentId: Number,
    name: String,
    exceptionUrl: String,
    combinedConsent: Boolean
  },
  emits: ['changedData'],
  data() {
    return {
      blueprintData: {},
      uploadStatus: 'pending',
      uploadAttempts: 0,
      generalErrors: [],
      ulModalInfoMsg: '',
      ulModalInfoTitle: '',
      combinedDonation: null
    }
  },
  created() {
    // Create dictionary to hold post data.
    this.blueprints.forEach(bp => {
      let id = bp.id;
      let blueprintInfo = {
        name_uploaded_file: null,
        consent: null,
        extracted_data: [],
        extracted_fields: new Map(),
        status: 'pending',
        errors: [],
        fb_pos_lower: 0,
        fb_pos_upper: 10,
        error_log: {},
      }
      this.blueprintData[id.toString()] = blueprintInfo
    })
    this.resetErrorLog();
    this.emitToParent();
  },
  methods: {
    /**
     * Validate that a file is a ZIP file.
     * @param file
     */
    checkIsZip(file) {
      const extensionIsValid = file.name.toLowerCase().endsWith('.zip');
      const mimeIsValid = [
          'application/zip',
          'application/x-zip-compressed',
          'multipart/x-zip'
      ].includes(file.type);
      if(extensionIsValid && mimeIsValid) {
        return true;
      } else {
        return false;
      }
    },
    /**
     * Processes the file uploaded by the participant.
     * @param event
     */
    processFile(event) {
      let uploader = this;
      uploader.uploadStatus = 'processing';
      uploader.uploadAttempts += 1;
      uploader.resetErrorLog();
      const files = event.target.files;

      // Procedure if supplied file is expected to be a zip-folder.
      if (uploader.expectsZip && files.length === 1) {

        // Check that file is a ZIP file.
        const uploadedFile = files[0]
        if (uploader.checkIsZip(uploadedFile) === false) {
          uploader.postError(4101, uploader.$t('error-not-zip'));
          uploader.recordError(uploader.$t('error-not-zip'), 'general');
        } else {

          JSZip
              .loadAsync(uploadedFile)
              .then(z => {
                uploader.blueprints.forEach(blueprint => {
                  let re = new RegExp(blueprint.regex_path);
                  let reHasMatched = false;
                  z.file(re).forEach(f => {
                    reHasMatched = true;
                    f
                        .async("string")
                        .then(c => uploader.processContent(c, blueprint))
                        .catch(e => {
                          uploader.postError(4199, e.message);
                          uploader.recordError(uploader.$t('error-generic') + e.message, blueprint.id.toString());
                        })
                  })
                  if (!reHasMatched) {
                    uploader.postError(4180, uploader.$t('error-regex-not-matched'), blueprint.id);
                    uploader.postError(4181, `Files in uploaded folder: ${Object.keys(z.files)}`, blueprint.id);
                    uploader.recordError(uploader.$t('error-regex-not-matched'), blueprint.id.toString());
                  }
                })
              })
              .catch(e => {
                let myMess = '';
                let statusCode = 0;
                if (e.message.includes('zip') && e.message.includes('central')) {
                  myMess = uploader.$t('error-not-zip');
                  statusCode = 4101;
                } else if (e.message.includes('Corrupted zip')) {
                  myMess = uploader.$t('error-zip-corrupted');
                  statusCode = 4102;
                } else if (e.message.includes('Encrypted zip')) {
                  myMess = uploader.$t('error-zip-encrypted');
                  statusCode = 4103;
                } else {
                  myMess = uploader.$t('error-generic') + e.message;
                  statusCode = 4198;
                }
                uploader.postError(statusCode, e.message);
                uploader.recordError(myMess, 'general');
              })
        }
      }

      // Procedure if supplied file is expected to be a single file.
      else if (!uploader.expectsZip && files.length === 1) {

        if (uploader.blueprints[0].format === 'json') {
          if (!files[0].name.endsWith('.json')) {
            let errorMsg = uploader.$t('error-wrong-file-type', 'en', {actualType: files[0].name.substr(files[0].name.lastIndexOf(".")), expectedType: '.json'})
            uploader.postError(4105, errorMsg, uploader.blueprints[0].id);
            uploader.recordError(uploader.$t('error-wrong-file-type', {actualType: files[0].name.substr(files[0].name.lastIndexOf(".")), expectedType: '.json'}), uploader.blueprints[0].id.toString());
          }
        }

        if (uploader.blueprints[0].format === 'csv') {
          if (!files[0].name.endsWith('.csv')) {
            let errorMsg = uploader.$t('error-wrong-file-type', 'en', {actualType: files[0].name.substr(files[0].name.lastIndexOf(".")), expectedType: '.csv'});
            uploader.postError(4105, errorMsg, uploader.blueprints[0].id);
            uploader.recordError(uploader.$t('error-wrong-file-type', {actualType: files[0].name.substr(files[0].name.lastIndexOf(".")), expectedType: '.csv'}), uploader.blueprints[0].id.toString());
          }
        }

        let reader = new FileReader();
        reader.onload = function(event) {
          let content = event.target.result;
          try {
            // uploader.processContent(content, uploader.blueprints[0]);  // TODO: Check this
            uploader.blueprints.forEach(blueprint => {
              uploader.processContent(content, blueprint)
            })

          } catch(e) {
            uploader.postError(4199, e.message, uploader.blueprints[0].id);
            uploader.recordError(uploader.$t('error-generic') + e.message, uploader.blueprints[0].id.toString());
          }
        }
        reader.readAsText(files[0]);
      }

      // Procedure if files.length != 1
      else {
        uploader.postError(4104, uploader.$t('error-multiple-files', 'en'));
        uploader.recordError(uploader.$t('error-multiple-files'), 'general');
      }

      setTimeout(() => {
        uploader.updateStatus();
        uploader.$nextTick(function () {
          uploader.emitToParent();
        });
      }, 1000);

    },

    /**
     * Extracts the content of a file according to the defined extraction and
     * validation rules.
     * @param {string } content   A file's content.
     * @param {Object}  blueprint A blueprint.
     */
    processContent(content, blueprint) {
      let uploader = this;
      let blueprintID = blueprint.id.toString();
      let fileContent = null;
      let extractedData = [];

      // PARSING
      if (blueprint.format === 'json') {
        try {
          fileContent = JSON.parse(content);
        } catch(e) {
          uploader.postError(4106, e.message, blueprint.id);
          uploader.recordError(uploader.$t('error-json-syntax'), blueprintID);
        }

        if(fileContent) {
          if (blueprint.json_extraction_root !== '') {
            try {
              fileContent = this.getNestedJsonEntry(fileContent, blueprint.json_extraction_root);
            } catch (e) {
              uploader.postError(4207, uploader.$t('error-no-data-in-file'), blueprint.id);
              uploader.recordError(uploader.$t('error-no-data-in-file'), blueprintID);
              return
            }
          }

          // Check if fileContent is null.
          if (fileContent === null || fileContent === undefined) {
            uploader.postError(4207, uploader.$t('error-no-data-in-file'), blueprint.id);
            uploader.recordError(uploader.$t('error-no-data-in-file'), blueprintID);
            return;
          }

          // Check if fileContent must be converted to array.
          if (!(Symbol.iterator in Object(fileContent))) {
            fileContent = new Array(fileContent);
          }
        }
      }

      else if (blueprint.format === 'csv') {
        try {
          let parserResult = Papa.parse(content, {header: true, delimiter: blueprint.csv_delimiter });
          fileContent = parserResult.data;
        } catch(e) {
          uploader.postError(4106, e.message, blueprint.id);
          uploader.recordError(uploader.$t('error-json-syntax'), blueprintID);
        }
      }

      // FILTERING
      if (fileContent) {
        let nEntriesWithMissingFields = 0;
        let nEntriesFilteredOut = 0;

        fileContent.forEach(entry => {

          // Check if file contains all expected fields
          let missingFields = [];
          if (!blueprint.expected_fields.every(field => {

            if (blueprint.exp_fields_regex_matching) {
              let fieldRegex = new RegExp(field);
              if (Object.keys(entry).filter(key => fieldRegex.test(key)).length > 0){
                return true;
              } else {
                missingFields.push(field)
                nEntriesWithMissingFields += 1;
                return false;
              }
            } else if (Object.keys(entry).filter(key => field === key).length > 0) {
                return true;
            } else {
              missingFields.push(field)
              nEntriesWithMissingFields += 1;
              return false;
            }
          })) {
            // TODO: Check whether and how to implement this:
            //  Go to next entry and record exception
            // let errorMsg = `Entry does not contain the expected field(s) "${missingFields.toString()}".`;
            // uploader.postError(4203, errorMsg, blueprint.id);
            return;
          }

          // Match variable names to the keys contained in an entry.
          let rules = blueprint.filter_rules;
          let keyMap = new Map();
          rules.forEach(rule => {
            let keys = Object.keys(entry);
            if (rule.regex_field) {
              let fieldRegex = new RegExp(rule.field);
              keys = keys.filter(key => fieldRegex.test(key));
            } else {
              let field = rule.field;
              keys = keys.filter(key => field === key);
            }

            if(keys.length > 1) {
              let errorMsg = `More than 1 key matches for variable "${rule.field}": ${keys}; Associated "${keys[0]}" to variable.`;
              uploader.postError(4203, errorMsg, blueprint.id);
            } else if(keys.length === 0) {
              let errorMsg = `No key matches for variable "${rule.field}": ${Object.keys(entry)}`;
              uploader.postError(4203, errorMsg, blueprint.id);
            } else {
              keyMap.set(rule.field, keys[0]);
            }
          })

          // Apply filters, Pop unused keys and add to result.
          let result = {};
          try {
            if (rules.length > 0) {
              rules.forEach(rule => {
                let key = keyMap.get(rule.field);
                if (key === 'undefined') {
                  throw `Field "${key}" not in entry.`
                }

                switch (rule.comparison_operator) {
                  case null:
                    result[rule.field] = entry[key];
                    break;
                  case '==':
                    if (valueIsEqual(entry[key], rule.comparison_value)) {
                      // discard entry
                      throw `Field "${key}" matches filter value "${rule.comparison_value}" for entry.`
                    }
                    break;
                  case '!=':
                    if (valueIsNotEqual(entry[key], rule.comparison_value)) {
                      // discard entry
                      throw `Field "${key}" matches filter value "${rule.comparison_value}" for entry.`
                    }
                    break;
                  case '<=':
                    if (valueIsSmallerOrEqual(entry[key], rule.comparison_value)) {
                      // discard entry
                      throw `Field "${key}" matches filter value "${rule.comparison_value}" for entry.`
                    }
                    break;
                  case '>=':
                    if (valueIsGreaterOrEqual(entry[key], rule.comparison_value)) {
                      // discard entry
                      throw `Field "${key}" matches filter value "${rule.comparison_value}" for entry.`
                    }
                    break;
                  case '<':
                    if (valueIsSmaller(entry[key], rule.comparison_value)) {
                      // discard entry
                      throw `Field "${key}" matches filter value "${rule.comparison_value}" for entry.`
                    }
                    break;
                  case '>':
                    if (valueIsGreater(entry[key], rule.comparison_value)) {
                      // discard entry
                      throw `Field "${key}" matches filter value "${rule.comparison_value}" for entry.`
                    }
                    break;
                  case 'regex-delete-match':
                    if (key in result) {
                      try {
                        let newValue = regexDeleteMatch(entry[key], rule.comparison_value);
                        result[rule.field] = newValue;
                        entry[key] = newValue;
                      } catch {
                        let errorMsg = `RegexDeleteMatch failed for field ${rule.field}.`;
                        uploader.postError(4220, errorMsg, blueprint.id);
                        result[rule.field] = entry[key];
                      }
                    }
                    break;
                  case 'regex-replace-match':
                    if (key in result) {
                      try {
                        let newValue = regexReplaceMatch(entry[key], rule.comparison_value, rule.replacement_value);
                        result[rule.field] = newValue;
                        entry[key] = newValue;
                      } catch {
                        let errorMsg = `RegexReplaceMatch failed for field ${rule.field}.`;
                        uploader.postError(4221, errorMsg, blueprint.id);
                        result[rule.field] = entry[key];
                      }
                    }
                    break;
                  case 'regex-delete-row':
                    if (key in entry) {
                      let deleteRow = false;
                      try {
                        deleteRow = regexDeleteRow(entry[key], rule.comparison_value);
                      } catch {
                        let errorMsg = `RegexDeleteRow failed for field ${rule.field}.`;
                        uploader.postError(4222, errorMsg, blueprint.id);
                        break;
                      }
                      if (deleteRow) {
                        // discard entry
                        throw `Field "${key}" matches RegExp "${rule.comparison_value}".`
                      }
                    }
                    break;
                  default: break;
                }
              });
            }
            extractedData.push(result);
          } catch (e) {
            nEntriesFilteredOut += 1;
          }

          for (let [key, value] of  keyMap.entries()) {
            uploader.blueprintData[blueprintID].extracted_fields.set(key, value);
          }

        })
        uploader.blueprintData[blueprintID].extracted_data = extractedData;
        extractedData = null;
        if (nEntriesWithMissingFields === fileContent.length) {
          let errorMsg = `No data extracted: Expected fields missing in ${nEntriesWithMissingFields}/${fileContent.length} entries.`;
          uploader.postError(4201, errorMsg, blueprint.id);
          uploader.recordError(uploader.$t('error-all-expected-fields-missing'), blueprint.id.toString());
        }
        else if (nEntriesFilteredOut === fileContent.length) {
          let errorMsg = `No data extracted: All entries (${nEntriesFilteredOut}/${fileContent.length}) were filtered out.`;
          uploader.postError(4204, errorMsg, blueprint.id);
          uploader.recordError(uploader.$t('error-all-fields-filtered-out'), blueprint.id.toString());
        }
        else if ((nEntriesWithMissingFields + nEntriesFilteredOut) === fileContent.length) {
          let errorMsg = `No data extracted: Expected fields missing in ${nEntriesWithMissingFields}/${fileContent.length} entries and ${nEntriesFilteredOut}/${fileContent.length} filtered out.`;
          uploader.postError(4205, errorMsg, blueprint.id);
          uploader.recordError(uploader.$t('error-all-fields-filtered-out'), blueprint.id.toString());
        } else if (nEntriesFilteredOut > 0) {
          let msg = `${nEntriesFilteredOut}/${fileContent.length} rows omitted due to a filter rule match.`;
          uploader.postError(4206, msg, blueprint.id);
        }

        try {
          let msg = `${uploader.blueprintData[blueprintID].extracted_data.length} entries were extracted.`;
          uploader.postError(7004, msg, blueprint.id);
        } catch {
          // continue regardless of error
        }
      }
    },

    getNestedJsonEntry(fileContent, path) {
      path = path.replace(/\[(\w+)\]/g, '.$1'); // convert indexes to properties
      path = path.replace(/^\./, '');           // strip a leading dot
      let a = path.split('.');
      for (let i = 0, n = a.length; i < n; ++i) {
        let k = a[i];
        if (k in fileContent) {
          fileContent = fileContent[k];
        } else {
          return;
        }
      }
      return fileContent;
    },

    /**
     * Emit data to UploaderApp.
     */
    emitToParent() {
      let dataToEmit = JSON.parse(JSON.stringify(this.blueprintData));

      if (this.combinedConsent === false) {
        Object.keys(dataToEmit).forEach(key => {
          if (dataToEmit[key].consent === null) {
            dataToEmit[key].consent = null;
            dataToEmit[key].extracted_data = [];
          }
          else if (dataToEmit[key].consent === 'false') {
            dataToEmit[key].extracted_data = [];
            dataToEmit[key].consent = false;
          } else if (dataToEmit[key].consent === 'true') {
            dataToEmit[key].consent = true;
          }
        })
      } else {
        let consent = this.combinedDonation;
        Object.keys(dataToEmit).forEach(key => {
          if (consent === null) {
            dataToEmit[key].consent = null;
            dataToEmit[key].extracted_data = [];
          } else if (consent === 'false') {
            dataToEmit[key].consent = false;
            dataToEmit[key].extracted_data = [];
          } else if (consent === 'true') {
            dataToEmit[key].consent = true;
          }
        })
      }

      this.$emit('changedData', dataToEmit);
    },

    /**
     * Resets the client-side error log.
     */
    resetErrorLog() {
      this.generalErrors = [];
      for (let bp in this.blueprintData){
        this.blueprintData[bp].errors = [];
      }
    },

    /**
     * Records errors that will be displayed to participants on the client-side.
     * @param {string} e      Error message that is displayed to the user.
     * @param {string} target If error relates to a specific blueprint a blueprint ID.
     *                        'general' if it is a general error.
     */
    recordError(e, target) {
      if (target == 'general') {
        this.generalErrors.push(e)
      } else {
        this.blueprintData[target].errors.push(e);
      }
    },

    /**
     * Posts error to server through DDM's exception API (endpoint specified
     * in the exceptionUrl variable). Targeted at researchers administrating
     * the project.
     * @param {number}  code        Exception code (see DDM documentation).
     * @param {string}  msg         Exception description that will be submitted to
     *                              the server-side exception log.
     * @param {number}  blueprintID ID of related blueprint. Default is null.
     */
    postError(code, msg, blueprintID=null) {
      // Limit the number of times an error message is posted to the server.
      if (blueprintID != null) {
        let bp = this.blueprintData[blueprintID];
        if (!(code in bp.error_log)) {
          bp.error_log[code] = 1;
        } else {
          bp.error_log[code] += 1;
        }
        if (bp.error_log[code] > 5) {
          return;
        }
      }

      let data = {
        'status_code': code,
        'message': this.name + ': ' + msg,
        'raised_by': 'client',
        'blueprint': blueprintID
      }
      axios.post(this.exceptionUrl, data)
          .catch(e => console.error(`Could not post error message, ${e}`));
    },

    /**
     * Updates the upload status displayed to the participant.
     * Status will be updated to either 'success', 'failed', or 'partial'.
     */
    updateStatus() {
      let nNothingExtracted = 0;
      let nSuccess = 0;
      let nFailed = 0;
      let nBlueprints = Object.keys(this.blueprintData).length;
      console.log(this.generalErrors)
      console.log(this.generalErrors.length)
      for (let bp in this.blueprintData){
        if (this.generalErrors.length !== 0) {
          this.blueprintData[bp].status = 'failed';
          this.blueprintData[bp].consent = 'false';
          nFailed += 1;
          continue;
        }

        if (this.blueprintData[bp].errors.length) {
          let errorSet = new Set(this.blueprintData[bp].errors);

          if (errorSet.size === 1 && (errorSet.has(this.$t('error-all-fields-filtered-out')) || errorSet.has(this.$t('error-no-data-in-file')))) {
            this.blueprintData[bp].status = 'nothing extracted';
            this.blueprintData[bp].consent = 'false';
            nNothingExtracted += 1;
          } else {
            this.blueprintData[bp].status = 'failed';
            this.blueprintData[bp].consent = 'false';
            nFailed += 1;
          }
        } else {
          this.blueprintData[bp].status = 'success';
          nSuccess += 1;
          // this.blueprintData[bp].consent = 'true';
        }
      }

      this.$nextTick(function () {
        let modalIcon = document.getElementById('ul-modal-info-icon');

        if (nSuccess === nBlueprints) {
          this.uploadStatus = 'success';
          modalIcon.className = 'bi bi-file-check text-success';
          this.ulModalInfoTitle = this.$t('ul-success-modal-title');
          this.ulModalInfoMsg = this.$t('ul-success-modal-body');

        } else if (nNothingExtracted === nBlueprints) {
          this.uploadStatus = 'partial';
          modalIcon.className = 'bi bi-exclamation-diamond text-orange';
          this.ulModalInfoTitle = this.$t('ul-nothing-extracted-modal-title');
          this.ulModalInfoMsg = this.$t('ul-nothing-extracted-modal-body');

          this.$refs.ulInfoModal.style.display = 'block';
          this.$refs.modalBackdrop.style.display = 'block';

        } else if ((nSuccess + nNothingExtracted) === nBlueprints) {
          this.uploadStatus = 'success';
          modalIcon.className = 'bi bi-file-check text-success';
          this.ulModalInfoTitle = this.$t('ul-success-modal-title');
          this.ulModalInfoMsg = this.$t('ul-success-modal-body');

        } else {
          this.uploadStatus = 'failed';
          modalIcon.className = 'bi bi-x-octagon text-danger';
          this.ulModalInfoTitle = this.$t('ul-failed-modal-title');
          this.ulModalInfoMsg = this.$t('ul-failed-modal-body');

          for (let bp in this.blueprintData){
            this.blueprintData[bp].status = 'failed';
          }
          this.$refs.ulInfoModal.style.display = 'block';
          this.$refs.modalBackdrop.style.display = 'block';
        }
      });
    },

    showHideData(bpId) {
      let elementId = 'donation-container-' + bpId;
      let target = document.getElementById(elementId);
      let targetLabel = document.getElementById(elementId.concat('-toggle-label'));
      let controlElement = document.getElementById('expansion-control-' + bpId);

      let newLabel = '';
      if (target.classList.contains('ul-data-condensed')) {
        target.classList.replace('ul-data-condensed', 'ul-data-expanded');
        controlElement.classList.replace('control-condensed', 'control-expanded');
        newLabel = this.$t('hide-extracted-data');
      } else {
        target.classList.replace('ul-data-expanded', 'ul-data-condensed');
        controlElement.classList.replace('control-expanded', 'control-condensed');
        newLabel = this.$t('show-extracted-data');
      }
      targetLabel.innerHTML = newLabel;
    },

    closeUlInfoModal() {
      this.$refs.ulInfoModal.style.display = 'none';
      this.$refs.modalBackdrop.style.display = 'none';
    },

    updateFbPos(bpId, dir) {
      let stepSize = 10;
      let bp = this.blueprintData[bpId];
      if (dir === 'up') {
        bp.fb_pos_lower += stepSize;
        bp.fb_pos_upper += stepSize;
      } else {
        if (bp.fb_pos_lower < stepSize) {
          bp.fb_pos_lower = 0;
          bp.fb_pos_upper = stepSize;
        } else {
          bp.fb_pos_lower -= stepSize;
          bp.fb_pos_upper -= stepSize;
        }
      }
    }
  },
}
</script>

<style scoped>
.accordion-button:focus {
  outline: none;
  box-shadow: none;
}
.accordion-button:not(.collapsed) {
  background-color: white;
  color: black;
  border-bottom: none;
  box-shadow: none;
}
.accordion-button {
  color: black;
  border-bottom: none;
}
.accordion-button:not(.collapsed)::after {
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16' fill='%23212529'%3e%3cpath fill-rule='evenodd' d='M1.646 4.646a.5.5 0 0 1 .708 0L8 10.293l5.646-5.647a.5.5 0 0 1 .708.708l-6 6a.5.5 0 0 1-.708 0l-6-6a.5.5 0 0 1 0-.708z'/%3e%3c/svg%3e");
}
.accordion-button {
  border-radius: 0 !important;
}
@media (max-width: 768px) {
  .accordion-body {
    padding: 10px 5px;
  }
}
.form-check-label {
  cursor: pointer;
}
.ul-success {

}
.ul-status-icon {
  font-size: 2.5rem;
}
.ul-status p,
.ul-status-description p,
.ul-status-message p,
.ul-status-message ul {
  margin: 0;
}
.text-grey {
  color: #d0d0d0;
}
.bp-description {
  font-weight: bold;
}
.ul-data-container {
  display: block;
}
.ul-data-condensed {
  max-height: 180px;
  overflow: hidden;
}
.ul-data-expanded {
  color: black;
}
.ul-data-container th {
  position: sticky;
  top: 0;
  z-index: 1;
  background-color: white !important;
  box-shadow: 0px 1px black;
  min-width: 200px;
}
.ul-data-expansion-control {
  text-align: center;
  z-index: 10;
  position: relative;
  cursor: pointer;
}
.control-expanded {
  background: white;
  margin-top: 0;
  height:30px;
}
.control-condensed {
  background: rgb(255, 255, 255);
  background: linear-gradient(180deg, rgba(255,255,255,0) 0%, rgba(255,255,255,1) 70%);
  height: 120px;
  margin-top: -120px;
  padding-top: 80px;
}
.fs-09 {
  font-size: 0.9rem;
}
.w-small {
  max-width: 20px;
  padding-left: 0.25rem;
  padding-right: 0.25rem;
}
.consent-question-container {
  width: 100%;
}
.feedback-col {
  padding-left: 33px;
}
.extraction-information-container {
  padding-top: 6px;
}
.ul-status {
  border-top: 1px solid #212529;
}
.extraction-information-container .ul-status:last-of-type {
  border-bottom: 1px solid #212529;
}
.text-orange {
  color: #ef7000;
}
.upload-other a {
  color: #767676 !important;
}
.ul-status-message {
  padding-left: 25px;
}
.ul-data-container table {
  table-layout: auto;
  min-width: 100%;
}
.ul-data-container table td {
  max-width: 33%;
  word-break: break-all;
}
.data-donation-table {
  width: 100%;
  overflow-x: scroll;
  margin-bottom: 15px;
  display: block;
}
.data-donation-table tbody {
  border-top: none;
}
.uploader-container {
  border-top: 2px solid #000;
  border-bottom: 2px solid #000;
}
.btn-pagination {
  background: #f4f4f4;
  border: none;
  color: black;
}
.btn-active:hover {
  color: black !important;
  background: #cacaca;
}
.btn-muted {
  display: inline-block;
  vertical-align: middle;
}

.selected-donate-agree {
  background: #069143 !important;
  color: white !important;
  font-weight: bold;
}

.selected-donate-disagree {
  background: #f38896 !important;
  font-weight: bold;
}

.donation-btn {
  width: 120px;
  color: #000;
  background-color: #dfdfdf;
  border: none;
  margin: 5px;
}

@media (min-width: 576px) {}

@media (min-width: 768px) {
  .uploader-container {
    box-shadow: 6px 7px 20px #80808040;
    border-radius: 8px;
    border: none;
  }
}

@media (min-width: 992px) {}

@media (min-width: 1200px) {}

/* XX-Large devices (larger desktops, 1400px and up) */
@media (min-width: 1400px) {}

</style>
