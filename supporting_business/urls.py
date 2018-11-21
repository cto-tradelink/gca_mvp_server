from django.conf.urls import url, include
from django.contrib import admin
from . import views
from . import views_paging
from .views import *

urlpatterns = [

    # 전체 공통 라우팅
    url(r'^$', views.index, name='index', ),
    url(r'^login_sns/', views.login_sns, name='login_sns', ),
    url(r'^logout', views.logout, name='logout', ),
    url(r'^get_site_statics_update', views.get_site_statics_update, name='get_site_statics_update', ),
    url(r'^vue_login_check/', views.vue_login_check, name='vue_login_check', ),
    url(r'^vue_get_startup_public_detail/', views.vue_get_startup_public_detail, name='vue_get_startup_public_detail', ),
    url(r'^vue_home_support_business', views.vue_home_support_business, name='vue_home_support_business', ),
    url(r'^get_support_business_detail', views.get_support_business_detail, name='get_support_business_detail', ),
    url(r'^vue_get_filter', views.vue_get_filter, name='vue_get_filter', ),
    url(r'^similar_support_business/', views.similar_support_business, name='similar_support_business', ),
    url(r'^vue_get_startup_list/', views_paging.startup_list, name='startup_list', ),
    url(r'^vue_login_user/', views.vue_login_user, name='vue_login_user', ),
    url(r'^vue_login_user/', views.vue_login_user, name='vue_login_user', ),
    url(r'^cert_email/', views.cert_email, name='cert_email', ),
    url(r'^vue_signup/', views.vue_signup, name='vue_signup', ),
    url(r'^vue_get_clip/', views.vue_get_clip, name='vue_get_clip', ),
    url(r'^vue_get_course_information/', views.vue_get_course_information, name='vue_get_course_information', ),
    url(r'^vue_get_clip_all/', views.vue_get_clip_all, name='vue_get_clip_all', ),
    url(r'^get_home_info/', views.get_home_info, name='get_home_info', ),
    url(r'^get_realtime_support_business_appliance/', views.get_realtime_support_business_appliance, name='get_realtime_support_business_appliance', ),
    url(r'^other_support_business_support_business/', views_paging.other_support_business_support_business, name='other_support_business_support_business', ),
    url(r'^user_account_person/', views_paging.user_account_person,    name='mng_user_account_person', ),
    url(r'^support_business_detail_appliance/', views_paging.support_business_detail_appliance,  name='support_business_detail_appliance', ),
    url(r'^support_business_detail_favorite/', views_paging.support_business_detail_favorite,  name='support_business_detail_favorite', ),
    url(r'^support_business_detail_awarded/', views_paging.support_business_detail_awarded,name='support_business_detail_awarded', ),
    url(r'^statics_my_support_business_ing_hit/', views_paging.statics_my_support_business_ing_hit,  name='statics_my_support_business_ing_hit', ),
    url(r'^statics_my_support_business_ing_fav/', views_paging.statics_my_support_business_ing_fav, name='statics_my_support_business_ing_fav', ),
    url(r'^statics_my_support_business_ing_appliance/', views_paging.statics_my_support_business_ing_appliance,   name='statics_my_support_business_ing_appliance', ),
    url(r'^email_check', views.email_check, name='email_check', ),
    url(r'^excel_down_support_business_gwanri_aw', views.excel_down_support_business_gwanri_aw, name='excel_down_support_business_gwanri_aw', ),
    url(r'^check_company_name', views.check_company_name,  name='check_company_name', ),


    url(r'^vue_get_name', views.vue_get_name, name='vue_get_name', ),
    url(r'^make_pdf', views.make_pdf, name='make_pdf', ),
    url(r'^vue_get_download_usr_account_selected', views.vue_get_download_usr_account_selected, name='vue_get_download_usr_account_selected', ),
    url(r'^mng_vue_get_kikwan_account_excel', views.mng_vue_get_kikwan_account_excel, name='mng_vue_get_kikwan_account_excel', ),
    url(r'^similar_filter_support_business', views.similar_filter_support_business,name='similar_filter_support_business', ),
    url(r'^startup_list_by_or', views_paging.startup_list_by_or, name='startup_list_by_or', ),
    url(r'^download_appliance/', views.download_appliance, name='download_appliance', ),
    url(r'^download', views.download, name='download', ),
    url(r'^del_file', views.del_file, name='del_file', ),
    url(r'^vue_home_support_business_new', views.vue_home_support_business_new, name='vue_home_support_business_new', ),



    # 로그인한 스타트업 유저
    url(r'^vue_get_startup_detail', views.vue_get_startup_detail, name='vue_get_startup_detail', ),
    url(r'^vue_update_startup_detail/', views.vue_update_startup_detail, name='vue_update_startup_detail', ),
    url(r'^vue_update_startup_head_detail/', views.vue_update_startup_head_detail,name='vue_update_startup_head_detail', ),
    url(r'^vue_update_startup_with_application_1/', views.vue_update_startup_with_application_1,name='vue_update_startup_with_application_1', ),
    url(r'^vue_update_startup_with_application_2/', views.vue_update_startup_with_application_2, name='vue_update_startup_with_application_2', ),
    url(r'^vue_update_startup_with_application_3/', views.vue_update_startup_with_application_3,name='vue_update_startup_with_application_3', ),
    url(r'^vue_update_startup_with_application_4/', views.vue_update_startup_with_application_4, name='vue_update_startup_with_application_4', ),
    url(r'^vue_update_startup_with_application_6/', views.vue_update_startup_with_application_6, name='vue_update_startup_with_application_6', ),
    url(r'^vue_get_application/', views.vue_get_application, name='vue_get_application', ),
    url(r'^vue_my_favorite_set/', views.vue_my_favorite_set, name='vue_my_favorite_set', ),
    url(r'^vue_upload_clip/', views.vue_upload_clip, name='vue_upload_clip', ),
    url(r'^vue_get_lec_tag/', views.vue_get_lec_tag, name='vue_get_lec_tag', ),
    url(r'^vue_get_author_lecture/', views.vue_get_author_lecture, name='vue_get_author_lecture', ),
    url(r'^get_favorite_support_business_list/', views.get_favorite_support_business_list, name='get_favorite_support_business_list', ),
    url(r'^vue_upload_course/', views.vue_upload_course, name='vue_upload_course', ),
    url(r'^vue_get_course/', views.vue_get_course, name='vue_get_course', ),
    url(r'^vue_upload_path/', views.vue_upload_path, name='vue_upload_path', ),
    url(r'^get_favorite_startup/', views.get_favorite_startup, name='get_favorite_startup', ),
    url(r'^get_support_business_favorite_startup/', views.get_support_business_favorite_startup, name='get_support_business_favorite_startup', ),
    url(r'^vue_modify_course/', views.vue_modify_course, name='vue_modify_course', ),
    url(r'^vue_get_path/', views.vue_get_path, name='vue_get_path', ),
    url(r'^get_startup_application', views.get_startup_application, name='get_startup_application', ),
    url(r'^vue_remove_service_product/', views.vue_remove_service_product, name='vue_remove_service_product', ),
    url(r'^vue_del_startup_news/', views.vue_del_startup_news, name='vue_del_startup_news', ),
    url(r'^vue_get_usr_info/', views.vue_get_usr_info, name='vue_get_usr_info', ),
    url(r'^get_home_info/', views.get_home_info, name='get_home_info', ),
    url(r'^vue_get_startup_list_sample/', views.vue_get_startup_list_sample, name='vue_get_startup_list_sample', ),
    url(r'^vue_get_sns_auth/', views.vue_get_sns_auth, name='vue_get_sns_auth', ),
    url(r'^vue_submit_application/', views.vue_submit_application, name='vue_submit_application', ),
    url(r'^vue_hit_clip_log/', views.vue_hit_clip_log, name='vue_hit_clip_log', ),
    url(r'^vue_watch_history/', views.vue_watch_history, name='vue_watch_history', ),
    url(r'^vue_channel_process_check/', views.vue_channel_process_check, name='vue_channel_process_check', ),
    url(r'^vue_hit_course_log/', views.vue_hit_course_log, name='vue_hit_course_log', ),
    url(r'^vue_hit_path_log/', views.vue_hit_path_log, name='vue_hit_path_log', ),
    url(r'^vue_get_clip_uploaded/', views.vue_get_clip_uploaded, name='vue_get_clip_uploaded', ),
    url(r'^vue_get_course_uploaded/', views.vue_get_course_uploaded, name='vue_get_course_uploaded', ),
    url(r'^vue_get_author_lecture/', views.vue_get_author_lecture, name='vue_get_author_lecture', ),
    url(r'^vue_set_activity_like/', views.vue_set_activity_like, name='vue_set_activity_like', ),
    url(r'^vue_get_all_favorite/', views.vue_get_all_favorite, name='vue_get_all_favorite', ),
    url(r'^hit_support_business/', views.hit_support_business, name='hit_support_business', ),
    url(r'^vue_set_usr_info/', views.vue_set_usr_info, name='vue_set_usr_info', ),
    url(r'^vue_update_startup_detail_base/', views.vue_update_startup_detail_base, name='vue_update_startup_detail_base', ),
    url(r'^vue_get_startup_detail_base/', views.vue_get_startup_detail_base, name='vue_get_startup_detail_base', ),
    url(r'^get_unread_alarm/', views.get_unread_alarm, name='get_unread_alarm', ),
    url(r'save_filter/', views.save_filter, name='save_filter', ),
    url(r'vue_get_course_all/', views.vue_get_course_all, name='vue_get_course_all', ),
    url(r'vue_modify_path/', views.vue_modify_path, name='vue_modify_path', ),
    url(r'^vue_get_path_all/', views.vue_get_path_all, name='vue_get_path_all', ),

    url(r'^vue_get_support_business_name/', views.vue_get_support_business_name, name='vue_get_support_business_name', ),
    url(r'^vue_del_history/', views.vue_del_history, name='vue_del_history', ),
    url(r'^set_alarm_read/', views.set_alarm_read, name='set_alarm_read', ),
    url(r'^save_user_appliance_data_url/', views.save_user_appliance_data_url,   name='save_user_appliance_data_url', ),
    url(r'^vue_get_statics_by_channel/', views.vue_get_statics_by_channel,   name='vue_get_statics_by_channel', ),
    url(r'^vue_get_path_information/', views.vue_get_path_information,   name='vue_get_path_information', ),
    url(r'^vue_update_startup_detail_base/', views.vue_update_startup_detail_base, name='vue_update_startup_detail_base', ),
    url(r'^vue_get_register_channel/', views.vue_get_register_channel,name='vue_get_register_channel', ),
    url(r'^vue_update_startup_news_detail/', views.vue_update_startup_news_detail, name='vue_update_startup_news_detail', ),
    url(r'^vue_del_history/', views.vue_del_history,name='vue_del_history', ),
    url(r'^vue_channel_register_check/', views.vue_channel_register_check,name='vue_channel_register_check', ),
    url(r'^vue_get_registerd_channel/', views.vue_get_registerd_channel,name='vue_get_registerd_channel', ),
    url(r'^appliance_delete_service/', views.appliance_delete_service, name='appliance_delete_service', ),
    url(r'^get_usr_filter', views.get_usr_filter, name='get_usr_filter', ),
    url(r'^get_usr_appliance_check', views.get_usr_appliance_check, name='get_usr_appliance_check', ),
    url(r'^vue_modify_clip', views.vue_modify_clip, name='vue_modify_clip', ),
    url(r'^vue_get_startup_list', views_paging.startup_list, name='startup_list', ),
    url(r'^sync_with_appliance', views.sync_with_appliance, name='sync_with_appliance', ),

    url(r'add_favorite_support_business', views.add_favorite_support_business, name='add_favorite_support_business', ),
    url(r'remove_favorite_support_business', views.remove_favorite_support_business, name='remove_favorite_support_business', ),
    url(r'add_favorite_path', views.add_favorite_path, name='add_favorite_path', ),
    url(r'remove_favorite_path', views.remove_favorite_path, name='remove_favorite_path', ),
    url(r'add_favorite_course', views.add_favorite_course, name='add_favorite_course', ),
    url(r'remove_favorite_course', views.remove_favorite_course, name='remove_favorite_course', ),
    url(r'add_favorite_clip', views.add_favorite_clip, name='add_favorite_clip', ),
    url(r'remove_favorite_clip', views.remove_favorite_clip, name='remove_favorite_clip', ),
    url(r'add_favorite_startup', views.add_favorite_startup, name='add_favorite_startup', ),
    url(r'remove_favorite_startup', views.remove_favorite_startup, name='remove_favorite_startup', ),
    url(r'delete_application', views.delete_application, name='delete_application', ),
    url(r'updated_support_statics', views.updated_support_statics, name='updated_support_statics', ),



#     기관관리자
    url(r'^vue_get_opr_dashboard/', views.vue_get_opr_dashboard, name='vue_get_opr_dashboard', ),
    url(r'^vue_get_opr_acc/', views.vue_get_opr_acc, name='vue_get_opr_acc', ),
    url(r'^opr_vue_get_startup_account/', views.opr_vue_get_startup_account, name='opr_vue_get_startup_account', ),
    url(r'^opr_vue_get_support_business_list/', views.opr_vue_get_support_business_list,
        name='opr_vue_get_support_business_list', ),
    url(r'^opr_vue_get_awarded/', views.opr_vue_get_awarded, name='opr_vue_get_awarded', ),
    url(r'^opr_vue_get_support_business_appliance/', views.opr_vue_get_support_business_appliance,
        name='opr_vue_get_support_business_appliance', ),
    url(r'^opr_vue_get_support_business_info/', views.opr_vue_get_support_business_info,
        name='opr_vue_get_support_business_info', ),
    url(r'^vue_add_mng_acc/', views.vue_add_mng_acc, name='vue_add_mng_acc', ),
    url(r'^opr_vue_get_kikwan_account/', views.opr_vue_get_kikwan_account, name='opr_vue_get_kikwan_account', ),
    url(r'^vue_get_support_business_list_excel/', views.vue_get_support_business_list_excel,
        name='vue_get_support_business_list_excel', ),
    url(r'^vue_get_mng_list/', views.vue_get_mng_list, name='vue_get_mng_list', ),
    url(r'^vue_set_opr_acc/', views.vue_set_opr_acc, name='vue_set_opr_acc', ),
    url(r'support_business_open/', views.support_business_open, name='support_business_open', ),
    url(r'support_business_blind/', views.support_business_blind, name='support_business_blind', ),
    url(r'vue_get_favorite_channel/', views.vue_get_favorite_channel, name='vue_get_favorite_channel', ),
    url(r'excel_down_support_business_gwanri_ap/', views.excel_down_support_business_gwanri_ap,
        name='excel_down_support_business_gwanri_ap', ),
    url(r'excel_down_support_business_gwanri_fav/', views.excel_down_support_business_gwanri_fav,
        name='excel_down_support_business_gwanri_fav', ),
    url(r'vue_get_download_usr_account/', views.vue_get_download_usr_account, name='vue_get_download_usr_account', ),
    url(r'opr_account_kikwan_all_account/', views_paging.opr_account_kikwan_all_account,
        name='opr_account_kikwan_all_account', ),
    url(r'opr_account_kikwan_mng_account/', views_paging.opr_account_kikwan_mng_account,
        name='opr_account_kikwan_mng_account', ),

#     매니저
    url(r'mng_account_kikwan_mng_account/', views_paging.mng_account_kikwan_mng_account,
        name='mng_account_kikwan_mng_account', ),
    url(r'^vue_get_support_business_by_author/', views.vue_get_support_business_by_author,
        name='vue_get_support_business_by_author', ),
    url(r'^vue_make_application/', views.vue_make_application, name='vue_make_application', ),
    url(r'^vue_get_dashboard/', views.vue_get_dashboard, name='vue_get_dashboard', ),
    url(r'^vue_submit_support_business/', views.vue_submit_support_business, name='vue_submit_support_business', ),
    url(r'^vue_get_mng_acc/', views.vue_get_mng_acc, name='vue_get_mng_acc', ),
    url(r'^vue_get_support_business_info/', views.vue_get_support_business_info,
        name='vue_get_support_business_info', ),
    url(r'^vue_set_mng_support_business_1/', views.vue_set_mng_support_business_step_1,
        name='vue_set_mng_support_business_step_1', ),
    url(r'^vue_set_mng_support_business_2/', views.vue_set_mng_support_business_step_2,
        name='vue_set_mng_support_business_step_2', ),
    url(r'^vue_set_mng_support_business_3/', views.vue_set_mng_support_business_step_3,
        name='vue_set_mng_support_business_step_3', ),
    url(r'^vue_set_mng_support_business_4/', views.vue_set_mng_support_business_step_4,
        name='vue_set_mng_support_business_step_4', ),
    url(r'^vue_set_mng_support_business_5/', views.vue_set_mng_support_business_step_5,
        name='vue_set_mng_support_business_step_5', ),
    url(r'^vue_set_mng_support_business_6/', views.vue_set_mng_support_business_step_6,
        name='vue_set_mng_support_business_step_6', ),
    url(r'^vue_static_usr/', views.vue_static_usr, name='vue_static_usr', ),
    url(r'^vue_get_support_business_list/', views.vue_get_support_business_list,
        name='vue_get_support_business_list', ),
    url(r'mng_vue_get_kikwan_account/', views.mng_vue_get_kikwan_account, name='mng_vue_get_kikwan_account', ),
    url(r'^vue_get_support_business_selected_list_excel/', views.vue_get_support_business_selected_list_excel,
        name='vue_get_support_business_selected_list_excel', ),
    url(r'^mng_vue_get_support_business_list/', views.mng_vue_get_support_business_list,
        name='mng_vue_get_support_business_list', ),
    url(r'^vue_set_mng_acc/', views.vue_set_mng_acc, name='vue_set_mng_acc', ),
    url(r'^vue_set_support_business_information/', views.vue_set_support_business_information,
        name='vue_set_support_business_information', ),
    url(r'^vue_get_support_business_appliance/', views.vue_get_support_business_appliance,
        name='vue_get_support_business_appliance', ),
    url(r'vue_set_awarded/', views.vue_set_awarded, name='vue_set_awarded', ),
    url(r'vue_get_awarded/', views.vue_get_awarded, name='vue_get_awarded', ),
    url(r'get_static_info_from_stattable/', views.get_static_info_from_stattable,
        name='get_static_info_from_stattable', ),
    url(r'vue_get_support_business_select_name_1/', views.vue_get_support_business_select_name_1,
        name='vue_get_support_business_select_name_1', ),
    url(r'vue_get_support_business_select_name_2/', views.vue_get_support_business_select_name_2,
        name='vue_get_support_business_select_name_2', ),
    url(r'vue_get_support_business_select_name_3/', views.vue_get_support_business_select_name_3,
        name='vue_get_support_business_select_name_3', ),
    url(r'vue_get_support_business_select_name_4/', views.vue_get_support_business_select_name_4,
        name='vue_get_support_business_select_name_4', ),
    url(r'get_support_business_static/', views.get_support_business_static, name='get_support_business_static', ),
    url(r'mng_vue_get_startup_account/', views.mng_vue_get_startup_account, name='mng_vue_get_startup_account', ),
    url(r'mng_vue_get_kikwan_account_excel/', views.mng_vue_get_kikwan_account_excel,
        name='mng_vue_get_kikwan_account_excel', ),
    url(r'vue_get_support_business_select_name_by_kikwan_1/', views.vue_get_support_business_select_name_by_kikwan_1,
        name='vue_get_support_business_select_name_by_kikwan_1', ),
    url(r'vue_get_support_business_select_name_by_kikwan_2/', views.vue_get_support_business_select_name_by_kikwan_2,
        name='vue_get_support_business_select_name_by_kikwan_2', ),
    url(r'excel_down_statics/', views.excel_down_statics, name='excel_down_statics', ),
    url(r'vue_get_channel_statics_clip/', views.vue_get_channel_statics_clip, name='vue_get_channel_statics_clip', ),
    url(r'vue_get_channel_statics_course/', views.vue_get_channel_statics_course,
        name='vue_get_channel_statics_course', ),
    url(r'vue_get_channel_statics_path/', views.vue_get_channel_statics_path, name='vue_get_channel_statics_path', ),
    url(r'get_site_statics/', views.get_site_statics, name='get_site_statics', ),
    url(r'delete_support_business/', views.delete_support_business, name='delete_support_business', ),
    url(r'delete_support_business_file', views.delete_support_business_file, name='delete_support_business_file', ),
    url(r'superuser_grant_check', views.superuser_grant_check, name='superuser_grant_check', ),





























]
import debug_toolbar
urlpatterns.append(url(r'^__debug__/', include(debug_toolbar.urls)))
