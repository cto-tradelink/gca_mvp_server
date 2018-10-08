
@csrf_exempt
def vue_get_channel_statics_path(request):
    # if gca_check_session(request)== False:
    #     return HttpResponse("{}")
    path = Path.objects.get(id=request.GET.get("path_id"))
    hit_date_list = HitPathLog.objects.all().filter(hit_path=path).values("hit_path_date").distinct()
    result = {}
    result["hit_static"] = []
    for hd in hit_date_list:
        temp = {}
        temp["date"] = hd["hit_path_date"]
        temp["hit_num"] = len(HitPathLog.objects.filter(hit_path=path).filter(hit_path_date=hd["hit_path_date"]))
        result["hit_static"].append(copy.deepcopy(temp))
    favorite_date_list = FavoriteLog.objects.all().filter(path=path).values("date").distinct()
    result["favorite_static"] = []
    for fd in favorite_date_list:
        temp = {}
        temp["date"] = fd["date"]
        temp["favorite_num"] = len(FavoriteLog.objects.filter(path=path).filter(date=fd["date"]))
        result["favorite_static"].append(copy.deepcopy(temp))
    registered_date_list = RegisteredChannel.objects.all().filter(path=path).values("date").distinct()
    result["registered_static"] = []
    for fd in registered_date_list:
        temp = {}
        temp["date"] = fd["date"]
        temp["registered_num"] = len(RegisteredChannel.objects.filter(path=path).filter(date=fd["date"]))
        result["registered_static"].append(copy.deepcopy(temp))
        # 전체
    # 먼저 각각의 스타트업 리스트 추출 하고 전체 리스트 만들어서 push

    all_user_list = []
    hit_user_list = []
    favorite_usr_list = []
    registered_usr_list = []

    for hit_row in HitPathLog.objects.all().filter(hit_path=path):
        try:
            hit_user_list.append(hit_row.hit_path_user.user.startup)
        except:
            pass
    for fav_row in FavoriteLog.objects.all().filter(path=path):
        try:
            favorite_usr_list.append(fav_row.user.user.startup)
        except:
            pass
    for reg_row in RegisteredChannel.objects.all().filter(path=path):
        try:
            registered_usr_list.append(reg_row.channel_user.user.startup)
        except:
            pass
    all_usr_list = list(set(hit_user_list + favorite_usr_list + registered_usr_list))
    result["all_usr_num"] = len(all_user_list)
    result["hit_usr_num"] = len(hit_user_list)
    result["favorite_usr_num"] = len(favorite_usr_list)
    result["registered_usr_num"] = len(registered_usr_list)
    # 전체
    all_comtype_filter = []
    all_location_filter = []
    all_genre_filter = []
    all_area_filter = []
    result["all_startup_list"] = []
    k = 1
    com_kind = ""
    local = ""
    for startup in all_usr_list:

        filter_list = startup.selected_company_filter_list.all()
        for filter in filter_list:
            if filter.cat_1 == "기업형태":
                all_comtype_filter.append(filter.filter_name)
                com_kind = filter.filter_name
            if filter.cat_1 == "소재지":
                all_location_filter.append(filter.filter_name)
                local = filter.filter_name
            if filter.cat_0 == "기본장르":
                all_genre_filter.append(filter.filter_name)

            if filter.cat_0 == "영역":
                all_area_filter.append(filter.filter_name)
        result["all_startup_list"].append({
            "startup_id": startup.id,
            "index": k, "repre_email": startup.repre_email, "company_name": startup.company_name,
            "company_kind": com_kind,
            "local": local,
            "company_total_employee": startup.company_total_employee, "repre_tel": startup.repre_tel
        })
        k = k + 1
    # 방문자
    hit_comtype_filter = []
    hit_location_filter = []
    hit_genre_filter = []
    hit_area_filter = []
    result["hit_startup_list"] = []
    k = 1
    com_kind = ""
    local = ""
    for startup in hit_user_list:
        filter_list = startup.selected_company_filter_list.all()
        for filter in filter_list:
            if filter.cat_1 == "기업형태":
                hit_comtype_filter.append(filter.filter_name)
                com_kind = filter.filter_name
            if filter.cat_1 == "소재지":
                hit_location_filter.append(filter.filter_name)
                local = filter.filter_name
            if filter.cat_0 == "기본장르":
                hit_genre_filter.append(filter.filter_name)

            if filter.cat_0 == "영역":
                hit_area_filter.append(filter.filter_name)
        result["hit_startup_list"].append({
            "startup_id": startup.id,
            "index": k, "repre_email": startup.repre_email, "company_name": startup.company_name,
            "company_kind": com_kind,
            "local": local,
            "company_total_employee": startup.company_total_employee, "repre_tel": startup.repre_tel
        })
        k = k + 1
        # 등록자
    reg_comtype_filter = []
    reg_location_filter = []
    reg_genre_filter = []
    reg_area_filter = []
    result["reg_startup_list"] = []
    k = 1
    com_kind = ""
    local = ""
    for startup in registered_usr_list:
        filter_list = startup.selected_company_filter_list.all()
        for filter in filter_list:
            if filter.cat_1 == "기업형태":
                reg_comtype_filter.append(filter.filter_name)
                com_kind = filter.filter_name
            if filter.cat_1 == "소재지":
                reg_location_filter.append(filter.filter_name)
                local = filter.filter_name
            if filter.cat_0 == "기본장르":
                reg_genre_filter.append(filter.filter_name)
            if filter.cat_0 == "영역":
                reg_area_filter.append(filter.filter_name)

        result["reg_startup_list"].append({
            "startup_id": startup.id,
            "index": k, "repre_email": startup.repre_email, "company_name": startup.company_name,
            "company_kind": com_kind,
            "local": local,
            "company_total_employee": startup.company_total_employee, "repre_tel": startup.repre_tel
        })
        k = k + 1
        # 좋아요
    fav_comtype_filter = []
    fav_location_filter = []
    fav_genre_filter = []
    fav_area_filter = []
    result["fav_startup_list"] = []
    k = 1
    com_kind = ""
    local = ""
    for startup in hit_user_list:
        filter_list = startup.selected_company_filter_list.all()
        for filter in filter_list:
            if filter.cat_1 == "기업형태":
                fav_comtype_filter.append(filter.filter_name)
                com_kind = filter.filter_name
            if filter.cat_1 == "소재지":
                fav_location_filter.append(filter.filter_name)
                local = filter.filter_name
            if filter.cat_0 == "기본장르":
                fav_genre_filter.append(filter.filter_name)

            if filter.cat_0 == "영역":
                fav_area_filter.append(filter.filter_name)
        result["fav_startup_list"].append({
            "startup_id": startup.id,
            "index": k, "repre_email": startup.repre_email, "company_name": startup.company_name,
            "company_kind": com_kind,
            "local": local,
            "company_total_employee": startup.company_total_employee, "repre_tel": startup.repre_tel
        })
        k = k + 1
    return JsonResponse({"data": result, })