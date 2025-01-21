async function downloadData(endpointUrl, fileName, nParticipants) {

    try {
        const downloadOverlay = document.getElementById('download-overlay');
        const downloadProgress = document.getElementById('download-progress');
        const progressBar = document.getElementById('ddm-progress-bar');

        downloadOverlay.style.display = 'block';
        downloadProgress.value = '0 %'

        const response = await fetch(endpointUrl);
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        // Read the response as a stream,
        let nRows = 0;
        let first = true;
        let progress = 0;

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        const chunks = [];
        while (true) {
            const { done, value } = await reader.read();
            // First row is the header of the file.
            if (!first) {
                progress = Math.round((nRows/nParticipants) * 100);
                if (progress > 100) {
                    progress = 100;  // Account for last yield which would overshoot 100%.
                }
                downloadProgress.innerHTML = String(progress).concat(' %');
                progressBar.style.width = String(progress).concat('%');
                nRows += 10;  // Server sends batches of 10 participants.
            } else {
                first = false;
            }
            if (done) break;

            // Decode the binary chunk and add to chunks array.
            const chunk = decoder.decode(value, { stream: true });
            chunks.push(chunk);
        }
        downloadProgress.innerHTML = '100 %';
        progressBar.style.width = '100%';

        const csvContent = chunks.join('');
        const blob = new Blob([csvContent], { type: 'text/csv' });

        // Create a temporary download link.
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = fileName.concat('.csv');
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
        await new Promise(r => setTimeout(r, 800));
        downloadOverlay.style.display = 'none';
    } catch (err) {
        document.getElementById('download-error-message').textContent = err;

        const downloadOverlay = document.getElementById('download-overlay');
        downloadOverlay.style.display = 'none';

        const errorModal = new bootstrap.Modal(document.getElementById('modal-download-error'));
        errorModal.show();
    }
}

async function downloadResponses(endpointUrl) {

    try {
        const downloadOverlay = document.getElementById('download-overlay-no-bar');
        downloadOverlay.style.display = 'block';

        const endpoint = endpointUrl.concat('?csv=true');
        const response = await fetch(endpoint);
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        // Extract filename.
        const contentDisposition = response.headers.get('Content-Disposition');
        let filename = 'ddm_responses.csv';
        if (contentDisposition && contentDisposition.includes('filename=')) {
            const filenameMatch = contentDisposition.match(/filename="?([^"]+)"?/);
            if (filenameMatch && filenameMatch[1]) {
                filename = filenameMatch[1];
            }
        }

        // Create download.
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
        await new Promise(r => setTimeout(r, 800));
        downloadOverlay.style.display = 'none';
    } catch (err) {
        document.getElementById('download-error-message').textContent = err;

        const downloadOverlay = document.getElementById('download-overlay-no-bar');
        downloadOverlay.style.display = 'none';

        const errorModal = new bootstrap.Modal(document.getElementById('modal-download-error'));
        errorModal.show();
    }
}
