function askSecret() {
  $('#modal-secret-input').modal('toggle');
}

function downloadData(postUrl, fileName, get_secret=false) {
  let secret = null;
  if (get_secret) {
    secret = $('#secret-input').val();
    if (secret === '') {
      $('#error-no-secret').removeAttr('hidden');
      return;
    }
    $('#secret-input').val('');
    $('#modal-secret-input').modal('toggle');
  }

  $.ajax({
    type: 'GET',
    url: postUrl,
    headers: {'Super-Secret': secret},
    xhrFields:{
      responseType: 'blob'
    },
    beforeSend: function (xhr) {
      $('#download-overlay').toggle();
    },
    success: function (data, status, result) {
      let blob = new Blob([data], {type: 'application/zip'});
      let link = document.createElement('a');
      link.href = window.URL.createObjectURL(blob);
      link.download = fileName.concat('.zip');
      link.click();
      $('#download-overlay').toggle();
    },
    error: function(request, status, error) {
      $('#download-error-message').text(request.responseText);
      $('#download-overlay').toggle();
      $('#modal-download-error').modal('toggle');
    },
  });
}
