<template>

  <!-- File Upload Section (either single file or zip level). -->
  <div class="ul-block container mb-3" :class="{ 'ul-success': extraction_complete}">
    <div class="ul-row row float-left bg-dark text-white pt-2 rounded-top">
      <div class="col-sm">
        <h4>Upload File {{ comp_id }}</h4>
      </div>
      <div class="col-sm">
        <input :name="'ul-' + comp_id"
               type="file"
               @change="processFile"
               :class="{ 'd-none': extraction_complete}">
        <p class="float-right" :class="{ 'd-none': !extraction_complete }">
          <span class="badge bg-success fs-6">Upload abgeschlossen.</span>
        </p>
      </div>
    </div>

    <!-- Create div for each blueprint -->
    <div v-for="bp in blueprints"
         :key="bp"
         :set="bp_index = bp.id.toString()"
         class="row rounded">
      <!-- :class="{ 'd-none': !post_data[bp_index].status.ul_complete }" -->

      <!-- Upload Feedback Section (single file level). -->
      <div class="ul-feedback col bg-primary">
        <p>Daten erfolgreich verarbeitet.</p>

        <p>Daten anschauen -> link to popup</p>

        <div class="result-table table-responsive">
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

      <!-- Consent Section (single file level). -->
      <div class="ul-consent col bg-light">
        <input class="form-check-input"
               :id="'ul-consent-' + bp_index"
               type="checkbox"
               @change="emitToParent"
               v-model="post_data[bp.id.toString()].consent">
        <label class="form-check-label"
               :for="'ul-consent-' + bp_index">
          Ich bin damit einverstanden, diese Daten zu übermitteln.
        </label>
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
      post_data: {}
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
    },

    processContent(content, bp) {
      let vm = this;
      let bp_post = vm.post_data[bp.id.toString()];

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
              bp_post.extracted_data.push(entry);

            } else {
              // Add error message TODO: adjust this to something meaningful.
              bp_post.status.errors.push('some error');
            }
          })
        }

      // TODO: update status
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
.result-table {
  max-height: 300px;
}
.ul-success {
  border: 5px solid green;
  border-radius: .25rem;
}
</style>