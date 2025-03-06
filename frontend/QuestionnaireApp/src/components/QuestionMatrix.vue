<template>
  <div>
    <div v-html="text"></div>

    <div>
      <template v-for="(item, id) in items" :key="id">

      <div :id="'answer-item-' + item.id" class="item-container">
        <div class="item-label-container" v-html="item.label"></div>
        <div class="scale-container">
          <div v-for="(point, id) in scale"
               :key="id"
               :class="['scale-label-container', { 'main-scale': !point.secondary_point, 'secondary-scale': point.secondary_point }]">
            <input type="radio"
                   :id="this.qid + '-' + item.id + '-' + point.value"
                   :name="item.id"
                   :value="point.value"
                   @change="responseChanged($event)">
            <label :for="this.qid + '-' + item.id + '-' + point.value"
                   class="scale-label"
                   :class="{ 'main-label': !point.secondary_point }">
              <span class="scale-label-span" v-html="point.label"></span>
            </label>
          </div>
        </div>
      </div>

      </template>
    </div>
  </div>
</template>

<script>
export default {
  name: 'MatrixQuestion',
  props: ['qid', 'text', 'items', 'scale'],
  emits: ['responseChanged'],
  data: function() {
    return {
      response: {},
      shouldScroll: window.innerWidth <= 768,
    }
  },
  created() {
    this.items.forEach(i => {
      this.response[i.id] = -99;
    })
    this.$emit('responseChanged', {id: this.qid, response: this.response, question: this.text, items: this.items});
  },
  mounted() {
    window.addEventListener('resize', this.updateScrollSetting);
    this.addClasses();
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.updateScrollSetting);
  },
  methods: {
    updateScrollSetting() {
      this.shouldScroll = window.innerWidth <= 768;
    },
    responseChanged(event) {
      this.response[event.target.name] = event.target.value;
      this.$emit('responseChanged', {id: this.qid, response: this.response, question: this.text, items: this.items});

      // Scroll to next <tr> if it exists. TODO
      const currentRow = event.target.closest('div.item-container');
      if (currentRow) {
        const nextRow = currentRow.nextElementSibling;
        if (this.shouldScroll && nextRow) {
          nextRow.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      }
    },
    addClasses() {
      const containers = document.querySelectorAll('.item-container');

      containers.forEach(container => {
        const mainScales = container.querySelectorAll('.main-scale');

        if (mainScales.length > 0) {
          // Remove old classes in case of re-renders
          mainScales.forEach(el => {
            el.classList.remove("main-scale-first", "main-scale-last");
          });

          // Add class to first .main-scale
          mainScales[0].classList.add("main-scale-first");

          // Add class to last .main-scale (if different from first)
          if (mainScales.length > 1) {
            mainScales[mainScales.length - 1].classList.add("main-scale-last");
          }
        }
      });
    }
  }
}
</script>

<style scoped>
.item-container {
  display: flex;
  flex-direction: column;
  padding-bottom: 20px;
  padding-top: 70px;
  border-bottom: 1px solid lightgrey;
  width: 70%;
  text-align: center;
  margin: auto;
}

.item-label-container {
  padding-bottom: 15px;
}

.scale-label-container {
  flex: 1;
  width: 100%;
  padding-top: 2px;
  padding-bottom: 2px;
}

.scale-label {
  cursor: pointer;
  width: 100%;
  height: 100%;
  padding: 5px;
  text-align: center;
  background: #eaeaea;
  text-wrap: auto;
  word-wrap: break-word;
  overflow-wrap: break-word;
  white-space: normal;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 25px;
  font-size: 0.9rem;
}

.scale-label:hover {
  background: #cfcfcf;
}

.main-scale {}

.main-scale-first label {
  border-radius: 5px 5px 0 0;
}

.main-scale-last label {
  border-radius: 0 0 5px 5px;
}
.main-scale-last {
  margin-bottom: 20px;
}

.secondary-scale > label {
  background: #f4f4f4;
  border-radius: 5px;
}

input[type="radio"] {
  display: none;
}

input[type="radio"]:checked + label {
  background-color: #45819e;
  color: white;
}

@media (min-width: 769px) {
  .item-container {
    display: flex;
    flex-direction: row;
    align-items: center;
    padding-bottom: 20px;
    padding-top: 20px;
    border-bottom: 1px solid lightgrey;
    width: 100%;
  }

  .scale-container {
    display: flex;
    flex-direction: row;
    align-items: stretch;
    min-height: 25px;
    width: 100%;
    height: 100%;
  }

  .scale-label-container {
    flex: 1;
    width: 100%;
    padding-left: 2px;
    padding-right: 2px;
    text-wrap: auto;
    word-wrap: break-word;
    overflow-wrap: break-word;
    white-space: normal;
  }

  .scale-label {}

  .item-label-container {
    width: 30%;
    text-align: left;
    padding-bottom: 0;
    display: flex;
    align-items: center;
    overflow-wrap: anywhere;
    hyphens: auto;
    padding-right: 10px;
  }

  .main-scale-first label {
    border-radius: 5px 0 0 5px;
  }

  .main-scale-last label {
    border-radius: 0 5px 5px 0;
  }

  .main-scale-last {
    margin-right: 20px;
    margin-bottom: 0;
  }
}
</style>