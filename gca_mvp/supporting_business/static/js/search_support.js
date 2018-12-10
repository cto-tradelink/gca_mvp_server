function search_get() {
    console.log("sdfs")
    var filter_list = []
    var em = $("#range_01").val()
    if (em === "") {
        em = "0"
    }
    if (em === "제한없음") {
        em = "0"
    }
    for (var k = 0; k < $(".on").length; k++) {
        if($(".on:eq(" + k + ")").attr("data-id") != "" && $(".on:eq(" + k + ")").attr("data-id") != undefined)
        filter_list.push($(".on:eq(" + k + ")").attr("data-id"))
        console.log($(".on:eq(" + k + ")").attr("data-id"))
    }
    console.log(filter_list)
    try {
        if (getParameter("cat") === undefined) {
            location.href = absolute_url + "?filter=" + filter_list.join(",") + "&em=" + em + "&q=" + $("#search_bar").val()
        } else {
            location.href = absolute_url + "?filter=" + filter_list.join(",") + "&cat=" + getParameter("cat") + "&em=" + em + "&q=" + $("#search_bar").val()
            console.log(getParameter("cat"))
        }
    }
    catch (e) {
        console.log(e)
        location.href = absolute_url + "?filter=" + filter_list.join(",") + "&em=" + em
    }
}

$(document).ready(function () {

    try {
        var filter_url_list = getParameter("filter").split(",")
        for (var k = 0; k < filter_url_list.length; k++) {
            $("span[data-id='" + filter_url_list[k] + "']").addClass("on");
        }


    }
    catch (e) {
        console.log(e)
    }
    $("td > .tag").on("click", function () {
        if ($(this).attr("data-case") != "") {
            $("." + $(this).attr("data-case")).removeClass("on")
        }
        console.log(absolute_url)
        if ($(this).hasClass("on")) {
            $(this).removeClass("on")
        } else {
            $(this).addClass("on")
        }
        var filter_list = []
        for (var k = 0; k < $(".on").length; k++) {
            if($(".on:eq(" + k + ")").attr("data-id") != "" && $(".on:eq(" + k + ")").attr("data-id") != undefined)
            filter_list.push($(".on:eq(" + k + ")").attr("data-id"))

        }

        try {
            if (getParameter("cat") === undefined) {
                //location.href = absolute_url + "?filter=" + filter_list.join(",")
            } else {
                //location.href = absolute_url + "?filter=" + filter_list.join(",") + "&cat=" + getParameter("cat")

            }
        }
        catch (e) {
            console.log(e)
            //location.href = absolute_url + "?filter=" + filter_list.join(",")
        }
        $("#filter_list").val(filter_list.join(","))

    })

    $("#search_btn_f").on("click", function () {
        search_get()
    })


    $("#up_btn").on("click", function () {
        $("#select_filter").removeClass("hidden");
        $("#filter_con").empty()
        for (var k = 0; k < $("td>.on").length; k++) {
            var seg = '<span class="tag on" data-id="' + $("td>.on:eq(" + k + ")").attr("data-id") + '">' + $("td>.on:eq(" + k + ")").text() + '</span>'
            $("#filter_con").append(seg);
            $("#filter_ttl").text("선택한 필터")
        }
        $("table").not("#sort_tbl").addClass("hidden")
    });


    $("#down_btn_2").on("click", function () {
        $("table").removeClass("hidden")
        $("#select_filter").addClass("hidden");
    })
    for (var k = 0; k < $(".sm_ttl_num").length; k++) {
        $(".sm_num:eq(" + k + ")").text($(".sm_ttl_num:eq(" + k + ")").parent().find(".sm_cd_a").length)
        $(".sm_num:eq(" + k + ")").parent().find(".sm_cd_a:eq(0)").addClass("cd");
        $(".sm_num:eq(" + k + ")").parent().find(".sm_cd_a:eq(1)").addClass("cd");
        $(".sm_num:eq(" + k + ")").parent().find(".sm_cd_a:eq(2)").addClass("cd");
        $(".sm_num:eq(" + k + ")").parent().find(".sm_cd_a:eq(0)").removeClass("hidden");
        $(".sm_num:eq(" + k + ")").parent().find(".sm_cd_a:eq(1)").removeClass("hidden");
        $(".sm_num:eq(" + k + ")").parent().find(".sm_cd_a:eq(2)").removeClass("hidden");
        $(".sm_num:eq(" + k + ")").parent().find(".sm_cd_a:eq(2)").css("margin-right", "0");
        $(".sm_num:eq(" + k + ")").parent().find(".sm_l_a:eq(0)").addClass("lst");
        $(".sm_num:eq(" + k + ")").parent().find(".sm_l_a:eq(1)").addClass("lst");
        $(".sm_num:eq(" + k + ")").parent().find(".sm_l_a:eq(2)").addClass("lst");
    }
    $("#list").on("click", function () {
        $(this).parent().find("img").each(function () {
            $(this).attr("src", $(this).attr("data-off") )
        })
        $(this).attr("src", $(this).attr("data-on"))
        $(".cd").addClass("hidden");
        $(".lst").removeClass("hidden")
    })
    $("#card").on("click", function () {
          $(this).parent().find("img").each(function () {
            $(this).attr("src", $(this).attr("data-off") )
        })
        $(this).attr("src", $(this).attr("data-on"))
        $(".cd").removeClass("hidden");
        $(".lst").addClass("hidden")
    })
})

function set_cat(num) {

    var filter_list = []
    $(".tag.on").each(function () {
        filter_list.push($(this).attr("data-id"))
    })
    if (num == -1) {
        // location.href = absolute_url
        location.href = "/search/?filter="
    }
    else {

        location.href = absolute_url + "?filter=" + filter_list.join(",") + "&cat=" + num
    }

}

