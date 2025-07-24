export async function sendToAPI(query) {
    const res = await fetch('http://127.0.0.1:8000/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
    });

    if (!res.ok) {
        let errorDetail = '';
        try {
            const errorJson = await res.json();
            errorDetail = errorJson.detail || JSON.stringify(errorJson);
        } catch {
            errorDetail = res.statusText;
        }
        throw new Error(`Failed to fetch: ${res.status} ${res.statusText} - ${errorDetail}`);
    }

    return res.json();
}
