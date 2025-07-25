<script setup lang="ts">
import { ref, watch } from 'vue'
import { QUESTION, ANSWER, ANSWER_ERROR, LOADING } from '../constants/chatTypes.js'
import SourceList from './SourceList.vue'

const props = defineProps({
  qAndAs: {
    type: Array,
    required: true,
  },
})

// Log when qAndAs changes
watch(() => props.qAndAs, (newVal) => {
  console.log('🔄 qAndAs updated:', newVal)
}, { deep: true, immediate: true })

// Log each item during rendering
function logItem(item: any, index: number): boolean {
  console.log(`🧾 Rendering item ${index}:`, item)
  return false // No-op for template
}
</script>

<template>
  <div class="chat-output" ref="output">
    <template v-for="(item, index) in qAndAs" :key="index">
      <!-- Logging call (doesn't render anything) -->
      <div v-if="logItem(item, index)"></div>

      <article v-if="item && typeof item.type !== 'undefined'" :class="{
        message: true,
        query: item.type === QUESTION,
        response: item.type === ANSWER || item.type === LOADING,
        error: item.type === ANSWER_ERROR,
      }">
        <div v-if="item.text" v-html="item.text"></div>

        <div v-if="item.type === ANSWER">
          <SourceList v-if="item.sources?.length" :sources="item.sources" />

          <div v-if="typeof item.llm_response_time_sec === 'number'" class="timing">
            Answered in {{ item.llm_response_time_sec.toFixed(1) }}s
          </div>
        </div>
      </article>
    </template>
  </div>
</template>

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
  border-radius: 8pt;
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

.answer {
  margin-bottom: 0.5rem;
}

.sources {
  font-size: 0.9rem;
  color: #aaa;
  margin-top: 0.5rem;
  padding-left: 1.2rem;
}

.timing {
  font-size: 0.75rem;
  color: #666;
  margin-top: 0.3rem;
  float: right;
}

.yt-thumbnail {
  min-width: 4em;
  max-width: 4em;
}
</style>
