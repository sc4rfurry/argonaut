let scene, camera, renderer, cube, particles, terminal;

function initPreloader() {
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.getElementById('cyber-scene').appendChild(renderer.domElement);

    // Create a cube representing a secure server
    const geometry = new THREE.BoxGeometry(1, 1, 1);
    const material = new THREE.MeshPhongMaterial({
        color: 0x00ff00,
        wireframe: true,
        wireframeLinewidth: 2,
        emissive: 0x00ff00,
        emissiveIntensity: 0.5
    });
    cube = new THREE.Mesh(geometry, material);
    scene.add(cube);

    // Add particles representing data packets
    const particlesGeometry = new THREE.BufferGeometry();
    const particlesCnt = 5000;
    const posArray = new Float32Array(particlesCnt * 3);
    for (let i = 0; i < particlesCnt * 3; i++) {
        posArray[i] = (Math.random() - 0.5) * 5;
    }
    particlesGeometry.setAttribute('position', new THREE.BufferAttribute(posArray, 3));
    const particlesMaterial = new THREE.PointsMaterial({
        size: 0.005,
        color: 0x00ffff
    });
    particles = new THREE.Points(particlesGeometry, particlesMaterial);
    scene.add(particles);

    // Add lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);
    const pointLight = new THREE.PointLight(0xffffff, 1);
    pointLight.position.set(5, 5, 5);
    scene.add(pointLight);

    camera.position.z = 3;

    animate();
}

function animate() {
    requestAnimationFrame(animate);

    cube.rotation.x += 0.01;
    cube.rotation.y += 0.01;

    particles.rotation.x += 0.001;
    particles.rotation.y += 0.001;

    renderer.render(scene, camera);
}

function shareOnTwitter() {
    const text = "Check out ArgøNaut, a powerful and flexible argument parsing library for Python!";
    const url = encodeURIComponent(window.location.href);
    const twitterUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${url}`;
    window.open(twitterUrl, '_blank');
}

function shareOnLinkedIn() {
    const url = encodeURIComponent(window.location.href);
    const title = encodeURIComponent("ArgøNaut - Python Argument Parsing Library");
    const summary = encodeURIComponent("A powerful and flexible argument parsing library for Python");
    const linkedInUrl = `https://www.linkedin.com/shareArticle?mini=true&url=${url}&title=${title}&summary=${summary}`;
    window.open(linkedInUrl, '_blank');
}

function shareOnFacebook() {
    const url = encodeURIComponent(window.location.href);
    const facebookUrl = `https://www.facebook.com/sharer/sharer.php?u=${url}`;
    window.open(facebookUrl, '_blank');
}

function initializePrism() {
    if (typeof Prism !== 'undefined') {
        Prism.highlightAll();
    } else {
        console.warn('Prism.js is not loaded. Code highlighting may not work.');
    }
}

function typeCode(element) {
    const text = element.textContent;
    element.textContent = '';
    let i = 0;
    const timer = setInterval(() => {
        if (i < text.length) {
            element.textContent += text.charAt(i);
            Prism.highlightElement(element);
            i++;
        } else {
            clearInterval(timer);
        }
    }, 20);
}

document.addEventListener('DOMContentLoaded', () => {
    document.body.classList.add('loading');

    const cursor = document.createElement('div');
    cursor.classList.add('custom-cursor');
    document.body.appendChild(cursor);

    let cursorVisible = false;

    function updateCursor(e) {
        const x = e.clientX;
        const y = e.clientY;

        cursor.style.transform = `translate3d(${x}px, ${y}px, 0)`;

        if (!cursorVisible) {
            cursorVisible = true;
            cursor.style.opacity = 1;
        }
    }

    document.addEventListener('mousemove', updateCursor);

    document.addEventListener('mouseenter', () => {
        cursorVisible = true;
        cursor.style.opacity = 1;
    });

    document.addEventListener('mouseleave', () => {
        cursorVisible = false;
        cursor.style.opacity = 0;
    });

    // Update this part to change cursor color instead of size
    document.querySelectorAll('a, button, input, textarea, select').forEach(el => {
        el.addEventListener('mouseenter', () => {
            cursor.style.borderColor = 'var(--secondary-color)';
            cursor.style.backgroundColor = 'var(--secondary-color)';
        });
        el.addEventListener('mouseleave', () => {
            cursor.style.borderColor = 'var(--primary-color)';
            cursor.style.backgroundColor = 'transparent';
        });
    });

    // Prevent default cursor style
    document.body.style.cursor = 'none';
    document.querySelectorAll('a, button, input, textarea, select').forEach(el => {
        el.style.cursor = 'none';
    });

    initPreloader();

    const preloader = document.getElementById('preloader');
    const loadingStatus = document.getElementById('loading-status');
    const mainContent = document.querySelector('main');
    const header = document.querySelector('header');

    const loadingMessages = [
        'Establishing secure connection...',
        'Verifying encryption protocols...',
        'Scanning for vulnerabilities...',
        'Initializing firewall...',
        'Syncing quantum entanglement...',
        'Bypassing security measures...',
        'Accessing ArgøNaut mainframe...'
    ];

    function updateLoadingStatus() {
        let index = 0;
        return setInterval(() => {
            loadingStatus.textContent = loadingMessages[index];
            index = (index + 1) % loadingMessages.length;
        }, 2000);
    }

    const loadingInterval = updateLoadingStatus();

    setTimeout(() => {
        clearInterval(loadingInterval);
        loadingStatus.textContent = 'Access granted. Welcome to ArgøNaut!';

        gsap.to(cube.scale, { x: 2, y: 2, z: 2, duration: 1, ease: 'power2.out' });
        gsap.to(particles.material, { size: 0.02, duration: 1, ease: 'power2.out' });

        gsap.to(preloader, {
            opacity: 0,
            duration: 1,
            onComplete: () => {
                preloader.style.display = 'none';
                document.body.style.overflow = 'hidden';
                header.style.display = 'block';
                mainContent.style.display = 'block';
                document.body.classList.remove('loading');
                setTimeout(() => {
                    header.classList.add('show');
                    mainContent.classList.add('show');
                }, 50);
            }
        });
    }, 5000);

    const darkModeToggle = document.getElementById('darkModeToggle');
    const body = document.body;

    function updateTheme(isDark) {
        const root = document.documentElement;
        const colors = isDark ?
            ['#ff00ff', '#00ffff', '#1a1a1a', '#2b2b2b', 'rgba(255, 0, 255, 0.5)', 'rgba(26, 26, 26, 0.9)', '#cc00cc'] :
            ['#00ffff', '#ff00ff', '#0a0a0a', '#1a1a1a', 'rgba(0, 255, 255, 0.5)', 'rgba(10, 10, 10, 0.9)', '#00cccc'];

        ['--primary-color', '--secondary-color', '--background-color', '--card-bg', '--card-shadow', '--navbar-bg', '--button-hover']
            .forEach((prop, i) => root.style.setProperty(prop, colors[i]));

        updateCursorColor();
        updateTerminalTheme(isDark);
    }

    darkModeToggle.addEventListener('click', () => {
        const isDark = body.classList.toggle('dark-mode');
        darkModeToggle.querySelector('i').classList.toggle('fa-moon');
        darkModeToggle.querySelector('i').classList.toggle('fa-sun');

        updateTheme(isDark);
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
    });

    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        body.classList.add('dark-mode');
        darkModeToggle.querySelector('i').classList.replace('fa-moon', 'fa-sun');
        updateTheme(true);
    }

    function updateCursorColor() {
        cursor.style.borderColor = 'var(--primary-color)';
    }

    const copyButtons = document.querySelectorAll('.copy-btn');
    copyButtons.forEach(button => {
        button.addEventListener('click', () => {
            const textToCopy = button.getAttribute('data-clipboard-text') ||
                button.closest('.card-body').querySelector('pre code').textContent;

            if (navigator.clipboard && window.isSecureContext) {
                navigator.clipboard.writeText(textToCopy).then(() => showCopyFeedback(button));
            } else {
                const textArea = document.createElement('textarea');
                textArea.value = textToCopy;
                document.body.appendChild(textArea);
                textArea.select();
                try {
                    document.execCommand('copy');
                    showCopyFeedback(button);
                } catch (err) {
                    console.error('Failed to copy: ', err);
                }
                document.body.removeChild(textArea);
            }
        });
    });

    function showCopyFeedback(button) {
        const originalText = button.innerHTML;
        button.innerHTML = '<i class="fas fa-check"></i> Copied!';
        button.disabled = true;
        setTimeout(() => {
            button.innerHTML = originalText;
            button.disabled = false;
        }, 2000);
    }

    function initAdvancedCLI() {
        terminal = new Terminal({
            theme: getTerminalTheme(document.body.classList.contains('dark-mode')),
            cursorBlink: true,
            fontSize: 14,
            fontFamily: '"Fira Code", monospace',
            convertEol: true,
        });

        const fitAddon = new FitAddon.FitAddon();
        terminal.loadAddon(fitAddon);

        const terminalElement = document.getElementById('terminal');
        if (terminalElement) {
            terminal.open(terminalElement);
            fitAddon.fit();

            window.addEventListener('resize', () => fitAddon.fit());

            let currentLine = '';
            let commandHistory = [];
            let historyIndex = -1;

            terminal.writeln('Welcome to the ArgøNaut Interactive CLI!');
            terminal.writeln('Type "help" for a list of commands.');
            terminal.write('\r\n$ ');

            terminal.onKey(({ key, domEvent }) => {
                const printable = !domEvent.altKey && !domEvent.ctrlKey && !domEvent.metaKey;

                if (domEvent.keyCode === 13) {
                    terminal.write('\r\n');
                    handleCommand(currentLine.trim());
                    commandHistory.push(currentLine.trim());
                    historyIndex = -1;
                    currentLine = '';
                    terminal.write('\r\n$ ');
                } else if (domEvent.keyCode === 8) {
                    if (currentLine.length > 0) {
                        currentLine = currentLine.slice(0, -1);
                        terminal.write('\b \b');
                    }
                } else if (domEvent.keyCode === 38) {
                    if (historyIndex < commandHistory.length - 1) {
                        historyIndex++;
                        currentLine = commandHistory[commandHistory.length - 1 - historyIndex];
                        terminal.write('\r$ ' + currentLine + ' '.repeat(terminal.cols - currentLine.length - 2));
                    }
                } else if (domEvent.keyCode === 40) {
                    if (historyIndex > 0) {
                        historyIndex--;
                        currentLine = commandHistory[commandHistory.length - 1 - historyIndex];
                        terminal.write('\r$ ' + currentLine + ' '.repeat(terminal.cols - currentLine.length - 2));
                    } else if (historyIndex === 0) {
                        historyIndex = -1;
                        currentLine = '';
                        terminal.write('\r$ ' + ' '.repeat(terminal.cols - 2));
                    }
                } else if (printable) {
                    currentLine += key;
                    terminal.write(key);
                }
            });

            function simulateTyping(text, callback) {
                let i = 0;
                const interval = setInterval(() => {
                    if (i < text.length) {
                        terminal.write(text.charAt(i));
                        i++;
                    } else {
                        clearInterval(interval);
                        if (callback) callback();
                    }
                }, 50);
            }

            function handleCommand(command) {
                switch (command.toLowerCase()) {
                    case 'help':
                        simulateTyping('Available commands:\r\n  help     - Show this help message\r\n  create   - Create a new Argonaut parser\r\n  add      - Add an argument to the parser\r\n  parse    - Parse arguments\r\n  clear    - Clear the terminal\r\n');
                        break;
                    case 'create':
                        terminal.writeln('Creating a new Argonaut parser...');
                        terminal.writeln('Parser created with default settings.');
                        break;
                    case 'add':
                        terminal.writeln('Adding a new argument...');
                        terminal.writeln('Argument "--example" added successfully.');
                        break;
                    case 'parse':
                        terminal.writeln('Parsing arguments...');
                        terminal.writeln('Arguments parsed successfully.');
                        break;
                    case 'clear':
                        terminal.clear();
                        return;
                    default:
                        terminal.writeln(`Unknown command: ${command}`);
                        terminal.writeln('Type "help" for a list of available commands.');
                }
            }
        }
    }

    function getTerminalTheme(isDark) {
        return {
            background: isDark ? '#1a1a1a' : '#0a0a0a',
            foreground: isDark ? '#ff00ff' : '#00ffff',
            cursor: isDark ? '#ff00ff' : '#00ffff',
            cursorAccent: isDark ? '#00ffff' : '#ff00ff',
            selection: 'rgba(255, 255, 255, 0.3)',
        };
    }

    function updateTerminalTheme(isDark) {
        if (terminal) {
            terminal.setOption('theme', getTerminalTheme(isDark));
        }
    }

    document.body.style.cursor = 'none';

    updateCursorColor();

    initAdvancedCLI();

    function createTooltip(element, content) {
        const tooltip = document.createElement('div');
        tooltip.classList.add('-tooltip');
        tooltip.innerHTML = content;

        element.addEventListener('mouseenter', () => {
            document.body.appendChild(tooltip);
            positionTooltip(element, tooltip);
        });

        element.addEventListener('mouseleave', () => {
            document.body.removeChild(tooltip);
        });
    }

    function positionTooltip(element, tooltip) {
        const rect = element.getBoundingClientRect();
        const tooltipRect = tooltip.getBoundingClientRect();

        tooltip.style.left = `${rect.left + (rect.width / 2) - (tooltipRect.width / 2)}px`;
        tooltip.style.top = `${rect.bottom + 10}px`;
    }

    document.querySelectorAll('[data-tooltip]').forEach(element => {
        createTooltip(element, element.getAttribute('data-tooltip'));
    });

    // Custom Scrollbar
    const scrollableContent = document.querySelector('.scrollable-content');
    const customScrollbarContainer = document.createElement('div');
    customScrollbarContainer.classList.add('custom-scrollbar-container');
    const customScrollbar = document.createElement('div');
    customScrollbar.classList.add('custom-scrollbar');
    customScrollbarContainer.appendChild(customScrollbar);
    document.body.appendChild(customScrollbarContainer);

    let scrollTimeout;

    // Update the updateScrollbar function
    function updateScrollbar() {
        const scrollableContent = document.querySelector('.scrollable-content');
        const customScrollbar = document.querySelector('.custom-scrollbar');
        const footer = document.querySelector('footer');

        if (!scrollableContent || !customScrollbar || !footer) return;

        const scrollPercentage = scrollableContent.scrollTop / (scrollableContent.scrollHeight - scrollableContent.clientHeight);
        const scrollbarHeight = Math.max(30, scrollableContent.clientHeight * (scrollableContent.clientHeight / scrollableContent.scrollHeight));

        customScrollbar.style.height = `${scrollbarHeight}px`;
        customScrollbar.style.top = `${scrollPercentage * (scrollableContent.clientHeight - scrollbarHeight)}px`;
        customScrollbar.style.opacity = '1';

        if (scrollPercentage > 0.99) {
            footer.style.opacity = '1';
        } else {
            footer.style.opacity = '0';
        }

        clearTimeout(scrollTimeout);
        scrollTimeout = setTimeout(() => {
            customScrollbar.style.opacity = '0';
        }, 2000);
    }

    if (scrollableContent) {
        scrollableContent.addEventListener('scroll', updateScrollbar);
        window.addEventListener('resize', updateScrollbar);

        // Initial update
        setTimeout(updateScrollbar, 100);
    }

    // Add this line after the existing event listeners for scrollableContent
    if (scrollableContent) {
        scrollableContent.addEventListener('mousemove', () => {
            const customScrollbar = document.querySelector('.custom-scrollbar');
            if (customScrollbar) {
                customScrollbar.style.opacity = '1';
            }
        });
    }

    const logoContainer = document.querySelector('.logo-container');

    // Three.js setup
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, logoContainer.offsetWidth / logoContainer.offsetHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ alpha: true });
    renderer.setSize(logoContainer.offsetWidth, logoContainer.offsetHeight);
    logoContainer.appendChild(renderer.domElement);

    // Create a plane for the logo
    const geometry = new THREE.PlaneGeometry(1, 1);
    const texture = new THREE.TextureLoader().load('Argonaut-Logo.png');
    const material = new THREE.MeshBasicMaterial({ map: texture, transparent: true });
    const mesh = new THREE.Mesh(geometry, material);
    scene.add(mesh);

    camera.position.z = 1.5;

    function animate() {
        requestAnimationFrame(animate);
        mesh.rotation.y += 0.01;
        renderer.render(scene, camera);
    }
    animate();

    // Parallax effect
    logoContainer.addEventListener('mousemove', (e) => {
        const { left, top, width, height } = logoContainer.getBoundingClientRect();
        const x = (e.clientX - left) / width - 0.5;
        const y = (e.clientY - top) / height - 0.5;

        gsap.to(mesh.rotation, {
            x: -y * 0.5,
            y: x * 0.5,
            duration: 0.5
        });
    });

    function loadParticlesJS(callback) {
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/particles.js@2.0.0/particles.min.js';
        script.onload = callback;
        document.head.appendChild(script);
    }

    function initParticleBackground() {
        if (typeof particlesJS === 'undefined') {
            loadParticlesJS(() => {
                setupParticles();
            });
        } else {
            setupParticles();
        }
    }

    function setupParticles() {
        particlesJS("particles-js", {
            particles: {
                number: {
                    value: 100,
                    density: {
                        enable: true,
                        value_area: 800
                    }
                },
                color: {
                    value: ["#00ffff", "#ff00ff", "#ffffff"]
                },
                shape: {
                    type: ["circle", "triangle", "edge", "polygon"],
                    stroke: {
                        width: 0,
                        color: "#000000"
                    },
                    polygon: {
                        nb_sides: 5
                    }
                },
                opacity: {
                    value: 0.5,
                    random: true,
                    anim: {
                        enable: true,
                        speed: 1,
                        opacity_min: 0.1,
                        sync: false
                    }
                },
                size: {
                    value: 3,
                    random: true,
                    anim: {
                        enable: true,
                        speed: 2,
                        size_min: 0.1,
                        sync: false
                    }
                },
                line_linked: {
                    enable: true,
                    distance: 150,
                    color: "#00ffff",
                    opacity: 0.4,
                    width: 1
                },
                move: {
                    enable: true,
                    speed: 2,
                    direction: "none",
                    random: true,
                    straight: false,
                    out_mode: "out",
                    bounce: false,
                    attract: {
                        enable: true,
                        rotateX: 600,
                        rotateY: 1200
                    }
                }
            },
            interactivity: {
                detect_on: "canvas",
                events: {
                    onhover: {
                        enable: true,
                        mode: ["grab", "bubble"]
                    },
                    onclick: {
                        enable: true,
                        mode: "push"
                    },
                    resize: true
                },
                modes: {
                    grab: {
                        distance: 140,
                        line_linked: {
                            opacity: 1
                        }
                    },
                    bubble: {
                        distance: 200,
                        size: 6,
                        duration: 2,
                        opacity: 0.8,
                        speed: 3
                    },
                    repulse: {
                        distance: 200,
                        duration: 0.4
                    },
                    push: {
                        particles_nb: 4
                    },
                    remove: {
                        particles_nb: 2
                    }
                }
            },
            retina_detect: true
        });
    }

    // Call this function after the page loads
    document.addEventListener('DOMContentLoaded', initParticleBackground);

    // Initialize Prism
    initializePrism();

    // Apply typing effect to code blocks
    document.querySelectorAll('pre code').forEach(block => {
        block.textContent = block.textContent.trim();
        typeCode(block);
    });

    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const href = this.getAttribute('href');
            if (href !== '#') {
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth'
                    });
                }
            }
        });
    });

    // Set up event listeners for share buttons
    document.querySelectorAll('.dropdown-item[data-share]').forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const platform = e.currentTarget.getAttribute('data-share');
            switch (platform) {
                case 'twitter':
                    shareOnTwitter();
                    break;
                case 'linkedin':
                    shareOnLinkedIn();
                    break;
                case 'facebook':
                    shareOnFacebook();
                    break;
            }
        });
    });
});