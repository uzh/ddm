<template>
  <div>
    <div v-html="text"></div>
  </div>
</template>

<script>
export default {
  name: "TransitionQuestion",
  props: ['text'],
}
</script>

<style scoped>

</style>
