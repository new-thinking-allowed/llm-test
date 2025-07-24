import { test, expect } from '@playwright/test'
import fs from 'fs'
import path from 'path'

const TIMEOUT = 1000 * 120; // CPU...
const OUTPUT_PATH = path.join(__dirname, 'results.jsonl')

// Full test prompts organized by category
const prompts = [
    // PHILOSOPHY & CONSCIOUSNESS
    "What did Jeffrey Mishlove say about the nature of consciousness?",
    "How do different guests define the soul?",
    "Is there life after death according to the interviews?",
    "What is the relationship between consciousness and quantum physics?",
    "How is psi described by the various experts?",

    // UFOS, PSI, AND THE PARANORMAL
    "What are UFOs, according to Nick Cook?",
    "Are UFOs physical or psychic in nature?",
    "What links have been suggested between UFOs and the afterlife?",
    "How do guests describe experiences with non-human intelligence?",
    "What role do altered states play in contact experiences?",

    // MIND & PSI ABILITIES
    "Can anyone learn remote viewing?",
    "How did Ingo Swann describe his experiences?",
    "Are there scientific studies supporting telepathy or precognition?",
    "How is intuition different from psi?",

    // SPIRITUALITY, SCIENCE, AND MYSTICISM
    "What do different traditions say about reincarnation?",
    "How do modern scientists interpret mystical experiences?",
    "Are science and spirituality fundamentally in conflict?",
    "What has Dean Radin said about consciousness and the field?",

    // GUEST-SPECIFIC
    "What are the key ideas shared by Rupert Sheldrake on morphic resonance?",
    "Summarize Bernardo Kastrup’s argument for idealism.",
    "What were the most surprising claims made by Stephan Schwartz?",
    "What did Nanci Trivellato say about the out-of-body experience?"
]

test.describe('Log LLM responses and timing for prompts', () => {
    test.beforeAll(() => {
        if (fs.existsSync(OUTPUT_PATH)) fs.unlinkSync(OUTPUT_PATH)
    })

    for (const prompt of prompts) {
        test(`Prompt: ${prompt}`, async ({ page }) => {
            const result = { prompt }

            await page.goto('http://localhost:5173')

            const input = page.locator('input[type="text"]')
            await input.fill(prompt)

            const start = Date.now()
            let error = null
            let responseText = ''

            try {
                await page.keyboard.press('Enter')

                const responseLocator = page.locator('.chat-message')
                await responseLocator.first().waitFor({ timeout: TIMEOUT })

                const allMessages = await responseLocator.allTextContents()
                responseText = allMessages[allMessages.length - 1] || ''
                result.response = responseText.trim()
            } catch (err) {
                result.response = ''
                error = String(err)
            }

            result.timeMs = Date.now() - start
            result.error = error

            fs.appendFileSync(OUTPUT_PATH, JSON.stringify(result) + '\n')
        })
    }
})
