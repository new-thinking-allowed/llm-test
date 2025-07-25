import { ref } from 'vue'

const sessionId = ref(null)

export function useSessionId() {
    if (!sessionId.value) {
        let storedId = localStorage.getItem('chat_session_id')
        if (!storedId) {
            storedId = crypto.randomUUID()
            localStorage.setItem('chat_session_id', storedId)
        }
        sessionId.value = storedId
    }
    return { sessionId }
}
