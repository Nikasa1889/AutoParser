/*
Log that we received the message.
Then display a notification. The notification contains the URL,
which we read from the message.
*/
function notify(message) {
  var title = "Notification";
  var content = message;
  chrome.notifications.create({
    "type": "basic",
    "iconUrl": chrome.extension.getURL("icons/link-48.png"),
    "title": title,
    "message": content
  });
}

function getCatalogName(offers){
    var branding = offers[0]["branding"]["name"];
    var run_from = offers[0]["run_from"];
    var catalog_name = branding+"_"+run_from;
    return catalog_name;
}
function storeNote(catalog_name, str_offers){
    chrome.storage.local.set({ [catalog_name] : str_offers }, function() {
    if(chrome.runtime.lastError) {
      console.log(chrome.runtime.lastError);
    } else {
      notify(catalog_name+" has been stored");
    }
  });
}

function receiveOffers(message){
    console.log("background script received offers");
    var offers = message.offers;
    var str_offers = message.str_offers;
    var catalog_name = getCatalogName(offers);
    console.log(catalog_name);
    storeNote(catalog_name, str_offers);
}
/*
Assign `notify()` as a listener to messages from the content script.
*/
chrome.runtime.onMessage.addListener(receiveOffers);
