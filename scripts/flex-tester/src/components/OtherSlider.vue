<template>
  <div class="axis-slider">
    <label :for="id">{{ name }}</label>
    <input :id="id" type="range" :min="min" :max="max" v-model="_value" />
    <span class="buttons">
      <input type="number" v-model="_value" />
    </span>
  </div>
</template>

<script lang="ts">
import Vue from "vue";

export default Vue.extend({
  props: {
    name: String,
    min: Number,
    max: Number,
    defaultValue: Number,
    value: Number,
  },
  computed: {
    id() {
      return `slider-${this.name}`;
    },
    _value: {
      get() {
        return this.value;
      },
      set(value) {
        this.$emit("input", Number(value));
      },
    },
  },
});
</script>

<style scoped>
.axis-slider {
  display: flex;
}
label {
  width: 8em;
}
input[type="range"] {
  flex-grow: 1;
}
.buttons {
  width: max-content;
}
</style>
