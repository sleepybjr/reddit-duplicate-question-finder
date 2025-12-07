/**
 * Content script for Reddit Helper browser extension.
 * Extracts post data and injects analysis results into the page.
 */

console.log("[content] Reddit Helper content script injected on", location.href);

function onUrlChange() {
    console.log("Reddit navigation detected:", location.href);
}

(function () {
    let oldHref = document.location.href;
    const body = document.querySelector("body");

    const observer = new MutationObserver(() => {
        if (oldHref !== document.location.href) {
            oldHref = document.location.href;
            onUrlChange();
        }
    });

    observer.observe(body, { childList: true, subtree: true });
})();

function sleep(ms) {
    return new Promise(r => setTimeout(r, ms));
}

async function extractPostData() {
    console.log("[content] extractPostData start");
    await sleep(500);

    const titleEl =
        document.querySelector('h1[slot="title"]') ||
        document.querySelector('h1[id^="post-title-"]') ||
        document.querySelector('h1[data-test-id="post-title"]') ||
        document.querySelector('h1._eYtD2XCVieq6emjKBH3m') ||
        document.querySelector("h1");

    const title = titleEl?.innerText.trim() || "";
    console.log("[content] title:", title);

    const bodyEl =
        document.querySelector('div[property="schema:articleBody"]') ||
        document.querySelector('div[id$="-post-rtjson-content"]') ||
        document.querySelector('[data-test-id="post-content"]') ||
        document.querySelector('div[data-click-id="text"]') ||
        document.querySelector('div[slot="text-body"]');

    const body = bodyEl?.innerText.trim() || "";
    console.log("[content] body length:", body.length);

    const fromUrl = getSubredditFromUrl();
    const subreddit = fromUrl || "";
    console.log("[content] subreddit:", subreddit);

    return { title, body, source: subreddit, url: window.location.href };
}

function getSubredditFromUrl() {
    const match = window.location.href.match(/reddit\.com\/r\/([^/]+)/i);
    return match ? match[1] : "";
}

function escapeHtml(str) {
    return String(str).replace(/[&<>"]/g, c => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        "\"": "&quot;"
    }[c]));
}

function buildPluginBox(bodyEl, final_summary, per_source_results) {
    const container = document.createElement("div");

    const parent = bodyEl?.parentElement;
    if (parent && parent.className) {
        container.className = parent.className + " plugin-result-box";
    } else {
        container.className = "plugin-result-box mt-md mb-md px-md py-sm";
    }

    container.style.border = "1px solid var(--color-action-upvote, #ff4500)";
    container.style.borderRadius = "6px";
    container.style.marginTop = "12px";
    container.style.padding = "12px";
    container.style.background = "var(--color-neutral-background-weak, transparent)";

    console.log("[content] typeof markdownit:", typeof markdownit);

    let md;
    try {
        md = markdownit({
            html: false,
            breaks: false,
            linkify: true,
        });
        console.log("[content] markdown-it initialized");
    } catch (e) {
        console.error("[content] Failed to init markdown-it:", e);
    }

    const cleanSummary = final_summary.trim();
    let htmlSummary;
    if (md) {
        htmlSummary = md.render(cleanSummary);
    } else {
        htmlSummary = escapeHtml(cleanSummary).replace(/\n/g, "<br>");
    }

    const iconUrl = browser.runtime.getURL("icon48.png");

    let html = `
    <div class="mb-xs">
    <img src="${iconUrl}" alt="Duplicate Finder Icon"
        style="width: 28px; height: 28px; vertical-align: middle;">
    <span class="text-neutral-content-strong font-semibold text-24 xs:text-24">
        Reddit Duplicate Question Finder
    </span>
    </div>
    <div class="text-neutral-content text-14 mb-sm">
      ${htmlSummary}
    </div>
  `;

    if (per_source_results && per_source_results.length) {
        html += `<div class="text-12 text-neutral-content-weak">
      <strong>Sources:</strong>
      <ul class="mt-2 ml-4">`;

        html += per_source_results.slice(0, 5).map(psr => {
            const label = escapeHtml(psr.title || psr.url || psr.source || "Unknown");
            const sourceName = psr.source ? ` (${escapeHtml(psr.source)})` : "";
            if (psr.url) {
                return `<li><a href="${escapeHtml(psr.url)}" target="_blank" rel="noopener noreferrer">${label}</a>${sourceName}</li>`;
            }
            return `<li>${label}${sourceName}</li>`;
        }).join("");

        html += `</ul></div>`;
    }

    container.innerHTML = html;
    return container;
}


function injectPluginBox(aggregated) {
    console.log("[content] injectPluginBox", aggregated);

    const { final_summary, per_source_results } = aggregated || {};
    if (!final_summary && (!per_source_results || !per_source_results.length)) {
        console.warn("[content] Nothing to inject");
        return;
    }

    const bodyEl =
        document.querySelector('div[property="schema:articleBody"]') ||
        document.querySelector('div[id$="-post-rtjson-content"]') ||
        document.querySelector('[data-test-id="post-content"]') ||
        document.querySelector('div[data-click-id="text"]') ||
        document.querySelector('div[slot="text-body"]');

    if (!bodyEl) {
        console.warn("[content] No post body found. Appending plugin box to document.body.");
        const box = buildPluginBox(null, final_summary, per_source_results);
        document.body.appendChild(box);
        return;
    }

    const box = buildPluginBox(bodyEl, final_summary, per_source_results);
    bodyEl.insertAdjacentElement("afterend", box);
}

browser.runtime.onMessage.addListener((message, sender) => {
    console.log("[content] onMessage:", message);

    if (message.action === "GET_POST_DATA") {
        return extractPostData();
    }

    if (message.action === "INJECT_RESULT") {
        injectPluginBox(message.aggregated);
    }

});
