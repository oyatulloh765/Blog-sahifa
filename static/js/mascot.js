// Mascot configuration
const mascotConfig = {
    states: {
        idle: 'idle',
        happy: 'happy',
        reading: 'reading',
        sleep: 'sleep'
    },
    messages: [
        "Ajoyib post!",
        "O'qishda davom eting!",
        "Siz superstarsiz!",
        "Salom, do'stim!",
        "Bugun qanday kayfiyatdasiz?"
    ]
};

// SVG Content for the Mascot (Simple Owl Shape)
const owlSVG = `
<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg" class="w-full h-full drop-shadow-xl">
    <!-- Body -->
    <circle cx="100" cy="110" r="60" fill="#22c55e" /> <!-- Green body -->
    <ellipse cx="100" cy="110" rx="45" ry="50" fill="#16a34a" opacity="0.2" /> <!-- Shading -->
    
    <!-- Face Background -->
    <ellipse cx="100" cy="100" rx="45" ry="35" fill="#dcfce7" />
    
    <!-- Eyes -->
    <g id="eyes">
        <circle class="eye" cx="80" cy="95" r="12" fill="white" stroke="#15803d" stroke-width="2"/>
        <circle class="pupil" cx="80" cy="95" r="4" fill="#0f172a"/>
        
        <circle class="eye" cx="120" cy="95" r="12" fill="white" stroke="#15803d" stroke-width="2"/>
        <circle class="pupil" cx="120" cy="95" r="4" fill="#0f172a"/>
    </g>
    
    <!-- Beak -->
    <path d="M95 110 L105 110 L100 120 Z" fill="#f59e0b" stroke="#b45309" stroke-width="1"/>
    
    <!-- Wings -->
    <g id="wings">
        <path class="wing-left" d="M45 110 Q 30 140 50 160" stroke="#166534" stroke-width="3" fill="none"/>
        <path class="wing-right" d="M155 110 Q 170 140 150 160" stroke="#166534" stroke-width="3" fill="none"/>
    </g>
    
    <!-- Feet -->
    <g transform="translate(0, 10)">
        <path d="M85 165 L85 175 M90 165 L90 175" stroke="#f59e0b" stroke-width="3" stroke-linecap="round"/>
        <path d="M110 165 L110 175 M115 165 L115 175" stroke="#f59e0b" stroke-width="3" stroke-linecap="round"/>
    </g>
    
    <!-- Speech Bubble (Hidden by default) -->
    <g id="speech-bubble" opacity="0" transform="translate(140, 20) scale(0)">
        <path d="M0 0 L100 0 L100 50 L20 50 L0 70 L0 0" fill="white" stroke="#e2e8f0" stroke-width="2"/>
        <text id="bubble-text" x="50" y="30" font-family="sans-serif" font-size="12" text-anchor="middle" fill="#334155">Salom!</text>
    </g>
</svg>
`;

// Initialize Mascot
document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('mascot-container');
    if (!container) return;

    container.innerHTML = owlSVG;

    // Animations
    const timeline = gsap.timeline({ repeat: -1, yoyo: true });

    // Idle Animation (Breathing)
    timeline.to("#mascot-container svg", {
        y: -5,
        duration: 2,
        ease: "sine.inOut"
    });

    // Blinking Eyes
    setInterval(() => {
        gsap.to(".eye", { scaleY: 0.1, duration: 0.1, yoyo: true, repeat: 1 });
    }, 4000);

    // Interaction
    container.addEventListener('click', () => {
        // Jump animation
        gsap.to(container, { y: -20, duration: 0.3, yoyo: true, repeat: 1 });

        // Show random message
        const bubble = document.getElementById('speech-bubble');
        const textElement = document.getElementById('bubble-text');
        const randomMsg = mascotConfig.messages[Math.floor(Math.random() * mascotConfig.messages.length)];

        textElement.textContent = randomMsg;

        gsap.to(bubble, {
            opacity: 1,
            scale: 1,
            duration: 0.5,
            ease: "back.out(1.7)",
            onComplete: () => {
                setTimeout(() => {
                    gsap.to(bubble, { opacity: 0, scale: 0, duration: 0.3 });
                }, 3000);
            }
        });
    });

    // Check reading progress
    window.addEventListener('scroll', () => {
        const scrolled = (window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100;
        if (scrolled > 90) {
            // Celebrate at bottom
            gsap.to(".wing-left", { rotation: 30, transformOrigin: "top left", duration: 0.2, yoyo: true, repeat: 5 });
            gsap.to(".wing-right", { rotation: -30, transformOrigin: "top right", duration: 0.2, yoyo: true, repeat: 5 });
        }
    });
});
