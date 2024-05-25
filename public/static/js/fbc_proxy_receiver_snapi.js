var fbc_error_zcode = {
	"1383001":200,
	"1383002":200,
	"1383003":270,
	"1383004":200,
	"1383005":200,
	"1383006":200,
	"1383007":271,
	"1383008":200,
	"1383009":200,
	"1383011":200,
	"1353010":272,
	"1353011":273
}
var fbc_error_cancel = 1383010;
var fbc_return_exempt = ['/promo', '/donation'];

function call_fbc(info_string, return_url, zugid){
	
	try{
		fbc_info_obj = jQuery.parseJSON(info_string);
	}catch(err){
		try {
			fbc_info_obj = JSON.parse(info_string);
		}catch(err){
			fbc_info_obj = false;
		}
	}
	
	fbc_payments_zugid = unescape(zugid);
	
	fbc_return_url = return_url ;

	var pay_obj = {
	           method: 'pay.prompt',
	           order_info: info_string,
	           purchase_type: 'item'
		};
	pay_obj.dev_purchase_params = { "oscif": true };	
	fb = SNAPI.getNativeInterface();
	fb.ui(pay_obj, fbc_complete);

}
function fbc_complete (response) {
	if (response.error_code != null){
		fbc_track_error(response.error_code);
	}
	fbc_reload_payments(response);
}
function fbc_reload_payments(response){

	var payments_iframe = fbc_iframe_seek(document.getElementsByTagName('iframe'));

	if (payments_iframe){
		if (response.order_id != null  && fbc_info_obj){

			payments_iframe.src = "https://secure1.zynga.com/zbillr/receipts/fbc" + "?order_id=" + response.order_id +
													  "&zugid=" + fbc_payments_zugid+
													  "&game_id="+fbc_game_id(fbc_payments_zugid)+
													  "&uid="+fbc_uid(fbc_payments_zugid)+
													  "&sn_id="+fbc_sn_id(fbc_payments_zugid)+
													  "&full_locale="+fbc_info_obj.full_locale+
													  "&terms_id=" + fbc_info_obj.terms_id+ 
													  "&layout=" + fbc_info_obj.layout;  
		}else if (response.error_code != null){
			if (parseInt(response.error_code) == fbc_error_cancel){
                payments_iframe.src = payments_iframe.src + "&cancel";
			}else if (fbc_error_zcode[response.error_code.toString()]  && fbc_info_obj){
				payments_iframe.src = "https://secure1.zynga.com/zbillr/errors" + "?game_id="+fbc_game_id(fbc_payments_zugid)+
										           "&uid="+fbc_uid(fbc_payments_zugid)+
										    	   "&sn_id="+fbc_sn_id(fbc_payments_zugid)+
												   "&ec="  + fbc_error_zcode[response.error_code.toString()]+
 												   "&full_locale="+fbc_info_obj.full_locale;
			}else{
				setTimeout('fbc_return_to_game', 500);
			}
		}
	}else{
		setTimeout('fbc_return_to_game', 500);
	}
}
function fbc_return_to_game () {
	top.location.href = fbc_return_url;
}
function fbc_game_id (zugid) {
	var arr = zugid.split(':');
	return arr[2];
}
function fbc_sn_id (zugid) {
	var arr = zugid.split(':');
	return arr[0];
}
function fbc_uid (zugid) {
	var arr = zugid.split(':');
	return arr[1];
}
function fbc_track_error (ec) {
	var zugid     = fbc_payments_zugid;
	var game_id   = fbc_game_id(zugid);
    var sn_id     = fbc_sn_id(zugid);
	var track_host = "https://secure1.zynga.com/zbillr/facebook_credits/track_cancel";
	var track_params = "zugid=" + zugid + "&game_id=" + game_id + "&sn_id=" + sn_id + "&ec=" + ec;
	if (!fbc_info_obj){
		track_params += "&json=false"
	}
	var track_url = track_host + "?" + track_params;

	var fbc_track_iframe = document.createElement('iframe');
	fbc_track_iframe.setAttribute('src',track_url);
	fbc_track_iframe.style.height = "0";
	fbc_track_iframe.style.width = "0";
	fbc_track_iframe.style.display = "none";
	document.body.appendChild(fbc_track_iframe);
}
function fbc_iframe_seek (iframes) {
	var static_url = "http://zpay.static.zynga.com/zbillr"; 
	var secure_url = "https://secure1.zynga.com/zbillr"; 
	for (var i=0; i < iframes.length; i++) {
		if (fbc_iframe_check(static_url, iframes[i].src)  || fbc_iframe_check(secure_url, iframes[i].src) ){
			return  iframes[i];
		}
	}
	for (var i=0; i < iframes.length; i++) {
		try {
			var subframes = iframes[i].contentWindow.document.getElementsByTagName('iframe');
		}catch(err){ 
			var subframes = null;
		}
		if (subframes != null && subframes.length > 0){
			var elem = fbc_iframe_seek(subframes);
			if (elem){
				return elem;
			}
		}
	}
	return false;
}
function fbc_iframe_check(name, url){
	for (var i=0; i < fbc_return_exempt.length; i++) {
		if (url.indexOf(fbc_return_exempt[i]) != -1){
			return false;
		}
	}
	return url.indexOf(name) != -1 && url.indexOf('packages') != -1;
}
