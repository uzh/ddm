<i18n src="./translations/uploader_app.json"></i18n>

<template>

    {{ postData }}

  <FileUploader
      v-for="(uploadConfig, id) in parsedUploadConfig"
      :key="id"
      :component-id="id"
      :expects-zip="uploadConfig.upload_type === 'zip file'"
      :name="uploadConfig.name"
      :blueprints="uploadConfig.blueprints"
      :instructions="uploadConfig.instructions"
      :exception-url="this.exceptionUrl"
      @changedData="updatePostData"
  ></FileUploader>

  <div class="row">
    <div class="col">
      <button
          class="flow-btn"
          type="button"
          @click="zipData"
      >{{ $t('next-btn-label') }}&nbsp;&nbsp;&#8250;</button>
    </div>
  </div>
  <!-- data-bs-toggle="modal"
  data-bs-target="#overlayModal" -->
  <div class="modal custom-modal" id="overlayModal" data-bs-backdrop="static" data-bs-keyboard="false" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered custom-modal-container">
      <div class="modal-content fs-1 text-center custom-modal-content">
        <div class="p-3 modal-message">{{ $t('data-submit-wait') }}</div>
        <div class="dot-floating"></div>
      </div>
    </div>
  </div>

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
    language: String,
  },
  data() {
    this.$i18n.locale = this.language;
    return {
      parsedUploadConfig: JSON.parse(this.uploadConfig),
      postData: {},
      locale: this.language,
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
     * Checks if the consent question for all files has been answered.
     * If not, displays a message to the user.
     */
    checkConsent() {
      // loop through postData
      let success = [];
      let failed = [];
      let pending = [];
      let consents = [];
      let stati = [];
      Object.keys(this.postData).forEach(entry => {
        consents.push(this.postData[entry].consent);
        stati.push(this.postData[entry].status);

        switch (this.postData[entry].status) {
          case 'success':
            success.push(this.postData[entry]);
            break;
          case 'failed':
            failed.push(this.postData[entry]);
            break;
          case 'pending':
            pending.push(this.postData[entry]);
        }
      });

      // Case 1: No upload attempted
      if (!success.length && !failed.length && pending.length) {
        console.log('No upload attempted');
      }

      // Case 2: No upload, not all attempted
      if(!success.length && pending.length && failed.length) {
        console.log('No upload, not all attempted')
      }

      // Case 3: No upload, all attempted
      if (!success.length && !pending.length) {
        console.log('No upload, but attempted');
      }

      // Case 4: Partial Upload, not all attempted
      if (success.length && pending.length) {
        console.log('Partial Upload, not all attempted');
      }

      // Case 5: Partial upload, all attempted
      if (success.length && !pending.length && failed.length) {
        console.log('Partial upload, all attempted');
      }

      // Case 6: All uploaded
      if (success.length && !pending.length && !failed.length) {
        console.log('All uploaded');
      }
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
     * Zips the data and sends them to the server.
     */
    zipData() {
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
          .generateAsync({type: "blob"})
          .then(blob => {
            form.append("post_data", blob);

            fetch(this.actionUrl, {method: "POST", body: form})
                .then(response => {
                  console.log(response)
                  if (response.redirected) {
                    window.location.href = response.url;
                  }
                })
                .catch(err => {
                  console.info(err);
                });
          })
    }
  },

}
</script>

<style>
#uapp {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
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
