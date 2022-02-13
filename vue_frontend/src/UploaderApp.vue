<template>
  <h1>Uploader App</h1>
  <FileUploader
      v-for="(uploadBP, id) in ul_config"
      :key="id"
      :ul_id="uploadBP.id"
      :format="uploadBP.format"
      :expected_fields="uploadBP.exp_fields"
      :fields_to_extract="uploadBP.extr_fields"
  ></FileUploader>
  <FileUploader
      key="3"
      ul_id="12"
      format="json"
      :expected_fields='["title", "titleUrl"]'
      :fields_to_extract='["title", "titleUrl", "time"]'
  ></FileUploader>
</template>

<script>
import FileUploader from './components/FileUploader.vue'

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
      ul_config: JSON.parse(this.uploadconfig)
    }
  },
  methods: {
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
