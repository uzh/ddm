<template>

  <div class="ul-block mb-3">
    <div class="ul-row row float-left bg-dark text-white pt-2 rounded-top">
      <div class="col-sm">
        <h4>Upload File {{ ul_id }}</h4>
      </div>
      <div class="col-sm">
        <input
            :id="'ul-' + ul_id"
            :name="'ul-' + ul_id"
            type="file"
            @change="ProcessFile"
            :class="{ 'd-none': !extraction_pending}"
        >
        <p class="float-right" :class="{ 'd-none': extraction_pending }">
          <span class="badge bg-success fs-6">Sie haben Ihre Daten erfolgreich hochgeladen!</span></p>
      </div>
    </div>

    <div class="ul-result row float-left bg-light text-black pt-2" :class="{ 'd-none': extraction_pending }">
      <p class="fs-5">Die folgenden Daten wurden aus der hochgeladenen Datei ausgelesen:</p>
      <div class="result-table table-responsive">
        <table :id="'ul-result-' + ul_id" class="table table-striped fs-6 text">
          <tr>
            <th v-for="field in fields_to_extract" :key="field">{{ field }}</th>
          </tr>
          <tr v-for="row in row_data" :key="row">
            <td v-for="v in row" :key="v">{{ v }}</td>
          </tr>
        </table>
      </div>
    </div>

    <div class="row bg-dark text-white p-3 px-4 fs-5 rounded-bottom" :class="{ 'd-none': extraction_pending }">
      <div class="form-check">
        <input class="form-check-input" type="checkbox" v-model="consent" :id="'ul-consent-' + ul_id">
        <label class="form-check-label" :for="'ul-consent-' + ul_id">
          Ich bin damit einverstanden, diese Daten zu übermitteln.
        </label>
      </div>
    </div>

    <input class="d-none" :name="'data-ul-' + ul_id" :value="post_data">

  </div>

</template>

<script>
export default {
  name: "ProcessFile",
  props: {
    ul_id: Number,
    format: String,
    expected_fields: Array,
    fields_to_extract: Array
  },
  data() {
    return {
      row_data: [],
      extraction_pending: true,
      status: {
        msg: 'not processed',
        errors: []
      },
      consent: false
    }
  },
  computed: {
    post_data() {
      let ul_data = [];
      if (this.consent) {
        ul_data = this.row_data;
      }
      return JSON.stringify({
        id: this.ul_id,
        status: this.status,
        data: ul_data,
        consent: this.consent
      })
    }
  },
  methods: {
    ProcessFile(event) {
      let vm = this;
      const file = event.target.files[0];
      const reader = new FileReader();

      reader.onload = function(event) {
        let fileContent = JSON.parse(event.target.result);
        for (let i = 0; i < fileContent.length; i++) {
          if (vm.expected_fields.every(element => Object.keys(fileContent[i]).includes(element))) {

            // pop unused keys
            for (let k in fileContent[i]) {
              if (vm.fields_to_extract.indexOf(k) < 0) {
                delete fileContent[i][k];
              }
            }
            // add to result
            vm.row_data.push(fileContent[i]);

          } else {
            // Add error message
            vm.status.errors.push('some error');
          }
        }
      }
      reader.readAsText(file);

      // update status
      vm.extraction_pending = false;
      vm.status.msg = 'success';
    },
  }
}
</script>

<style scoped>
.result-table {
  max-height: 300px;
}
</style>