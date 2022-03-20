function isIE() { 
	//indexOf() 若找到, 返回大于0; 若没有找到,则返回 -1 。
    if (window.navigator.userAgent.toString().toLowerCase().indexOf("msie") >= 1)
        return true;
    else
        return false;
}
//firefox innerText define
//if (!isIE()) {   
//	HTMLElement.prototype.__defineGetter__( "innerText",
//		function () {
//			var anyString = "";
//			var childS = this.childNodes;
//			for(var i = 0; i < childS.length; i++) {
//				//处理空白字符
//				if(childS[i].nodeType == 1)
//					anyString += childS[i].tagName == "BR" ? '\n' : childS[i].innerText;
//				else if(childS[i].nodeType == 3)
//					anyString += childS[i].nodeValue;
//			}
//			return anyString;
//		}
//	);
//	HTMLElement.prototype.__defineSetter__( "innerText",
//		function (sText) {
//			this.textContent = sText;
//		}
//	);
//}

//记录当前页的浏览器高度
var currentClientHeight = 0;
//记录当前页的浏览器宽度
var currentClientWidth = 0;

function onLoadLine(tbodyId, startIndex, len, cssName) {
 
    if (currentClientHeight == document.documentElement.clientHeight
        && currentClientWidth == document.documentElement.clientWidth) {
　　　　return;
　　}
　　currentClientHeight = document.documentElement.clientHeight;
    currentClientWidth = document.documentElement.clientWidth;

    oZXZ.clear();    
    //分析参数
    var indexParam = getArrayFormString(startIndex);     
    var lenParam = getArrayFormString(len);
    var cssParam = getCssArrayFormString(cssName);
    
    //加载线
    objectZXZ = oZXZ.bind(tbodyId, cssParam);
    for (var i = 0; i < indexParam.length; i++) {
        objectZXZ.add(indexParam[i], 0, lenParam[i], 0);
        //从左边开始第几个单元格
        //从上边开始第几个单元格
        //单元格个数
        //离下面的行数(0：到最后一行)             a
    }
    objectZXZ.draw(ESUNChart.ini.default_has_line);
}

//分析参数
function getArrayFormString(param) {
    //分析参数
    var returnArray = new Array();
    if (param != "" && param != undefined) {
        //有线的情况
        if (param.indexOf(",") > 0) {
             //有多条线的情况
             returnArray = param.split(",");
        } else {
             //只有一条线的情况
             returnArray[0] = param;
        }
    }
    return returnArray;
}

//分析CSS
function getCssArrayFormString(param) {
    //分析参数
    var returnArray = new Array();
    var cssParamTemp = new Array();
    if (param != "" && param != undefined) {
        //有线的情况
        if (param.indexOf(",") > 0) {
             //有多条线的情况
             cssParamTemp = param.split(",");
        } else {
         //只有一条线的情况
         cssParamTemp[0] = param;
        }
    }
    countIndex = 0;
    for (var i = 0; i < cssParamTemp.length; i++) {
        returnArray[countIndex] = cssParamTemp[i];
        countIndex = countIndex + 1;
        returnArray[countIndex] = "backChange " + cssParamTemp[i];
        countIndex = countIndex + 1;
    }
    return returnArray;
}