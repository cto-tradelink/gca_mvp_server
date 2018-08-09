from django.conf.urls import url, include
from django.contrib import admin
from . import views
from .views import *

urlpatterns = [
    url(r'^login3/$', views.login_user3, name='login_user3', ),
    url(r'^$', views.index, name='index', ),
    url(r'^category/(?P<category>.*)/(?P<id>[0-9]+)/$', views.category_last_depth, name='category_last_depth', ),
    url(r'^category/(?P<category>.*)/$', views.category, name='category', ),
    url(r'^login2/$', views.login_user, name='login', ),
    url(r'^signup/$', views.signup, name='signup', ),
    url(r'^logout/$', views.logout_user, name='logout', ),
    url(r'^accounts/social/signup/$', views.repeated_email, name='repeated_email'),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^startup_list/$', views.startup_list, name='startup_list', ),
    url(r'^startup/(?P<id>[0-9]+)/$', views.startup_detail, name='startup_detail', ),
    url(r'^mypage/profile_thumbnail$', views.profile_thumbnail, name='profile_thumbnail'),
    url(r'^mypage/edit$', views.edit_mypage, name='edit_mypage', ),
    url(r'^mypage/$', views.mypage, name='mypage', ),
    url(r'^mypage/company_profile/$', views.company_profile, name='company_profile', ),
    url(r'^mypage/company_profile/new/$', views.company_profile_new, name='company_profile_new', ),
    url(r'^mypage/company_profile/edit/$', views.company_profile_edit, name='company_profile_edit', ),
    url(r'^mypage/company_thumbnail$', views.company_thumbnail, name='company_thumbnail'),
    url(r'^mypage/my_profile/$', views.my_profile, name='my_profile', ),
    url(r'^mypage/my_profile/edit/$', views.my_profile_edit, name='my_profile_edit', ),
    url(r'^matching_business/$', views.matching_business, name='matching_business'),
    url(r'^matching/$', views.matching, name='matching'),
    url(r'^search/', views.support_list, name='support_list', ),
    url(r'^mypage/apply/$', views.new_apply, name='new_apply', ),
    url(r'^mypage/apply/(?P<id>[0-9]+)/$', views.apply, name='apply', ),
    url(r'^support/(?P<id>[0-9]+)/$', views.support, name='support', ),
    url(r'^new_support/$', views.new_support, name='new_support', ),
    url(r'^manage/mypage$', views.manage_mypage, name='manage_mypage', ),
    url(r'^manage/support_list', views.manage_support, name='manage_support', ),
    url(r'^manage/support/(?P<id>[0-9]+)/$', views.manage_support_detail, name='manage_support_detail', ),
    url(r'^pdfver_support/(?P<id>[0-9]+)/$', views.pdfver_support, name='pdfver_support', ),
    url(r'^pdf/(?P<id>[0-9]+)/', views.pdf, name="pdf"),
    url(r'^search/', views.search, name='search', ),
    url(r'^apply/(?P<id>[0-9]+)/', views.apply, name='apply', ),
    url(r'^apply/edit/(?P<sbid>[0-9]+)/(?P<id>[0-9]+)', views.apply_edit, name='apply_edit', ),
    url(r'^add_interest/', views.add_interest, name='add_interest', ),
    url(r'^manager/$', views.manager, name='manager', ),
    url(r'^manager/account/edit/$', views.manager_edit, name='manager_edit', ),
    url(r'^manager/total/$', views.total, name='total', ),
    url(r'^manager/sb_list/$', views.sb_list, name='sb_list', ),
    url(r'^manager/all/sb_list/$', views.sb_list_all, name='sb_list_all', ),
    url(r'^manager/sb_detail/(?P<id>[0-9]+)/$', views.sb_detail, name='sb_detail', ),
    url(r'^manager/dashboard/$', views.dashboard, name='dashboard', ),
    url(r'^manager/write/$', views.write, name='write', ),
    url(r'^manager/support/edit/(?P<id>[0-9]+)/$', views.sb_edit, name='sb_edit', ),
    url(r'^manager/sb_example/(?P<id>[0-9]+)/$', views.example, name='example', ),
    url(r'^manager/select/(?P<id>[0-9]+)$', views.pick_winner, name='pick_winner', ),
    url(r'^save_filter/$', views.save_filter, name='save_filter', ),
    url(r'^preview/(?P<id>[0-9]+)/$', views.sb_preview, name='preview', ),
    url(r'^preview_pdf/(?P<id>[0-9]+)/$', views.sb_preview, name='preview_pdf', ),
    url(r'^load_recent_appliance/$', views.load_recent_appliance, name='load_recent_appliance', ),
    url(r'^rate_page/$', views.rate_page, name='rate_page', ),
    url(r'^get_alarm_status/$', views.get_alarm_status, name='get_alarm_status', ),
    url(r'^apply/preview/(?P<sbid>[0-9]+)/(?P<id>[0-9]+)', views.apply_preview, name='apply_preview', ),
    url(r'^apply/preview/pdf/(?P<sbid>[0-9]+)/(?P<id>[0-9]+)', views.apply_preview_pdf, name='apply_preview_pdf', ),
    url(r'^apply_preview/(?P<sbid>[0-9]+)/', views.apply_preview_doc, name='apply_preview_doc', ),
    url(r'^get_all_award/(?P<sbid>[0-9]+)/', views.get_all_award, name='get_all_award', ),
    url(r'^get_all_inter/(?P<sbid>[0-9]+)/', views.get_all_inter, name='get_all_inter', ),
    url(r'^appliance_download/(?P<apid>[0-9]+)/', views.appliance_download, name='appliance_download', ),
    url(r'^appliance_all_download/(?P<sb>[0-9]+)/', views.appliance_all_download, name='appliance_all_download', ),
    url(r'^manage/startup_list_manage/', views.startup_sb_manage, name='startup_sb_manage', ),
    url(r'^manage/startup_list_manage_all/', views.startup_sb_manage_all, name='startup_sb_manage_all', ),
    url(r'^manage/startup_list_manage_person/', views.startup_p_manage_all, name='startup_p_manage_all', ),
    url(r'^manage/pick_winner_pdf/(?P<id>[0-9]+)/', views.pick_winner_pdf, name='pick_winner_pdf', ),
    url(r'^pdf_down_pick_winner/(?P<id>[0-9]+)/', views.pdf_down_pick_winner, name='pdf_down_pick_winner', ),
    url(r'^sb_detail_pdf/(?P<id>[0-9]+)/', views.sb_detail_pdf, name='sb_detail_pdf', ),
    url(r'^sb_detail_pdf_down/(?P<id>[0-9]+)/', views.sb_detail_pdf_down, name='sb_detail_pdf_down', ),
    url(r'^all_sp_download/(?P<id>.*)/', views.all_sp_download, name='all_sp_download', ),
    url(r'^all_user_sp_download_index/', views.all_user_sp_download_index, name='all_user_sp_download_index', ),
    url(r'^all_user_sp_download/', views.all_user_sp_download, name='all_user_sp_download', ),
    url(r'^set_stop/', views.set_stop, name='set_stop', ),
    url(r'^set_start/', views.set_start, name='set_start', ),
    url(r'^delete_sb/', views.delete_sb, name='delete_sb', ),
    url(r'^manage/manager_account/', views.manager_account, name='manager_account', ),
    url(r'^manage/add_manager_acc/', views.add_manager_acc, name='add_manager_acc', ),
    url(r'^manage/del_manager_acc/', views.del_manager_acc, name='del_manager_acc', ),
    url(r'^stop/', views.stop_sb, name='stop_sb', ),
    url(r'^accept/', views.accept_sb, name='accept_sb', ),
    url(r'^upload_xls_startup/', views.upload_xls_startup, name='upload_xls_startup', ),
    url(r'^upload_xls_acc/', views.upload_xls_admin, name='upload_xls_admin', ),
    url(r'^send_email/', views.send_email, name='send_email', ),
    url(r'^get_sp_excel/', views.get_sp_excel, name='get_sp_excel', ),
    url(r'^get_stl_excel/', views.get_stl_excel, name='get_stl_excel', ),
    url(r'^get_stp_excel/', views.get_stp_excel, name='get_stp_excel', ),
    url(r'^get_sbtl_excel/', views.get_sbtl_excel, name='get_sbtl_excel', ),
    url(r'^get_sbtl2_excel/', views.get_sbtl2_excel, name='get_sbtl2_excel', ),
    url(r'^get_repre/', views.get_repre, name='get_repre', ),
    url(r'^change_stage/', views.change_stage, name='change_stage', ),
    url(r'^static_graph/', views.static, name='static', ),














    url(r'^vue_home_grant/', views.vue_home_grant, name='vue_home_grant', ),
    url(r'^get_grant_detail/', views.get_grant_detail, name='get_grant_detail', ),
    url(r'^get_static_info/', views.get_static_info, name='get_static_info', ),
    url(r'^get_grant_static_detail/', views.get_grant_static_detail, name='get_grant_static_detail', ),
    url(r'^get_all_static_info/', views.get_all_static_info, name='get_all_static_info', ),

    url(r'^similar_grant/', views.similar_grant, name='similar_grant', ),
    url(r'^vue_get_startup_list/', views.vue_get_startup_list, name='vue_get_startup_list', ),
    url(r'^vue_get_startup_detail/', views.vue_get_startup_detail, name='vue_get_startup_detail', ),
    url(r'^vue_update_startup_detail/', views.vue_update_startup_detail, name='vue_update_startup_detail', ),
    url(r'^vue_update_startup_with_application_1/', views.vue_update_startup_with_application_1, name='vue_update_startup_with_application_1', ),
    url(r'^vue_update_startup_with_application_2/', views.vue_update_startup_with_application_2, name='vue_update_startup_with_application_2', ),

    url(r'^vue_get_application/', views.vue_get_application, name='vue_get_application', ),
    url(r'^vue_update_application/', views.vue_update_application, name='vue_update_application', ),
    url(r'^vue_get_dashboard/', views.vue_get_dashboard, name='vue_get_dashboard', ),
    url(r'^vue_set_application/', views.vue_set_application, name='vue_set_application', ),

    url(r'^vue_get_grant_info/', views.vue_get_grant_info, name='vue_get_grant_info', ),
    url(r'^vue_set_grant_1/', views.vue_set_grant_1, name='vue_set_grant_1', ),
    url(r'^vue_set_grant_2/', views.vue_set_grant_2, name='vue_set_grant_2', ),
    url(r'^vue_set_grant_3/', views.vue_set_grant_3, name='vue_set_grant_3', ),
    url(r'^vue_set_grant_4/', views.vue_set_grant_4, name='vue_set_grant_4', ),
    url(r'^vue_set_grant_5/', views.vue_set_grant_5, name='vue_set_grant_5', ),
    url(r'^vue_set_grant_6/', views.vue_set_grant_6, name='vue_set_grant_6', ),
    url(r'^vue_static_user/', views.vue_static_user, name='vue_static_user', ),
    url(r'^vue_get_startup_account/', views.vue_get_startup_account, name='vue_get_startup_account', ),
    url(r'^vue_add_manager_acc/', views.vue_add_manager_acc, name='vue_add_manager_acc', ),
    url(r'^vue_get_grant_list/', views.vue_get_grant_list, name='vue_get_grant_list', ),
    url(r'^vue_get_child/', views.vue_get_child, name='vue_get_child', ),
    url(r'^vue_get_grant_by_manager/', views.vue_get_grant_by_manager, name='vue_get_grant_by_manager', ),
    url(r'^vue_sign/', views.vue_sign, name='vue_sign', ),
    url(r'^vue_get_Kakao_auth/', views.vue_get_Kakao_auth, name='vue_get_Kakao_auth', ),
    url(r'^vue_get_agent_dashboard/', views.vue_get_agent_dashboard, name='vue_get_agent_dashboard', ),
    url(r'^vue_get_agent_account/', views.vue_get_agent_account, name='vue_get_agent_account', ),
    url(r'^vue_get_grant_list_excel/', views.vue_get_grant_list_excel, name='vue_get_grant_list_excel', ),
    url(r'^cert_email/', views.cert_email, name='cert_email', ),
    url(r'^vue_login_user/', views.vue_login_user, name='vue_login_user', ),
    url(r'^vue_toggle_interest_st/', views.vue_toggle_interest_st, name='vue_toggle_interest_st', ),
    url(r'^vue_toggle_interest_sb/', views.vue_toggle_interest_sb, name='vue_toggle_interest_sb', ),
    url(r'^vue_my_interest_set/', views.vue_my_interest_set, name='vue_my_interest_set', ),
    url(r'^vue_my_interest_set_detail/', views.vue_my_interest_set_detail, name='vue_my_interest_set_detail', ),
    url(r'^vue_signup/', views.vue_signup, name='vue_signup', ),
    url(r'^vue_upload_clip/', views.vue_upload_clip, name='vue_upload_clip', ),
    url(r'^vue_get_lec_tag/', views.vue_get_lec_tag, name='vue_get_lec_tag', ),
    url(r'^vue_get_clip/', views.vue_get_clip, name='vue_get_clip', ),
    url(r'^vue_upload_course/', views.vue_upload_course, name='vue_upload_course', ),
    url(r'^vue_get_course/', views.vue_get_course, name='vue_get_course', ),
    url(r'^vue_upload_path/', views.vue_upload_path, name='vue_upload_path', ),

    url(r'^vue_get_course/', views.vue_get_course, name='vue_get_course', ),
    url(r'^vue_get_path/', views.vue_get_path, name='vue_get_path', ),
    url(r'^get_startup_application/', views.get_startup_application, name='get_startup_application', ),
    url(r'^vue_remove_service_product/', views.vue_remove_service_product, name='vue_remove_service_product', ),
    url(r'^vue_del_startup_news/', views.vue_del_startup_news, name='vue_del_startup_news', ),
    url(r'^vue_get_user_info/', views.vue_get_user_info, name='vue_get_user_info', ),
    url(r'^get_home_info/', views.get_home_info, name='get_home_info', ),
    url(r'^vue_get_startup_list_sample/', views.vue_get_startup_list_sample, name='vue_get_startup_list_sample', ),
    url(r'^vue_sample_list_clip/', views.vue_sample_list_clip, name='vue_sample_list_clip', ),
    url(r'^vue_sample_course_path/', views.vue_sample_course_path, name='vue_sample_course_path', ),
    url(r'^vue_sample_path_path/', views.vue_sample_path_path, name='vue_sample_path_path', ),
    url(r'^vue_get_statics_by_channel/', views.vue_get_statics_by_channel, name='vue_get_statics_by_channel', ),
    url(r'^vue_get_sns_auth/', views.vue_get_sns_auth, name='vue_get_sns_auth', ),
    url(r'^vue_get_startup_detail_manager/', views.vue_get_startup_detail_manager, name='vue_get_startup_detail_manager', ),
    url(r'^vue_get_grant_detail/', views.vue_get_grant_detail, name='vue_get_grant_detail', ),
    url(r'^vue_get_manager_list/', views.vue_get_manager_list, name='vue_get_manager_list', ),
    url(r'^vue_get_grant_ttl/', views.vue_get_grant_ttl, name='vue_get_grant_ttl', ),
    url(r'^toggle_int_clip/', views.toggle_int_clip, name='toggle_int_clip', ),
    url(r'^toggle_int_course/', views.toggle_int_course, name='toggle_int_course', ),
    url(r'^toggle_int_path/', views.toggle_int_path, name='toggle_int_path', ),

    url(r'^vue_hit_clip_log/', views.vue_hit_clip_log, name='vue_hit_clip_log', ),
    url(r'^vue_watch_clip_history/', views.vue_watch_clip_history, name='vue_watch_clip_history', ),
    url(r'^vue_hit_course_log/', views.vue_hit_course_log, name='vue_hit_course_log', ),
    url(r'^vue_watch_course_history/', views.vue_watch_course_history, name='vue_watch_course_history', ),
    url(r'^vue_hit_path_log/', views.vue_hit_path_log, name='vue_hit_path_log', ),
    url(r'^vue_watch_path_history/', views.vue_watch_path_history, name='vue_watch_path_history', ),
    url(r'^vue_get_ing_lecture/', views.vue_get_ing_lecture, name='vue_get_ing_lecture', ),
    url(r'^vue_get_clip_uploaded/', views.vue_get_clip_uploaded, name='vue_get_clip_uploaded', ),
    url(r'^vue_get_course_uploaded/', views.vue_get_course_uploaded, name='vue_get_course_uploaded', ),
    url(r'^vue_get_manager_lecture/', views.vue_get_manager_lecture, name='vue_get_manager_lecture', ),
    url(r'^vue_get_channel_statics_path/', views.vue_get_channel_statics_path, name='vue_get_channel_statics_path', ),
    url(r'^vue_get_channel_statics_course/', views.vue_get_channel_statics_course, name='vue_get_channel_statics_course', ),
    url(r'^vue_get_channel_statics_clip/', views.vue_get_channel_statics_clip, name='vue_get_channel_statics_clip', ),
    url(r'^getfiles/', views.getfiles, name='getfiles', ),
    url(r'^vue_get_clip_all/', views.vue_get_clip_all, name='vue_get_clip_all', ),
    url(r'^vue_get_course_all/', views.vue_get_course_all, name='vue_get_course_all', ),
    url(r'^vue_get_path_all/', views.vue_get_path_all, name='vue_get_path_all', ),
    url(r'^vue_set_grant_information/', views.vue_set_grant_information, name='vue_set_grant_information', ),
    url(r'^vue_get_grant_information/', views.vue_get_grant_information, name='vue_get_grant_information', ),
    url(r'^vue_set_service_show/', views.vue_set_service_show, name='vue_set_service_show', ),
    url(r'^vue_get_grant_appliance/', views.vue_get_grant_appliance, name='vue_get_grant_appliance', ),
    url(r'^vue_set_activity_like/', views.vue_set_activity_like, name='vue_set_activity_like', ),
    url(r'^vue_get_all_fav/', views.vue_get_all_fav, name='vue_get_all_fav', ),
    url(r'^hit_sb/', views.hit_sb, name='hit_sb', ),
    url(r'^search2/', views.search2, name='search2', ),
    url(r'^vue_get_grant_optional_data/', views.vue_get_grant_optional_data, name='vue_get_grant_optional_data', ),
    url(r'^vue_set_user_info/', views.vue_set_user_info, name='vue_set_user_info', ),
    url(r'^vue_get_startup_detail_manager_base/', views.vue_get_startup_detail_manager_base, name='vue_get_startup_detail_manager_base', ),
    url(r'^vue_update_startup_detail_base/', views.vue_update_startup_detail_base, name='vue_update_startup_detail_base', ),
    url(r'^get_unread_alarm/', views.get_unread_alarm, name='get_unread_alarm', ),
    url(r'^vue_fav_sb_list/', views.vue_fav_sb_list,name='vue_fav_sb_list', ),
    url(r'^get_sb_hit_log/', views.get_sb_hit_log,name='get_sb_hit_log', ),


]
import debug_toolbar

urlpatterns.append(url(r'^__debug__/', include(debug_toolbar.urls)))
