// Generar estrellas
const starsContainer = document.getElementById('expanse-stars');
for (let i = 0; i < 150; i++) {
    const star = document.createElement('div');
    star.className = 'expanse-star';
    star.style.width = Math.random() * 2 + 0.5 + 'px';
    star.style.height = star.style.width;
    star.style.top = Math.random() * 100 + '%';
    star.style.left = Math.random() * 100 + '%';
    star.style.setProperty('--duration', Math.random() * 3 + 2 + 's');
    starsContainer.appendChild(star);
}

// Configuración del canvas
const canvas = document.getElementById('expanse-canvas');
const ctx = canvas.getContext('2d');
let isPaused = false;
let rotation = 0;
let speedMultiplier = 1;

// Variable global para controlar el zoom dinámicamente
// Se inicializa basándose en el tamaño de pantalla original
let currentZoomLevel = window.innerWidth <= 768 ? 0.7 : 1;
const ZOOM_STEP = 0.1;
const MIN_ZOOM = 0.3;
const MAX_ZOOM = 3.0;

function resizeCanvas() {
    canvas.width = canvas.clientWidth;
    canvas.height = canvas.clientHeight;
}
resizeCanvas();
window.addEventListener('resize', resizeCanvas);

// URLs de los sitios web
const siteUrls = {
    meneame: '/rrss/rss/Meneame',
    renegados: '/rrss/rss/Renegados',
    mediatize: '/rrss/rss/Mediatize',
    tardigram: '/rrss/rss/Tardigram',
    killbait: '/rrss/rss/Killbait'
};

// Datos de los cuerpos celestes
const celestialBodies = {
    meneame: {
        name: 'Menéame',
        type: 'Planeta Central',
        description: 'El planeta principal del sistema, un gigante naranja brillante con anillos de información que orbitan constantemente.',
        baseSize: 54,
        color: '#f97316',
        x: 0,
        y: 0
    },
    renegados: {
        name: 'Renegados',
        type: 'Luna',
        description: 'Una luna rebelde de tono amarillo dorado, conocida por su atmósfera turbulenta y su órbita irregular.',
        distance: 144,
        speed: 1,
        baseSize: 23.4,
        color: '#eab308'
    },
    mediatize: {
        name: 'Mediatize',
        type: 'Luna',
        description: 'Luna púrpura brillante, famosa por sus cristales reflectantes que difunden luz por todo el sistema.',
        distance: 198,
        speed: 0.7,
        baseSize: 23.4,
        color: '#a855f7'
    },
    killbait: {
        name: 'Killbait',
        type: 'Luna',
        description: 'Una luna tecnológica de color azul cian que utiliza inteligencia artificial para curar y sintetizar información de todo el sistema.',
        distance: 252,
        speed: 0.5,
        baseSize: 23.4,
        color: '#06b6d4'
    },
    tardigram: {
        name: 'Tardigram',
        type: 'Luna',
        description: 'Tardigram, afirman no pertenecer a ningún sistema, pero aún así, aquí están, girando a toda velocidad.',
        distance: 306,
        speed: 0.4,
        baseSize: 17.8,
        color: '#10b981'
    }
};

// Función para obtener el factor de escala (ahora devuelve el zoom actual)
function getMobileScaleFactor() {
    return currentZoomLevel;
}

// Función para calcular posición orbital
function calculatePosition(distance, speed, rotation) {
    const angle = (rotation * speed * speedMultiplier * Math.PI) / 180;
    return {
        x: Math.cos(angle) * distance,
        y: Math.sin(angle) * distance
    };
}

// Función para dibujar un planeta/luna
function drawPlanet(x, y, size, color, hasRing = false) {
    // Gradiente radial
    const gradient = ctx.createRadialGradient(
        x - size * 0.3, y - size * 0.3, size * 0.1,
        x, y, size
    );
    gradient.addColorStop(0, color + 'dd');
    gradient.addColorStop(1, color);

    // Planeta
    ctx.beginPath();
    ctx.arc(x, y, size, 0, Math.PI * 2);
    ctx.fillStyle = gradient;
    ctx.fill();

    // Sombra interior
    ctx.beginPath();
    ctx.arc(x + size * 0.3, y + size * 0.3, size * 0.4, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(0, 0, 0, 0.3)';
    ctx.fill();

    // Brillo
    ctx.shadowBlur = 25;
    ctx.shadowColor = color;
    ctx.beginPath();
    ctx.arc(x, y, size, 0, Math.PI * 2);
    ctx.strokeStyle = color;
    ctx.lineWidth = 1.8;
    ctx.stroke();
    ctx.shadowBlur = 0;

    // Anillo para Menéame
    if (hasRing) {
        ctx.save();
        ctx.translate(x, y);
        ctx.scale(1, 0.25);
        ctx.beginPath();
        ctx.arc(0, 0, size * 1.215, 0, Math.PI * 2);
        ctx.strokeStyle = '#fb923c';
        ctx.lineWidth = 5.4;
        ctx.shadowBlur = 18;
        ctx.shadowColor = '#fb923c';
        ctx.stroke();
        ctx.restore();
    }

    // Cráteres para lunas
    if (!hasRing && size < 48.6) {
        ctx.fillStyle = 'rgba(0, 0, 0, 0.2)';
        ctx.beginPath();
        ctx.arc(x + size * 0.2, y - size * 0.3, size * 0.15, 0, Math.PI * 2);
        ctx.fill();
        ctx.beginPath();
        ctx.arc(x - size * 0.3, y + size * 0.1, size * 0.12, 0, Math.PI * 2);
        ctx.fill();
    }
}

// Función para dibujar órbitas
function drawOrbit(centerX, centerY, radius) {
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
    ctx.strokeStyle = 'rgba(107, 114, 128, 0.3)';
    ctx.lineWidth = 0.9;
    ctx.stroke();
}

// Función para dibujar etiquetas
function drawLabel(x, y, text, color, offsetY) {
    const fontSize = window.innerWidth < 768 ? '11px' : '13px';
    ctx.font = `bold ${fontSize} "Segoe UI"`;
    ctx.fillStyle = color;
    ctx.shadowBlur = 7;
    ctx.shadowColor = color;
    ctx.textAlign = 'center';
    ctx.fillText(text, x, y + offsetY);
    ctx.shadowBlur = 0;
}

// Función principal de animación
function animate() {
    if (!isPaused) {
        rotation += 0.1 * speedMultiplier;
    }

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;

    // Obtenemos el factor de escala actual (manejado por zoom)
    const mobileScale = getMobileScaleFactor();

    // Dibujar órbitas con escala móvil
    Object.entries(celestialBodies).forEach(([key, body]) => {
        if (key !== 'meneame') {
            const orbitDistance = body.distance * mobileScale;
            drawOrbit(centerX, centerY, orbitDistance);
        }
    });

    // Dibujar planeta Menéame con tamaño escalado
    const meneameBaseSize = celestialBodies.meneame.baseSize;
    const meneameSize = meneameBaseSize * mobileScale;
    drawPlanet(centerX, centerY, meneameSize, celestialBodies.meneame.color, true);
    const labelOffsetY = meneameSize + 16.2;
    drawLabel(centerX, centerY, 'Menéame', '#ffffff', labelOffsetY);

    // Actualizar y dibujar lunas
    Object.entries(celestialBodies).forEach(([key, body]) => {
        if (key !== 'meneame') {
            const distance = body.distance * mobileScale;
            const size = body.baseSize * mobileScale;
            const pos = calculatePosition(distance, body.speed, rotation);
            body.x = centerX + pos.x;
            body.y = centerY + pos.y;
            drawPlanet(body.x, body.y, size, body.color);
            drawLabel(body.x, body.y, body.name, body.color, size + 16.2);
        }
    });

    requestAnimationFrame(animate);
}

// Manejo de clics
canvas.addEventListener('click', (e) => {
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    Object.entries(celestialBodies).forEach(([key, body]) => {
        const bodyX = key === 'meneame' ? canvas.width / 2 : body.x;
        const bodyY = key === 'meneame' ? canvas.height / 2 : body.y;
        const currentScale = getMobileScaleFactor();
        const currentSize = key === 'meneame' ? celestialBodies.meneame.baseSize * currentScale : body.baseSize * currentScale;
        const distance = Math.sqrt((x - bodyX) ** 2 + (y - bodyY) ** 2);

        if (distance < currentSize * 1.2) {
            showInfo(key, body);
        }
    });
});

// Mostrar información de cuerpo celeste + enlace
function showInfo(key, body) {
    document.getElementById('expanse-infoName').textContent = body.name;
    document.getElementById('expanse-infoType').textContent = body.type;
    document.getElementById('expanse-infoDescription').textContent = body.description;

    const linkEl = document.getElementById('expanse-infoLink');
    linkEl.href = siteUrls[key];
    linkEl.textContent = `Noticias ${body.name}`;

    document.getElementById('expanse-infoPanel').classList.add('active');
}

// Controles de velocidad
function setSpeed(multiplier) {
    speedMultiplier = multiplier;
    // Actualizar clases activas
    document.getElementById('expanse-speed1Btn').classList.remove('active');
    document.getElementById('expanse-speed2Btn').classList.remove('active');
    document.getElementById('expanse-speed3Btn').classList.remove('active');
    document.getElementById(`expanse-speed${multiplier}Btn`).classList.add('active');
}

document.getElementById('expanse-speed1Btn').addEventListener('click', () => setSpeed(1));
document.getElementById('expanse-speed2Btn').addEventListener('click', () => setSpeed(2));
document.getElementById('expanse-speed3Btn').addEventListener('click', () => setSpeed(3));

// Control de pausa
document.getElementById('expanse-pauseBtn').addEventListener('click', () => {
    isPaused = !isPaused;
    document.getElementById('expanse-pauseBtn').textContent = isPaused ? '▶' : '⏸';
});

// Control de Zoom
document.getElementById('expanse-zoomInBtn').addEventListener('click', () => {
    if (currentZoomLevel < MAX_ZOOM) {
        currentZoomLevel += ZOOM_STEP;
    }
});

document.getElementById('expanse-zoomOutBtn').addEventListener('click', () => {
    if (currentZoomLevel > MIN_ZOOM) {
        currentZoomLevel -= ZOOM_STEP;
    }
});

// Paneles de información
document.getElementById('expanse-closeBtn').addEventListener('click', () => {
    document.getElementById('expanse-infoPanel').classList.remove('active');
});

document.getElementById('expanse-projectInfoBtn').addEventListener('click', () => {
    document.getElementById('expanse-projectInfoPanel').classList.add('active');
});

document.getElementById('expanse-closeProjectBtn').addEventListener('click', () => {
    document.getElementById('expanse-projectInfoPanel').classList.remove('active');
});

// Iniciar animación
animate();
