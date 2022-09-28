<i18n src="../translations/file_uploader.json"></i18n>

<template>

  <div class="mb-5">
    <div class="float-left bg-dark text-white pt-2 ps-2 pb-1 rounded-top">
      <div class="col-sm">
        <h4>Upload {{ name }}</h4>
      </div>
    </div>

    <!-- INSTRUCTIONS -->
    <div class="accordion" :id="'ul-acc-'+componentId">
      <div class="accordion-item">

        <h3 class="accordion-header" :id="'acc-instr-head-'+componentId">
          <button class="accordion-button" type="button" data-bs-toggle="collapse" :data-bs-target="'#acc-instr-body-'+componentId" aria-expanded="true" :aria-controls="'acc-instr-body-'+componentId">
            <b>{{ $t('instructions') }}</b>
          </button>
        </h3>

        <div :id="'acc-instr-body-'+componentId" class="accordion-collapse collapse show" aria-labelledby="headingOne" :data-bs-parent="'#ul-acc-'+componentId">
          <div class="accordion-body">
            <DonationInstructions v-if="instructions.length" :instructions="instructions" :component-id="componentId"></DonationInstructions>
            <div v-else>{{ $t('no-instructions-defined') }}.</div>
          </div>
        </div>

      </div>
    </div>

    <!-- DATA UPLOAD -->
    <div class="accordion-body border">
      <div class="row align-items-center">

        <!-- Upload pending -->
        <template v-if="uploadStatus === 'pending'">
          <div class="col-auto ul-status-icon"><i class="bi bi-upload"></i></div>

          <div class="col ul-status-description">
            <p v-if="!uploadAttempts">{{ $t('upload-file') }}:</p>
            <p v-else-if="uploadAttempts">{{ $t('upload-different-file') }}:</p>
          </div>

          <div class="col ul-status-message">
            <label class="select-file-btn">
              <input :name="'ul-' + componentId" type="file" @change="processFile" class="d-none">
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
            <p class="text-success fw-bold">{{ $t('upload-success') }}</p>
            <p><a @click="uploadStatus = 'pending'" class="upload-other">{{ $t('choose-different-file') }}</a></p>
          </div>

          <div class="col ul-status-message"></div>
        </template>

        <!-- Upload partial -->
        <template v-else-if="uploadStatus === 'partial'">
          <div class="col-auto ul-status-icon"><i class="bi bi-exclamation-diamond text-warning"></i></div>

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
          <div class="col-auto ul-status-icon"><i class="bi bi-exclamation-diamond text-danger"></i></div>

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

      <!-- UPLOAD FEEDBACK -->
      <div class="ul-feedback-container row border-bottom mt-3">
        <div class="col">
        <template v-for="bp in blueprints"
                :key="bp"
        >
        <div class="ul-status row align-items-center border-top pt-2 pb-2" :class="{ 'ul-success': blueprintData[bp.id.toString()].status === 'success', 'ul-failed': blueprintData[bp.id.toString()].status === 'failed'}">

          <!-- Pending -->
          <template v-if="blueprintData[bp.id.toString()].status === 'pending'">
            <div class="col-auto bp-ul-icon"><i class="bi bi-file-earmark-fill text-grey"></i></div>
            <div class="col-2 bp-description">{{ bp.name }}</div>
            <div class="col bp-ul-status">{{ $t('not-yet-extracted') }}</div>
            <div class="col bp-ul-data"></div>
            <div class="col bp-ul-consent"></div>
          </template>

          <!-- Success -->
          <template v-if="blueprintData[bp.id.toString()].status === 'success'">
            <div class="row pb-2">
              <div class="col-auto bp-ul-icon"><i class="bi bi-file-earmark-check-fill text-success"></i></div>
              <div class="col-2 bp-description">{{ bp.name }}</div>
              <div class="col bp-ul-status">{{ $t('upload-success-short') }}</div>
              <div class="col-auto bp-ul-data">
                <a class="text-orange text-decoration-none" :id="'collapse-toggle-'+bp.id.toString()" data-bs-toggle="collapse" v-on:click="toggleCollapseLabel('collapse-toggle-'+bp.id.toString())" :href="'#bp-fb-'+bp.id.toString()" role="button" aria-expanded="true" :aria-controls="'bp-fb-'+bp.id.toString()"><span :id="'collapse-toggle-'+bp.id.toString()+'-label'">{{ $t('hide-extracted-data') }}</span> <i class="bi bi-arrow-bar-down collapse-icon rotate-down"></i></a>
              </div>
            </div>

            <div class="row ms-2">
              <div :id="'bp-fb-'+bp.id.toString()" class="row bg-white ul-data-collapsible collapse show">
                <p>{{ $t('extracted-data-intro') }}:</p>
                <div class="ul-data-container">
                  <table :id="'ul-result-' + bp.id.toString()" class="table table-sm">
                    <thead>
                    <tr>
                      <th v-for="field in bp.f_extract" :key="field">{{ field }}</th>
                    </tr>
                    </thead>
                    <tbody>
                    <tr v-for="row in blueprintData[bp.id.toString()].extracted_data" :key="row">
                      <td v-for="v in row" :key="v">{{ v }}</td>
                    </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>

            <div class="row ms-2">
              <div class="row bg-white pb-3 pt-3 pl-32">
                <p class="fw-bold">{{ $t('donation-question') }}</p>
                <div class="surquest-gq-response surquest-cq-response">
                  <div class="surquest-choice-item form-check">
                    <label class="form-check-label rb-cb-label" for="donate-agree">
                      <input type="radio" id="donate-agree" value="true" v-model="blueprintData[bp.id.toString()].consent" @change="emitToParent">
                       {{ $t('donation-agree') }}
                    </label>
                  </div>
                  <div class="surquest-choice-item form-check">
                    <label class="form-check-label rb-cb-label" for="donate-disagree">
                      <input type="radio" id="donate-disagree" value="false" v-model="blueprintData[bp.id.toString()].consent" @change="emitToParent">
                       {{ $t('donation-disagree') }}
                    </label>
                  </div>
                </div>
              </div>
            </div>

          </template>


          <!-- Failed -->
          <template v-if="blueprintData[bp.id.toString()].status === 'failed'">
            <div class="col-auto bp-ul-icon"><i class="bi bi-file-earmark-x-fill text-danger"></i></div>
            <div class="col-2 bp-description">{{ bp.name }}</div>
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
  </div>

</template>

<script>
import JSZip from "jszip";
import DonationInstructions from "./DonationInstructions";
import axios from "axios";


export default {
  name: 'ProcessFile',
  components: {DonationInstructions},
  props: {
    expectsZip: Boolean,
    blueprints: Array,
    instructions: Array,
    componentId: Number,
    name: String,
    exceptionUrl: String
  },
  emits: ['changedData'],
  data() {
    return {
      blueprintData: {},
      uploadStatus: 'pending',
      uploadAttempts: 0,
      generalErrors: [],
    }
  },
  created() {
    // Create dictionary to hold post data.
    this.blueprints.forEach(bp => {
      let id = bp.id;
      let blueprintInfo = {
        name_uploaded_file: null,
        consent: '',
        extracted_data: [],
        status: 'pending',
        errors: []
      }
      this.blueprintData[id.toString()] = blueprintInfo
    })
    this.resetErrorLog();
    this.emitToParent();
  },
  methods: {
    toggleCollapseLabel(elementId) {
      let element = document.getElementById(elementId);
      let label = document.getElementById(elementId.concat('-label'));
      let newLabel = '';
      if (element.getAttribute('aria-expanded') === 'true') {
        newLabel = this.$t('hide-extracted-data');
        element.getElementsByTagName('i')[0].classList.add('rotate-down');
      } else {
        newLabel = this.$t('show-extracted-data');
        element.getElementsByTagName('i')[0].classList.remove('rotate-down');
      }
      setTimeout(() => {
        label.innerHTML = newLabel;
      }, 300);
    },

    processFile(event) {
      let uploader = this;
      uploader.uploadStatus = 'processing';
      uploader.uploadAttempts += 1;
      uploader.resetErrorLog();
      const files = event.target.files;

      // Procedure if supplied file is expected to be a zip-folder.
      if (uploader.expectsZip && files.length === 1) {
        JSZip
            .loadAsync(files[0])
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
                        axios.post(uploader.exceptionUrl, {'status_code': 4199, 'message': e.message}).catch(e => console.error(`Could not post error message, ${e}`));
                        uploader.recordError(uploader.$t('error-generic') + e.message, blueprint.id.toString());
                      })
                })
                if (!reHasMatched) {
                  axios.post(uploader.exceptionUrl, {'status_code': 418, 'message': uploader.$t('error-regex-not-matched')}).catch(e => console.error(`Could not post error message, ${e}`));
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
              axios.post(uploader.exceptionUrl, {'status_code': statusCode, 'message': e.message}).catch(e => console.error(`Could not post error message, ${e}`));
              uploader.recordError(myMess, 'general');
        })
      }

      // Procedure if supplied file is expected to be a single file.
      else if (!uploader.expectsZip && files.length === 1) {

        if (uploader.blueprints[0].format === 'json') {
          if (!files[0].name.endsWith('.json')) {
            axios.post(uploader.exceptionUrl, {'status_code': 4105, 'message': uploader.$t('error-wrong-file-type', 'en', {actualType: files[0].name.substr(files[0].name.lastIndexOf(".")), expectedType: '.json'})}).catch(e => console.error(`Could not post error message, ${e}`));
            uploader.recordError(uploader.$t('error-wrong-file-type', {actualType: files[0].name.substr(files[0].name.lastIndexOf(".")), expectedType: '.json'}), uploader.blueprints[0].id.toString());
          }
        }

        // TODO: Add selection of which file they're trying to upload if multiple (i.e. a zip-upload) is expected.
        let reader = new FileReader();
        reader.onload = function(event) {
          let content = event.target.result;
          try {
            uploader.processContent(content, uploader.blueprints[0]);
          } catch(e) {
            axios.post(uploader.exceptionUrl, {'status_code': 4199, 'message': e.message}).catch(e => console.error(`Could not post error message, ${e}`));
            uploader.recordError(uploader.$t('error-generic') + e.message, uploader.blueprints[0].id.toString());
          }
        }
        reader.readAsText(files[0]);
      }

      // Procedure if files.length != 1
      else {
        axios.post(uploader.exceptionUrl, {'status_code': 4104, 'message': uploader.$t('error-multiple-files', 'en')}).catch(e => console.error(`Could not post error message, ${e}`));
        uploader.recordError(uploader.$t('error-multiple-files'), 'general');
      }

      setTimeout(() => {
        uploader.updateStatus();
        uploader.emitToParent();
        }, 1000);
    },

    processContent(content, blueprint) {
      let uploader = this;
      let blueprintID = blueprint.id.toString();
      let fileContent = null;
      let extractedData = [];

      if (blueprint.format === 'json') {
        try {
          fileContent = JSON.parse(content);
        } catch(e) {
          axios.post(uploader.exceptionUrl, {'status_code': 4106, 'message': e.message}).catch(e => console.error(`Could not post error message, ${e}`));
          uploader.recordError(uploader.$t('error-json-syntax'), uploader.blueprints[0].id.toString());
        }

        if (fileContent) {
          let nMissingFields = 0;
          fileContent.forEach(entry => {
            if (blueprint.f_expected.every(element => Object.keys(entry).includes(element))) {
              // TODO: Do filtering stuff here.

              // Pop unused keys and add to result.
              for (let key in entry) {
                if (blueprint.f_extract.indexOf(key) < 0) delete entry[key];
              }
              extractedData.push(entry);
            } else {
              nMissingFields += 1;
            }
          })
          // Log extraction error
          if (nMissingFields > 0) {
            axios.post(uploader.exceptionUrl, {'status_code': 4201, 'message': `Expected fields missing in ${nMissingFields}/${fileContent.length} entries.`}).catch(e => console.error(`Could not post error message, ${e}`))
            uploader.recordError(uploader.$t('error-expected-fields-missing'), blueprint.id.toString());
          }
          uploader.blueprintData[blueprintID].extracted_data = extractedData;
        }
      }
    },

    emitToParent() {
      // TODO: Emit extra information on the blueprint container level (e.g.: JSON.stringify({'errors_general': this.errorLog, 'ul_attempts': this.uploadAttempts, 'blueprints': this.blueprintData}))
      let dataToEmit = JSON.parse(JSON.stringify(this.blueprintData));
      Object.keys(dataToEmit).forEach(key => {
        if (dataToEmit[key].consent === 'false' | dataToEmit[key].consent === '') {
          dataToEmit[key].extracted_data = [];
        }
      })
      this.$emit('changedData', dataToEmit);
    },

    resetErrorLog() {
      this.generalErrors = [];
      for (let bp in this.blueprintData){
        this.blueprintData[bp].errors = [];
      }
    },

    recordError(e, target) {
      if (target == 'general') {
        this.generalErrors.push(e)
      } else {
        this.blueprintData[target].errors.push(e);
      }
    },

    updateStatus() {
      let bpErrorCount = 0;
      let nBlueprints = Object.keys(this.blueprintData).length
      for (let bp in this.blueprintData){
        if (this.blueprintData[bp].errors.length) {
          this.blueprintData[bp].status = 'failed';
          bpErrorCount += 1;
        } else {
          this.blueprintData[bp].status = 'success';
        }
      }

      if (!this.generalErrors.length && bpErrorCount === 0) {
        this.uploadStatus = 'success';
      } else if (!this.generalErrors.length && (bpErrorCount < nBlueprints)) {
        this.uploadStatus = 'partial';
      } else {
        this.uploadStatus = 'failed';
        for (let bp in this.blueprintData){
          this.blueprintData[bp].status = 'failed';
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
  background-color: #efefef;
  color: black;
  border-bottom: none;
}
.accordion-button:not(.collapsed)::after {
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16' fill='%23212529'%3e%3cpath fill-rule='evenodd' d='M1.646 4.646a.5.5 0 0 1 .708 0L8 10.293l5.646-5.647a.5.5 0 0 1 .708.708l-6 6a.5.5 0 0 1-.708 0l-6-6a.5.5 0 0 1 0-.708z'/%3e%3c/svg%3e");
}
.accordion-item,
.accordion-button,
.accordion-item:first-of-type {
  border-radius: 0 !important;
}
.form-check-label,
.form-check-input {
  cursor: pointer;
}
.form-check-input {
  margin-top: 0;
}
.ul-success {
  background-color: #55ff5517;
}
.ul-partial {
  background-color: rgba(255, 170, 85, 0.09);
}
.ul-failed {
  background-color: #f8d7da;
}
.fb-modal {
  max-width: 80%;
  height: 80%;
}
.modal-body-data {
  overflow: auto;
  max-height: 400px;
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
.ul-data-collapsible {
  padding: 10px 0px 0px 32px;
  font-size: 0.9rem;
}
.ul-data-container {
  display: block;
  max-height: 500px;
  overflow-y: scroll;
}
.ul-data-container th {
  position: sticky;
  top: 0;
  z-index: 1;
  background-color: white !important;
  box-shadow: 0px 1px black;
}
.collapse-icon {
  display: inline-block;
  transition:all 0.3s ease-out;
  transform: rotate(0deg);
  -moz-transform:rotate(0deg);
  -webkit-transform: rotate(0deg);
}
.rotate-down {
  transform: rotate(180deg) !important;
  -moz-transform:rotate(180deg) !important;
  -webkit-transform: rotate(180deg) !important;
}
.pl-32 {
  padding-left: 32px;
}
</style>
