<i18n src="./translations/uploader_app.json"></i18n>

<template>

  <FileUploader
      v-for="(uploadConfig, id) in parsedUploadConfig"
      :key="id"
      :component-id="id"
      :expects-zip="uploadConfig.upload_type === 'zip file'"
      :name="uploadConfig.name"
      :blueprints="uploadConfig.blueprints"
      :instructions="uploadConfig.instructions"
      :exception-url="this.exceptionUrl"
      :combined-consent="uploadConfig.combined_consent"
      @changedData="updatePostData"
  ></FileUploader>

  <div class="row">
    <div class="col">
      <button
          class="flow-btn"
          type="button"
          @click="processData(false)"
      >{{ $t('next-btn-label') }}&nbsp;&nbsp;&#8250;</button>
    </div>
  </div>

  <div class="modal custom-modal" id="processingModal" ref="processingModal" style="display: none">
    <div class="modal-dialog modal-dialog-centered custom-modal-container">
      <div class="modal-content fs-1 text-center custom-modal-content">
        <div class="p-3 modal-message">{{ $t('data-submit-wait') }}</div>
        <div class="dot-floating"></div>
      </div>
    </div>
  </div>

  <div class="default-modal" id="infoModal" ref="infoModal" style="display: none">
    <div class="modal-body d-flex flex-row align-items-center pt-5">
      <div class="ps-2 pe-3 color-blue"><i class="bi bi-info-circle-fill fs-1"></i></div>
      <div>{{ this.infoModalMsg }}</div>
    </div>
    <div class="modal-footer">
      <button class="ddm-btn" type="button" id="closeInfoModal" @click="closeInfoModal">OK</button>
    </div>
  </div>

  <div class="default-modal" id="statusModal" ref="statusModal" style="display: none">
    <div class="modal-body d-flex flex-row align-items-center pt-5">
      <div class="ps-2 pe-3 color-blue"><i class="bi bi-info-circle-fill fs-1"></i></div>
      <div id="statusModalMsg" ref="statusModalMsg"></div>
    </div>
    <div class="modal-footer">
      <button class="ddm-btn" type="button" id="cancelStatusModal" @click="closeStatusModal">{{ $t('cancel-label') }}</button>
      <button class="ddm-btn" type="button" id="closeStatusModal" @click="processData(true)">{{ $t('continue-anyway-label') }}</button>
    </div>
  </div>

  <div class="modal-backdrop" ref="modalBackdrop" style="display: none"></div>

</template>

<script>
import FileUploader from './components/FileUploader.vue'
import JSZip from 'jszip'

export default {
  name: 'UApp',
  components: {
    FileUploader
  },
  props: {
    uploadConfig: String,
    actionUrl: String,
    exceptionUrl: String,
    language: String
  },
  data() {
    this.$i18n.locale = this.language;
    return {
      parsedUploadConfig: JSON.parse(this.uploadConfig),
      postData: {},
      locale: this.language,
      donationStatus: 0,
      infoModalMsg: 'undefined'
    }
  },
  watch: {
    locale (val){
      this.$i18n.locale = val
    }
  },
  methods: {
    updatePostData(data) {
      Object.keys(data).forEach(key => {
        this.postData[key] = data[key]
      })
    },

    /**
     * Evaluates the donation status
     */
    getStatus() {
      // loop through postData
      let success = [];
      let failed = [];
      let pending = [];
      Object.keys(this.postData).forEach(entry => {
        switch (this.postData[entry].status) {
          case 'success':
            success.push(this.postData[entry]);
            break;
          case 'failed':
            failed.push(this.postData[entry]);
            break;
          case 'nothing extracted':
            failed.push(this.postData[entry]);
            break;
          case 'pending':
            pending.push(this.postData[entry]);
        }
      });

      // Case 1: No upload attempted
      if (!success.length && !failed.length && pending.length) {
        this.donationStatus = 1;
      }
      // Case 2: No upload, not all attempted
      else if(!success.length && pending.length && failed.length) {
        this.donationStatus =  2;
      }
      // Case 3: No upload, all attempted
      else if (!success.length && !pending.length) {
        this.donationStatus =  3;
      }
      // Case 4: Partial Upload, not all attempted
      else if (success.length && pending.length) {
        this.donationStatus =  4;
      }
      // Case 5: Partial upload, all attempted
      else if (success.length && !pending.length && failed.length) {
        this.donationStatus =  5;
      }
      // Case 6: All uploaded
      else if (success.length && !pending.length && !failed.length) {
        this.donationStatus =  6;
      }
    },

    /**
     * Checks if consent question has been answered for all blueprints.
     */
    consentValid() {
      let consents = [];
      Object.keys(this.postData).forEach(entry => {
        if (this.postData[entry].status !== 'pending') {
          consents.push(this.postData[entry].consent);
        }
      });

      if (consents.includes(null) === true) {
        this.$refs.processingModal.style.display = 'none';
        this.infoModalMsg = this.$t('consent-error-msg');
        this.$refs.infoModal.style.display = 'block';
        return false;
      }
      return true;
    },

    /**
     * Sets consent to false in postData where consent is null.
     * This is necessary because the server will only accept Boolean values for
     * consent.
     */
    cleanConsent() {
      Object.keys(this.postData).forEach(entry => {
        if (this.postData[entry].consent == null) {
          this.postData[entry].consent = false;
        }
      })
    },

    /**
     * Processes the uploaded data.
     */
    processData(skipStatus=false) {
      // Show processing overlay.
      this.$refs.statusModal.style.display = 'none'
      this.$refs.processingModal.style.display = 'block';
      this.$refs.modalBackdrop.style.display = 'block';

      // Check consent data.
      if (!this.consentValid()) return;

      if (!skipStatus) {
        // Determine donation status across all donation blueprints.
        this.getStatus();
        if (this.donationStatus === 1) {  // means no upload attempted.
          this.$refs.processingModal.style.display = 'none';
          this.$refs.statusModalMsg.innerHTML = this.$t('status-info-msg-none-attempted');
          this.$refs.statusModal.style.display = 'block';
          return;
        }

        if (this.donationStatus === 2 || this.donationStatus === 4) {  // means not all uploads attempted.
          this.$refs.processingModal.style.display = 'none';
          this.$refs.statusModalMsg.innerHTML = this.$t('status-info-msg-not-all-attempted');
          this.$refs.statusModal.style.display = 'block';
          return;
        }
      }

      // Zip and send data to server.
      this.zipData();
    },

    /**
     * Zips the data and sends them to the server.
     */
    zipData() {
      // Clean consent data.
      this.cleanConsent();

      // Disable file inputs.
      let fileInputs = document.querySelectorAll("input[type=file]")
      fileInputs.forEach(fi => {
        fi.disabled = true;
      })

      // Zip uploaded and processed data and attach it to form.
      let form = new FormData(document.getElementById("uploader-form"));
      let zip = new JSZip();

      zip.file("ul_data.json", JSON.stringify(this.postData))
          .generateAsync({
            type: "blob",
            compression: "DEFLATE",
            compressionOptions: {
              level: 5
            }
          })
          .then(blob => {
            form.append("post_data", blob);

            fetch(this.actionUrl, {method: "POST", body: form})
                .then(response => {
                  if (response.redirected) {
                    window.location.href = response.url;
                  }
                })
                .catch(err => {
                  console.info(err);
                });
          })
    },

    closeInfoModal() {
      this.$refs.infoModal.style.display = 'none';
      this.$refs.modalBackdrop.style.display = 'none';
    },

    closeStatusModal() {
      this.$refs.statusModal.style.display = 'none';
      this.$refs.modalBackdrop.style.display = 'none';
    }
  },

}
</script>

<style>
#uapp {
  font-family: 'Nunito Sans', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}
.default-modal {
  background: white;
  z-index: 2000;
  position: fixed;
  top: 35%;
  margin-left: auto;
  margin-right: auto;
  left: 0;
  right: 0;
  width: 30%;
  border-radius: 5px;
}

@media (max-width: 768px) {
  .default-modal {
    width: 85%;
    top: 5%;
    max-height: 90%;
    overflow-y: scroll;
  }
}

@media (min-width: 769px) {
  .default-modal {
    width: 50%;
  }
}

.modal-backdrop {
  position: fixed;
  height: 100%;
  width: 100%;
  background: #959595;
  opacity: .75;
  z-index: 1000;
}
.custom-modal-container {
  width: 100%;
  max-width: none;
  animation: fade-in-right ease 0.6s forwards;
}
.custom-modal-content {
  background: #212529 !important;
  color: white !important;
  border: none;
  border-radius: 0px;
  font-size: 2.5rem !important;
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  overflow: hidden;
  padding-bottom: 30px;
  box-shadow: 0px 3px #ffffff17;
}
@keyframes fade-in-right {
  from {
    opacity: 0;
    transform: translateX(-15px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.dot-floating {
  position: relative;
  width: 12px;
  height: 12px;
  border-radius: 6px;
  background-color: #009c94;
  color: #009c94;
  animation: dotFloating 3s infinite cubic-bezier(0.15, 0.6, 0.9, 0.1);
}

.dot-floating::before, .dot-floating::after {
  content: '';
  display: inline-block;
  position: absolute;
  top: 0;
}

.dot-floating::before {
  left: -14px;
  width: 12px;
  height: 12px;
  border-radius: 6px;
  background-color: #009c94;
  color: #009c94;
  animation: dotFloatingBefore 3s infinite ease-in-out;
}

.dot-floating::after {
  left: -26px;
  width: 12px;
  height: 12px;
  border-radius: 6px;
  background-color: #009c94;
  color: #009c94;
  animation: dotFloatingAfter 3s infinite cubic-bezier(0.4, 0, 1, 1);
}

.ddm-btn {
  background-color: #1a1a1a;
  color: white !important;
  border-radius: 5px;
  border: 1px solid #8e8e8e;
  padding: 3px 10px !important;
  font-size: 0.9rem;
  text-decoration: none;
}

.color-blue {
  color: #0068b3;
}

@keyframes dotFloating {
  0% {
    left: calc(-50% - 5px);
  }
  75% {
    left: calc(50% + 105px);
  }
  100% {
    left: calc(50% + 105px);
  }
}

@keyframes dotFloatingBefore {
  0% {
    left: -50px;
  }
  50% {
    left: -14px;
  }
  75% {
    left: -50px;
  }
  100% {
    left: -50px;
  }
}

@keyframes dotFloatingAfter {
  0% {
    left: -100px;
  }
  50% {
    left: -26px;
  }
  75% {
    left: -100px;
  }
  100% {
    left: -100px;
  }
}
</style>
