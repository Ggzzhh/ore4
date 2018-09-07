$(document).ready(function () {
    // 添加一行新的插入家庭表格
    $('#add-family-tr').bind('click', function () {
        f_count.increment();
        var f_id = "family-" + f_count.value();
        var f_tr = $('<tr id="'+ f_id + '"></tr>');
        f_tr.append($('<td class="index">'+ f_count.value() + '</td>'));
        f_tr.append($(notNullText));
        f_tr.append($(notNullText));
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
        r_and_p_tr.append($(notNullText));
        r_and_p_tr.append($(notNullText));
        r_and_p_tr.append($(notNullText));
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
        edu_tr.append($(notNullText));
        edu_tr.append($(notNullText));
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
});
