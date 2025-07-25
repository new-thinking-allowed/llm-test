<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{
    sessionId: string
}>()

const isClearing = ref(false)
const resultMessage = ref<string | null>(null)

const clearContext = async () => {
    if (!props.sessionId) return

    isClearing.value = true
    resultMessage.value = null

    try {
        const res = await fetch(`http://localhost:8000/context/${props.sessionId}`, {
            method: 'DELETE',
        })

        if (!res.ok) {
            const data = await res.json()
            throw new Error(data.detail || 'Unknown error')
        }

        const data = await res.json()
        resultMessage.value = data.message
    }
    catch (err: any) {
        resultMessage.value = `Failed: ${err.message}`
    }
    finally {
        isClearing.value = false
    }
}
</script>

<template>
    <div>
        <button @click="clearContext" :disabled="isClearing" class="small">
            {{ isClearing ? 'Clearing…' : 'Clear Session Context' }}
        </button>
        <p v-if="resultMessage" class="mt-2 text-sm text-gray-700">
            {{ resultMessage }}
        </p>
    </div>
</template>

<!-- <style scoped>
</style> -->
