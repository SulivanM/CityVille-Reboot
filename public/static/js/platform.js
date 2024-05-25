var _____WB$wombat$assign$function_____ = function(name) {return (self._wb_wombat && self._wb_wombat.local_init && self._wb_wombat.local_init(name)) || self[name]; };
if (!self.__WB_pmw) { self.__WB_pmw = function(obj) { this.__WB_source = obj; return this; } }
{
  let window = _____WB$wombat$assign$function_____("window");
  let self = _____WB$wombat$assign$function_____("self");
  let document = _____WB$wombat$assign$function_____("document");
  let location = _____WB$wombat$assign$function_____("location");
  let top = _____WB$wombat$assign$function_____("top");
  let parent = _____WB$wombat$assign$function_____("parent");
  let frames = _____WB$wombat$assign$function_____("frames");
  let opener = _____WB$wombat$assign$function_____("opener");


var ZPAYMENTS;
if (!ZPAYMENTS) {ZPAYMENTS = {};};

ZPAYMENTS.zbillr_url = "https://secure1.zynga.com/zbillr";
ZPAYMENTS.offers_service_url = "https://secureapi.payments.zynga.com";
ZPAYMENTS.offers_path = "/platformservice/offerService/content";
ZPAYMENTS.provider_fb = "FACEBOOK_CREDITS";
ZPAYMENTS.provider_fbcoc = "FACEBOOK_CONNECT";
ZPAYMENTS.fbc_error_cancel = 1383010;
ZPAYMENTS.fbc_error_zcode = {"1383001":200, "1383002":200, "1383003":270, "1383004":200, "1383005":200, "1383006":200, "1383007":271, "1383008":200, "1383009":200, "1383011":200, "1353010":272, "1353011":273};

ZPAYMENTS.tp_start_url = ZPAYMENTS.zbillr_url + "/offers/tp_start";
ZPAYMENTS.tp_callback_url = ZPAYMENTS.offers_service_url  + "/platformservice/pricing/apps/%game_id%/offers/v0/vendors/trial_pay/";
ZPAYMENTS.tp_vendor_id = "5IZII44Z";
ZPAYMENTS.tp_type = 1;


if(window.jQuery){
	jQuery(document).ready(function(){
		ZPAYMENTS.tp_load();
	});
}

ZPAYMENTS.get_offerurl = function(gameid, snid, uid, clientid) {
	return ZPAYMENTS.offers_service_url + ZPAYMENTS.offers_path + "/gameId/" + gameid + "/snId/" + snid + "/uid/" + uid + "/client/" + clientid;
};

ZPAYMENTS.load_altpay = function (gameid, snid, uid, clientid, cb_fcn){
	var url = "https://zpay.static.zynga.com/zbillr/pages/altpay/banner.html";
	if(snid == 1){
		cb_fcn(url);
	}else{
		cb_fcn(false);
	};
};

ZPAYMENTS.earn = function(obj){
	if (typeof obj !== "object"){return false;}
	if (!obj.snid || !obj.gameid || !obj.uid){
		if (typeof window.console !== "undefined"){console.log("Earn Failed: Missing Params");};
		return;
	};
	ZPAYMENTS.sn_id   = obj.snid;
	ZPAYMENTS.uid     = obj.uid;
	ZPAYMENTS.game_id = obj.gameid;
	if (!obj.zhash || !obj.appid){
		ZPAYMENTS.fb_earn(obj);
		if (typeof window.console !== "undefined"){console.log("Missing required TRIALPAY params, using default earn method.");};
		return;
	};
	if (typeof window.TRIALPAY === "undefined"){
		ZPAYMENTS.tp_load();
	}
	jQuery.ajax({
		url: ZPAYMENTS.tp_start_url,
		data: {game_id: obj.gameid, sn_id: obj.snid, uid: obj.uid, tp_type: ZPAYMENTS.tp_type},
		dataType: "jsonp",
		success: function(data){
			if (data){
				obj.ip_address = data.ip_address;
				obj.pricing_system = data.pricing_system;
				obj.item_code = data.item_code;
				if (data.tp_direct){
					ZPAYMENTS.tp_earn(obj);
					return;
				}
			}
			ZPAYMENTS.fb_earn(obj);
		}
	});
};
ZPAYMENTS.deal_spot = function(obj){
	ZPAYMENTS.tp_type = 2;
	ZPAYMENTS.earn(obj);
};

ZPAYMENTS.tp_load  = function(){
	if (typeof window.TRIALPAY !== "undefined"){return;};
	var tp_script = document.createElement("script");
	tp_script.type = "text/javascript";
	tp_script.src = "//s-assets.tp-cdn.com/static3/js/api/payment_overlay.js";
	document.getElementsByTagName("body")[0].appendChild(tp_script);
}

ZPAYMENTS.tp_earn = function(obj){
	var order_info = "{}", callback_url = "", tp_obj = {}, currency_url = "", zindex = (obj.zindex) ? obj.zindex : 21;
	if (!obj.appid){return;}
	order_info = '{"s": '  + obj.snid + 
			     ',"t": '  + ZPAYMENTS.tp_type + 
			     ',"i": "' + obj.ip_address + 
			    '","c": '  + obj.clientid +'}';
	callback_url = ZPAYMENTS.tp_callback_url.replace('%game_id%', obj.gameid);
	currency_url = ZPAYMENTS.zbillr_url + "/offers/object?game_id=" + obj.gameid + "&app_id=" + obj.appid + "&consumer=facebook" + "&item_code=" + encodeURIComponent(obj.item_code);
	tp_obj = {
		"tp_vendor_id" 	: ZPAYMENTS.tp_vendor_id,
		"sid" 			: obj.zhash,
		"order_info" 	: order_info,
		"zIndex"		: zindex,
		"callback_url" 	: callback_url,
		"currency_url"	: currency_url,
		"onClose" 		: "ZPAYMENTS.tp_complete",
		"onTransact" 	: "ZPAYMENTS.tp_complete"
	};
	ZPAYMENTS.tp_callback = obj.callback;
	if (typeof window.console !== "undefined"){console.log ("TRIALPAY payload: appid=" + obj.appid +" ", tp_obj );};
	TRIALPAY.fb.show_overlay(
		obj.appid,
        "fbdirect",
		tp_obj
	);
	ZPAYMENTS.tp_type = 1;
};

ZPAYMENTS.tp_complete = function(response){
	if (response && response.vc_name){
		ZPAYMENTS.tp_response = response;
	}else if (ZPAYMENTS.tp_response) {
		ZPAYMENTS.tp_callback({order_id: "none", status: "settled", tp_response: ZPAYMENTS.tp_response});
		ZPAYMENTS.tp_response = undefined;
	}else{
		ZPAYMENTS.tp_callback({error_code:"cancel", error_message: "User closed/cancelled"});
	}
};

ZPAYMENTS.fb_earn = function(obj){
	obj.precallback = obj.precallback || function(){};
	ZPAYMENTS.get_offers(obj.gameid, obj.snid, obj.uid, obj.clientid, obj.precallback, obj.callback, obj.appid);
};

ZPAYMENTS.get_offers = function (gameid, snid, uid, clientid, cb_fcn, complete_fcn, appid){
	if (typeof window.console !== "undefined"){console.log("Calling FB Earn.");};
	ZPAYMENTS.sn_id   = snid;
	ZPAYMENTS.uid     = uid;
	ZPAYMENTS.game_id = gameid;
	if (complete_fcn === undefined){
		ZPAYMENTS.complete_fcn = false;
	}else{
		ZPAYMENTS.complete_fcn = complete_fcn;
	}
	ZPAYMENTS.app_id = (appid !== undefined) ? appid : false;
	cb_fcn(false);
	ZPAYMENTS.call_fbo(gameid, snid, uid,{});
};

ZPAYMENTS.call_fbo = function(gameid, snid, uid, data){
	var appinfo = ZPAYMENTS.app_id ? ', "app_id":"'+ZPAYMENTS.app_id+'" ' : '';
	var info = '{'+'"game_id":'+ ZPAYMENTS.game_id + 
					',"sn_id":'+ ZPAYMENTS.sn_id + 
			 		 ',"type":'+ '"offer"' + 
				 	   appinfo + '}';
				 	   
	var pay_obj ={};
	pay_obj = {
		method: 'pay.prompt',
		credits_purchase: false,
		order_info: info
	 };
	pay_obj.dev_purchase_params = {"oscif":true, "shortcut":"offer"};
	
	if (typeof(FB) == 'object'){
		if (typeof(FB.ui) == 'function'){
			FB.ui(pay_obj, ZPAYMENTS.fbo_complete);
		}
	}else if (typeof(SNAPI) == 'object'){
		SNAPI.registerOnload(function () {
			var fb = SNAPI.getNativeInterface();
			fb.ui(pay_obj, ZPAYMENTS.fbo_complete);
		});
	};
};
ZPAYMENTS.fbo_complete = function (response){
	if (response != null && response.error_code != null && parseInt(response.error_code) == ZPAYMENTS.fbc_error_cancel) {
		ZPAYMENTS.fbo_track_error(response.error_code);
	}
	if (ZPAYMENTS.complete_fcn){
		ZPAYMENTS.complete_fcn(response);
	}
};
ZPAYMENTS.fbo_track_error = function(ec){
	var track_host = ZPAYMENTS.zbillr_url + "/facebook_credits/track_offer_cancel";
	var track_params = "uid=" + ZPAYMENTS.uid + "&game_id=" + ZPAYMENTS.game_id + "&sn_id=" + ZPAYMENTS.sn_id + "&ec=" + ec;
	var track_url = track_host + "?" + track_params;

	var fbc_track_iframe = document.createElement('iframe');
	fbc_track_iframe.setAttribute('src',track_url);
	fbc_track_iframe.style.height = "0";
	fbc_track_iframe.style.width = "0";
	fbc_track_iframe.style.display = "none";
	document.body.appendChild(fbc_track_iframe);
};

ZPAYMENTS.crossFrameConfig = null;

ZPAYMENTS.openIframe = function(config){
  if(config.containerElementId && config.paymentsIframeUrl && config.iframeId){
    this.crossFrameConfig=config;
		var iframe=document.createElement("iframe");
		iframe.id= this.iframeId;
		iframe.src=config.paymentsIframeUrl;
		if(iframe.src.indexOf("?")==-1){
			iframe.src=iframe.src+"?";
		}
		var containerElement= document.getElementById(config.containerElementId);
		if(containerElement){
		  containerElement.innerHTML="";
			containerElement.appendChild(iframe);
			containerElement.style.display='block';
		}
	}
};

ZPAYMENTS.closeIframe = function(){
  if(this.crossFrameConfig.containerElementId){
		var containerElement= document.getElementById(this.crossFrameConfig.containerElementId);
		containerElement.style.display='none';
	}
	var iframe= document.getElementById(this.crossFrameConfig.iframeId);
	if(iframe){
		iframe.parentNode.style.display='none';
		iframe.parentNode.removeChild(iframe);
	}
};

if (jQuery && jQuery.receiveMessage){
	jQuery.receiveMessage(
		function(e){
			if(!e.origin || e.origin.toLowerCase().indexOf("zynga") <0){
				return;
			}
			if(e.data){
				try{
					var data = jQuery.parseJSON(e.data);
					if(data && data.action && (data.action ==1)){
						ZPAYMENTS.closeIframe();
					}
				}catch (ex){}
			}
		}
	);
};



/**
* BC: Legacy
*/
function loadOfferContent(){
};


}