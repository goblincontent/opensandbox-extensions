chrome.runtime.onMessage.addListener(function (message, sender, sendResponse) {
  if(message.action === "getURL") {
    getCurrentTab().then(tab => {
      // console.log(tab);
      if (tab.url !== undefined)
      {
        sendResponse({url: tab.url});
      }
    });
  }
  return true;
})

chrome.runtime.onMessage.addListener(function (message, sender, sendResponse) {
  if(message.action === "sendText") {
    getCurrentTab().then(tab => {
      if (tab.url !== undefined)
      {
        sendResponse({url: tab.url});
      }
    });
  }
  return true;
})

chrome.runtime.onMessage.addListener(function (message, sender, sendResponse) {
  if(message.action === "getVideoURL") {
    getCurrentTab().then(tab => {
      if (tab.url !== undefined)
      {
        sendResponse({url: tab.url});
      }
    });
  }
  return true;
});

chrome.runtime.onMessage.addListener(function(message, sender, sendResponse) {
  if (message.action === "getChannelID") {
    getCurrentTab().then(tab => {
      // Inject a content script to access and return the page's content
      // console.log("tab:");
      // console.log(tab);
      chrome.scripting.executeScript(
        {
          target: { "tabId": tab.id }, func: getOuterHTML
        }, (results) => {
          if (chrome.runtime.lastError) {
              sendResponse({
                  success: false,
                  error: chrome.runtime.lastError.message
              });
              return;
          }
          
          const content = results[0]["result"];
          const channelIdMatch = String(content).match(/channel_id=([a-zA-Z0-9_-]+)/);

          if (channelIdMatch) {
              sendResponse({
                  success: true,
                  channelId: channelIdMatch[1]
              });
          } else {
              sendResponse({
                  success: false,
                  error: 'Channel ID not found'
              });
          }
      });
    })
      return true;
  }
});

function getOuterHTML() {
  return document.documentElement.outerHTML;
}

function getCurrentTab() {
  return new Promise((resolve, reject) => {
      chrome.tabs.query({active: true, currentWindow: true}, tabs => {
          if (chrome.runtime.lastError) {
              reject(new Error(chrome.runtime.lastError));
          } else {
              resolve(tabs[0]);
          }
      });
  });
}

