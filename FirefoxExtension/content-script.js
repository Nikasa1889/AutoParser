XToken = '00irkrr9xcl7tyfp';
token_upload_products = "b2h6ylyfn6pfvoz5wuvc";
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

//Skip error when ajax return status:0 
$(document).ajaxError(function(e, jqxhr, settings, exception) {
  if (jqxhr.readyState == 0 || jqxhr.status == 0) {
    return; //Skip this error
  }
});


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
function getOffer(offerId, offers){
    console.log('getting offer '+ offerId);
    //Return a promise
    return $.ajax({
            url: 'https://api.etilbudsavis.dk/v2/offers/'+offerId+'?r_lat=59.95&r_lng=10.75&r_radius=100000&api_av=0.1.23',
            type: 'GET',
            dataType: 'json',
            headers: {
                'X-token': XToken,
                'Origin': 'https://etilbudsavis.dk'},
            success: function(returnedOffer){
                offers.push(returnedOffer);
                }
            });
}
function parse(url){
    console.log("Parsing "+url);
    var prefix = /^(http|https)?:\/\/etilbudsavis\.dk\/catalogs\//
    catalogId= url.replace(prefix, "");
    var offers = [];
    console.log(catalogId);
    $.ajax({
        url: 'https://api.etilbudsavis.dk/v2/catalogs/'+catalogId+'/hotspots?r_lat=59.95&r_lng=10.75&r_radius=100000&api_av=0.1.23',
        type: 'GET',
        dataType: 'json',
        headers: {
            'X-token': XToken,
            'Origin': 'https://etilbudsavis.dk'},
        success: function(result) {
            //console.log(JSON.stringify(result));
            var offerPromises = [];
            result.forEach(function(obj){
                offerPromises.push(getOffer(obj.id, offers));
            });
            $.when.apply($, offerPromises).then(function(){
                    console.log("All ajax finished");
                    console.log(JSON.stringify(offers));
                    chrome.runtime.sendMessage({"offers": offers, "str_offers":JSON.stringify(offers)});
                }
            ).then(function(){
                submitOffers(getStoreId(offers), JSON.stringify(offers));
            });
        },
        error: function(err){
            alert(JSON.stringify(err));
            },
        complete: function(){
            console.log("complete parsing");
        }
    });
}

function getStoreId(offers){
    var branding = offers[0]["branding"]["name"];
    if (branding.indexOf("Coop") >= 0 && branding.indexOf("Extra") >= 0) {
        return 3;
    }
    if (branding.indexOf("Coop") >= 0 && branding.indexOf("Prix") >= 0) {
        return 4;
    }
    if (branding.indexOf("Coop") >= 0 && branding.indexOf("Mega") >= 0) {
        return 6;
    }
    if (branding.indexOf("Kiwi") >= 0) {
        return 5;
    }
    return 0;
}
function submitOffers(store_id, str_offers){
    $.ajax({
        url: 'http://52.59.243.6:8000/upload_products/'+store_id+'/'+token_upload_products+'/',
        type: 'GET',
        headers: {
            'Origin': 'http://52.59.243.6:8000/'},
        crossDomain: true,
        contentType: "application/json",
        data: {"offer.offer.offerId.USSellerId": {"$gt": 50}},
        success: function(result) {
            console.log(JSON.stringify(result));
        },
        error: function(err){
            console.log(JSON.stringify(err));
        },
        complete: function(){
            console.log("Complete submitting");
        }
    });
    //notify("Document for "+store_id+ " has been submitted");
}


var hasStorage = (function() {
	try {
		localStorage.setItem("mod", "mod");
		localStorage.removeItem("mod");
		return true;
	} catch (exception) {
        console.log(exception);
		return false;
	}
}());

function getXToken(){
    if (hasStorage){
        try {
            var session = localStorage.getItem("com.eta.sdk.sessions");
            session = JSON.parse(session);
            var data = session.data;
            var token = data[Object.keys(data)[0]].token;
            XToken = token;
            console.log("Catched token: " + token);
        }
        catch (e){
            alert("Can't get token automatically, use pre-set token");
            console.log(e);
        }
    }

}

function notifyExtension(e) {
  var target = e.target;
  while ((target.tagName != "A" || !target.href) && target.parentNode) {
    target = target.parentNode;
  }
  if (target.tagName != "A")
    return;
  if (isValidUrl(target.href)){
    getXToken();
    parse(target.href);
  }
}

/*
Add notifyExtension() as a listener to click events.
*/
window.addEventListener("click", notifyExtension);
