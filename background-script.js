/*
Log that we received the message.
Then display a notification. The notification contains the URL,
which we read from the message.
*/
function notify(url) {
  var title = chrome.i18n.getMessage("notificationTitle");
  var content = chrome.i18n.getMessage("notificationContent", url);
  chrome.notifications.create({
    "type": "basic",
    "iconUrl": chrome.extension.getURL("icons/link-48.png"),
    "title": title,
    "message": content
  });
}
function receiveURL(message){
    console.log("background script received message");
    var url = message.url;
    notify(url);
}
/*
Assign `notify()` as a listener to messages from the content script.
*/
chrome.runtime.onMessage.addListener(receiveURL);
