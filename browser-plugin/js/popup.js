/**
 * Handles the click event for the "Run" button in the popup.
 * Sends a message to the background script to run analysis on the active tab.
 */

document.getElementById("runBtn").addEventListener("click", async () => {
  console.log("[popup] Run clicked");

  const [tab] = await browser.tabs.query({ active: true, currentWindow: true });
  if (!tab) {
    console.warn("[popup] No active tab");
    return;
  }

  await browser.runtime.sendMessage({
    action: "RUN_ANALYSIS",
    tabId: tab.id
  });
});
