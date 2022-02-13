<template>
  <img alt="Vue logo" src="./assets/logo.png">
  <HelloWorld :msg="mssg"/>
  <HelloWorld :msg="msg"/>
<!--  <QuestionnaireList messssage="somemess"/>-->
  <p>Message: {{ this.msg }}</p>
  <p>Message2: {{ msg }}</p>
  <p>Message3: {{ mssg }}</p>
</template>

<script>
import HelloWorld from './components/HelloWorld.vue'
// import QuestionnaireList from './components/questionnaire-list.vue'
// module.exports = {
//   props: ['msage']
// }
export default {
  name: 'QApp',
  components: {
     HelloWorld,
  //   QuestionnaireList
  },
  props: {
    msg: String,
  },
  data() {
    return {
      mssg: 'abcd'
    }
  }
}
</script>

<style>
#qapp {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
