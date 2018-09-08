var myCount = function () {
    var privateCounter = 0;
    function changeBy(val) {
        privateCounter += val;
    }
    return {
        increment: function() {
            changeBy(1);
        },
        decrement: function() {
            changeBy(-1);
        },
        value: function() {
            return privateCounter;
        },
        init: function (val) {
            privateCounter = val;
        }
    }
};

var notNullText = "<td class='input-group-inline input-group-sm'>" +
    "<input type='text' class='form-control' " + "required " +
    "placeholder='请输入...'>" +
    "</td>";

var myText = "<td class='input-group-inline input-group-sm'>" +
    "<input type='text' class='form-control' " +
    "placeholder='请输入...'>" +
    "</td>";

var myNum = "<td class='input-group-inline input-group-sm'>" +
    "<input type='number' class='form-control' " +
    "placeholder='请输入...'>" +
    "</td>";

var myDate = "<td class='input-group-inline input-group-sm'>" +
    "<input type='text' class='form-control mydate' " +
    "placeholder='请选择...'>" +
    "</td>";

var myDisText = "<td class='input-group-inline input-group-sm'>" +
    "<input type='text' class='form-control' disabled " +
    "placeholder='请输入...'>" +
    "</td>";

var td = "<td class='input-group-inline input-group-sm'></td>";
var select = "<td class='input-group-inline input-group-sm'>" +
    "<select class='mt-1'>" +
    "</select>" +
    "</td>";


var handle = {
    del: function (id, d_id) {
        if (confirm('确定删除该项么？'))
            $('#'+id).remove();
    }
};

var get_families = function () {
    var family_arr = [];
    var temp = {};
    var families = $('#family-tbody').children();
    for (var i=0; i < families.length; i++) {
        temp = {};
        var td_arr = families.eq(i).find('td');
        temp.relationship = td_arr.eq(1).find('input').val();
        temp.name = td_arr.eq(2).find('input').val();
        temp.age = Number(td_arr.eq(3).find('input').val());
        temp.p_c = td_arr.eq(4).find('input').val();
        temp.workplace = td_arr.eq(5).find('input').val();
        family_arr.push(temp);
    }
    return family_arr;
};

var get_r_and_p = function () {
    var r_and_p_arr = [];
    var temp = {};
    var r_and_p = $('#r-and-p-tbody').children();
    for (var i=0; i < r_and_p.length; i++) {
        temp = {};
        var td_arr = r_and_p.eq(i).find('td');
        temp.time = td_arr.eq(1).find('input').val();
        temp.dept = td_arr.eq(2).find('input').val();
        temp.reason = td_arr.eq(3).find('input').val();
        temp.workplace = td_arr.eq(4).find('input').val();
        temp.remarks = td_arr.eq(5).find('input').val();
        r_and_p_arr.push(temp);
    }
    return r_and_p_arr;
};

var get_edu = function () {
    var edu_arr = [];
    var temp = {};
    var edu = $('#edu-tbody').children();
    for (var i=0; i < edu.length; i++) {
        temp = {};
        var td_arr = edu.eq(i).find('td');
        temp.edu_level_id = td_arr.eq(1).find('select').val();
        temp.enrolment_time = td_arr.eq(2).find('input').val();
        temp.graduation_time = td_arr.eq(3).find('input').val();
        temp.edu_name = td_arr.eq(4).find('input').val();
        temp.department = td_arr.eq(5).find('input').val();
        temp.degree = td_arr.eq(6).find('input').val();
        temp.learn_id = td_arr.eq(7).find('select').val();
        edu_arr.push(temp);
    }
    return edu_arr;
};

var get_title = function () {
    var title_arr = [];
    var temp = {};
    var title = $('#title-tbody').children();
    for (var i=0; i < title.length; i++) {
        temp = {};
        var td_arr = title.eq(i).find('td');
        temp.name_id = td_arr.eq(3).find('select').val();
        temp.major = td_arr.eq(4).find('input').val();
        temp.get_time = td_arr.eq(5).find('input').val();
        temp.page_no = td_arr.eq(6).find('input').val();
        temp.engage = td_arr.eq(7).find('select').val();
        temp.engage_time = td_arr.eq(8).find('input').val();
        temp.remarks = td_arr.eq(9).find('input').val();
        title_arr.push(temp);
    }
    return title_arr;
};

var get_resume = function () {
    var resume_arr = [];
    var temp = {};
    var resume = $('#resume-tbody').children();
    for (var i=0; i < resume.length; i++) {
        temp = {};
        var td_arr = resume.eq(i).find('td');
        temp.change_time = td_arr.eq(1).find('input').val();
        temp.dept = td_arr.eq(2).find('input').val();
        temp.identifier = td_arr.eq(3).find('input').val();
        temp.work_time = td_arr.eq(4).find('input').val();
        resume_arr.push(temp);
    }
    return resume_arr;
};

$(document).ready(function () {
    // 添加一行新的插入家庭表格
    $('#add-family-tr').bind('click', function () {
        f_count.increment();
        var f_id = "family-" + f_count.value();
        var f_tr = $('<tr id="'+ f_id + '"></tr>');
        f_tr.append($('<td class="index">'+ f_count.value() + '</td>'));
        f_tr.append($(myText));
        f_tr.append($(myText));
        f_tr.append($(myNum));
        f_tr.append($(myText));
        f_tr.append($(myText));
        f_tr.append($("<td><button type='button' class='btn btn-link " +
            "btn-sm' onclick=" + "handle.del('family-" + f_count
                .value() + "')" + ">删除</button></td>"));
        $('#family-tbody').append(f_tr)
    });

    // 添加新的奖惩行
    $('#add-r-and-p-tr').bind('click', function () {
        r_and_p_count.increment();
        var r_and_p_id = "r-and-p-" + r_and_p_count.value();
        var r_and_p_tr = $('<tr id="'+ r_and_p_id + '"></tr>');
        var time = $(myDate);
        time.attr('id', 'r-and-p-time');
        r_and_p_tr.append($('<td class="index">'+ r_and_p_count.value() + '</td>'));
        r_and_p_tr.append($(time));
        r_and_p_tr.append($(myText));
        r_and_p_tr.append($(myText));
        r_and_p_tr.append($(myText));
        r_and_p_tr.append($(myText));
        r_and_p_tr.append($("<td><button type='button' class='btn btn-link " +
            "btn-sm' onclick=" + "handle.del('r-and-p-" + r_and_p_count.value()
            + "')" + ">删除</button></td>"));
        $('#r-and-p-tbody').append(r_and_p_tr);

        $('.mydate').datepicker({
            language: "zh-CN"
        });
    });

    // 新建一行学历表格
    $('#add-edu-tr').bind('click', function () {
        edu_count.increment();
        var edu_id = "edu-" + edu_count.value();
        var edu_tr = $('<tr id="'+ edu_id + '"></tr>');
        var edu_lv = $(select), learn_form=$(select);
        _edu_lv.forEach(function (i) {
            var option = $('<option value="' + i[0] + '">'
                + i[1] + '</option>');
            edu_lv.children('select').append(option);
        });

        _learn_from.forEach(function (i) {
            var option = $('<option value="' + i[0] + '">'
                + i[1] + '</option>');
            learn_form.children('select').append(option);
        });

        edu_tr.append($('<td class="index">'+ edu_count.value() + '</td>'));
        edu_tr.append(edu_lv);
        edu_tr.append($(myDate));
        edu_tr.append($(myDate));
        edu_tr.append($(myText));
        edu_tr.append($(myText));
        edu_tr.append($(myText));
        edu_tr.append($(learn_form));
        edu_tr.append($("<td><button type='button' class='btn btn-link " +
            "btn-sm' onclick=" + "handle.del('edu-" + edu_count
                .value()
            + "')" + ">删除</button></td>"));
        $('#edu-tbody').append(edu_tr);

        $('.mydate').datepicker({
            language: "zh-CN"
        });
    });

    // 添加新的职称行
    $('#add-title-tr').bind('click', function () {
        title_count.increment();
        var title_id = "title-" + title_count.value();
        var title_tr = $('<tr id="'+ title_id + '"></tr>');
        var _title_name = $(title_name);
        _title_name.attr('onchange', 'title_change("' + title_id + '")');

        title_tr.append($('<td class="index">'+ title_count.value() + '</td>'));
        title_tr.append($(myDisText));
        title_tr.children(':last-child').find('input').val
        (_titles[1][0]);
        title_tr.append($(myDisText));
        title_tr.children(':last-child').find('input').val
        (_titles[1][1]);
        title_tr.append(_title_name);
        title_tr.append($(myText));
        title_tr.append($(myDate));
        title_tr.append($(myText));
        var engage = $(select);
        engage.find('select').append("<option " +
            "value='true'>是</option>");
        engage.find('select').append("<option " +
            "value='false'>否</option>");
        title_tr.append(engage);
        title_tr.append($(myDate));
        title_tr.append($(myText));
        title_tr.append($("<td><button type='button' class='btn btn-link " +
            "btn-sm' onclick=" + "handle.del('title-" + title_count
                .value()
            + "')" + ">删除</button></td>"));
        $('#title-tbody').append(title_tr);
        $('.mydate').datepicker({
            language: "zh-CN"
        });
    });

    // 添加新的奖惩行
    $('#add-resume-tr').bind('click', function () {
        resume_count.increment();
        var resume_id = "resume-" + resume_count.value();
        var resume_tr = $('<tr id="'+ resume_id + '"></tr>');
        resume_tr.append($('<td class="index">'+ resume_count.value() + '</td>'));
        resume_tr.append($(myDate));
        resume_tr.append($(myText));
        resume_tr.append($(myText));
        resume_tr.append($(myDate));
        resume_tr.append($("<td><button type='button' class='btn btn-link " +
            "btn-sm' onclick=" + "handle.del('resume-" + resume_count.value()
            + "')" + ">删除</button></td>"));
        $('#resume-tbody').append(resume_tr);

        $('.mydate').datepicker({
            language: "zh-CN"
        });
    });
});
