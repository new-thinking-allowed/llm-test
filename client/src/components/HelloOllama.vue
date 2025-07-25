<template>
  <section class="chat-container">
    <div class="output-container" ref="outputContainer">
      <article v-for="(item, index) in qAndAs" :key="index"
        :class="{ 'message': true, 'query': item.type === QUESTION, 'response': item.type === ANSWER }">
        <p class="datetime"><time>{{ item.datetime.toLocaleTimeString() }}</time></p>
        <div v-if="item.type === QUESTION" class="query">{{ item.text }}</div>
        <div v-if="item.type === ANSWER" class="response" v-html="item.text"></div>
      </article>
    </div>

    <div class="input-container">
      <div class="field border large padding">
        <input id="input" type="text" placeholder="Type a question..." @keyup.enter="handleKeyUp" :disabled="inProgress"
          autocomplete="off">
        <span class="helper" v-if="noRequestSentYet">Press return to send</span>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, watch, onMounted, nextTick } from 'vue';
import { marked } from 'marked';

const FASTAPI_URI = 'http://127.0.0.1:8000/query';

const qAndAs = ref([]);
const error = ref('');
const inProgress = ref(false);
const noRequestSentYet = ref(true);
const outputContainer = ref(null);

const QUESTION = 0;
const ANSWER = 1;

async function handleKeyUp(event) {
  if (event.key !== 'Enter') return;

  const query = event.target.value.trim();
  if (!query) return;

  recordQandA({ type: QUESTION, datetime: new Date(), text: query });
  event.target.value = '';
  scrollOutputToBottom();

  try {
    const response = await sendChatToAPI(query);
    recordQandA({ type: ANSWER, datetime: new Date(), text: marked.parse(response.answer) });
    scrollOutputToBottom();
  } catch (err) {
    error.value = err.message || 'Unknown error occurred';
  }
}

async function sendChatToAPI(text) {
  inProgress.value = true;
  noRequestSentYet.value = false;
  try {
    const res = await fetch(FASTAPI_URI, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query: text }),
    });

    if (!res.ok) throw new Error(`Failed to fetch: ${res.status} ${res.statusText}`);

    return await res.json();
  }

  catch (err) {
    console.error('Error in sendChatToAPI:', err);
    throw err;
  }

  finally {
    inProgress.value = false;
  }
}

function recordQandA(item) {
  qAndAs.value.push(item);
}

async function scrollOutputToBottom() {
  if (outputContainer.value) {
    await nextTick();
    outputContainer.value.scrollTop = outputContainer.value.scrollHeight;
  }
}

watch(qAndAs, scrollOutputToBottom);
</script>

<style scoped>
main {
  width: 100% !important;
  background-color: #121212;
  color: #e0e0e0;
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

.output-container {
  padding: 1em;
  flex: 1;
  width: 100%;
  height: 100%;
  overflow-y: auto;
  background-color: #121212;
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

input[type="text"] {
  width: 100%;
  height: 100%;
  padding: 0.5em;
  background-color: #2c2c2c;
  color: #f0f0f0;
}

input[type="text"]:disabled {
  background-color: #333;
  color: #888;
}

.helper {
  display: block;
  font-size: 0.8em;
  color: #888;
  margin-top: 0.25em;
}

.message {
  margin-bottom: 1em;
  padding: 1em;
}

.datetime {
  font-style: italic;
  margin-bottom: 0.5em;
  opacity: 0.5;
  font-size: 0.8em;
}

.query {
  background-color: #2a2a2a;
  color: #f5f5f5;
  text-align: right;
}

.response {
  background-color: #1f2a36;
  color: #d1eaff;
  text-align: left;
}
</style>
