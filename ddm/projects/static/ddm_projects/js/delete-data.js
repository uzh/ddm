/* Delete Project Data */
const deleteDataBtn = document.getElementById('delete-data-button');
if (deleteDataBtn) {
    const endpointUrl = deleteDataBtn.dataset.endpointUrl;
    const csrfToken = deleteDataBtn.dataset.csrfToken;
    deleteDataBtn.addEventListener('click', () => {
        deleteData(endpointUrl, csrfToken);
    });
}
function deleteData(postUrl, csrfToken) {
  fetch(postUrl, {
    method: 'DELETE',
    headers: {
      'X-CSRFToken': csrfToken,
      'Content-Type': 'application/json'
    }
  })
  .then(response => {
    if (!response.ok) {
      return response.text().then(text => { throw new Error(text) });
    }
    return response.json();
  })
  .then(data => {
    const successModalEl = document.getElementById('modal-delete-success');
    const successModal = bootstrap.Modal.getOrCreateInstance(successModalEl);
    successModal.toggle();

    setTimeout(() => {
      window.location.reload();
    }, 3000);
  })
  .catch(error => {
    const errorMessageEl = document.getElementById('delete-error-message');
    if (errorMessageEl) {
      errorMessageEl.textContent = error.message;
    }
    const errorModalEl = document.getElementById('modal-delete-error');
    const errorModal = bootstrap.Modal.getOrCreateInstance(errorModalEl);
    errorModal.toggle();
  });
}


/* Delete Participant Data */
const deleteParticipantBtn = document.getElementById('delete-participant-button');
if (deleteParticipantBtn) {
    const endpointUrl = deleteParticipantBtn.dataset.endpointUrl;
    const csrfToken = deleteParticipantBtn.dataset.csrfToken;
    deleteParticipantBtn.addEventListener('click', () => {
        deleteParticipant(endpointUrl, csrfToken);
    });
}
function deleteParticipant(postUrl, csrfToken) {
  const participantInput = document.getElementById('participant-id-input');
  const participantId = participantInput ? participantInput.value : null;
  const requestUrl = postUrl.replace('placeholder', participantId);

  fetch(requestUrl, {
    method: 'DELETE',
    headers: {
      'X-CSRFToken': csrfToken,
      'Content-Type': 'application/json'
    }
  })
  .then(response => {
    if (!response.ok) {
      return response.text().then(text => { throw new Error(text); });
    }
    return response.json();
  })
  .then(data => {
    const successModalEl = document.getElementById('modal-participant-delete-success');
    const successModal = bootstrap.Modal.getOrCreateInstance(successModalEl);
    successModal.toggle();

    setTimeout(() => {
      window.location.reload();
    }, 3000);
  })
  .catch(error => {
    const errorMessageEl = document.getElementById('delete-error-message');
    if (errorMessageEl) {
      errorMessageEl.textContent = JSON.parse(error.message).message;
    }
    const errorModalEl = document.getElementById('modal-delete-error');
    const errorModal = bootstrap.Modal.getOrCreateInstance(errorModalEl);
    errorModal.toggle();
  });
}
