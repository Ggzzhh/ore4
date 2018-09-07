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
});
