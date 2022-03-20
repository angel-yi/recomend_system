function dj(i){
  $('.bottom2 .n_tab_title a').removeClass('n_on').eq(i).addClass('n_on');
  $('.bottom2 .n_tabcons .n_tabcon').hide().eq(i).show();
}