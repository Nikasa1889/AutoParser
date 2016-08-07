$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (settings.type == 'POST' || settings.type == 'PUT' || settings.type == 'DELETE') {
            function getCookie(name) {
                var cookieValue = null;
                if (document.cookie && document.cookie != '') {
                    var cookies = document.cookie.split(';');
                    for (var i = 0; i < cookies.length; i++) {
                        var cookie = jQuery.trim(cookies[i]);
                        // Does this cookie string begin with the name we want?
                        if (cookie.substring(0, name.length + 1) == (name + '=')) {
                            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                            break;
                        }
                    }
                }
                return cookieValue;
            }
            if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                // Only send the token to relative URLs i.e. locally.
                xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
            }
        }
    }
});

JSON.stringify = JSON.stringify || function (obj) {
    var t = typeof (obj);
    if (t != "object" || obj === null) {
        // simple data type
        if (t == "string") obj = '"'+obj+'"';
        return String(obj);
    }
    else {
        // recurse array or object
        var n, v, json = [], arr = (obj && obj.constructor == Array);
        for (n in obj) {
            v = obj[n]; t = typeof(v);
            if (t == "string") v = '"'+v+'"';
            else if (t == "object" && v !== null) v = JSON.stringify(v);
            json.push((arr ? "" : '"' + n + '":') + String(v));
        }
        return (arr ? "[" : "{") + String(json) + (arr ? "]" : "}");
    }
};

// Check valid URL from etilbudsavis.dk
function isValidUrl(url)
{
    //regular expression for one shop in etilbudsavis.dk
    var pattern = /^(http|https)?:\/\/etilbudsavis\.dk\/catalogs\/\S*/;
 
    if(pattern.test(url)){
        return true;
    } else {
        return false;
    }
}
function parse(url){
    console.log("Parsing "+url);
    var prefix = /^(http|https)?:\/\/etilbudsavis\.dk\/catalogs\//
    catalogId= url.replace(prefix, "");
    console.log(catalogId);
/*     $.ajax({
        url: 'https://api.etilbudsavis.dk/v2/sessions',
        type: 'POST',
        dataType: 'json',
        headers: {
            'Host': 'api.etilbudsavis.dk',
            'Origin': 'https://etilbudsavis.dk'},
        success: function(result) {
            alert(JSON.stringify(result));
            data = result;
        },
        error: function(err){
            alert(JSON.stringify(err));
            data = err;
        }
    });
 */    
    $.ajax({
        url: 'https://api.etilbudsavis.dk/v2/catalogs/'+catalogId+'/hotspots?r_lat=59.95&r_lng=10.75&r_radius=100000&api_av=0.1.23',
        type: 'GET',
        dataType: 'json',
        headers: {
            'X-token': '00irkrr9xcl7tyfp',
            'Origin': 'https://etilbudsavis.dk'},
        success: function(result) {
            alert(JSON.stringify(result));
            data = result;
        },
        error: function(err){
            alert(JSON.stringify(err));
            data = err;
        }
    });
}

function notifyExtension(e) {
  var target = e.target;
  while ((target.tagName != "A" || !target.href) && target.parentNode) {
    target = target.parentNode;
  }
  if (target.tagName != "A")
    return;
  if (isValidUrl(target.href)){
    console.log("content script sending message");
    chrome.runtime.sendMessage({"url": target.href});
    parse(target.href);
  }
}

/*
Add notifyExtension() as a listener to click events.
*/
window.addEventListener("click", notifyExtension);
