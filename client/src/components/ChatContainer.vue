<script setup>
import { ref, nextTick } from 'vue'
import { useSessionId } from '../composables/useSessionId.js'
import { sendChatToAPI } from '../composables/useChatApi.js'
import { QUESTION, ANSWER, ANSWER_ERROR, LOADING } from '../constants/chatTypes.js'
import ChatOutput from './ChatOutput.vue'
import ChatInput from './ChatInput.vue'
import ClearContextButton from './ClearContextButton.vue'

const qAndAs = ref([])
const inProgress = ref(false)
const noRequestSentYet = ref(true)
const outputContainer = ref(null)


const { sessionId } = useSessionId()

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

    const response = await sendChatToAPI(query, sessionId.value)

    qAndAs.value[loadingIndex] = {
      type: ANSWER,
      datetime: new Date(),
      text: response.answer,
      sources: response.sources,
      llm_response_time_sec: response.llm_response_time_sec,
    }

    await scrollOutputToBottom()
  } catch (err) {
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

<template>
  <h1>NTA Archive Chatbot
    <ClearContextButton :session-id="sessionId" />
  </h1>

  <section class="chat-container">
    <ChatOutput ref="outputContainer" :qAndAs="qAndAs" />
    <ChatInput :inProgress="inProgress" :noRequestSentYet="noRequestSentYet" @sendQuery="handleSendQuery" />
  </section>
</template>

<style scoped>
h1 {
  justify-content: space-between;
  color: #e0e0e099;
  font-size: 2em;
  margin: 1em;
  margin-top: 0;
}

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
