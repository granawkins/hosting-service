const siteUrl = (siteName) => `http://${siteName}.localhost`;

const loadSites = async () => {
    const response = await fetch('/api/active_sites');
    const sites = await response.json();
    const siteList = document.getElementById('siteList');
    siteList.innerHTML = Object.entries(sites)
        .map(([site, port]) => `
            <div>
                <a href="#" onclick="previewSite('${site}'); return false;">${siteUrl(site)}</a> (Port: ${port})
                <button onclick="removeSite('${site}')">Stop</button>
            </div>
        `).join('') || 'No active sites';
}

const clearPreview = () => {
    const iframe = document.getElementById('sitePreview');
    const screenshotButton = document.getElementById('screenshotButton');
    const screenshot = document.getElementById('screenshot');
    iframe.style.display = 'none';
    screenshotButton.style.display = 'none';
    screenshot.style.display = 'none';
}

const previewSite = (site) => {
    clearPreview();
    const iframe = document.getElementById('sitePreview');
    const screenshotButton = document.getElementById('screenshotButton');
    iframe.style.display = 'block';
    screenshotButton.style.display = 'block';
    iframe.src = siteUrl(site);
    iframe.setAttribute('crossorigin', 'anonymous');
    iframe.setAttribute('loading', 'eager');
    iframe.setAttribute('allow', 'cross-origin-isolated');
}

const handleScreenshot = async () => {
    try {
        const iframe = document.querySelector('iframe');

        const imageData = await new Promise((resolve, reject) => {
            const handleMessage = (event) => {
                if (event.data.type === 'snapshot') {
                    window.removeEventListener('message', handleMessage);
                    resolve(event.data.imageData);
                } else if (event.data.type === 'snapshot_error') {
                    window.removeEventListener('message', handleMessage);
                    reject(new Error(event.data.error));
                }
            };

            window.addEventListener('message', handleMessage);
            iframe.contentWindow.postMessage({ type: 'takeSnapshot' }, iframe.src);

            setTimeout(() => {
                window.removeEventListener('message', handleMessage);
                reject(new Error('Snapshot timeout'));
            }, 10000);
        });

        const screenshot = document.getElementById('screenshot');
        screenshot.src = imageData;
        screenshot.style.display = 'block';
    } catch (err) {
        console.error('Failed to take snapshot:', err);
        alert('Failed to take snapshot: ' + err.message);
    }
};
document.getElementById('screenshotButton').onclick = handleScreenshot;

const deploySite = async () => {
    const siteName = document.getElementById('siteName').value;
    const port = document.getElementById('port').value;
    await fetch('/api/deploy', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ site_name: siteName, port: parseInt(port) })
    });
    loadSites();
}

const removeSite = async (siteName) => {
    await fetch('/api/remove', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ site_name: siteName })
    });
    clearPreview();
    loadSites();
}

loadSites();