<template>

  <div class="mb-5">
    <div class="float-left bg-dark text-white pt-2 ps-2 pb-1 rounded-top">
      <div class="col-sm">
        <h4>Upload File {{ comp_id }}</h4>
      </div>
    </div>

    <div class="accordion" :id="'ul-acc-'+comp_id">
      <div class="accordion-item">

        <!-- Instruction Section -->
        <h3 class="accordion-header" :id="'acc-instr-head-'+comp_id">
          <button class="accordion-button" type="button" data-bs-toggle="collapse" :data-bs-target="'#acc-instr-body-'+comp_id" aria-expanded="true" :aria-controls="'acc-instr-body-'+comp_id">
            <b>Instruktionen</b>
          </button>
        </h3>

        <div :id="'acc-instr-body-'+comp_id" class="accordion-collapse collapse show" aria-labelledby="headingOne" :data-bs-parent="'#ul-acc-'+comp_id">
          <div class="accordion-body">Tatsächliche Instruktionen</div>
        </div>

      </div>
  </div>

    <!-- Data Upload Section -->
    <div class="accordion-body border" :class="{ 'ul-success': extraction_complete}">
      <div class="row">

        <div class="col">
          <p class="accordion-header mb-0">
            <span :class="{ 'd-none': !upload_enabled & extraction_complete | processing | extraction_complete }"><b>Datei hochladen:</b></span>
            <span :class="{ 'd-none': !upload_enabled & extraction_complete | processing | !extraction_complete }"><b>Andere Datei hochladen:</b></span>

            <span class="fs-6 text-success" :class="{ 'd-none': upload_enabled & extraction_complete | processing | !extraction_complete }"><b>Upload erfolgreich abgeschlossen</b></span>
            <span :class="{ 'd-none': upload_enabled & extraction_complete | processing | !extraction_complete }">
              <a @click="upload_enabled = !upload_enabled" class="upload-other">eine andere Datei auswählen</a>
            </span>

            <span :class="{ 'd-none': !upload_enabled | processing }">
              <label class="select-file-btn">
              <input :name="'ul-' + comp_id"
                     type="file"
                     @change="processFile"
                     class="d-none">
              Datei Auswählen
            </label>
            </span>


          </p>

          <div class="clearfix" :class="{ 'd-none': !processing }">
            <p>
              <span class="spinner-border float-right me-3" role="status"><span class="sr-only"></span></span>
              Datei wird hochgeladen...
            </p>
          </div>

        </div>

      </div>
    </div>

    <!-- Upload Feedback Section -->
    <div class="accordion-body border">
      <div class="pb-2">
        <b>Ausgelesene Dateien:</b> <span :class="{ 'd-none': extraction_complete }">Es wurden noch keine Daten ausgelesen.</span>
      </div>

      <div
          v-for="bp in blueprints"
          :key="bp"
          :set="bp_index = bp.id.toString()"
          :id="'bp-entry-'+bp_index"
          class="ul-status row border-top pt-2 pb-2"
        >
          <div class="col">
            <p>
              Datei {{ bp.id }}:
              <span :class="{ 'd-none': extraction_complete }">Noch nicht hochgeladen</span>
              <span :class="{ 'd-none': !extraction_complete }">Erfolgreich hochgeladen</span>
            </p>
          </div>

          <div class="col" :class="{ 'd-none': !extraction_complete }">
            <a class="text-orange text-decoration-none" role="button" data-bs-toggle="modal" :href="'#bp-fb-'+bp_index" :aria-controls="'bp-fb-'+bp_index">Ausgelesene
              Daten ansehen &#8599;</a>
          </div>

          <div class="col-6 text-end" :class="{ 'd-none': !extraction_complete }">
            <p>
              <label class="form-check-label"
                     :for="'ul-consent-' + bp_index">
                <input class="form-check-input consent-checkbox"
                       :id="'ul-consent-' + bp_index"
                       type="checkbox"
                       @change="emitToParent"
                       v-model="post_data[bp.id.toString()].consent">
                &nbsp;Ich bin damit einverstanden, diese Daten zu übermitteln
              </label>
            </p>
          </div>

        </div>
    </div>
  </div>


  <!-- Data Overview Modals -->
  <div v-for="bp in blueprints"
       :key="bp"
       :set="bp_index = bp.id.toString()"
       class="modal fade"
       :id="'bp-fb-'+bp_index"
       tabdindex="-1"
       :aria-labelledby="'bp-fb-'+bp_index"
       aria-hidden="true"
  >
    <div class="modal-dialog fb-modal">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Feedback for XY</h5>
        </div>

        <div class="modal-body">
          <div class="modal-body-intro">
            <p>Die folgenden Daten wurden ausgelesen und werden bei Ihrer Zustimmung an die Forschenden übermittelt:</p>
          </div>
          <div class="modal-body-data">
            <table :id="'ul-result-' + bp_index" class="table table-striped fs-6 text">
              <tr>
                <th v-for="field in bp.f_extract" :key="field">{{ field }}</th>
              </tr>
              <tr v-for="row in post_data[bp.id.toString()].extracted_data" :key="row">
                <td v-for="v in row" :key="v">{{ v }}</td>
              </tr>
            </table>
          </div>
        </div>

        <div class="modal-footer">
          <div>
            <label class="form-check-label fs-5 me-4"
                   :for="'ul-consent-' + bp_index">
            <input class="form-check-input consent-checkbox mt-1"
                   :id="'ul-consent--' + bp_index"
                   type="checkbox"
                   @change="emitToParent"
                   v-model="post_data[bp.id.toString()].consent">
              &nbsp;Ich bin damit einverstanden, diese Daten zu übermitteln
            </label>
          </div>
          <div>
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">OK</button>
          </div>
        </div>

      </div>
    </div>

  </div>

</template>

<script>
import JSZip from "jszip";

export default {
  name: "ProcessFile",
  props: {
    zipped: Boolean,
    blueprints: Array,
    comp_id: Number
  },
  emits: ["changedData"],
  data() {
    return {
      row_data: [],
      extraction_complete: false, // move to result array?
      post_data: {},
      processing: false,
      upload_enabled: true
    }
  },
  created() {
    // Create dictionary to hold post data.
    this.blueprints.forEach(bp => {
      let id = bp.id;
      let bp_data = {
        filename: null,
        consent: false,
        extracted_data: [],
        status: {
          ul_complete: false,
          errors: []
        }
      }
      this.post_data[id.toString()] = bp_data
    })
    this.emitToParent();
  },
  methods: {
    processFile(event) {
      let vm = this;
      vm.processing = true;
      const files = event.target.files;

        // Check if is zip.
        if (vm.zipped && files.length === 1) {
          let zip = new JSZip();
          zip.loadAsync(files[0]).then(function (z) {
            vm.blueprints.forEach(bp => {
              let re = new RegExp(bp.regex_path);

              z.file(re).forEach(f => {
                f.async("string").then(c => {
                  vm.processContent(c, bp);
                }) // TODO: Catch error.
              })

            })
          }).catch({
            // TODO: raise error
          })
        } else if (!this.zipped && files.length === 1) {
          // TODO: Add selection of which file they're trying to upload
          let bp = vm.blueprints[0]
          vm.processSingleFile(files[0], bp)

        } else {
          // TODO: raise error to you
        }
      vm.emitToParent();
      setTimeout(() => {
        vm.extraction_complete = true;
        vm.processing = false;
        vm.upload_enabled = false;
        }, 2000);
    },

    processContent(content, bp) {
      let vm = this;
      let bp_post = vm.post_data[bp.id.toString()];
      let new_extracted_data = []

        if (bp.format === 'json') {

          let fileContent = JSON.parse(content);
          fileContent.forEach(entry => {

            if (bp.f_expected.every(element => Object.keys(entry).includes(element))) {
              // Pop unused keys and add to result.
              for (let key in entry) {
                if (bp.f_extract.indexOf(key) < 0) {
                  delete entry[key];
                }
              }
              new_extracted_data.push(entry);

            } else {
              // Add error message TODO: adjust this to something meaningful.
              bp_post.status.errors.push('some error');
            }
          })
          bp_post.extracted_data = new_extracted_data;
        }

      // Update status
      if (bp_post.status.errors.length == 0) {
        bp_post.status.ul_complete = true;
      }
    },
    processSingleFile(file, bp) {
      let vm = this;
      let reader = new FileReader();
      reader.onload = function(event) {
        let content = event.target.result;
        vm.processContent(content, bp);
      }
      reader.readAsText(file);
    },
    emitToParent() {
      let emit_data = JSON.parse(JSON.stringify(this.post_data));
      Object.keys(emit_data).forEach(key => {
        if (!emit_data[key].consent) {
          emit_data[key].extracted_data = []
        }
      })
      this.$emit('changedData', emit_data);
    },
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
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16' fill='%23212529'%3e%3cpath fill-rule='evenodd' d='M1.646 4.646a.5.5 0 0 1 .708 0L8 10.293l5.646-5.647a.5.5 0 0 1 .708.708l-6 6a.5.5 0 0 1-.708 0l-6-6a.5.5 0 0 1 0-.708z'/%3e%3c/svg%3e");;
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
.fb-modal {
  max-width: 80%;
  height: 80%;
}
.modal-body-data {
  overflow: auto;
  max-height: 400px;
}
</style>
