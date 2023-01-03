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
      @changedData="updatePostData"
  ></FileUploader>

  <div class="row">
    <div class="col">
      <button
          class="flow-btn"
          type="button"
          data-bs-toggle="modal"
          data-bs-target="#overlayModal"
          @click="zipData"
      >{{ $t('next-btn-label') }}&nbsp;&nbsp;&#8250;</button>
    </div>
  </div>

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
    zipData() {
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
  justify-content: flex-end;
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
