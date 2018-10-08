
#-----[2/3]----
#---- (반복) zipfile 다운로드 : 합치고 수정할 것
import zipfile
def getfiles(request):
    # Files (local path) to put in the .zip
    # FIXME: Change this (get paths from DB etc)
    filenames = ["/home/ubuntu/google.pdf"]

    # Folder name in ZIP archive which contains the above files
    # E.g [thearchive.zip]/somefiles/file2.txt
    # FIXME: Set this to something better
    zip_subdir = "somefiles"
    zip_filename = "%s.zip" % zip_subdir

    # Open StringIO to grab in-memory ZIP contents
    s = io.BytesIO()

    # The zip compressor
    zf = zipfile.ZipFile(s, "w")

    for fpath in filenames:
        # Calculate path for file in zip
        fdir, fname = os.path.split(fpath)
        zip_path = os.path.join(zip_subdir, fname)

        # Add file, at correct path
        zf.write(fpath, zip_path)

    # Must close zip for all contents to be written
    zf.close()

    # Grab ZIP file from in-memory, make response with correct MIME-type
    resp = HttpResponse(s.getvalue(), mimetype="application/x-zip-compressed")
    # ..and correct content-disposition
    resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename

    return resp


# #-----[참고]----
# # --- (중복)
# def appliance_download(request, apid):
#     ap = apid
#     ap_target = Appliance.objects.get(id=ap)
#     # filenames = ["temp_folder/" + business_file.name.split("/")[-1], ]
#     zip_subdir = "applicance"
#     zip_filename = "%s.zip" % (
#         str(ap_target.sb.apply_end).split("-")[
#             0] + "_" + ap_target.sb.title + "_" + ap_target.startup.company_name + "_" + ap_target.startup.user.additionaluserinfo.repre_name)
#     s = io.BytesIO()
#     url = "http://gconnect.kr/grant/" + str(ap_target.sb_id) + "/" + str(apid)
#     print(url)
#     subprocess.run("/usr/bin/xvfb-run wkhtmltopdf " + url + "  test.pdf", shell=True, check=True)
#     print(os.path.abspath(os.path.dirname(__name__)) + "/test.pdf")
#     zf = ZipFile(s, "w")
#     if os.path.abspath(os.path.dirname(__name__)) + "/test.pdf":
#         zip_path = os.path.join("지원서.pdf")
#         zf.write(os.path.abspath(os.path.dirname(__name__)) + "/test.pdf", zip_path)
#         print(os.path.abspath(os.path.dirname(__name__)) + "/test.pdf")
#     if ap_target.business_file != "":
#         fdir, fname = os.path.split(ap_target.business_file.path)
#         zip_path = os.path.join("사업자등록증." + fname.split(".")[-1])
#         zf.write(ap_target.business_file.path, zip_path)
#     if ap_target.fund_file != "":
#         fdir, fname = os.path.split(ap_target.fund_file.path)
#         zip_path = os.path.join("투자증명서." + fname.split(".")[-1])
#         zf.write(ap_target.fund_file.path, zip_path)
#     if ap_target.etc_file != "":
#         fdir, fname = os.path.split(ap_target.etc_file.path)
#         zip_path = os.path.join("기타첨부파일." + fname.split(".")[-1])
#         zf.write(ap_target.etc_file.path, zip_path)
#     if ap_target.ir_file != "":
#         fdir, fname = os.path.split(ap_target.ir_file.path)
#         zip_path = os.path.join("사업소개서." + fname.split(".")[-1])
#         zf.write(ap_target.ir_file.path, zip_path)
#     if ap_target.ppt_file != "":
#         fdir, fname = os.path.split(ap_target.ppt_file.path)
#         zip_path = os.path.join("ppt파일." + fname.split(".")[-1])
#         zf.write(ap_target.ppt_file.path, zip_path)
#     if ap_target.tax_file != "":
#         fdir, fname = os.path.split(ap_target.tax_file.path)
#         zip_path = os.path.join("납세증명서." + fname.split(".")[-1])
#         zf.write(ap_target.tax_file.path, zip_path)
#     # for fpath in filenames:
#     #     # Calculate path for file in zip
#     #     fdir, fname = os.path.split(fpath)
#     #     zip_path = os.path.join(zip_subdir, fname)
#     #
#     #     # Add file, at correct path
#     #     zf.write(fpath, zip_path)
#
#     # Must close zip for all contents to be written
#     zf.close()
#
#     # Grab ZIP file from in-memory, make response with correct MIME-type
#     resp = HttpResponse(s.getvalue(), content_type="application/x-zip-compressed")
#     resp['Content-Disposition'] = 'attachment;filename*=UTF-8\'\'%s' % urllib.parse.quote(zip_filename, safe='')
#     return resp
# import time



#-----[3/3]----
#---- (반복) zipfile 다운로드 : 합치고 수정할 것

def appliance_all_download(request, sb):
    ap_list = Appliance.objects.filter(sb_id=sb)
    zip_filename = "%s.zip" % (
        str(ap_list[0].sb.apply_end).split("-")[
            0] + "_" + ap_list[0].sb.title)
    s = io.BytesIO()
    zf = ZipFile(s, "w")
    for ap in ap_list:
        zip_subdir = "applicance"
        url = "http://gconnect.kr/apply/preview/pdf/" + str(ap_list[0].sb_id) + "/" + str(ap.id)
        subprocess.run("/usr/bin/xvfb-run wkhtmltopdf " + url + "  test.pdf ", shell=True, check=True)
        print(os.path.abspath(os.path.dirname(__name__)) + "/test.pdf")
        if os.path.abspath(os.path.dirname(__name__)) + "/test.pdf":
            zip_path = os.path.join(ap.startup.name + "/지원서.pdf")
            zf.write(os.path.abspath(os.path.dirname(__name__)) + "/test.pdf", zip_path)
            print(os.path.abspath(os.path.dirname(__name__)) + "/test.pdf")
            time.sleep(1)
        if ap.business_file != "":
            fdir, fname = os.path.split(ap.business_file.path)
            zip_path = os.path.join(ap.startup.name + "/사업자등록증." + fname.split(".")[-1])
            zf.write(ap.business_file.path, zip_path)
        if ap.fund_file != "":
            fdir, fname = os.path.split(ap.fund_file.path)
            zip_path = os.path.join(ap.startup.name + "/투자증명서." + fname.split(".")[-1])
            zf.write(ap.fund_file.path, zip_path)
        if ap.etc_file != "":
            fdir, fname = os.path.split(ap.etc_file.path)
            zip_path = os.path.join(ap.startup.name + "/기타첨부파일." + fname.split(".")[-1])
            zf.write(ap.etc_file.path, zip_path)
        if ap.ir_file != "":
            fdir, fname = os.path.split(ap.ir_file.path)
            zip_path = os.path.join(ap.startup.name + "/사업소개서." + fname.split(".")[-1])
            zf.write(ap.ir_file.path, zip_path)
        if ap.ppt_file != "":
            fdir, fname = os.path.split(ap.ppt_file.path)
            zip_path = os.path.join(ap.startup.name + "/ppt파일." + fname.split(".")[-1])
            zf.write(ap.ppt_file.path, zip_path)
        if ap.tax_file != "":
            fdir, fname = os.path.split(ap.tax_file.path)
            zip_path = os.path.join(ap.startup.name + "/납세증명서." + fname.split(".")[-1])
            zf.write(ap.tax_file.path, zip_path)
    f = io.BytesIO()
    book = xlwt.Workbook()
    sheet = book.add_sheet("지원자 리스트")
    sheet.write(0, 0, "순서")
    sheet.write(0, 1, "기업명")
    sheet.write(0, 2, "업종")
    sheet.write(0, 3, "대표자명")
    sheet.write(0, 4, "사업자 등록번호")
    sheet.write(0, 5, "이메일")
    sheet.write(0, 6, "대표 전화번호")
    sheet.write(0, 7, "필터")
    k = 1
    for a in ap_list:
        sheet.write(k, 0, k)
        sheet.write(k, 1, a.startup.company_name)
        sheet.write(k, 2, a.startup.category)
        sheet.write(k, 3, a.startup.user.additionaluserinfo.repre_name)
        sheet.write(k, 4, Appliance.objects.all().filter(sb_id=sb).filter(startup_id=a.startup.id)[0].business_number)
        sheet.write(k, 5, a.startup.user.username)
        sheet.write(k, 6, a.startup.user.additionaluserinfo.repre_tel)
        filter_list = a.startup.filter.all()
        f_arr = []
        for fil in filter_list:
            f_arr.append(fil.jiwon_filter_name)
        sheet.write(k, 7, ",".join(f_arr))
        k = k + 1
    book.save(f)
    out_content = f.getvalue()
    zf.writestr("전체 리스트.xls", f.getvalue())

    zf.close()

    resp = HttpResponse(s.getvalue(), content_type="application/x-zip-compressed")
    resp['Content-Disposition'] = 'attachment;filename*=UTF-8\'\'%s' % urllib.parse.quote(zip_filename, safe='')
    return resp

