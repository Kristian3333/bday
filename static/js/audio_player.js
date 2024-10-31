document.addEventListener('DOMContentLoaded', function() {
    const player = document.getElementById('song-player');
    
    player.addEventListener('error', function(e) {
        console.error('Error loading audio:', e);
        alert('Error loading the audio. Please try again later.');
    });
});
