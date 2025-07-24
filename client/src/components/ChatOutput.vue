<script setup>
import { QUESTION, ANSWER, LOADING } from '../constants/chatTypes.js'

defineProps({
  qAndAs: {
    type: Array,
    required: true,
  },
})
</script>

<style scoped>
.chat-output {
  padding: 1rem;
  background-color: #1e1e1e;
  overflow-y: auto;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.message {
  margin-bottom: 1rem;
  padding: 0.75rem;
  border-radius: 8px;
  max-width: 80%;
}

.query {
  align-self: flex-end;
  background-color: #2c2c2c;
  color: #ffffff;
}

.response {
  align-self: flex-start;
  background-color: #333333;
  color: #cccccc;
}
</style>

<template>
  <div class="chat-output" ref="output">
    <template v-for="(item, index) in qAndAs" :key="index">
      <article
        v-if="item && typeof item.type !== 'undefined'"
        :class="{
          message: true,
          query: item.type === QUESTION,
          response: item.type === ANSWER || item.type === LOADING,
        }"
      >
        <div v-html="item.text"></div>
      </article>
    </template>
  </div>
</template>
