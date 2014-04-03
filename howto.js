function fnSelect(objId)
{
   fnDeSelect();
   if (document.selection) 
   {
      var range = document.body.createTextRange();
      range.moveToElementText(document.getElementById(objId));
      range.select();
   }
   else if (window.getSelection) 
   {
      var range = document.createRange();
      range.selectNode(document.getElementById(objId));
      window.getSelection().addRange(range);
   }
}

function fnDeSelect() 
{
   if (document.selection)
             document.selection.empty();
   else if (window.getSelection)
              window.getSelection().removeAllRanges();
} 

function hasClass(clsName,elem)
{
  var re;
  var str = elem.className;
  re = new RegExp('(?:^|\\s+)' + clsName + '(?:\\s+|$)');
  return re.test(str) ? 1 : 0;
} 

function getElementsByClassName1(clsName, htmltag)
{
  var arr = new Array();   
  var elems = document.getElementsByTagName(htmltag);
  for ( var cls, i = 0; ( elem = elems[i] ); i++ ) {
    if ( hasClass(clsName,elem) ) {
      arr[arr.length] = elem;
    }
  }
  return arr;
}

function replaceWord( distVer, ver )
{
  fnDeSelect ();
  var version = document.getElementById (distVer).value;
  if ( document.getElementsByClassName != undefined ) {
    var vers = document.getElementsByClassName (ver);
  } else {
    var vers = getElementsByClassName1 (ver, 'span');
  }
  for ( var i = 0; i < vers.length; ++i) {
   vers[i].innerHTML = version;
  }
}
