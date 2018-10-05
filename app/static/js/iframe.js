var checkeds = document.getElementsByName("per-id");
var fields = document.getElementsByName("fields");

$('#easy-search').bind('click', function () {
    var frm = $('#es-frm');
    var easy = frm.find('input').val();
    if (easy == '' || easy == null){
        alert('请输入姓名/拼音!');
        return;
    }
    frm.attr('action', '/search');
    frm.submit();
});

$('#all-field').click(function () {
    for (var i=0; i < fields.length; i++) {
        fields[i].checked = true
    }
});

$('#reverse-field').bind('click', function () {
    for (var i=0; i < fields.length; i++) {
        fields[i].checked = !fields[i].checked
    }
});

$('#all-check').bind('click', function () {
    for (var i=0; i < checkeds.length; i++) {
        checkeds[i].checked = true
    }
});

$('#reverse-check').bind('click', function () {
    for (var i=0; i < checkeds.length; i++) {
        checkeds[i].checked = !checkeds[i].checked
    }
});

$('#coordinator').bind('click', function () {
    var ids= [];
    $('input[name="per-id"]:checked').map(function (i, e) {
        ids.push($(e).val())
    });
    if (ids.length === 0) {
        alert('请选择至少一个人进行调配！');
        return false;
    }
    if (confirm("请确认，即将更改这些人员的数据！"))
        a_json(
            "/v1/choice-state",
            "UPDATE",
            JSON.stringify(
                {
                    'ids': ids,
                    'state': 4
                }
            ),
            function (data) {
                alert(data.message);
                window.location.reload()
            }
        )
});

$('#transfer').bind('click', function () {
    var ids= [];
    $('input[name="per-id"]:checked').map(function (i, e) {
        ids.push($(e).val())
    });
    if (ids.length === 0) {
        alert('请选择至少一个人进行调配！');
        return false;
    }
    if (confirm("请确认，即将更改这些人员的数据！"))
        a_json(
            "/v1/choice-state",
            "UPDATE",
            JSON.stringify(
                {
                    'ids': ids,
                    'state': 5
                }
            ),
            function (data) {
                alert(data.message);
                window.location.reload()
            }
        )
});

$('#punished').bind('click', function () {
    var ids= [];
    $('input[name="per-id"]:checked').map(function (i, e) {
        ids.push($(e).val())
    });
    if (ids.length === 0) {
        alert('请选择至少一个人进行调配！');
        return false;
    }
    if (confirm("请确认，即将更改这些人员的数据！"))
        a_json(
            "/v1/punished",
            "UPDATE",
            JSON.stringify(
                {'ids': ids}
            ),
            function (data) {
                alert(data.message);
                window.location.reload()
            }
        )
});

$('#choice_state').bind('click', function () {
    var ids= [];
    $('input[name="per-id"]:checked').map(function (i, e) {
        ids.push($(e).val())
    });
    if (ids.length === 0) {
        alert('请选择至少一个人进行调配！');
        return false;
    }
    if (confirm("请确认，即将更改这些人员的数据！"))
        a_json(
            "/v1/choice-state",
            "UPDATE",
            JSON.stringify(
                {
                    'ids': ids,
                    'state': $('input[name="state"]:checked').val()
                }
            ),
            function (data) {
                alert(data.message);
                window.location.reload()
            }
        )
});

$('#choice-s-btn').bind('click', function () {
    var per_id = $('input[name="per-id"]:checked');
    if (per_id.length === 0) {
        alert('请选择至少一个人进行调动！');
        return false;
    }
    $('#choice-state').modal('show');
});

$('#w-m-btn').bind('click', function () {
    var per_id = $('input[name="per-id"]:checked');
    if (per_id.length === 0) {
        alert('请选择一个人进行调动！');
        return false;
    }
    this.modal('show');
});

$('#work-move-form').bind('submit', function () {
    var per_id = $('input[name="per-id"]:checked');
    var id = per_id.val();
    if (confirm("请确认，即将更改人员的数据！"))
        a_json(
            "/v1/work-move",
            "UPDATE",
            JSON.stringify(
                {
                    'id': id,
                    'dept_id': $('#dept-id').val(),
                    'duty_name': $('#duty-name').val(),
                    'duty_lv': $('#duty-lv').val(),
                    'identifier': $('#identifier').val(),
                    'work_time': $('#work_time').val()
                }
            ),
            function (data) {
                alert(data.message);
                window.location.reload()
            }
        );
    return false;
});

$('#del_per').bind('click', function () {
    var ids= [];
    $('input[name="per-id"]:checked').map(function (i, e) {
        ids.push($(e).val())
    });
    if (confirm("请确认，即将删除这些人员的数据！此操作不可逆！"))
        a_json(
            "/v1/del_per",
            "DELETE",
            JSON.stringify(
                {
                    'ids': ids
                }
            ),
            function (data) {
                alert(data.message);
                window.location.reload()
            }
        )
});