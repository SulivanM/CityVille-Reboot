(function(c){c.fn.colorTip=function(e){var d={color:"black",timeout:50};var f=["red","green","blue","white","yellow","black"];e=c.extend(d,e);return this.each(function(){var j=c(this);if(!j.attr("title")){return true}var l=new a();var k=new b(j.attr("title"));j.append(k.generate()).addClass("colorTipContainer");var h=false;for(var g=0;g<f.length;g++){if(j.hasClass(f[g])){h=true;break}}if(!h){j.addClass(e.color)}j.hover(function(){k.show();l.clear()},function(){l.set(function(){k.hide()},e.timeout)});j.removeAttr("title")})};function a(){}a.prototype={set:function(d,e){this.timer=setTimeout(d,e)},clear:function(){clearTimeout(this.timer)}};function b(d){this.content=d;this.shown=false}b.prototype={generate:function(){return this.tip||(this.tip=c('<span class="colorTip">'+this.content+'<span class="pointyTipShadow"></span><span class="pointyTip"></span></span>'))},show:function(){if(this.shown){return}this.tip.css("margin-left",-this.tip.outerWidth()/2).fadeIn("fast");this.shown=true},hide:function(){this.tip.fadeOut();this.shown=false}}})(jQuery);