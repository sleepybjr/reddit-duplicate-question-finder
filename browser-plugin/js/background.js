/**
 * Background script for Reddit Helper browser extension.
 * Listens for messages from popup and content scripts to run analysis.
 */

async function getPostData(tabId) {
    console.log("[bg] Asking content script for post data on tab", tabId);
    return await browser.tabs.sendMessage(tabId, { action: "GET_POST_DATA" });
}

async function callBackend(postData) {
    console.log("[bg] Calling backend with:", postData);

    let resp;
    try {
        resp = await fetch("http://localhost:8000/generate_summary", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(postData)
        });
    } catch (e) {
        console.error("[bg] FETCH FAILED:", e);
        return {
            final_summary: `Fetch error: ${String(e)}`,
            per_source_results: []
        };
    }

    console.log("[bg] Backend status:", resp.status);

    let data = null;
    try {
        data = await resp.json();
        console.log("[bg] Backend JSON:", data);
    } catch (e) {
        console.error("[bg] JSON PARSE FAILED:", e);
        return {
            final_summary: `JSON parse error from backend: ${String(e)}`,
            per_source_results: []
        };
    }

    if (!resp.ok) {
        const detail = data?.detail || JSON.stringify(data);
        console.error("[bg] Backend returned error:", detail);
        return {
            final_summary: `Backend error (${resp.status}): ${detail}`,
            per_source_results: []
        };
    }

    return {
        final_summary: data.final_summary ?? "",
        per_source_results: Array.isArray(data.per_source_results)
            ? data.per_source_results
            : []
    };
}

browser.runtime.onMessage.addListener((message, sender) => {
    if (message.action === "RUN_ANALYSIS") {
        const tabId = message.tabId;
        console.log("[bg] RUN_ANALYSIS for tab", tabId);

        (async () => {
            try {
                const postData = await getPostData(tabId);
                console.log("[bg] Got post data:", postData);

                if (!postData || (!postData.title && !postData.body)) {
                    console.warn("[bg] No title/body found");
                    return;
                }

                const aggregated = await callBackend(postData);
                console.log("[bg] Got aggregated answer, sending to content script");

                await browser.tabs.sendMessage(tabId, {
                    action: "INJECT_RESULT",
                    aggregated
                });
            } catch (e) {
                console.error("[bg] Error in RUN_ANALYSIS flow:", e);
            }
        })();
    }
});
