jQuery.download = function(url, method, filedir, filename){
    jQuery('<form action="'+url+'" method="'+(method||'post')+'">' +
        '<input type="text" name="filedir" value="'+filedir+'"/>' +
        '<input type="text" name="filename" value="'+filename+'"/>' +
        '</form>')
        .appendTo('body').submit().remove();
};

function get_export_ids() {
    var ids= [];
    $('input[name="per-id"]:checked').map(function (i, e) {
        ids.push($(e).val())
    });
    if (ids.length === 0) {
        alert('请选择至少一个人进行导出！');
        return false;
    }
    get_export_url(
        '/v1/make-ids',
        'POST',
        JSON.stringify({
            ids: ids
        })
    )
}

function get_export_url(url, type, _data) {
    if (type == null){
        type = "GET"
    }
    var _success = function (data) {
        window.setTimeout(function () {
            $('#loading').modal('hide');
            $.download(data.url, "GET");
        }, 1000)

    };
    $.ajax({
        url: url,
        type: type,
        data: _data,
        dataType: 'json',
        contentType: 'application/json',
        beforeSend: function () {
            $('#loading').modal('show');
        },
        complete: function () {
            $('#loading').modal('hide');
        },
        success: _success
    })
};

function a_json(url, type, data, success, error, cache) {
    if (error == null){
        error = function (data) {
            // console.log(data)
        }
    }

    if (cache == null){
        cache = true
    }

    $.ajax({
        type: type,
        url: url,
        data: data,
        cache: cache,
        dataType: 'json',
        contentType: 'application/json',
        success: function (data) {
            if (data.error){
                alert(data.error_message);
                location.reload();
            }
            else
                success(data);
        },
        error: function(data){
            error(data)
        }
    })
}