<template>
  <section class="chat-container">
    <div class="output-container" ref="outputContainer">
      <article v-for="(item, index) in qAndAs" :key="index"
        :class="{ 'message': true, 'question': item.type === QUESTION, 'response': item.type === 'ANSWER' }">
        <p class="datetime"><time>{{ item.datetime.toLocaleTimeString() }}</time></p>
        <div v-if="item.type === QUESTION" class="question">{{ item.text }}</div>
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
import { ref, watch, onMounted } from 'vue';
import { marked } from 'marked';

const OLLAMA_URI = 'http://localhost:11434/api/generate';

const qAndAs = ref( [] );
const error = ref( '' );
const inProgress = ref( false );
const noRequestSentYet = ref( true );
const outputContainer = ref( null );

const QUESTION = 0;
const ANSWER = 1;

qAndAs.value = [
  { type: QUESTION, datetime: new Date(), text: 'foo bar baz foo bar baz foo bar baz foo bar baz foo bar baz ' },
  { type: ANSWER, datetime: new Date(), text: 'foo bar baz foo bar baz foo bar baz foo bar baz foo bar baz ' },
  { type: QUESTION, datetime: new Date(), text: 'foo bar baz foo bar baz foo bar baz foo bar baz foo bar baz ' },
  { type: ANSWER, datetime: new Date(), text: 'foo bar baz foo bar baz foo bar baz foo bar baz foo bar baz ' },
  { type: QUESTION, datetime: new Date(), text: 'foo bar baz foo bar baz foo bar baz foo bar baz foo bar baz ' },
  { type: ANSWER, datetime: new Date(), text: 'foo bar baz foo bar baz foo bar baz foo bar baz foo bar baz ' },
  { type: QUESTION, datetime: new Date(), text: 'foo bar baz foo bar baz foo bar baz foo bar baz foo bar baz ' },
  { type: ANSWER, datetime: new Date(), text: 'foo bar baz foo bar baz foo bar baz foo bar baz foo bar baz ' },
  { type: QUESTION, datetime: new Date(), text: 'foo bar baz foo bar baz foo bar baz foo bar baz foo bar baz ' },
  { type: ANSWER, datetime: new Date(), text: 'foo bar baz foo bar baz foo bar baz foo bar baz foo bar baz ' },
  { type: QUESTION, datetime: new Date(), text: 'foo bar baz foo bar baz foo bar baz foo bar baz foo bar baz ' },
  { type: ANSWER, datetime: new Date(), text: 'foo bar baz foo bar baz foo bar baz foo bar baz foo bar baz ' },
  { type: QUESTION, datetime: new Date(), text: 'foo bar baz foo bar baz foo bar baz foo bar baz foo bar baz ' },
  { type: ANSWER, datetime: new Date(), text: 'foo bar baz foo bar baz foo bar baz foo bar baz foo bar baz ' },
  { type: QUESTION, datetime: new Date(), text: 'foo bar baz foo bar baz foo bar baz foo bar baz foo bar baz ' },
  { type: ANSWER, datetime: new Date(), text: 'foo bar baz foo bar baz foo bar baz foo bar baz foo bar baz ' },

]

onMounted( async () => {
  scrollOutputToBottom();
  try {
    const res = await fetch( OLLAMA_URI, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify( {
        stream: false,
        keep_alive: -1,
        model: 'llama3',
        // options: {
        //   num_ctx: 4096
        // }
      } ),
    } );

    if ( !res.ok ) {
      throw new Error( `Failed to initialise: ${ res.status } ${ res.statusText }` );
    }

    const body = await res.json();
    console.log( body );
    return body;
  } catch ( err ) {
    console.error( 'Error in send function:', err );
    throw err;
  } finally {
    inProgress.value = false;
  }
} );

async function handleKeyUp ( event ) {
  if ( event.key !== 'Enter' ) {
    return;
  }

  const question = event.target.value.trim();

  try {
    recordQandA( { type: QUESTION, datetime: new Date(), text: question } );
    event.target.value = '';
    scrollOutputToBottom();
    const response = await send( question );
    recordQandA( { type: ANSWER, datetime: new Date( response.created_at ), text: marked.parse( response.response ) } );
    scrollOutputToBottom();
  } catch ( err ) {
    error.value = err.message || 'Unknown error occurred';
  }
}

async function send ( text ) {
  inProgress.value = true;
  noRequestSentYet.value = false;
  try {
    const res = await fetch( OLLAMA_URI, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify( {
        stream: false,
        prompt: text,
        model: 'llama3',
      } ),
    } );

    if ( !res.ok ) {
      throw new Error( `Failed to fetch: ${ res.status } ${ res.statusText }` );
    }

    const body = await res.json();
    console.log( body );
    return body;
  } catch ( err ) {
    console.error( 'Error in send function:', err );
    throw err;
  } finally {
    inProgress.value = false;
  }
}

function recordQandA ( item ) {
  qAndAs.value.push( item );
}

function scrollOutputToBottom () {
  if ( outputContainer.value ) {
    outputContainer.value.scrollTop = outputContainer.value.scrollHeight;
  }
}

// Watch for changes in qAndAs and scroll to bottom when new messages are added
watch( qAndAs, scrollOutputToBottom );

</script>

<style scoped>
main {
  width: 100% !important;
}

.chat-container {
  display: flex;
  flex-direction: column;
  height: 85vh;
  width: 100%;
  box-sizing: border-box;
  overflow: hidden;
}

.output-container {
  padding: 1em;
  flex: 1;
  width: 100%;
  height: 100%;
  overflow-y: auto;
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
}

.field {
  margin-top: 2em;
  width: 100%;
  height: 100%;
}

.message {
  margin-bottom: 1em;
  padding: 1em;
}

.datetime {
  font-style: italic;
  margin-bottom: 0.5em;
  opacity: 50%;
}

.question {
  background-color: #f0f0f0;
  text-align: right;
}

.response {
  background-color: #e6f7ff;
  text-align: left;
}
</style>
