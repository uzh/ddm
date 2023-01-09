function deleteData(postUrl, csrfToken) {
  $.ajax({
    type: 'DELETE',
    url: postUrl,
    headers: {
      'X-CSRFToken': csrfToken
    },
    success: function (data, status, result) {
      $('#modal-delete-success').modal('toggle');
    },
    error: function(request, status, error) {
      $('#delete-error-message').text(request.responseText);
      $('#modal-delete-error').modal('toggle');
    },
  });
}
