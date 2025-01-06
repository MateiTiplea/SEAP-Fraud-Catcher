chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  chrome.runtime.sendMessage(message, (response) => {
    if (chrome.runtime.lastError) {
      console.log("Popup nu este deschis");
    }
  });

  sendResponse({ status: "Mesaj procesat cu succes în background.js" });
});
