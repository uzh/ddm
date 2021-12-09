function sleep(ms) {
	return new Promise(resolve => setTimeout(resolve, ms));
}

function submitFile(postUrl, inputId) {
	// show upload in progress message & disable clicks of any kind
	const csrftoken = $('input[name="csrfmiddlewaretoken"]').val();
	let inputElement = $('#q'.concat(inputId).concat('-upload'));

	// show overlay
	inputElement.before('<div id="overlay" class="surquest-overlay"><div class="surquest-loader"></div><div class="surquest-overlay-text">File wird verarbeitet</div></div>');
	let overlay = $('#overlay');
	overlay.css('display', 'block');

	// check filesize
	let max_filesize = parseInt(inputElement[0].getAttribute( 'maxsize' ));

	if (inputElement[0].files[0] !== undefined) {
		if (inputElement[0].files[0].size/1000 > max_filesize ) {
			let invalidInfoClass = 'surquest-invalid-upload-infobox';
			if ( $('.'.concat(invalidInfoClass) ).length ) {
				$('.'.concat(invalidInfoClass)).remove()
			}
			let errorMessage = 'Die Datei ist zu gross.';
			let errorDiv = '<div id="q'.concat(inputId).concat('-invalid" class="').concat(invalidInfoClass).concat('">').concat(errorMessage).concat('</div>');
			$('#sq-fileupload-info').after(errorDiv);
			overlay.css('display', 'none');
			return;
		}
	}

	// remove error message if it is shown
	$( '#q'.concat(inputId).concat('-invalid') ).remove()

	// remove last info messages
	$( '.surquest-success-addendum' ).remove()
	$( '.surquest-fail-addendum' ).remove()
	$( '.sq-msg-box-title' ).remove()

	$( '.surquest-success-infobox' ).remove()

	let timeStart = new Date().getTime();

	let formData = new FormData();
	formData.append('file', inputElement[0].files[0]);
	formData.append('csrfmiddlewaretoken', csrftoken);
	formData.append('question_id', inputId);

	$.ajax({
		type: 'POST',
		url: postUrl,
		beforeSend:     function (request) {
			request.setRequestHeader('X-CSRFToken', csrftoken);
		},
		data: formData,
		processData: false,
		contentType: false,
		success: async function (data) {
			// show overlay for at least 1 seconds (1000ms)
			while (Date.now() - timeStart < 1000) {
				await sleep(500);
			}
			if (data.status == 'complete_ul') {
				if (data.upload_mode == 'multiple files') {
					let msg_box = $('#sq-fileupload-msg-box');

					Object.keys(data.uploaded_files).forEach(function(key) {
						let filenode = document.createElement('P');
						filenode.classList.add('surquest-success-addendum');
						let text = 'Die Datei "'.concat(key).concat('" wurde erfolgreich hochgeladen');
						filenode.innerHTML = text;
						msg_box.append(filenode);
					});
					let filenode = document.createElement('P');
					filenode.innerHTML = 'Alle Dateien wurden erfolgreich ausgelesen';
					filenode.classList.add('sq-msg-box-title');
					msg_box.prepend(filenode);
					msg_box.removeClass('surquest-hidden');
				}

				$('.surquest-success-infobox').addClass('surquest-hidden');
				inputElement.after('<p class="surquest-success-infobox">&#10004;   File Upload erfolgreich abgeschlossen.</p>');
				$('#q'.concat(inputId).concat('-button')).addClass('surquest-hidden');
				$('#q'.concat(inputId).concat('-upload')).addClass('surquest-hidden');
				$('#q'.concat(inputId)).val(data.status);
				if ( $('#q'.concat(inputId).concat('-invalid')).length ) {
					$('#q'.concat(inputId).concat('-invalid')).remove();
				}

			} else if (data.status == 'partial_ul') {
				if (data.upload_mode == 'multiple files') {
					let msg_box =$('#sq-fileupload-msg-box');
					let success_count = 0;
					Object.keys(data.uploaded_files).forEach(function(key) {
						let filenode = document.createElement('P');
						let text;

						if (data.uploaded_files[key] == 'success') {
							filenode.classList.add('surquest-success-addendum');
							text = 'Die Datei "'.concat(key).concat('" wurde erfolgreich hochgeladen');
							success_count = success_count + 1;
						} else {
							filenode.classList.add('surquest-fail-addendum');
							text = 'Die Datei "'.concat(key).concat('" konnte nicht hochgeladen werden');
						}
						filenode.innerHTML = text;
						msg_box.append(filenode);
					});
					let filenode = document.createElement('P');
					filenode.innerHTML = ''.concat(success_count).concat(' von ').concat(Object.keys(data.uploaded_files).length).concat(' Dateien wurden erfolgreich hochgeladen');
					filenode.classList.add('sq-msg-box-title');
					msg_box.prepend(filenode);

					filenode = document.createElement('P');
					filenode.classList.add('surquest-fail-addendum');
					filenode.innerHTML = '<br>'.concat(data.message);
					msg_box.append(filenode)

					msg_box.removeClass('surquest-hidden');
				}
				$('#q'.concat(inputId)).val(data.status);

			} else {
				if (data.upload_mode == 'multiple files') {
					let msg_box =$('#sq-fileupload-msg-box');
					let success_count = 0;
					Object.keys(data.uploaded_files).forEach(function(key) {
						let filenode = document.createElement('P');
						let text;

						if (data.uploaded_files[key] == 'success') {
							filenode.classList.add('surquest-success-addendum');
							text = 'Die Datei "'.concat(key).concat('" wurde erfolgreich hochgeladen');
							success_count = success_count + 1;
						} else {
							filenode.classList.add('surquest-fail-addendum');
							text = 'Die Datei "'.concat(key).concat('" konnte nicht hochgeladen werden');
						}
						filenode.innerHTML = text;
						msg_box.append(filenode);
					});
					let filenode = document.createElement('P');
					filenode.innerHTML = ''.concat(success_count).concat(' von ').concat(Object.keys(data.uploaded_files).length).concat(' Dateien wurden erfolgreich hochgeladen');
					filenode.classList.add('sq-msg-box-title');
					msg_box.prepend(filenode);
					msg_box.removeClass('surquest-hidden');

					if (data.status == 'failed_ul') {
						let errorMessage = '<div id="q'.concat(inputId).concat('-invalid" class="').concat('surquest-invalid-ul-errorbox').concat('">').concat(data.message).concat('</div>');
						msg_box.after(errorMessage);
					}

				} else {
					let invalidInfoClass = 'surquest-invalid-upload-infobox';
					if ( $( ".".concat(invalidInfoClass) ).length ) {
						$(".".concat(invalidInfoClass)).remove()
					}
					let errorMessage = '<div id="q'.concat(inputId).concat('-invalid" class="').concat(invalidInfoClass).concat('">').concat(data.message).concat('</div>');
					$('#sq-fileupload-info').after(errorMessage);
				}
				$('#q'.concat(inputId)).val(data.status);
			}
			overlay.css('display', 'none');
		},
		error: function (request, status, error) {
			let invalidInfoClass = 'surquest-invalid-upload-infobox';
			if ( $('.'.concat(invalidInfoClass) ).length ) {
				$('.'.concat(invalidInfoClass)).remove()
			}
			let errorMessage = 'Bei der Verarbeitung der hochgeladenen Datei auf dem Server ist ein Fehler aufgetreten.'
			let errorDiv = '<div id="q'.concat(inputId).concat('-invalid" class="').concat(invalidInfoClass).concat('">').concat(errorMessage).concat('</div>');
			$('#sq-fileupload-info').after(errorDiv);
			overlay.css('display', 'none');
		}
	});
}

function checkFileUpload(inputId) {
	let upload_status = $('#q'.concat(inputId)).val();
	let form = document.getElementById('question-form');

	let hidden_input = document.createElement('input');
	hidden_input.setAttribute('type', 'hidden');
	hidden_input.setAttribute('name', 'submit-next');
	hidden_input.setAttribute('value', 'Weiter');

	if (upload_status == '-77' || upload_status == '') {
		let proceed = confirm("ACHTUNG: \nSie haben keine Datei hochgeladen. \n\nSind Sie sicher, dass Sie fortfahren möchten? Sie haben anschliessend keine Möglichkeit mehr, auf diese Seite zurückzukehren. \n\nWenn Sie dennoch fortfahren möchten, klicken Sie auf 'OK'.");
		if (proceed == true) {
			event.returnValue = true;
			form.appendChild(hidden_input);
			form.submit();
			return true;
		} else {
			return false;
		}
	} else if (upload_status == 'failed_ul') {
		let proceed = confirm("ACHTUNG: \nDer Upload Ihrer Daten ist fehlgeschlagen. \n\nSind Sie sicher, dass Sie fortfahren möchten? Sie haben anschliessend keine Möglichkeit mehr, auf diese Seite zurückzukehren. \n\nWenn Sie dennoch fortfahren möchten, klicken Sie auf 'OK'.");
		if (proceed == true) {
			event.returnValue = true;
			form.appendChild(hidden_input);
			form.submit();
			return true;
		} else {
			return false;
		}
	} else {
		event.returnValue = true;
		form.appendChild(hidden_input);
		form.submit();
		return true;
	}
}
