<script setup lang="ts">
const props = defineProps<{
  qid: string;
  text: string;
}>();
</script>

<template>
  <div class="ddm-question ddm-question--transition question-text">
    <div v-html="props.text" />
  </div>
</template>

<style scoped>
</style>
