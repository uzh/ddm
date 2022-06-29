function downloadData(postUrl, fileName) {
    $.ajax({
        type: 'GET',
        dataType: 'json',
        url: postUrl,
        success: function (data, status, result) {
            console.log('data: ', data);
            let blob = new Blob([JSON.stringify(data)], {type: 'octet/stream'});
            let link=document.createElement('a');
            link.href=window.URL.createObjectURL(blob);
            link.download=fileName.concat('.json');
            link.click();
        }
    });
}
