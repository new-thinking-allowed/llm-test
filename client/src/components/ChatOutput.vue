<script setup>
import { QUESTION, ANSWER, ANSWER_ERROR, LOADING } from '../constants/chatTypes.js'

defineProps({
  qAndAs: {
    type: Array,
    required: true,
  },
})

function parseTimestamp(timestamp) {
  const [minutes, seconds] = timestamp.split(':').map(Number)
  const totalSeconds = minutes * 60 + seconds
  return `https://img.youtube.com/vi/${videoId}/default.jpg?t=${totalSeconds}`
}

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

          <ul v-if="item.sources && item.sources.length" class="sources">
            <li v-for="(src, i) in item.sources" :key="i" class="source-item">
              <a :href="`https://www.youtube.com/watch?v=${src.videoId}&t=${parseTimestamp(src.timestamp)}s`"
                target="_blank" rel="noopener noreferrer" class="thumbnail-link">
                <img :src="`https://img.youtube.com/vi/${src.videoId}/hqdefault.jpg`" alt="YouTube thumbnail"
                  class="yt-thumbnail" />
              </a>
              <span class="source-text">{{ src.timestamp }}<span v-if="src.title"> – {{ src.title }}</span></span>
            </li>
          </ul>

          <div v-if="item.llm_response_time_sec" class="timing">
            Answered in {{ item.llm_response_time_sec.toFixed(1) }}s
          </div>
        </div>
      </article>
    </template>
  </div>
</template>
