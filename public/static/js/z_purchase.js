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

var ZPURCHASE;
if (!ZPURCHASE) {ZPURCHASE = {};}

ZPURCHASE.zbillr_url = "https://secure1.zynga.com/zbillr";
ZPURCHASE.service_url = "https://secureapi.payments.zynga.com";
ZPURCHASE.service_path = "/platformservice/v1/checkout/add_to_cart";
ZPURCHASE.bb_path = "/iovation/create";
ZPURCHASE.fbc_error_cancel = 1383010;
ZPURCHASE.fbc_return_exempt = ['/promo', '/donation'];
ZPURCHASE.fbc_error_zcode = {"1383001":200, "1383002":200, "1383003":270, "1383004":200, "1383005":200, "1383006":200, "1383007":271, "1383008":200, "1383009":200, "1383011":200, "1353010":272, "1353011":273};
ZPURCHASE.order_version = 1;
ZPURCHASE.order_type = 'gdp';
ZPURCHASE.ref = "in_game";	// default ref for ingame flow
ZPURCHASE.appid = ""; // default app id
ZPURCHASE.loop = 0;
ZPURCHASE.price_card_code = null;
 

ZPURCHASE.purchase_token_url = function() {
	return ZPURCHASE.service_url + ZPURCHASE.service_path ;
}
ZPURCHASE.encode_url_param = function(str) {
	return encodeURIComponent(str).replace(/!/g, '%21').replace(/'/g, '%27').replace(/\(/g, '%28').replace(/\)/g, '%29').replace(/\*/g, '%2A').replace(/%20/g, '+'); 
}
ZPURCHASE.item = {
	data: {},
	set_title: function (title){
		if (!title || title.length < 1) { return; }
		this.data.name = title;
	},
	set_description: function (description){
		if (!description || description.length < 1) { return; }
		this.data.user_facing_description = description;
	},
	set_image_url: function (image_url){
		if (!image_url || image_url.length < 1) { return; }
		this.data.absolute_image_url = image_url;
	},
	override: function (item){
		if (typeof(item)!='object') { return; }
	    this.set_title(item.title);
		this.set_description(item.description);
		this.set_image_url(item.image_url);
	},
	prep: function () {
		return ZPURCHASE.obj_to_json(ZPURCHASE.item.data);
	},
	_reset: function(){
		this.data = {};
	}
};
ZPURCHASE.add_to_cart = function (gameid, snid, uid, clientid, itemcode, qty, cb_fcn, complete_fcn, ref, appid, sig, session){

	if (!gameid || !snid || !uid || !clientid || !itemcode || !qty){
		if (typeof window.console !== "undefined"){
			console.log("add to cart FAILED: Missing Params");
		}
		cb_fcn({success:false, error_code: 0 , error_message: "Missing Params"});
		return;
	}
	ZPURCHASE.sn_id   = snid;
	ZPURCHASE.client_id = clientid;
	ZPURCHASE.uid     = uid;
	ZPURCHASE.game_id = gameid;
	ZPURCHASE.cb_fcn  = cb_fcn;
	if (typeof(complete_fcn) == "undefined"){
		ZPURCHASE.complete_fcn = false;
	}else{
		ZPURCHASE.complete_fcn = complete_fcn;
	}
	var token_url = ZPURCHASE.purchase_token_url();
	token_url = token_url + '?uid=' + uid + '&game_id=' + gameid + '&sn_id=' + snid + '&item_code=' + itemcode + '&quantity=' + qty + "&client_id=" + clientid;

	// append reference
	token_url += "&ref=";
	if (typeof(ref)!='undefined') {
		ZPURCHASE.ref = ref;
		token_url += ZPURCHASE.encode_url_param(ref);
	}
	
	// append app id
	token_url += "&appid=";
	if (typeof(appid)!='undefined') {
		ZPURCHASE.appid = appid;
		token_url += appid;
	}
	
	// append sig
	token_url += "&sig=";
	if (typeof(sig)!='undefined') {
		ZPURCHASE.sig = sig;
		token_url += ZPURCHASE.encode_url_param(sig);
	}
	
	if (typeof(ZPURCHASE.price_card_code)!='undefined' && ZPURCHASE.price_card_code != null) {
		token_url += "&price_card_code="+ZPURCHASE.encode_url_param(ZPURCHASE.price_card_code);
	}
	
	// if standalone
	if (parseInt(ZPURCHASE.sn_id) == 104){
		var price_card_code = (typeof(ZPURCHASE.price_card_code)!='undefined' && ZPURCHASE.price_card_code != null) ? ZPURCHASE.price_card_code : "" ;
		var dapi_params = {
			clientId: clientid,
			itemCode: itemcode,
			quantity: qty,
			priceCardCode: price_card_code,
			reference: ref
		};
		if (ZPURCHASE.item.data.name){dapi_params.overrideName = ZPURCHASE.item.data.name;}
		if (ZPURCHASE.item.data.user_facing_description){dapi_params.overrideDescription = ZPURCHASE.item.data.user_facing_description;}
		if (ZPURCHASE.item.data.image_url){dapi_params.overrideImageUrl = ZPURCHASE.item.data.image_url;}
		if (ZPURCHASE.sig){dapi_params.signature = ZPURCHASE.sig;}
		ZPURCHASE.zdc(dapi_params);
		return;
	}
	
	// append session if there's one present
	if (typeof(session)!='undefined') {
	    token_url += "&session=" + ZPURCHASE.encode_url_param(session);
	}

	token_url += "&item_data="+ ZPURCHASE.encode_url_param(ZPURCHASE.item.prep());
	
	token_url = token_url + "&callback=?";
	jQuery.getJSON(token_url, function(data){
		if (data.session){
			ZPURCHASE.create_bb(data.session);
			ZPURCHASE.session=data.session;
			if (data.product_url&&parseInt(ZPURCHASE.sn_id)==1) {
				var pay_obj = {
					method: 'pay',
					action: 'purchaseitem',
					product: data.product_url,
					quantity: 1, 
					request_id: data.session  
				}
			}else{
				var info = '{"session":"'+data.session+
						  '","version":' +ZPURCHASE.order_version+
						   ',"game_id":' + ZPURCHASE.game_id + 
						   ',"sn_id":' + ZPURCHASE.sn_id;
				if (ZPURCHASE.appid != undefined && ZPURCHASE.appid.length>0){
					info = info +    ',"app_id":' + ZPURCHASE.appid; 
				}
				info = info + ',"type":"'+ZPURCHASE.order_type+'"}';
				var pay_obj = {
					method: 'pay',
					order_info: info,
					purchase_type: 'item',
					dev_purchase_params: {"oscif":true}
				}
			}
			cb_fcn({success:true, response: data});
			ZPURCHASE.fbc(pay_obj);
		} else {
			cb_fcn({success:false, error_code: data.messageId , error_message: data.message, response: data});
		}
	});		
}

ZPURCHASE.zdc = function(params){
	if (typeof window.SNAPI === "undefined" || typeof window.DAPI === "undefined" || typeof window.ZDC === "undefined") {
		throw "Error: Missing required library, ZDC.js, SNAPI and/or DAPI is not loaded";
	} else {
		DAPI.api.send({
			method: 'payments.checkout',
			payload: params, 
			callback: function(session) {
				if (session && !session.error) {
					ZPURCHASE.cb_fcn({success:true});
					ZDC.ui.pay(params.itemCode, params.quantity, params.priceCardCode, null, {
						plain: true
					}).success(function(result) {
						ZPURCHASE.complete_fcn(result);
					}).error(function(err) {
						ZPURCHASE.complete_fcn(err);
					}).canceled(function(reason) {
						ZPURCHASE.complete_fcn(reason);
					}).closed(function() {
						ZPURCHASE.complete_fcn({error_code:1000, error_message: "User closed/canceled"});
					}).provide('paymentsSession', function(callbackSession) {
						callbackSession(session);
					});
				}else{
					ZPURCHASE.cb_fcn({success:false, response: session});
				}
			}
		});
	}
}

ZPURCHASE.fbc = function(pay_obj){
	if (typeof(FB) == 'object'){
		if (typeof(FB.ui) == 'function'){
			FB.ui(pay_obj, ZPURCHASE.fbc_complete);
		}
	}else if (typeof(SNAPI) == 'object'){
		SNAPI.registerOnload(function () {
			var fb = SNAPI.getNativeInterface();
			fb.ui(pay_obj, ZPURCHASE.fbc_complete);
		});
	}
};


ZPURCHASE.fbc_complete = function (response){
	ZPURCHASE.item._reset();
	if (response == null){return;}
	if (response.error_code != null && parseInt(response.error_code) == ZPURCHASE.fbc_error_cancel) {
		ZPURCHASE.track_error(response.error_code);
	}
	if (response.payment_id){
		ZPURCHASE.payment_complete(response);
	}
	if (ZPURCHASE.complete_fcn && typeof(ZPURCHASE.complete_fcn) != "undefined"){
		ZPURCHASE.complete_fcn(response); 
	}
}
ZPURCHASE.payment_complete = function(response){
	if(!response.payment_id){return;}
	var url = ZPURCHASE.zbillr_url + "/facebook_payment_processor/index?";
	var p = {
		session: ZPURCHASE.session,
		game_id: ZPURCHASE.game_id,
		sn_id: ZPURCHASE.sn_id,
		app_id: ZPURCHASE.appid,
		uid: ZPURCHASE.uid,
		ref: ZPURCHASE.ref,
		client_id: ZPURCHASE.client_id,
		response: ZPURCHASE.obj_to_json(response)
	};
	url +=  jQuery.param(p);
	ZPURCHASE.pixelTrack(url);
}
ZPURCHASE.track_error = function(ec){
	var track_host = ZPURCHASE.zbillr_url + "/facebook_credits/track_purchase_cancel";
	var track_params = "uid=" + ZPURCHASE.uid + "&game_id=" + ZPURCHASE.game_id + "&sn_id=" + ZPURCHASE.sn_id + "&ec=" + ec;
	track_params += "&ref=" + ZPURCHASE.ref;
	var track_url = track_host + "?" + track_params;
	if (document.getElementById('zpurchase_err')){
		document.getElementById('zpurchase_err').setAttribute('src',track_url);
	}else{
		var fbc_track_iframe = document.createElement('iframe');
		fbc_track_iframe.setAttribute('src',track_url);
		fbc_track_iframe.setAttribute('id','zpurchase_err');
		fbc_track_iframe.style.height = "0";
		fbc_track_iframe.style.width = "0";
		fbc_track_iframe.style.display = "none";
		document.body.appendChild(fbc_track_iframe);
	}
}
ZPURCHASE.pixelTrack =function(url){
	var img=document.createElement("img");
	img.style.height="0";
	img.style.width="0";
	img.src=url;
	document.getElementsByTagName("body")[0].appendChild(img);	
	document.getElementsByTagName("body")[0].removeChild(img);
}
ZPURCHASE.create_bb = function (token) {
	var iov_host = ZPURCHASE.zbillr_url + "/iovation/create";
	var iov_params = "token=" + token;
	var iov_url = iov_host + "?" + iov_params;
	if (document.getElementById('zpurchase_iov')){
		document.getElementById('zpurchase_iov').setAttribute('src',iov_url);
	}else{
		var iov_iframe = document.createElement('iframe');
		iov_iframe.setAttribute('src',iov_url);
		iov_iframe.setAttribute('id','zpurchase_iov');
		iov_iframe.style.height = "0";
		iov_iframe.style.width = "0";
		iov_iframe.style.display = "none";
		document.body.appendChild(iov_iframe);		
	}
}
ZPURCHASE.obj_to_json = function (obj) {
	var t = typeof (obj);
	if (t != "object" || obj === null) {
		if (t == "string") obj = '"'+obj+'"';
		return String(obj);
	}
	else {
		var n, v, json = [], arr = (obj && obj.constructor == Array);
		for (n in obj) {
			v = obj[n]; t = typeof(v);
			if (t == "string") v = '"'+v+'"';
			else if (t == "object" && v !== null) v = ZPURCHASE.obj_to_json(v);
			json.push((arr ? "" : '"' + n + '":') + String(v));
		}
		return (arr ? "[" : "{") + String(json) + (arr ? "]" : "}");
	}
};


}