<template>
  <main class="overlay-container">
    <div>
      <template v-for="(line, i) in lines">
        <div class="overlay-font1" :key="'1-' + i">{{ line }}</div>
        <div class="overlay-font2" :key="'2-' + i">{{ line }}</div>
      </template>
    </div>
  </main>
</template>

<script lang="ts">
import Vue from "vue";
import { UDHR_ENG } from "../udhr";

export default Vue.extend({
  data() {
    return { lines: UDHR_ENG.split("\n") };
  },
});
</script>

<style>
.overlay-container {
  position: relative;
  white-space: nowrap;
  overflow: auto;
  flex-grow: 1;
}
.overlay-container > div {
  padding: 1em;
}
.overlay-font1 {
  font-family: Font1;
  color: blue;
  line-height: 1.5em;
  height: 1.5em;
}
.overlay-font2 {
  font-family: Font2;
  color: red;
  line-height: 1.5em;
  height: 1.5em;
  margin-top: -1.5em;
}
</style>
