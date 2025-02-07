<i18n src="../translations/donation_instructions.json"></i18n>

<template>
  <div :id="'carousel-' + componentId" class="carousel carousel-dark slide" data-bs-interval="false" data-bs-ride="carousel" data-bs-wrap="false" >

    <div class="carousel-indicators" v-for="(i, index) in instructions" :key="index">
      <template v-for="(i, index) in instructions" :key="index">
        <button type="button"
                :data-bs-slide-to="index"
                :class="{ 'active step-arrow-active': index === currentStep }"
                class="step-arrow"
                :aria-current="{ 'true': index === 0 }"
                :data-bs-target="'#carousel-' + componentId"
                aria-label="Slide 1"
                @click="setStep(index)">
        </button>
      </template>
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
    },
    setStep(step) {
      this.currentStep = step;
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
.step-arrow {
  opacity: 0.2;
}
.step-arrow-active {
  opacity: 0.9;
}
</style>
