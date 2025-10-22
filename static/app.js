// Requires exifr loaded in HTML: <script src="https://unpkg.com/exifr/dist/lite.umd.js"></script>

const extractBtn = document.getElementById('extractBtn');
const removeBtn = document.getElementById('removeBtn');
const fileInput = document.getElementById('fileInput');
const outputArea = document.getElementById('outputArea');
const progressBar = document.getElementById('progressBar');

// Terminal scan animation
function terminalScanEffect(text, container, callback) {
    let i = 0;
    const interval = setInterval(() => {
        container.innerHTML += text[i];
        container.scrollTop = container.scrollHeight;
        i++;
        if (i >= text.length) {
            clearInterval(interval);
            if (callback) callback();
        }
    }, 25);
}

// Format lat/lon
function formatLatLon(lat, lon) {
    if (lat == null || lon == null) return 'N/A';
    return `${lat.toFixed(6)}, ${lon.toFixed(6)}`;
}

// Reverse-geocode using Nominatim
async function reverseGeocode(lat, lon) {
    try {
        const response = await fetch(`https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lon}&format=json`);
        if (!response.ok) throw new Error('Reverse geocode failed');
        const data = await response.json();
        return data.display_name || 'Unknown location';
    } catch (err) {
        console.warn(err);
        return 'Unknown location';
    }
}

// Extract metadata and GPS info
async function extractMetadata(file) {
    outputArea.innerHTML = '';
    const metadataFields = [
        { label: 'File Name', value: file.name },
        { label: 'Size', value: `${file.size} bytes` },
        { label: 'Type', value: file.type || 'N/A' },
        { label: 'Last Modified', value: new Date(file.lastModified).toLocaleString() }
    ];

    let gps = null;

    if (file.type && file.type.startsWith('image/')) {
        try {
            const exif = await window.exifr.parse(file, { gps: true });
            if (exif && (exif.latitude !== undefined && exif.longitude !== undefined)) {
                gps = { lat: exif.latitude, lon: exif.longitude, altitude: exif.altitude ?? null };
            }
        } catch (err) {
            console.warn('EXIF read failed', err);
        }
    }

    if (gps) {
        metadataFields.push({ label: 'GPS Coordinates', value: formatLatLon(gps.lat, gps.lon) });

        // Show initial GPS before reverse-geocode
        metadataFields.push({ label: 'Location', value: 'Fetching...' });
    } else {
        metadataFields.push({ label: 'GPS Coordinates', value: 'Not found' });
    }

    const totalFields = metadataFields.length;
    for (let i = 0; i < totalFields; i++) {
        const field = metadataFields[i];
        await new Promise(resolve => terminalScanEffect(`${field.label}: ${field.value}\n`, outputArea, resolve));

        const progress = Math.round(((i + 1) / totalFields) * 100);
        progressBar.style.width = `${progress}%`;
        progressBar.innerText = `${progress}%`;

        await new Promise(r => setTimeout(r, 150));
    }

    // If GPS present, fetch reverse-geocoded location and update the output
    if (gps) {
        const locationName = await reverseGeocode(gps.lat, gps.lon);

        // Replace the "Fetching..." line in output
        outputArea.innerHTML = outputArea.innerHTML.replace('Location: Fetching...', `Location: ${locationName}`);
    }
}

// Extract button
extractBtn.addEventListener('click', async () => {
    if (!fileInput.files.length) return alert('Select a file first!');
    progressBar.style.width = '0%';
    progressBar.innerText = '0%';
    const file = fileInput.files[0];
    await extractMetadata(file);
});

// Remove metadata button (same as before)
removeBtn.addEventListener('click', async () => {
    outputArea.innerHTML = '';
    progressBar.style.width = '0%';
    progressBar.innerText = '0%';

    const removalSteps = ['Scanning file...', 'Cleaning metadata...', 'Finalizing...'];
    const totalSteps = removalSteps.length;

    for (let i = 0; i < totalSteps; i++) {
        terminalScanEffect(removalSteps[i] + '\n', outputArea);
        const progress = Math.round(((i + 1) / totalSteps) * 100);
        progressBar.style.width = `${progress}%`;
        progressBar.innerText = `${progress}%`;
        await new Promise(r => setTimeout(r, 500));
    }

    terminalScanEffect('Metadata removed successfully!\n', outputArea);
});
