function delete_responses(postUrl, qId) {
	// show upload in progress message & disable clicks of any kind
	const csrftoken = $('input[name="csrfmiddlewaretoken"]').val();

	// show overlay
	// inputElement.before('<div id="overlay" class="surquest-overlay"><div class="surquest-loader"></div><div class="surquest-overlay-text">File wird verarbeitet</div></div>');
	// var overlay = $('#overlay');
	// overlay.css( "display", "block" );
	let confirm_msg = 'Are you sure you want to delete all responses that have been registered for this Questionnaire?' +
					  'This will also delete all uploaded data associated with the questionnaire. ' +
					  'This step cannot be undone.';

	let r = confirm(confirm_msg);
	if (r == true) {
		let formData = new FormData();
		formData.append('q_id', qId);
		formData.append('csrfmiddlewaretoken', csrftoken);

		$.ajax({
			type: 'POST',
			url: postUrl,
			beforeSend:     function (request) {
				request.setRequestHeader('X-CSRFToken', csrftoken);
			},
			data: formData,
			processData: false,
			contentType: false,
			success: function (data, textStatus, request) {
				window.alert(data.msg);
				 location.reload();
			}
		});
	} else {
		// pass
	}
}
