self.addEventListener('install', (e) => {
    console.log('[Service Worker] Installed successfully!');
});

self.addEventListener('fetch', (e) => {
    // This blank fetch listener is the minimum requirement 
    // to trigger the native "Install App" prompt on devices.
});