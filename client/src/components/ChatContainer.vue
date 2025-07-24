<template>
  <section class="chat-container">
    <ChatOutput ref="outputContainer" :qAndAs="qAndAs" />
    <ChatInput :inProgress="inProgress" :noRequestSentYet="noRequestSentYet" @sendQuery="handleSendQuery" />
  </section>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import ChatOutput from './ChatOutput.vue'
import ChatInput from './ChatInput.vue'
import { sendToAPI } from '../composables/useChatApi.js'
import { QUESTION, ANSWER, ANSWER_ERROR, LOADING } from '../constants/chatTypes.js'

const qAndAs = ref([])
const inProgress = ref(false)
const noRequestSentYet = ref(true)
const outputContainer = ref(null)

async function handleSendQuery(query) {
  if (!query) return

  recordQandA({ type: QUESTION, datetime: new Date(), text: query })
  noRequestSentYet.value = false
  await scrollOutputToBottom()

  recordQandA({
    type: LOADING,
    datetime: new Date(),
    text: '<div>Waiting for the LLM...</div>',
  })
  await scrollOutputToBottom()

  const loadingIndex = qAndAs.value.length - 1

  try {
    inProgress.value = true
    const response = await sendToAPI(query)

    // Replace the loading placeholder with real answer
    qAndAs.value[loadingIndex] = {
      type: ANSWER,
      datetime: new Date(),
      // text: response.answer,
      ...response,
    }

    await scrollOutputToBottom()
  }

  catch (err) {
    qAndAs.value[loadingIndex] = {
      type: ANSWER_ERROR,
      datetime: new Date(),
      text: `<span class="error">Error: ${err.message}</span>`,
    }
  } finally {
    inProgress.value = false
  }
}

function recordQandA(item) {
  qAndAs.value.push(item)
}

async function scrollOutputToBottom() {
  await nextTick()
  if (outputContainer.value?.$el) {
    const el = outputContainer.value.$el
    el.scrollTop = el.scrollHeight
  }
}
</script>

<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  height: 85vh;
  width: 100%;
  box-sizing: border-box;
  overflow: hidden;
  background-color: #121212;
  color: #e0e0e0;
}
</style>
