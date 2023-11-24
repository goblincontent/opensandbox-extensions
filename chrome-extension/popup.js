function getVideoId(url) {
  // console.log(url);
  // Use a regular expression to parse out the video ID
  var matchedExpression = url.match(/v=([a-zA-Z0-9_-]+)/);
  
  // If a match was found, return the first capture group (the video ID)
  if (matchedExpression) {
    // console.log(match[1]);
    return matchedExpression[1];
  }
  // If no match was found, return null
  else {
    return null;
  }
}

const sendVideoIdToPython = async (collection, message) => {
  try {
    const response = await fetch('http://localhost:5050/new_video_id', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ collection: collection, message: message }),
    });

    const responseData = await response.json();
    // console.log(responseData);
  } catch (error) {
    console.error("Error sending message:", error);
  }
}

const sendChannelIdToPython = async (collection, message) => {
  try {
    const response = await fetch('http://localhost:5050/new_channel_id', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ collection: collection, message: message }),
    });

    const responseData = await response.json();
    // console.log(responseData);
  } catch (error) {
    console.error("Error sending message:", error);
  }
}

const sendURLToPython = async (collection, message) => {
  try {
    const response = await fetch('http://localhost:5050/new_url', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ collection: collection, message: message }),
    });

    const responseData = await response.json();
    // console.log(responseData);
  } catch (error) {
    console.error("Error sending message:", error);
  }
}

const sendTextToPython = async (collection, message, url) => {
  try {
    const response = await fetch('http://localhost:5050/new_text', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ collection: collection, message: message, url: url }),
    });

    const responseData = await response.json();
    // console.log(responseData);
  } catch (error) {
    console.error("Error sending message:", error);
  }
}


document.getElementById("get-video").addEventListener("click", function() {
  chrome.runtime.sendMessage({action: "getVideoURL"}, function(response) {
      // If you want, you can display the video URL in the popup itself:
    document.getElementById("videoIdContainer").textContent = getVideoId(response.url);
    console.log("Sending " + getVideoId(response.url) + "video ID to Python");
    
    if (getVideoId(response.url) === undefined) {
      console.log("Video ID is undefined");
    }
    else {
      var collection = document.getElementById('collection-input').value;
      sendVideoIdToPython(collection, getVideoId(response.url));
    }
  });
});

document.getElementById("get-channel").addEventListener("click", function () {
  chrome.runtime.sendMessage({action: "getChannelID"}, function(response) {
      // If you want, you can display the video URL in the popup itself:
    document.getElementById("videoIdContainer").textContent = response.channelId;
    console.log("Sending " + response.channelId + " channel ID to Python");
    if(response.channelId === undefined) {
      console.log("Channel ID is undefined");
    }
    else {
      var collection = document.getElementById('collection-input').value;
      sendChannelIdToPython(collection, response.channelId);  
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
      sendURLToPython(collection, response.url);
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
      sendTextToPython(collection, text, response.url);
    }
  });
});