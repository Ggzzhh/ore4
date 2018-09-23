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