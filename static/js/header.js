/*收藏网页*/
function AddFavorite(sURL, sTitle) {
    try {
        window.external.addFavorite(sURL, sTitle);
    } catch (e) {
        try {
            window.sidebar.addPanel(sTitle, sURL, "");
        } catch (e) {
            alert("加入收藏失败，请使用Ctrl+D进行添加");
        }
    }
}

/*设置首页*/
function setcjcpHome(url) {
    if (document.all) {
        document.body.style.behavior = 'url(#default#homepage)';
        document.body.setHomePage(url);
    } else if (window.sidebar) {
        if (window.netscape) {
            try {
                netscape.security.PrivilegeManager.enablePrivilege("UniversalXPConnect");
            } catch (e) {
                alert("彩经网提示：该操作被浏览器拒绝，如果想启用该功能，请在地址栏内输入 about:config,然后将项 signed.applets.codebase_principal_support 值该为true");
            }
        }
        if (window.confirm("你确定要设置" + url + "为首页吗？") == 1) {
            var prefs = Components.classes['@mozilla.org/preferences-service;1'].getService(Components.interfaces.nsIPrefBranch);
            prefs.setCharPref('browser.startup.homepage', url);
        }
    }
}

/*头部onmouseover事件js*/
function xlcd(obj) {
    document.onmouseover = function (event) {
        var e = event || window.event;
        var elem = e.srcElement || e.target;

        var cz_arr = new Array("hzdl", "wbgz", "zhje", "wbgzh", "gddh");
        while (elem) {
            try {
                for (var i = 0; i < cz_arr.length; i++) {
                    if ($(elem).attr('id') == cz_arr[i] || $(elem).attr('id') == 'fl_' + cz_arr[i]) {
                        $("#" + cz_arr[i]).addClass("in");
                        $("#fl_" + cz_arr[i]).show();
                        //如何当前坐标在层上则返回
                        return;
                    } else {
                        $("#" + cz_arr[i]).removeClass("in")
                        $("#fl_" + cz_arr[i]).hide();
                    }
                }
            } catch (err) {
                //卸载onmouseover事件  
                document.onmouseover = null;
            }
            elem = elem.parentNode;
        }
        //卸载onmouseover事件
        document.onmouseover = null;
    };
}

/*头部客服专线QQ联系联系我们*/
function show_headerlx(imgpath) {
    document.write('<div class="zxqq"><script charset="utf-8" type="text/javascript" src="http://wpa.b.qq.com/cgi/wpa.php?key=XzkzODA1NzgwN18yODc1MzRfNDAwODE2ODg3Nl8"></script></div>');
}

/*头部搜索JS*/
function searchaa(obj) {
    if (obj.value == '' || obj.value == null) {
        alert('搜索内容不能为空！');
        return false;
    }
}

/*全部分类onmouseover事件 JS*/
function show_all(obj) {
    document.onmouseover = function (event) {
        var e = event || window.event;
        var elem = e.srcElement || e.target;
        while (elem) {
            try {
                if ($(elem).attr('id') == "fc_all" || $(elem).attr('id') == 'all_con' || $(elem).attr('id') == 'fl_div') {
                    $("#fc_all").attr('class', 'all_fl_s');
                    $("#all_con").show();
                    $("#cpyc").removeClass("li_in")
                    $("#fl_cpyc").hide();
                    return;//如何当前坐标在层上则返回                        
                } else {
                    $("#fc_all").attr('class', 'all_fl_x');
                    $("#all_con").hide();
                }

            } catch (err) {

                document.parentNode.onmouseover = null;//卸载onmouseover事件
            }
            elem = elem.parentNode;
        }
        //document.parentNode.onmouseover = null;//卸载onmouseover事件
    };
}

/*一级菜单onmouseover事件 JS*/
function xlcds_new(obj) {
    document.onmouseover = function (event) {
        var e = event || window.event;
        var elem = e.srcElement || e.target;

        var cz_arr = new Array("cpyc", "zjph", "cp_kj", "tz_gl", "jc_tz", "jjc", "zst_gj", "zm_tm", "jq_cd", "cmsc");
        while (elem) {
            try {
                for (var i = 0; i < cz_arr.length; i++) {
                    if ($(elem).attr('id') == cz_arr[i] || $(elem).attr('id') == 'fl_' + cz_arr[i] || $(elem).attr('id') == 'all_con') {
                        if ($(elem).attr('id') == 'all_con') return;
                        $("#" + cz_arr[i]).addClass("li_in");
                        $("#fl_" + cz_arr[i]).show();
                        return;//如何当前坐标在层上则返回                        
                    } else {
                        $("#" + cz_arr[i]).removeClass("li_in")
                        $("#fl_" + cz_arr[i]).hide();
                    }
                }
            } catch (err) {
                document.onmouseover = null;//卸载onmouseover事件
                $("#all_con").hide();
            }
            elem = elem.parentNode;
        }
        document.onmouseover = null;//卸载onmouseover事件
        $("#all_con").hide();
    };
}

/**
 *设置cookie weihongwei add <2013-10-28>
 */
function setCookie(c_name, value, expiredays) {
    var exdate = new Date();
    exdate.setDate(exdate.getDate() + expiredays);
    document.cookie = c_name + "=" + escape(value) +
        ((expiredays == null) ? "" : ";expires=" + exdate.toGMTString()) + ";path=/";
}

//获取cookie weihongwei add <2013-10-28>
function getCookie(c_name) {
    if (document.cookie.length > 0) {
        c_start = document.cookie.indexOf(c_name + "=");
        if (c_start != -1) {
            c_start = c_start + c_name.length + 1;
            c_end = document.cookie.indexOf(";", c_start);
            if (c_end == -1) {
                c_end = document.cookie.length;
            }
            return decodeURIComponent(document.cookie.substring(c_start, c_end));
        }
    }
    return null;
}

/*删除Cookie*/
function delcookie(name) {
    var exp = new Date();
    exp.setTime(exp.getTime() - 1);
    var cval = getcookie(name);
    document.cookie = name + "=" + cval + ";expires=" + exp.toGMTString();
}

//弹出层
/*登陆*/
function denglu() {
    $.webox({
        height: 280,
        width: 390,
        bgvisibel: true,
        title: '登录信息',
        html: $("#degnlu_con").html()
    });
}

/*注册*/
function zhuce() {
    $.webox({
        height: 465,
        width: 390,
        bgvisibel: true,
        title: '注册信息',
        //html:$("#zhuce_con").html()
        iframe: 'zhuce_con.php?' + Math.random
    });
}

//$.getJSON("http://www.cjcp.com.cn/member/ly_set.php?curl="+location.href+"&format=json&jsoncallback=?",function(data){
//}); 
