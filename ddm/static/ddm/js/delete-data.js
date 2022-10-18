function deleteData(postUrl, csrfToken) {
  $.ajax({
    type: 'DELETE',
    url: postUrl,
    headers: {
      'X-CSRFToken': csrfToken
    },
    success: function (data, status, result) {
      window.location.reload();
    }
  });
}
