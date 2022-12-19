function downloadData(postUrl, fileName) {
  $.ajax({
        type: 'GET',
        dataType: 'json',
        url: postUrl,
        beforeSend: function () {
          $("#download-overlay").toggle();
        },
        success: function (data, status, result) {
          let blob = new Blob([JSON.stringify(data)], {type: 'octet/stream'});
          let link=document.createElement('a');
          link.href=window.URL.createObjectURL(blob);
          link.download=fileName.concat('.json');
          link.click();
        },
        complete: function () {
          $("#download-overlay").toggle();
        }
    });
}
