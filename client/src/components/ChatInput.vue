<template>
  <div class="input-container">
    <div class="field border large padding">
      <input
        id="input"
        type="text"
        placeholder="Type a query..."
        @keyup.enter="onEnter"
        :disabled="inProgress"
        autocomplete="off"
        v-model="inputText"
      />
      <span class="helper" v-if="noRequestSentYet">Press return to send</span>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  inProgress: Boolean,
  noRequestSentYet: Boolean,
})

const emit = defineEmits(['sendQuery'])

const inputText = ref('')

function onEnter() {
  if (!inputText.value.trim()) return
  emit('sendQuery', inputText.value.trim())
  inputText.value = ''
}
</script>

<style scoped>
.input-container {
  position: fixed;
  display: flex;
  align-items: center;
  justify-content: center;
  bottom: 0;
  height: 10vh;
  width: 600px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1000;
  background-color: #1e1e1e;
  border-top: 1px solid #333;
}

.field {
  margin-top: 2em;
  width: 100%;
  height: 100%;
}

input[type='text'] {
  width: 100%;
  height: 100%;
  padding: 0.5em;
  background-color: #2c2c2c;
  color: #f0f0f0;
  border: 1px solid #444;
  border-radius: 4px;
}

input[type='text']:disabled {
  background-color: #333;
  color: #888;
}

.helper {
  display: block;
  font-size: 0.8em;
  color: #888;
  margin-top: 0.25em;
}
</style>
