<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{
    sessionId: string
}>()

const isClearing = ref(false)
const buttonText = ref('Clear Session Context')

const clearContext = async () => {
    if (!props.sessionId) return

    isClearing.value = true
    buttonText.value = 'Clearing…'

    try {
        const res = await fetch(`http://localhost:8000/context/${props.sessionId}`, {
            method: 'DELETE',
        })

        const data = await res.json()

        if (!res.ok) {
            throw new Error(data.detail || 'Unknown error')
        }

        buttonText.value = data.message || 'Cleared!'
    }
    catch (err: any) {
        buttonText.value = `Failed: ${err.message}`
    }
    finally {
        isClearing.value = false

        setTimeout(() => {
            buttonText.value = 'Clear Session Context'
        }, 5000)
    }
}
</script>

<template>
    <button @click="clearContext" :disabled="isClearing" class="small">
        {{ buttonText }}
    </button>
</template>
