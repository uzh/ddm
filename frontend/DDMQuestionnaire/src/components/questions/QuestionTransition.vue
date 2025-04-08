<script setup lang="ts">
const props = defineProps<{
  qid: string;
  text: string;
}>();
</script>

<template>
  <div class="question-text">
    <div v-html="props.text"></div>
  </div>
</template>

<style scoped>
</style>
