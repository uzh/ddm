<template>
  <h1>Uploader App</h1>
  <!--
  ul_config = [
    {'ul_type': 'zip',
     'blueprints': [
       {'id': 1, 'format': 'json', 'f_expected': ['field_A', 'field__B'], 'f_extract: ['field_A'], 'regex_path':"regex"},
       {...}
    },
    {'ul_type': 'singlefile',
    'blueprints': [{'id': 1, 'format': 'json', 'f_expected': ['field_A', 'field__B'], 'f_extract': ['field_A'], 'regex_path':''}
    ]}
     ]
  ]
  -->

  <div>ul_config: {{ ul_config }}</div>

  <FileUploader
      v-for="(uploadConfig, id) in ul_config"
      :key="id"
      :zipped="uploadConfig.ul_type === 'zip'"
      :blueprints="uploadConfig.blueprints"
  ></FileUploader>

  <input id="zipped-ul" name="zipped-ul" class="d-none">
  <div class="row float-right">
    <button
        class="btn btn-success fs-5 w-25"
        type="submit"
        @click="zipData"
    >Daten übermitteln</button>
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
    uploadconfig: String,
  },
  data() {
    return {
      ul_config: JSON.parse(this.uploadconfig),
    }
  },
  methods: {
    zipData() {
      let ul_data_inputs = document.querySelectorAll('input[name^=data-ul-]');
      window.alert("something happened.")
      let ul_data = [];
      for (let i=0; i < ul_data_inputs.length; i++) {
        let ul = ul_data_inputs[i];
        ul_data.push(ul.value);
      }

      // zip and include in input
      let zip = new JSZip();
      zip.file("ul_data.json", ul_data);
      let content = zip.generate({
        type: "blob",
        compression: "DEFLATE"
      });

      // let ul_form = document.getElementById("uploader-form");
      let form = new FormData() // FormData(ul_form);
      form.append("zipped_data", content, "data.zip");

      let httpRequest = new XMLHttpRequest();
      httpRequest.send(form);
      return(false);
    }
  },
  mounted() {
    document.getElementById("uploader-form").addEventListener("submit", this.zipData, false);
  }
}
</script>

<style>
#uapp {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
