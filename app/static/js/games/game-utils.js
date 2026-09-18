// Game utility functions for Manas Mitra

async function saveGameScore(gameType, score, durationSeconds) {
    try {
        const response = await fetch('/games/save-score', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                game_type: gameType,
                score: score,
                duration_seconds: durationSeconds
            })
        });
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error saving score:', error);
        return null;
    }
}

function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

function showCompletionModal(title, score, stats) {
    // This could dynamically create a modal, but for now we rely on Alpine components 
    // inside the templates to show results beautifully.
    console.log(`Game Complete: ${title}, Score: ${score}`, stats);
}

// Simple confetti implementation
function triggerConfetti() {
    const duration = 3000;
    const end = Date.now() + duration;

    // Check if canvas confetti is loaded, otherwise use a simple CSS one or load it
    if (typeof confetti === 'function') {
        (function frame() {
            confetti({
                particleCount: 5,
                angle: 60,
                spread: 55,
                origin: { x: 0 },
                colors: ['#2dd4bf', '#5eead4', '#ccfbf1', '#0d9488']
            });
            confetti({
                particleCount: 5,
                angle: 120,
                spread: 55,
                origin: { x: 1 },
                colors: ['#2dd4bf', '#5eead4', '#ccfbf1', '#0d9488']
            });

            if (Date.now() < end) {
                requestAnimationFrame(frame);
            }
        }());
    } else {
        // Fallback simple confetti loader
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js';
        script.onload = () => {
            triggerConfetti(); // call again once loaded
        };
        document.head.appendChild(script);
    }
}
