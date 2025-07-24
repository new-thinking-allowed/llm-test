<script setup>
defineProps({
    sources: {
        type: Array,
        required: true,
    },
})

function parseTimestamp(timestamp) {
    const [minutes, seconds] = timestamp.split(':').map(Number)
    return minutes * 60 + seconds
}
</script>

<template>
    <div v-if="sources.length" class="source-strip">
        <div v-for="(src, i) in sources" :key="i" class="source-thumbnail">
            <a :href="`https://www.youtube.com/watch?v=${src.video_id}&t=${parseTimestamp(src.timestamp)}s`"
                :title="`Starts at ${src.timestamp}`" target="_blank" rel="noopener noreferrer">
                <img :src="`https://img.youtube.com/vi/${src.video_id}/hqdefault.jpg`" alt="YouTube thumbnail"
                    class="yt-thumbnail" />
            </a>
            <div class="source-title">
                {{ src.title || 'Untitled' }}
            </div>
        </div>
    </div>
</template>

<style scoped>
.source-strip {
    display: flex;
    overflow-x: auto;
    gap: 2rem;
    padding: 0.5rem 0;
    scrollbar-width: thin;
}

.source-strip::-webkit-scrollbar {
    height: 6px;
}

.source-strip::-webkit-scrollbar-thumb {
    background-color: #666;
    border-radius: 2pt;
}

.source-strip::-webkit-scrollbar-track {
    background: transparent;
}

.source-thumbnail {
    flex: 0 0 auto;
    text-align: center;
    max-width: 10em;
    min-width: 10em;
}

.yt-thumbnail {
    width: 100%;
    border-radius: 2pt;
    display: block;
}

.source-title {
    font-size: 0.75rem;
    color: #ccc;
    margin-top: 0.25rem;
    word-wrap: break-word;
}
</style>
