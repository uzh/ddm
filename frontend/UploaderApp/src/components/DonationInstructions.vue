<template>
  <div :id="'carousel-' + componentId" class="carousel carousel-dark slide" data-bs-interval="false" data-bs-ride="carousel" data-bs-wrap="false" >

    <div class="carousel-inner">
      <div
          v-for="(i, index) in instructions"
          :key="index"
          class="carousel-item"
          :class="{ 'active': index === currentStep }"
          v-html="i.text">
      </div>
    </div>

    <div class="d-flex justify-content-between align-items-center slide-area">
      <div>
        <button class="slide-control-arrow" type="button" :data-bs-target="'#carousel-' + componentId" @click="stepDown">‹</button>
      </div>
      <div v-for="(i, index) in instructions" :key="index">
        <button
          type="button"
          :data-bs-target="'#carousel-' + componentId"
          :aria-label="'Step ' + index"
          :class="{ 'active active-item': index === currentStep }"
          :aria-current="index === currentStep"
          class="step-indicator d-hide"
          @click="currentStep = index"
      >•</button>
      </div>
      <div>
        <button class="slide-control-arrow" type="button" :data-bs-target="'#carousel-' + componentId" @click="stepUp">›</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "DonationInstructions",
  props: {
    instructions: Array,
    componentId: Number
  },
  data() {
    return {
      currentStep: 0,
    }
  },
  methods: {
    stepDown() {
      if (this.currentStep > 0) {
        this.currentStep -= 1;
      }
    },
    stepUp() {
      if (this.currentStep < (this.instructions.length - 1)) {
        this.currentStep += 1;
      }
    }
  }
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
@media (max-width: 768px) {
  .carousel-inner {
    padding-left: 10px;
    padding-right: 10px;
  }
  .carousel-control-next,
  .carousel-control-prev {
    width: 30px;
    opacity: 0.1;
  }
}
.carousel-item {
  transition: transform .3s ease, opacity .3s ease-out
}
.carousel-indicators {
  position: static;
  padding-top: 20px;
}
.step-indicator {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: darkgray;
}
.active-item {
  color: #545454;
}
.slide-control-arrow {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: darkgray;
  font-weight: bold;
}
.slide-area {
  margin-left: 33%;
  margin-right: 33%;
  background-color: #f5f5f5;
  border-radius: 50px;
  height: 20px;
  margin-bottom: 25px;
  padding-left: 10px;
  padding-right: 10px;
}
</style>
