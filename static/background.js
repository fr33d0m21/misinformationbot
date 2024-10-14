// background.js

// Ensure the script runs after the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('matrix-canvas');
    const ctx = canvas.getContext('2d');

    // Set canvas dimensions to full window size
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    // Characters - Unicode characters for extended effect
    const chars = 'アァカサタナハマヤャラワンヰヱガギグゲゴザジズゼゾダヂヅデドバビブベボパピプペポヴー0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ';

    // Convert the string into an array of single characters
    const characters = chars.split('');

    // Font size and number of columns
    const fontSize = 16;
    const columns = canvas.width / fontSize;

    // An array of drops - one per column
    const drops = new Array(Math.floor(columns)).fill(1);

    // Quantum random number generator function using XORShift algorithm
    function quantumRandom() {
        let seed = performance.now();
        return function() {
            seed ^= seed << 13;
            seed ^= seed >> 17;
            seed ^= seed << 5;
            return Math.abs(seed % 1);
        };
    }

    const random = quantumRandom();

    // Draw function
    function draw() {
        // Black background with slight opacity for the trail effect
        ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Set the text color to Matrix green and font
        ctx.fillStyle = '#00ff41';
        ctx.font = `${fontSize}px 'Share Tech Mono'`;

        // Loop over drops
        for (let i = 0; i < drops.length; i++) {
            // Use quantum random function to pick a character
            const text = characters[Math.floor(random() * characters.length)];

            // x coordinate of the character
            const x = i * fontSize;

            // y coordinate is drops[i] * fontSize
            const y = drops[i] * fontSize;

            // Draw the character
            ctx.fillText(text, x, y);

            // Randomly reset the drop
            if (y > canvas.height && random() > 0.975) {
                drops[i] = 0;
            }

            // Increment the drop
            drops[i]++;
        }
    }

    // Use GSAP ticker for smoother animation
    gsap.ticker.add(draw);

    // Handle window resize
    window.addEventListener('resize', () => {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        drops.length = Math.floor(canvas.width / fontSize);
        drops.fill(1);
    });

    // Optional: Add a Three.js effect overlay (Quantum Wave)
    // Create a 3D wave effect using Three.js and overlay it onto the canvas

    // Scene, Camera, Renderer
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.z = 50;

    const renderer = new THREE.WebGLRenderer({ alpha: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.domElement.style.position = 'fixed';
    renderer.domElement.style.top = '0';
    renderer.domElement.style.left = '0';
    renderer.domElement.style.zIndex = '-1'; // Ensure it stays behind other elements

    document.body.appendChild(renderer.domElement);

    // Create a plane geometry and apply a shader material to create a quantum wave effect
    const geometry = new THREE.PlaneGeometry(100, 100, 100, 100);

    // Shader material with custom shaders
    const material = new THREE.ShaderMaterial({
        uniforms: {
            time: { value: 1.0 },
            amplitude: { value: 5.0 }
        },
        vertexShader: `
            uniform float time;
            uniform float amplitude;
            varying vec2 vUv;

            void main() {
                vUv = uv;
                vec3 pos = position;
                pos.z = sin(pos.x * 0.1 + time) * amplitude;
                gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
            }
        `,
        fragmentShader: `
            varying vec2 vUv;

            void main() {
                gl_FragColor = vec4(0.0, 1.0, 0.25, 0.1); // Matrix green with transparency
            }
        `,
        transparent: true,
        side: THREE.DoubleSide,
    });

    const plane = new THREE.Mesh(geometry, material);
    scene.add(plane);

    // Animation function for Three.js
    function animate() {
        requestAnimationFrame(animate);
        material.uniforms.time.value += 0.05;
        renderer.render(scene, camera);
    }

    animate();

    // Adjust renderer on window resize
    window.addEventListener('resize', () => {
        renderer.setSize(window.innerWidth, window.innerHeight);
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
    });
});
