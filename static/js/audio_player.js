document.addEventListener('DOMContentLoaded', function() {
    const player = document.getElementById('song-player');
    const PREVIEW_DURATION = 30; // Preview duration in seconds
    
    player.addEventListener('loadedmetadata', function() {
        // Only implement preview restriction if payment is still pending
        const purchaseSection = document.querySelector('.purchase-section');
        if (purchaseSection && purchaseSection.querySelector('#payment-element')) {
            player.addEventListener('timeupdate', function() {
                if (player.currentTime >= PREVIEW_DURATION) {
                    player.pause();
                    player.currentTime = 0;
                }
            });
        }
    });

    player.addEventListener('error', function(e) {
        console.error('Error loading audio:', e);
        alert('Error loading the audio. Please try again later.');
    });
});
