!function(e){"object"==typeof exports&&"object"==typeof module?e(require("../../lib/codemirror")):"function"==typeof define&&define.amd?define(["../../lib/codemirror"],e):e(CodeMirror)}(function(e){"use strict";e.defineMode("ruby",function(e){function t(e){for(var t={},n=0,r=e.length;n<r;++n)t[e[n]]=!0;return t}function n(e,t,n){return n.tokenize.push(e),e(t,n)}function r(e,t){if(e.sol()&&e.match("=begin")&&e.eol())return t.tokenize.push(l),"comment";if(e.eatSpace())return null;var r,o=e.next();if("`"==o||"'"==o||'"'==o)return n(u(o,"string",'"'==o||"`"==o),e,t);if("/"==o)return i(e)?n(u(o,"string-2",!0),e,t):"operator";if("%"==o){var a="string",s=!0;e.eat("s")?a="atom":e.eat(/[WQ]/)?a="string":e.eat(/[r]/)?a="string-2":e.eat(/[wxq]/)&&(a="string",s=!1);var c=e.eat(/[^\w\s=]/);return c?(k.propertyIsEnumerable(c)&&(c=k[c]),n(u(c,a,s,!0),e,t)):"operator"}if("#"==o)return e.skipToEnd(),"comment";if("<"==o&&(r=e.match(/^<-?[\`\"\']?([a-zA-Z_?]\w*)[\`\"\']?(?:;|$)/)))return n(f(r[1]),e,t);if("0"==o)return e.eat("x")?e.eatWhile(/[\da-fA-F]/):e.eat("b")?e.eatWhile(/[01]/):e.eatWhile(/[0-7]/),"number";if(/\d/.test(o))return e.match(/^[\d_]*(?:\.[\d_]+)?(?:[eE][+\-]?[\d_]+)?/),"number";if("?"==o){for(;e.match(/^\\[CM]-/););return e.eat("\\")?e.eatWhile(/\w/):e.next(),"string"}if(":"==o)return e.eat("'")?n(u("'","atom",!1),e,t):e.eat('"')?n(u('"',"atom",!0),e,t):e.eat(/[\<\>]/)?(e.eat(/[\<\>]/),"atom"):e.eat(/[\+\-\*\/\&\|\:\!]/)?"atom":e.eat(/[a-zA-Z$@_\xa1-\uffff]/)?(e.eatWhile(/[\w$\xa1-\uffff]/),e.eat(/[\?\!\=]/),"atom"):"operator";if("@"==o&&e.match(/^@?[a-zA-Z_\xa1-\uffff]/))return e.eat("@"),e.eatWhile(/[\w\xa1-\uffff]/),"variable-2";if("$"==o)return e.eat(/[a-zA-Z_]/)?e.eatWhile(/[\w]/):e.eat(/\d/)?e.eat(/\d/):e.next(),"variable-3";if(/[a-zA-Z_\xa1-\uffff]/.test(o))return e.eatWhile(/[\w\xa1-\uffff]/),e.eat(/[\?\!]/),e.eat(":")?"atom":"ident";if("|"!=o||!t.varList&&"{"!=t.lastTok&&"do"!=t.lastTok){if(/[\(\)\[\]{}\\;]/.test(o))return d=o,null;if("-"==o&&e.eat(">"))return"arrow";if(/[=+\-\/*:\.^%<>~|]/.test(o)){var p=e.eatWhile(/[=+\-\/*:\.^%<>~|]/);return"."!=o||p||(d="."),"operator"}return null}return d="|",null}function i(e){for(var t,n=e.pos,r=0,i=!1,o=!1;null!=(t=e.next());)if(o)o=!1;else{if("[{(".indexOf(t)>-1)r++;else if("]})".indexOf(t)>-1){if(--r<0)break}else if("/"==t&&0==r){i=!0;break}o="\\"==t}return e.backUp(e.pos-n),i}function o(e){return e||(e=1),function(t,n){if("}"==t.peek()){if(1==e)return n.tokenize.pop(),n.tokenize[n.tokenize.length-1](t,n);n.tokenize[n.tokenize.length-1]=o(e-1)}else"{"==t.peek()&&(n.tokenize[n.tokenize.length-1]=o(e+1));return r(t,n)}}function a(){var e=!1;return function(t,n){return e?(n.tokenize.pop(),n.tokenize[n.tokenize.length-1](t,n)):(e=!0,r(t,n))}}function u(e,t,n,r){return function(i,u){var f,l=!1;for("read-quoted-paused"===u.context.type&&(u.context=u.context.prev,i.eat("}"));null!=(f=i.next());){if(f==e&&(r||!l)){u.tokenize.pop();break}if(n&&"#"==f&&!l){if(i.eat("{")){"}"==e&&(u.context={prev:u.context,type:"read-quoted-paused"}),u.tokenize.push(o());break}if(/[@\$]/.test(i.peek())){u.tokenize.push(a());break}}l=!l&&"\\"==f}return t}}function f(e){return function(t,n){return t.match(e)?n.tokenize.pop():t.skipToEnd(),"string"}}function l(e,t){return e.sol()&&e.match("=end")&&e.eol()&&t.tokenize.pop(),e.skipToEnd(),"comment"}var d,s=t(["alias","and","BEGIN","begin","break","case","class","def","defined?","do","else","elsif","END","end","ensure","false","for","if","in","module","next","not","or","redo","rescue","retry","return","self","super","then","true","undef","unless","until","when","while","yield","nil","raise","throw","catch","fail","loop","callcc","caller","lambda","proc","public","protected","private","require","load","require_relative","extend","autoload","__END__","__FILE__","__LINE__","__dir__"]),c=t(["def","class","case","for","while","until","module","then","catch","loop","proc","begin"]),p=t(["end","until"]),k={"[":"]","{":"}","(":")"};return{startState:function(){return{tokenize:[r],indented:0,context:{type:"top",indented:-e.indentUnit},continuedLine:!1,lastTok:null,varList:!1}},token:function(e,t){d=null,e.sol()&&(t.indented=e.indentation());var n,r=t.tokenize[t.tokenize.length-1](e,t),i=d;if("ident"==r){var o=e.current();r="."==t.lastTok?"property":s.propertyIsEnumerable(e.current())?"keyword":/^[A-Z]/.test(o)?"tag":"def"==t.lastTok||"class"==t.lastTok||t.varList?"def":"variable","keyword"==r&&(i=o,c.propertyIsEnumerable(o)?n="indent":p.propertyIsEnumerable(o)?n="dedent":"if"!=o&&"unless"!=o||e.column()!=e.indentation()?"do"==o&&t.context.indented<t.indented&&(n="indent"):n="indent")}return(d||r&&"comment"!=r)&&(t.lastTok=i),"|"==d&&(t.varList=!t.varList),"indent"==n||/[\(\[\{]/.test(d)?t.context={prev:t.context,type:d||r,indented:t.indented}:("dedent"==n||/[\)\]\}]/.test(d))&&t.context.prev&&(t.context=t.context.prev),e.eol()&&(t.continuedLine="\\"==d||"operator"==r),r},indent:function(t,n){if(t.tokenize[t.tokenize.length-1]!=r)return 0;var i=n&&n.charAt(0),o=t.context,a=o.type==k[i]||"keyword"==o.type&&/^(?:end|until|else|elsif|when|rescue)\b/.test(n);return o.indented+(a?0:e.indentUnit)+(t.continuedLine?e.indentUnit:0)},electricInput:/^\s*(?:end|rescue|elsif|else|\})$/,lineComment:"#",fold:"indent"}}),e.defineMIME("text/x-ruby","ruby")});