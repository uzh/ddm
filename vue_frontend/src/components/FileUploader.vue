<template>

  <div class="bg-info p-2 mb-2 rounded">
    <h4>Variable overview (development)</h4>
    <div>zipped: {{ zipped }}</div>
    <div>blueprints: {{ blueprints }}</div>
    <div>post_data: {{ post_data }}</div>
  </div>

  <!-- File Upload Section (either single file or zip level). -->

  <div class="ul-block container mb-3" :class="{ 'ul-success': extraction_complete}">
    <div class="ul-row row float-left bg-dark text-white pt-2 rounded-top">
      <div class="col-sm">
        <h4>Upload File {{ ul_id }}</h4>
      </div>
      <div class="col-sm">
        <input
            :name="'ul-' + ul_id"
            type="file"
            @change="processFile"
            :class="{ 'd-none': extraction_complete}"
        >
        <p class="float-right" :class="{ 'd-none': !extraction_complete }">
          <span class="badge bg-success fs-6">Upload abgeschlossen.</span>
        </p>
      </div>
    </div>


    <!-- Create div for each blueprint -->
    <div
        v-for="bp in blueprints"
        :key="bp"
        :set="bp_index = bp.id.toString()"
        class="row rounded"
        > <!-- :class="{ 'd-none': !post_data[bp_index].status.ul_complete }" -->

      <!-- Upload Feedback Section (single file level). -->
      <div class="ul-feedback col bg-primary">
        <p>Daten erfolgreich verarbeitet.</p>

        <p>Daten anschauen -> link to popup</p>

        <div class="result-table table-responsive">
          <table :id="'ul-result-' + bp_index" class="table table-striped fs-6 text">
            <tr>
              <th v-for="field in bp.f_extract" :key="field">{{ field }}</th>
            </tr>
            <tr v-for="row in post_data[bp_index].extracted_data" :key="row">
              <td v-for="v in row" :key="v">{{ v }}</td>
            </tr>
          </table>
        </div>

      </div>

      <!-- Consent Section (single file level). -->
      <div class="ul-consent col bg-light">
        <input class="form-check-input" type="checkbox" v-model="post_data[bp_index].consent" :id="'ul-consent-' + bp_index">
        <label class="form-check-label" :for="'ul-consent-' + bp_index">
          Ich bin damit einverstanden, diese Daten zu übermitteln.
        </label>
      </div>
    </div>

    <!-- Hidden input holding the post data (single file level).
    <input :name="'data-ul-' + bp_index" :value="get_post_data()" class="d-none" >-->

  </div>

</template>

<script>
import JSZip from "jszip";

export default {
  name: "ProcessFile",
  props: {
    zipped: Boolean,
    blueprints: Array
  },
  data() {
    return {
      row_data: [],
      ul_id: -1, // move to result array?
      extraction_complete: false, // move to result array?
      post_data: {}
    }
  },
  created() {
    // Check if ul_id should be handled here.

    // Create dictionary to hold post data.
    this.blueprints.forEach(bp => {
      let id = bp.id;
      this.post_data[id.toString()] = {
        filename: null,
        consent: false,
        extracted_data: [],
        status: {
          ul_complete: false,
          errors: []
        }
      }
    })
  },
  computed: {
    // get_post_data(bp_index) {
    //   console.log(bp_index);
    //   let bp_data = this.post_data[bp_index];
    //
    //   let ul_data = [];
    //   if (bp_data.consent) {
    //     ul_data = bp_data.extracted_data;
    //   }
    //   return JSON.stringify({
    //     id: bp_index,
    //     status: bp_data.status,
    //     consent: bp_data.consent,
    //     data: ul_data
    //   })
    // }
  },
  methods: {
    processFile(event) {
      let vm = this;
      const files = event.target.files;

        // check if zip
        if (vm.zipped && files.length === 1) {
          let zip = new JSZip();
          zip.loadAsync(files[0]).then(function (z) {
            vm.blueprints.forEach(bp => {
              let re = new RegExp(bp.regex_path);
              let re_match = z.file(re);
              console.log(re_match);
              if (re_match !== null) {
                z.file(re).async("string").then(c => {
                  vm.processContent(c, bp);
                }).catch({

                })
              }
            })
          }).catch({
            // selection of which file they're trying to upload
            // raise error
          })
        } else if (!this.zipped && files.length === 1) {
          // selection of which file they're trying to upload
          // let reader = new FileReader();
          // reader.onload = function(event) {
          let bp = vm.blueprints[0]
          vm.processContent(files[0], bp);
          // }
          // reader.readAsText(files[0]);
        } else {
          // selection of which files they're trying to upload
          // raise error to you
        }
    },

    processContent(file, bp) {
      let vm = this;
      let bp_post = vm.post_data[bp.id.toString()]

      let reader = new FileReader();
      reader.onload = function(event) {
        if (bp.format === 'json') {

          let content = event.target.result;
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
              // Add error message.
              bp_post.status.errors.push('some error');
            }
          })
        }
      }
      reader.readAsText(file);

      // TODO: update status
    },
  }
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