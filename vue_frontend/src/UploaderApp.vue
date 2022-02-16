<template>
  <h1>Uploader App</h1>
  <div>POST DATA: {{ post_data }}</div>
  <div>Action URL: {{ actionurl }}</div>
  <div><br><br></div>

  <FileUploader
      v-for="(uploadConfig, id) in ul_config"
      :key="id"
      :comp_id="id"
      :zipped="uploadConfig.ul_type === 'zip'"
      :blueprints="uploadConfig.blueprints"
      @changedData="updatePostData"
  ></FileUploader>

  <div class="row float-right">
    <button
        class="btn btn-success fs-5 w-25"
        type="button"
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
    actionurl: String,
  },
  data() {
    return {
      ul_config: JSON.parse(this.uploadconfig),
      post_data: {},
    }
  },
  methods: {
    updatePostData(data) {
      Object.keys(data).forEach(key => {
        this.post_data[key] = data[key]
      })
    },
    zipData() {
      // Disable file inputs.
      let file_inputs = document.querySelectorAll("input[type=file]")
      file_inputs.forEach(fi => {
        fi.disabled = true;
      })

      // Zip uploaded and processed data and attach it to form.
      let form = new FormData(document.getElementById("uploader-form"));
      let zip = new JSZip();

      console.log(JSON.parse(JSON.stringify(Array.from(this.post_data))));

      zip.file("ul_data.json", JSON.stringify(this.post_data))
          .generateAsync({type: "blob"})
          .then(blob => {
            form.append("post_data", blob);
            for(let pair of form.entries()) {
              console.log(pair[1]);
            }

            let myReader = new FileReader();
            myReader.onload = function(event){
              console.log(event);
              console.log(JSON.stringify(myReader.result));
            };
            myReader.readAsText(blob);

            let xhr = new XMLHttpRequest();
            xhr.open("POST", this.actionurl);
            xhr.send(form);

            // fetch(this.actionurl,
            //     {method: "POST", body: form})
            return true;
          })
    }
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
