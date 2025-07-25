<script setup lang="ts">
import { QUESTION, ANSWER, ANSWER_ERROR, LOADING } from '../constants/chatTypes.js'
import SourceList from './SourceList.vue'

defineProps({
  qAndAs: {
    type: Array,
    required: true,
  },
})

</script>

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
  padding: 1em;
  background-color: #1e1e1e;
  overflow-y: auto;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.message {
  margin-bottom: 1em;
  padding: 0.75em;
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
  margin-bottom: 0.5em;
}

.sources {
  font-size: 0.9em;
  color: #aaa;
  margin-top: 0.5em;
  padding-left: 1.2em;
}

.timing {
  font-size: 0.75em;
  color: #666;
  margin-top: 0.3em;
  float: right;
}

.yt-thumbnail {
  min-width: 4em;
  max-width: 4em;
}
</style>
