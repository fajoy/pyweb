window.ljs=function(s,b){var j = document.createElement('script');j.type = 'text/javascript'; j.src = s;j.onload = j.onreadystatechange = function(){j.onreadystatechange = j.onload = null;b&&b();};document.getElementsByTagName('head')[0].appendChild(j);}
function lcs(h) {$("head").append($("<link>").attr({rel:"stylesheet",type: "text/css",href:h}));};
var llog=window.llog=function(){
    if($("#logger").length>0){
        $("#logger" ).dialog();
        return;
    }
    $("body").append($("<div>").attr({id:"logger",title:"logger"}).append($("<div>").attr({id:"_logger"})));
    $("#logger" ).dialog({height: 300,width: 600,resize: function(e,ui){$("#_logger div").height($("#logger").height()-10);}});
    ljs('//log4javascript.org/js/log4javascript.js',function(){
    var a = new log4javascript.InPageAppender("_logger",false);
    l = window.log = log4javascript.getLogger();l.addAppender(a);
    $=jQuery;
    });
}
var ljui=function (){
lcs("//ajax.googleapis.com/ajax/libs/jqueryui/1.10.3/themes/smoothness/jquery-ui.css");
ljs("//ajax.googleapis.com/ajax/libs/jqueryui/1.10.3/jquery-ui.min.js",function(){llog();});
}
if(window.jQuery){
    (jQuery.ui)?llog(): ljui();
}else{
ljs('//ajax.googleapis.com/ajax/libs/jquery/2.0.2/jquery.min.js',ljui);
}
