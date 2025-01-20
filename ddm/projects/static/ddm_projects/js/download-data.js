async function downloadData(endpointUrl, fileName, nParticipants) {

    try {
        const downloadOverlay = document.getElementById('download-overlay');
        downloadOverlay.style.display = 'block';

        const downloadProgress = document.getElementById('download-progress');
        downloadProgress.value = '0 %'
        const progressBar = document.getElementById('ddm-progress-bar');

        const response = await fetch(endpointUrl);

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        // Read the response as a stream
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        const chunks = [];

        let nRows = 0;
        let first = true;
        let progress = 0;
        while (true) {
            const { done, value } = await reader.read();
            // first row is the header of the file.
            if (!first) {
                progress = Math.round((nRows/nParticipants) * 100);
                if (progress > 100) {
                    progress = 100; // account for last yield which would overshoot 100%.
                }
                downloadProgress.innerHTML = String(progress).concat(' %');
                progressBar.style.width = String(progress).concat('%');
                nRows += 10; // Server sends batches of 10 participants.
            } else {
                first = false;
            }
            if (done) break;

            // Decode the binary chunk and add to chunks array
            const chunk = decoder.decode(value, { stream: true });
            chunks.push(chunk);
        }
        downloadProgress.innerHTML = '100 %';
        progressBar.style.width = '100%';

        const csvContent = chunks.join('');
        const blob = new Blob([csvContent], { type: 'text/csv' });

        // Create a temporary download link
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
        console.error('Error fetching CSV stream:', err);
        document.getElementById('download-error-message').textContent = err;

        const downloadOverlay = document.getElementById('download-overlay');
        downloadOverlay.style.display = 'none';

        const errorModal = new bootstrap.Modal(document.getElementById('modal-download-error'));
        errorModal.show();
    }
}
