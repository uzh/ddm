document.getElementById('secret-input-form').addEventListener('submit', function (event) {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);

    fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
        .then(response => {
            if (!response.ok) {
                return response.text().then(errorText => {
                    throw new Error(errorText);
                })
            }

            // Extract filename.
            const contentDisposition = response.headers.get('Content-Disposition');
            let filename = 'donation_{{ participant_id }}.zip';
            if (contentDisposition && contentDisposition.includes('filename=')) {
                const filenameMatch = contentDisposition.match(/filename="?([^"]+)"?/);
                if (filenameMatch && filenameMatch[1]) {
                    filename = filenameMatch[1];
                }
            }
            return response.blob().then((blob) => ({blob, filename}));

        })
        .then(({ blob, filename }) => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);

            const infoModal = new bootstrap.Modal(document.getElementById('modal-download-success'));
            infoModal.show();
            document.getElementById('message-placeholder').innerHTML = '<span class="text-success">Download Successful</span>'

        })
        .catch(error => {
            const errorModal = new bootstrap.Modal(document.getElementById('modal-download-error'));
            document.getElementById('download-error-message').textContent = error;
            errorModal.show();
            document.getElementById('message-placeholder').innerHTML = `<span class="text-danger">${error}</span>`
        });
});
