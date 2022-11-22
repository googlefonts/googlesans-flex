<template>
  <div id="app">
    <header>
      <div v-html="fontFaceHtml"></div>
      <div v-html="fontStyleHtml"></div>
      <div class="input-bar">
        <label class="input-font1">
          <input type="file" @input="setFont1" />
        </label>
        <label>
          <input type="radio" v-model="blendMode" v-bind:value="'blueOnTop'" />
          Blue on top
        </label>
        <label>
          <input type="radio" v-model="blendMode" v-bind:value="'multiply'" />
          Multiply
        </label>
        <label>
          <input type="radio" v-model="blendMode" v-bind:value="'redOnTop'" />
          Red on top
        </label>
        <label class="input-font2">
          <input type="file" @input="setFont2" />
        </label>
      </div>

      <div class="axis-sliders">
        <div style="flex-grow: 1">
          <AxisSlider
            v-model="userLocation.wght"
            name="Weight"
            :min="1"
            :max="1000"
            :defaultValue="400"
          />
          <AxisSlider
            v-model="userLocation.wdth"
            name="Width"
            :min="25"
            :max="151"
            :defaultValue="100"
          />
          <AxisSlider
            v-model="userLocation.opsz"
            name="Optical Size"
            :min="6"
            :max="144"
            :defaultValue="18"
          />
          <AxisSlider
            v-model="userLocation.GRAD"
            name="Grade"
            :min="-50"
            :max="50"
            :defaultValue="0"
          />
          <AxisSlider
            v-model="userLocation.ROND"
            name="Round"
            :min="0"
            :max="100"
            :defaultValue="0"
          />
        </div>
        <div>
          <InstanceDropdown v-model="userLocation" />
        </div>
      </div>

      <div class="overlay-options">
        <div style="flex-grow: 1">
          <OtherSlider v-model="size" name="Font Size" :min="6" :max="400" />
          <OtherSlider
            v-model="offset"
            name="Overlay Offset"
            :min="-100"
            :max="100"
          />
        </div>
        <div>
          <label>
            <input type="checkbox" v-model="kerning" />
            Kerning
          </label>
        </div>
      </div>
    </header>

    <router-view />
  </div>
</template>

<script lang="ts">
import Vue from "vue";
import AxisSlider from "./components/AxisSlider.vue";
import InstanceDropdown from "./components/InstanceDropdown.vue";
import OtherSlider from "./components/OtherSlider.vue";

export default Vue.extend({
  components: { AxisSlider, OtherSlider, InstanceDropdown },
  data() {
    return {
      font1: "",
      font2: "",
      blendMode: "redOnTop",
      userLocation: {
        wght: 400,
        wdth: 100,
        opsz: 18,
        GRAD: 0,
        ROND: 0,
      },
      size: 20,
      offset: 0,
      kerning: true,
    };
  },
  computed: {
    fontFaceHtml() {
      const css = [];
      if (this.font1)
        css.push(`
          @font-face{
            font-family: "Font1";
            src: url(${this.font1});
          }
        `);
      if (this.font2)
        css.push(`
          @font-face{
            font-family: "Font2";
            src: url(${this.font2});
          }
      `);
      return `<style>${css.join("\n")}</style>`;
    },
    fontStyleHtml() {
      const css = [
        `
          .overlay-font1, .overlay-font2 {
            font-size: ${this.size}px;
            font-variation-settings:
              "wght" ${this.userLocation.wght},
              "wdth" ${this.userLocation.wdth},
              "opsz" ${this.userLocation.opsz},
              "GRAD" ${this.userLocation.GRAD},
              "ROND" ${this.userLocation.ROND};
          }
          .overlay-font2 {
            position: relative;
            top: ${this.offset / 200}em;
          }
        `,
      ];
      if (this.blendMode == "blueOnTop") {
        css.push(`.overlay-font2 { z-index: -1; }`);
      } else if (this.blendMode == "multiply") {
        css.push(`.overlay-font2 { mix-blend-mode: multiply; }`);
      }
      if (!this.kerning) {
        css.push(`
          .overlay-font1, .overlay-font2 { font-feature-settings: "kern" 0; }
        `);
      }
      return `<style>${css.join("\n")}</style>`;
    },
  },
  methods: {
    setFont1(event: Event) {
      this.font1 = URL.createObjectURL(event.target.files[0]);
    },
    setFont2(event: Event) {
      this.font2 = URL.createObjectURL(event.target.files[0]);
    },
  },
});
</script>

<style>
#app {
  display: flex;
  flex-direction: column;
  width: 100vw;
  height: 100vh;
}

header {
  padding: 1em;
  border-bottom: 1px solid black;
}

.input-bar {
  display: flex;
}
.input-bar label {
  padding: 0 1em;
}
.input-font1 {
  color: white;
  background: blue;
  flex-grow: 1;
}
.input-font2 {
  color: white;
  background: red;
  flex-grow: 1;
}

.input-font1,
.input-font2 {
  display: flex;
}
.input-font1 input,
.input-font2 input {
  flex-grow: 1;
}

.axis-sliders {
  margin-top: 1em;
  display: flex;
  gap: 1em;
}

.overlay-options {
  margin-top: 1em;
  display: flex;
  gap: 1em;
}
</style>
