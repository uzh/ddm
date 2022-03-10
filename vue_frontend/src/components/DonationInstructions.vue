<template>
  <div :id="'carousel-' + comp_id" class="carousel carousel-dark slide" data-bs-interval="false" data-bs-ride="carousel">
    <div class="carousel-indicators">
      <button
          v-for="(i, index) in instructions"
          :key="index"
          type="button"
          :data-bs-target="'#carousel-' + comp_id"
          :data-bs-slide-to="index"
          :aria-label="'Step ' + index"
          :class="{ 'active': index === 0 }"
          :aria-current="index === 0"
      ></button>
    </div>
    <div class="carousel-inner">
      <div
          v-for="(i, index) in instructions"
          :key="index"
          class="carousel-item"
          :class="{ 'active': index === 0 }"
          v-html="i.text">
      </div>
    </div>
    <button class="carousel-control-prev" type="button" :data-bs-target="'#carousel-' + comp_id" data-bs-slide="prev">
      <span class="carousel-control-prev-icon" aria-hidden="true"></span>
      <span class="visually-hidden">Previous</span>
    </button>
    <button class="carousel-control-next" type="button" :data-bs-target="'#carousel-' + comp_id" data-bs-slide="next">
      <span class="carousel-control-next-icon" aria-hidden="true"></span>
      <span class="visually-hidden">Next</span>
    </button>
  </div>
</template>

<script>
export default {
  name: "DonationInstructions",
  props: {
    instructions: Array,
    comp_id: Number
  },
  data() {
    return {}
  },
  methods: {}
}
</script>

<style scoped>
.carousel {
  min-height: 250px;
}
.carousel-control-next,
.carousel-control-prev {
  width: auto;
}
.carousel-inner {
  padding-left: 42px;
  padding-right: 42px;
}
.carousel-item {
  transition: transform .3s ease, opacity .3s ease-out
}
</style>
