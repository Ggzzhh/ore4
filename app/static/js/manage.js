function uEdit(id) {
    $('#uEdit').modal('show');

    $('#u-edit').bind('submit', function () {
        var data = JSON.stringify({
            id: id,
            password: $('#u-new-pwd').val(),
            new: false
        });
        var _success = function (data) {
            alert(data.message);
            $('#uAdd').modal('hide');
            setTimeout(function () {
                location.href = '/system-manage/user';
            }, 1000);
        };

        a_json(
            "/v1/manage-user",
            "POST",
            data,
            _success);
        return false;
    });
}

function uDel(id) {
    var data = JSON.stringify({
        id: id
    });

    var _success = function (data) {
        alert(data.message);
        location.href = '/system-manage/user';
    };

    if (confirm('确定删除该项么？')){
        a_json(
            "/v1/manage-user",
            "DELETE",
            data,
            _success);
    }
    return false;
}

function dutyEdit(name, id, order, lv_id) {

    $('#i-dutyEdit').attr('value', name);

    $('#select_lv_2').val(lv_id);

    $('#order_2').val(order);

    $('#dutyEdit').modal('show');

    $('#duty-edit').bind('submit', function () {
        var data = JSON.stringify({
            id: id,
            name: $('#i-dutyEdit').val(),
            lv_id: $('#select_lv_2').val(),
            order: $('#order_2').val(),
            new: false
        });
        var _success = function (data) {
            alert(data.message);
            $('#uAdd').modal('hide');
            location.reload();
        };

        a_json(
            "/v1/manage-duty",
            "POST",
            data,
            _success);
        return false;
    })
}

function dutyDel(id) {
    var data = JSON.stringify({
        id: id
    });

    var _success = function (data) {
        alert(data.message);
        location.href = '/system-manage/duty';
    };

    if (confirm('确定删除该项么？'))
        a_json(
            "/v1/manage-duty",
            "DELETE",
            data,
            _success);
    return false;
}

function deptEdit(name, full_name, id, order, system_id, pro_id) {

    $('#i-edit-dept').attr('value', name);

    $('#system_2').val(system_id);

    $('#full_name_2').val(full_name);

    $('#dept_pro_2').val(pro_id);

    $('#order_2').val(order);

    $('#edit-dept').modal('show');

    $('#dept-form').bind('submit', function () {
        var data = JSON.stringify({
            id: id,
            name: $('#i-edit-dept').val(),
            full_name: $('#full_name_2').val(),
            order: $('#order_2').val(),
            system_id: $('#system_2').val(),
            dept_pro_id: $('#dept_pro_2').val(),
            'new': false
        });
        var _success = function (data) {
            alert(data.message);
            $('#edit-dept').modal('hide');
            setTimeout(function () {
                location.href = '/system-manage/dept';
            }, 1000);
        };
        a_json(
            "/v1/manage-dept",
            "POST",
            data,
            _success);
        return false;
    })
}

function deptDel(id) {
    var data = JSON.stringify({
        id: id
    });

    var _success = function (data) {
        alert(data.message);
        location.href = '/system-manage/dept';
    };

    if (confirm('确定删除该项么？'))
        a_json(
            "/v1/manage-dept",
            "DELETE",
            data,
            _success);
    return false;
}

function checkFile(){
    // 获取文件对象(该对象的类型是[object FileList]，其下有个length属性)
    var fileList = $('#fileUpLoad')[0].files;

    // 如果文件对象的length属性为0，就是没文件
    if (fileList.length === 0) {
        console.log('没选择文件');
        return false;
    };
    if (fileList.length > 0) {
        var re = /\.(xls|xlsx)/,
            filename = fileList[0].name;
        if(!re.test(filename)){
            alert('请下载给予的模版文件，在其中进行操作后上传。');
            return false;
        }
    }
    return fileList[0];
};

