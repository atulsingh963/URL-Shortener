document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const urlForm = document.getElementById('urlForm');
    const urlInput = document.getElementById('urlInput');
    const shortenBtn = document.getElementById('shortenBtn');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const errorMessage = document.getElementById('errorMessage');
    const resultCard = document.getElementById('resultCard');
    const shortUrlLink = document.getElementById('shortUrlLink');
    const copyBtn = document.getElementById('copyBtn');
    const copyBtnText = document.getElementById('copyBtnText');
    const originalUrlPreview = document.getElementById('originalUrlPreview');
    const viewStatsBtn = document.getElementById('viewStatsBtn');

    // Handle Form Submission (Home Page)
    if (urlForm) {
        urlForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            
            const rawUrl = urlInput.value.trim();

            // Client-side quick check
            if (!rawUrl) {
                showError('Please enter a URL to shorten.');
                return;
            }

            // Client-side protocol check
            if (!rawUrl.startsWith('http://') && !rawUrl.startsWith('https://')) {
                showError('URL must start with http:// or https://');
                return;
            }

            setLoading(true);
            hideError();
            if (resultCard) resultCard.style.display = 'none';

            try {
                const response = await fetch('/api/shorten', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ url: rawUrl }),
                });

                const data = await response.json();

                if (!response.ok || !data.success) {
                    throw new Error(data.error || 'Failed to shorten URL.');
                }

                // Render Success State
                if (resultCard) {
                    shortUrlLink.href = data.short_url;
                    shortUrlLink.textContent = data.short_url;

                    if (originalUrlPreview) {
                        originalUrlPreview.textContent = data.original_url;
                    }

                    if (viewStatsBtn) {
                        viewStatsBtn.href = `/stats/${data.short_code}`;
                    }

                    // Store short URL on copy button
                    if (copyBtn) {
                        copyBtn.dataset.url = data.short_url;
                    }

                    resultCard.style.display = 'block';
                }
            } catch (err) {
                showError(err.message || 'An error occurred. Please try again.');
            } finally {
                setLoading(false);
            }
        });
    }

    // Handle Copy Button Click (Home Page & Stats Page)
    if (copyBtn) {
        copyBtn.addEventListener('click', async () => {
            const textToCopy = copyBtn.dataset.url || (shortUrlLink ? shortUrlLink.href : '');
            
            if (!textToCopy) return;

            try {
                if (navigator.clipboard && navigator.clipboard.writeText) {
                    await navigator.clipboard.writeText(textToCopy);
                } else {
                    // Fallback for non-HTTPS or legacy browsers
                    const textArea = document.createElement('textarea');
                    textArea.value = textToCopy;
                    textArea.style.position = 'fixed';
                    textArea.style.opacity = '0';
                    document.body.appendChild(textArea);
                    textArea.focus();
                    textArea.select();
                    document.execCommand('copy');
                    document.body.removeChild(textArea);
                }

                // Temporary UI Feedback
                copyBtn.classList.add('btn-copied');
                if (copyBtnText) copyBtnText.textContent = 'Copied!';

                setTimeout(() => {
                    copyBtn.classList.remove('btn-copied');
                    if (copyBtnText) copyBtnText.textContent = 'Copy';
                }, 2000);
            } catch (err) {
                console.error('Failed to copy to clipboard:', err);
                if (copyBtnText) copyBtnText.textContent = 'Failed';
                setTimeout(() => {
                    if (copyBtnText) copyBtnText.textContent = 'Copy';
                }, 2000);
            }
        });
    }

    // Helper Functions
    function setLoading(isLoading) {
        if (!shortenBtn) return;

        shortenBtn.disabled = isLoading;
        const btnText = shortenBtn.querySelector('.btn-text');

        if (isLoading) {
            if (btnText) btnText.style.opacity = '0.5';
            if (loadingSpinner) loadingSpinner.style.display = 'inline-block';
        } else {
            if (btnText) btnText.style.opacity = '1';
            if (loadingSpinner) loadingSpinner.style.display = 'none';
        }
    }

    function showError(message) {
        if (!errorMessage) return;
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
    }

    function hideError() {
        if (!errorMessage) return;
        errorMessage.textContent = '';
        errorMessage.style.display = 'none';
    }
});
