<i18n src="../translations/donation_instructions.json"></i18n>

<template>
  <div :id="'carousel-' + componentId" class="carousel carousel-dark slide" data-bs-interval="false" data-bs-ride="carousel" data-bs-wrap="false" >

    <div class="d-flex justify-content-between align-items-center slide-area">
      <div class="slide-control-steps-heading">{{ $t('steps') }}</div>
      <div v-for="(i, index) in instructions" :key="index" class="flex-grow-1 text-center">
        <button
            type="button"
            :data-bs-target="'#carousel-' + componentId"
            :aria-label="'Step ' + index"
            :class="{ 'active active-item': index <= currentStep }"
            :aria-current="index === currentStep"
            class="step-indicator d-hide"
            @click="currentStep = index"
        >•</button>
      </div>
      <div class="slide-control-done-container">
        <div class="slide-control-done" :class="{ 'opacity-0': currentStep < (instructions.length - 1) }">✓</div>
      </div>
    </div>


    <div class="carousel-inner">
      <div
          v-for="(i, index) in instructions"
          :key="index"
          class="carousel-item"
          :class="{ 'active': index === currentStep }"
          v-html="i.text">
      </div>
    </div>

    <button
        class="carousel-control-prev"
        :class="{ 'd-none': currentStep === 0 }"
        type="button"
        data-bs-target="#carousel-0"
        @click="stepDown">
      <span class="carousel-control-prev-icon" aria-hidden="true"></span>
      <span class="visually-hidden">Previous</span>
    </button>
    <button
        class="carousel-control-next"
        :class="{ 'd-none': currentStep === (instructions.length - 1) }"
        type="button"
        data-bs-target="#carousel-0"
        @click="stepUp">
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
.step-indicator {
  background: none;
  border: none;
  font-size: 1.65rem;
  color: darkgray;
}
.active-item {
  color: #545454;
}
.slide-control-done {
  color: #198754;
  font-weight: bold;
  width: 25px;
  font-size: 1.2rem;
  margin-bottom: -4px;
}
.slide-area {
  background-color: #f5f5f599;
  border-radius: 50px;
  height: 25px;
  margin: 10px 0% 40px;
  padding-left: 10px;
  padding-right: 10px;
  padding-bottom: 2px;
}
.slide-control-steps-heading {
  color: #545454;
  font-weight: bold;
  padding-right: 5%;
  padding-top: 3px;
  padding-left: 1%;
}
.slide-control-done-container {
  padding-left: 3%;
  padding-right: 1%;
}
</style>
