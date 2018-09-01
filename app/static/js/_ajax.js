function a_json_post(url, type, data, success, error) {
    if (error == null){
        error = function (data) {
            // console.log(data)
        }
    }

    $.ajax({
        type: type,
        url: url,
        data: data,
        dataType: 'json',
        contentType: 'application/json',
        success: function (data) {
            if (data.error)
                alert(data.error_message);
            else
                success(data);
        },
        error: error(data)
    })
}