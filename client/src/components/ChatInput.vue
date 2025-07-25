<script setup>
import { ref } from 'vue'

const props = defineProps({
  inProgress: Boolean,
  noRequestSentYet: Boolean,
})
const emit = defineEmits(['sendQuery'])

const inputText = ref('')

// Suggestions (these can be randomized or rotated later)
const suggestions = [
  'What did Jeffrey Mishlove say about the nature of consciousness?',
  'Can anyone learn remote viewing?',
  'Are UFOs physical or psychic in nature?',
  'What do different traditions say about reincarnation?',
  'Summarize Bernardo Kastrup’s argument for idealism.',
]

function applySuggestion(suggestion) {
  inputText.value = suggestion
  handleSubmitRequest()
}

function handleSubmitRequest() {
  if (!inputText.value.trim()) return
  emit('sendQuery', inputText.value.trim())
  inputText.value = ''
}
</script>

<template>
  <div class="suggestion-container" v-if="noRequestSentYet">
    <span class="suggestion-label">Try asking:</span>
    <div class="suggestions">
      <button v-for="(suggestion, i) in suggestions" :key="i" @click="applySuggestion(suggestion)">
        {{ suggestion }}
      </button>
    </div>
  </div>

  <div class="input-container">
    <div class="field border large padding">
      <input id="input" type="text" placeholder="Type a question..." @keyup.enter="handleSubmitRequest"
        :disabled="inProgress" autocomplete="off" v-model="inputText" />
      <span class="helper" v-if="noRequestSentYet">Press return to send</span>
    </div>
  </div>
</template>

<style scoped>
.suggestion-container {
  position: fixed;
  bottom: 30vh;
  width: 600px;
  left: 50%;
  transform: translateX(-50%);
  background-color: #111;
  padding: 1em;
  border-top: 1px solid #333;
  z-index: 999;
  color: #ccc;
}

.suggestion-label {
  display: block;
  margin-bottom: 0.5em;
  font-weight: bold;
  font-size: 0.9em;
  color: #888;
}

.suggestions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5em;
}

.suggestions button {
  transition: background 0.2s;
}

.suggestions button:hover {
  border-color: #777;
}

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
