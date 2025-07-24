<script setup>
import { QUESTION, ANSWER, ANSWER_ERROR, LOADING } from '../constants/chatTypes.js'
import SourceList from './SourceList.vue'

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

<template>
  <div class="chat-output" ref="output">
    <template v-for="(item, index) in qAndAs" :key="index">
      <article v-if="item && typeof item.type !== 'undefined'" :class="{
        message: true,
        query: item.type === QUESTION,
        response: item.type === ANSWER || item.type === LOADING,
        error: item.type === ANSWER_ERROR,
      }">
        <div v-if="item.text" v-html="item.text"></div>
        <div v-else-if="item.answer">
          <div v-if="item.answer" class="answer" v-html="item.answer"></div>

          <SourceList v-if="item.sources && item.sources.length" :sources="item.sources" />

          <div v-if="item.llm_response_time_sec" class="timing">
            Answered in {{ item.llm_response_time_sec.toFixed(1) }}s
          </div>
        </div>
      </article>
    </template>
  </div>
</template>
