$( document ).ready(function() {
    $('.sq-tab').first().css('display', 'block');
    $('.subnav-card').first().addClass('nav-card-active');
});

function openTab(targetId) {
	$('.sq-tab').css('display', 'none');
	let tabId = '#' + targetId;
	$( tabId ).first().css('display', 'block');

	$('.subnav-card').removeClass('nav-card-active');
	let senderId = tabId + '-nc'
	$( senderId ).first().addClass('nav-card-active');
}

function requestFile(postUrl, dataSource, qId) {
	// show upload in progress message & disable clicks of any kind
	const csrftoken = $('input[name="csrfmiddlewaretoken"]').val();

	let formData = new FormData();
	formData.append('data_source', dataSource);
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
			const filename = request.getResponseHeader('filename');

			const a = document.createElement('a');
    		document.body.appendChild(a);
    		a.style = 'display: none';
			console.log('success!')
			console.log(data)
        	const blob = new Blob([data], {type: 'octet/stream'}),
            url = window.URL.createObjectURL(blob);
        	a.href = url;
        	a.download = filename;
        	a.click();
        	window.URL.revokeObjectURL(url);
		}
	});
}
