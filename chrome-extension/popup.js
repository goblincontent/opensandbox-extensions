function getVideoId(url) {
  var matchedExpression = url.match(/v=([a-zA-Z0-9_-]+)/);
  
  if (matchedExpression) {
    return matchedExpression[1];
  } else {
    return null;
  }
}

const sendVideoIdToPython = async (collection, message, vectorize) => {
  try {
    const response = await fetch('http://localhost:5050/new_video_id', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ collection: collection, message: message, vectorize: vectorize }),
    });

    const responseData = await response.json();
  } catch (error) {
    console.error("Error sending message:", error);
  }
}

const sendChannelIdToPython = async (collection, message, vectorize) => {
  try {
    const response = await fetch('http://localhost:5050/new_channel_id', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ collection: collection, message: message, vectorize: vectorize }),
    });

    const responseData = await response.json();
  } catch (error) {
    console.error("Error sending message:", error);
  }
}

const sendURLToPython = async (collection, message, vectorize) => {
  try {
    const response = await fetch('http://localhost:5050/new_url', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ collection: collection, message: message, vectorize: vectorize }),
    });

    const responseData = await response.json();
  } catch (error) {
    console.error("Error sending message:", error);
  }
}

const sendTextToPython = async (collection, message, url, vectorize) => {
  try {
    const response = await fetch('http://localhost:5050/new_text', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ collection: collection, message: message, url: url, vectorize: vectorize }),
    });

    const responseData = await response.json();
  } catch (error) {
    console.error("Error sending message:", error);
  }
}

document.getElementById("get-video").addEventListener("click", function() {
  chrome.runtime.sendMessage({action: "getVideoURL"}, function(response) {
    document.getElementById("videoIdContainer").textContent = getVideoId(response.url);
    console.log("Sending " + getVideoId(response.url) + "video ID to Python");
    
    if (getVideoId(response.url) === undefined) {
      console.log("Video ID is undefined");
    }
    else {
      var collection = document.getElementById('collection-input').value;
      var vectorize = document.getElementById('vectorize-checkbox').checked;
      sendVideoIdToPython(collection, getVideoId(response.url), vectorize);
    }
  });
});

document.getElementById("get-channel").addEventListener("click", function () {
  chrome.runtime.sendMessage({action: "getChannelID"}, function(response) {
    document.getElementById("videoIdContainer").textContent = response.channelId;
    console.log("Sending " + response.channelId + " channel ID to Python");
    if(response.channelId === undefined) {
      console.log("Channel ID is undefined");
    }
    else {
      var collection = document.getElementById('collection-input').value;
      var vectorize = document.getElementById('vectorize-checkbox').checked;
      sendChannelIdToPython(collection, response.channelId, vectorize);  
    }
  });
});

document.getElementById("get-url").addEventListener("click", function () {
  chrome.runtime.sendMessage({ action: "getURL" }, function (response) {
    document.getElementById("videoIdContainer").textContent = response.url;
    console.log("Sending " + response.url + " text to Python");

    if (response.url === undefined) {
      console.log("URL is undefined");
    }
    else {
      var collection = document.getElementById('collection-input').value;
      var vectorize = document.getElementById('vectorize-checkbox').checked;
      sendURLToPython(collection, response.url, vectorize);
    }
  });
});

document.getElementById("send-text").addEventListener("click", function () {
  chrome.runtime.sendMessage({ action: "sendText" }, function (response) {
    var text = document.getElementById("big-textarea").value;
    console.log("Sending " + text + " text to Python");

    if (text === undefined) {
      console.log("text is undefined");
    }
    else {
      var collection = document.getElementById('collection-input').value;
      var vectorize = document.getElementById('vectorize-checkbox').checked;
      sendTextToPython(collection, text, response.url, vectorize);
    }
  });
});