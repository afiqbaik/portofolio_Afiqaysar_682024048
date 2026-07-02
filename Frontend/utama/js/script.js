document.addEventListener('DOMContentLoaded', async () => {
    document.getElementById('current-year').textContent = new Date().getFullYear();

    await loadPublicData();
    setupContactForm();
    setupNavigation();
});

async function loadPublicData() {
    try {
        const response = await fetch('/api/main-profile');
        if (!response.ok) throw new Error(`Server error: ${response.status}`);

        const res = await response.json();

        if (!res.success || !res.data) {
            showError('Portfolio data is not available yet.');
            return;
        }

        const { skills, experiences, projects } = res.data;
        const profile = res.data;

        if (!profile.nama_lengkap) {
            showError('Profile name is empty.');
            return;
        }

        renderHero(profile);
        renderAbout(profile);
        renderSkills(skills || []);
        renderExperiences(experiences || []);
        renderProjects(projects || []);
        renderContact(profile);
    } catch (error) {
        console.error('Fetch Error:', error);
        showError('Unable to connect to the server.');
    }
}

function showError(msg) {
    const heroContent = document.getElementById('hero-content');
    if (heroContent) {
        heroContent.innerHTML = `<div class="error-state"><i class="fas fa-exclamation-circle"></i> ${msg}</div>`;
    }
}

function renderHero(p) {
    const hero = document.getElementById('hero-content');
    if (!hero) return;

    const name = escapeHtml(p?.nama_lengkap || 'Afiq Aysar Fajari');
    const role = escapeHtml(p?.prodi || 'Software Engineer');
    const campus = escapeHtml(p?.universitas || 'Indonesia');

    hero.innerHTML = `
        <h4>Welcome to my portfolio</h4>
        <h1>Hello, I am <span>${name}</span></h1>
        <p>${role} • ${campus}</p>
        <a href="#projects" class="btn">View My Projects</a>
    `;
}

function renderAbout(p) {
    const img = document.getElementById('profile-photo');
    const placeholder = document.getElementById('photo-placeholder');

    if (img && placeholder) {
        if (p.foto_url) {
            img.src = p.foto_url;
            img.style.display = 'block';
            placeholder.style.display = 'none';
        } else {
            img.style.display = 'none';
            placeholder.style.display = 'flex';
        }
    }

    const aboutText = document.getElementById('about-text');
    if (aboutText) {
        const name = escapeHtml(p?.nama_lengkap || 'Afiq Aysar Fajari');
        const role = escapeHtml(p?.prodi || 'Software Engineer');
        const institution = escapeHtml(p?.universitas || 'Indonesia');
        const faculty = escapeHtml(p?.fakultas || 'Technology');
        const address = escapeHtml(p?.alamat || 'Indonesia');
        const aboutMe = escapeHtml(p?.about_me || 'I focus on building modern web applications, reliable APIs, and clean, responsive user experiences.');

        aboutText.innerHTML = `
            <h3>${name} • ${role}</h3>
            <p>I am based in ${institution}, with a strong interest in ${faculty} and scalable system development.</p>
            <p>${aboutMe}</p>
            <p>Located in ${address}. I enjoy creating digital products that are functional, aesthetic, and production-ready.</p>
            <a href="#contact" class="btn">Contact Me</a>
        `;
    }
}

function renderSkills(skills) {
    const container = document.getElementById('skills-container');
    if (!container) return;

    if (!skills.length) {
        container.innerHTML = '<p class="empty-state">No skills available yet.</p>';
        return;
    }

    container.innerHTML = skills.map(s => `
        <div class="skill-card">
            <i class="${escapeHtml(s.icon_class || 'fas fa-code')}"></i>
            <h4>${escapeHtml(s.nama_skill)}</h4>
        </div>
    `).join('');
}

function renderExperiences(exps) {
    const container = document.getElementById('experience-container');
    if (!container) return;

    if (!exps.length) {
        container.innerHTML = '<p class="empty-state">No experience entries yet.</p>';
        return;
    }

    container.innerHTML = exps.map(e => `
        <div class="timeline-item">
            <div class="timeline-dot"></div>
            <div class="timeline-content">
                <span class="timeline-date">${escapeHtml(e.durasi)}</span>
                <h3>${escapeHtml(e.posisi)}</h3>
                <h4>${escapeHtml(e.perusahaan)}</h4>
                <p>${escapeHtml(e.deskripsi)}</p>
            </div>
        </div>
    `).join('');
}

function renderProjects(projs) {
    const container = document.getElementById('projects-container');
    if (!container) return;

    if (!projs.length) {
        container.innerHTML = '<p class="empty-state">No projects available yet.</p>';
        return;
    }

    container.innerHTML = projs.map(p => `
        <div class="project-card">
            <div class="project-img-wrapper">
                ${p.gambar_url
                    ? `<img src="${escapeHtml(p.gambar_url)}" alt="${escapeHtml(p.judul)}" class="project-img" loading="lazy">`
                    : '<div class="project-img" style="display:flex;align-items:center;justify-content:center;background:#eee;"><i class="fas fa-box-open"></i></div>'}
                <div class="project-overlay">
                    <h3 class="project-title-overlay">${escapeHtml(p.judul)}</h3>
                </div>
            </div>
            <div class="project-info">
                <p>${escapeHtml(p.deskripsi?.substring(0, 120))}${p.deskripsi?.length > 120 ? '...' : ''}</p>
                <div class="project-links">
                    ${p.link_project ? `<a href="${escapeHtml(p.link_project)}" target="_blank"><i class="fas fa-external-link-alt"></i> Demo</a>` : ''}
                </div>
            </div>
        </div>
    `).join('');
}

function renderContact(p) {
    const emailDisplay = document.getElementById('contact-email-display');
    if (emailDisplay && p.email) {
        emailDisplay.innerHTML = `Interested in collaborating? Send a message to <strong>${escapeHtml(p.email)}</strong>`;
    }
}

function setupContactForm() {
    const contactForm = document.getElementById('contactForm');
    if (!contactForm) return;

    contactForm.addEventListener('submit', async function(e) {
        e.preventDefault();

        const btn = document.getElementById('sendBtn');
        const originalText = btn.textContent;

        btn.disabled = true;
        btn.textContent = 'Sending...';

        try {
            const response = await fetch('/api/contact', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: document.getElementById('contactName').value,
                    email: document.getElementById('contactEmail').value,
                    message: document.getElementById('contactMessage').value
                })
            });

            const result = await response.json();

            if (response.ok) {
                alert('✅ ' + result.message);
                contactForm.reset();
            } else {
                alert('❌ ' + (result.error || 'Failed to send'));
            }
        } catch (error) {
            alert('❌ Network error.');
        } finally {
            btn.disabled = false;
            btn.textContent = originalText;
        }
    });
}

function setupNavigation() {
    const hamburger = document.getElementById('hamburger');
    const navMenu = document.getElementById('navMenu');
    const navLinks = Array.from(document.querySelectorAll('.nav-link'));
    const sections = navLinks.map(link => document.querySelector(link.getAttribute('href'))).filter(Boolean);

    if (hamburger && navMenu) {
        hamburger.addEventListener('click', () => navMenu.classList.toggle('active'));
        navMenu.querySelectorAll('a').forEach(link => link.addEventListener('click', () => navMenu.classList.remove('active')));
    }

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                navLinks.forEach(link => link.classList.toggle('active', link.getAttribute('href') === '#' + entry.target.id));
            }
        });
    }, { threshold: 0.5 });

    sections.forEach(section => observer.observe(section));

    window.addEventListener('scroll', () => {
        document.getElementById('navbar').classList.toggle('scrolled', window.scrollY > 12);
    });
}

function escapeHtml(text) {
    if (text === null || text === undefined) return '';
    const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
    return String(text).replace(/[&<>"']/g, m => map[m]);
}