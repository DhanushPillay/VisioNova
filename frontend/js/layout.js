/**
 * VisioNova Layout Manager v3.0
 * Forensic Intelligence Dashboard — injects header + sidebar
 */

const Layout = {
    init: function () {
        this.injectHeader();
        this.injectSidebar();
        this.highlightCurrentNav();
    },

    injectHeader: function () {
        const el = document.querySelector('header[data-inject], header:empty');
        if (!el) return;

        el.style.cssText = `
            display: flex;
            align-items: center;
            justify-content: space-between;
            height: 52px;
            padding: 0 24px;
            background: var(--header-bg);
            border-bottom: 1px solid var(--color-border);
            position: sticky;
            top: 0;
            z-index: 50;
            flex-shrink: 0;
        `;

        el.innerHTML = `
            <a href="homepage.html" style="display:flex;align-items:center;gap:10px;text-decoration:none;color:var(--color-text-main);">
                <div style="width:28px;height:28px;background:linear-gradient(135deg,var(--color-brand,#4B8EF5),var(--color-accent-success));clip-path:polygon(50% 0%,100% 25%,100% 75%,50% 100%,0% 75%,0% 25%);display:flex;align-items:center;justify-content:center;">
                    <span class="material-symbols-outlined" style="font-size:13px;color:#fff;">blur_on</span>
                </div>
                <span style="font-size:15px;font-weight:700;letter-spacing:-0.02em;">VisioNova</span>
                <span style="font-family:'Roboto Mono',monospace;font-size:10px;color:var(--color-accent-success);background:rgba(71,229,188,0.1);border:1px solid rgba(71,229,188,0.2);padding:1px 6px;">v2.1</span>
            </a>

            <nav style="display:flex;align-items:center;gap:2px;">
                <a class="nav-link" href="homepage.html" style="font-family:'Roboto Mono',monospace;font-size:11px;font-weight:500;color:var(--color-text-muted);text-decoration:none;padding:5px 14px;border:1px solid transparent;letter-spacing:0.04em;text-transform:uppercase;transition:all 0.15s;">Home</a>
                <a class="nav-link" href="AnalysisDashboard.html" style="font-family:'Roboto Mono',monospace;font-size:11px;font-weight:500;color:var(--color-text-muted);text-decoration:none;padding:5px 14px;border:1px solid transparent;letter-spacing:0.04em;text-transform:uppercase;transition:all 0.15s;">Analyze</a>
                <a class="nav-link" href="FactCheckPage.html" style="font-family:'Roboto Mono',monospace;font-size:11px;font-weight:500;color:var(--color-text-muted);text-decoration:none;padding:5px 14px;border:1px solid transparent;letter-spacing:0.04em;text-transform:uppercase;transition:all 0.15s;">Fact Check</a>
                <a class="nav-link" href="ReportPage.html" style="font-family:'Roboto Mono',monospace;font-size:11px;font-weight:500;color:var(--color-text-muted);text-decoration:none;padding:5px 14px;border:1px solid transparent;letter-spacing:0.04em;text-transform:uppercase;transition:all 0.15s;">Reports</a>
            </nav>

            <div style="display:flex;align-items:center;gap:12px;">
                <div style="display:flex;align-items:center;gap:6px;font-family:'Roboto Mono',monospace;font-size:10px;color:var(--color-accent-success);padding:4px 10px;border:1px solid rgba(71,229,188,0.2);background:rgba(71,229,188,0.08);">
                    <div style="width:6px;height:6px;background:var(--color-accent-success);border-radius:50%;animation:vn-pulse 2s infinite;"></div>
                    ONLINE
                </div>
                <button id="themeToggle" style="display:flex;align-items:center;gap:6px;padding:5px 12px;background:var(--color-bg-card);border:1px solid var(--color-border);color:var(--color-text-muted);cursor:pointer;font-family:'Roboto Mono',monospace;font-size:10px;text-transform:uppercase;letter-spacing:0.04em;transition:all 0.15s;" title="Toggle Theme">
                    <span class="material-symbols-outlined theme-icon-dark" style="font-size:14px;color:#FBBF24;">light_mode</span>
                    <span class="material-symbols-outlined theme-icon-light" style="font-size:14px;display:none;">dark_mode</span>
                    Theme
                </button>
            </div>
            <style>
                @keyframes vn-pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }
                .nav-link:hover { color: var(--color-text-main) !important; border-color: var(--color-border-hover) !important; background: var(--color-bg-panel) !important; }
            </style>
        `;
    },

    injectSidebar: function () {
        const el = document.querySelector('aside[data-inject], aside:empty');
        if (!el) return;

        el.style.cssText = `
            display: flex;
            flex-direction: column;
            align-items: center;
            width: 56px;
            background: var(--sidebar-bg);
            border-right: 1px solid var(--color-border);
            padding: 20px 0;
            gap: 4px;
            flex-shrink: 0;
            overflow: hidden;
            transition: width 0.25s ease;
            position: relative;
            z-index: 40;
        `;

        el.addEventListener('mouseenter', () => el.style.width = '200px');
        el.addEventListener('mouseleave', () => el.style.width = '56px');

        const linkStyle = `display:flex;align-items:center;gap:12px;width:100%;padding:11px 18px;text-decoration:none;color:var(--color-text-muted);font-size:12px;font-weight:500;white-space:nowrap;transition:all 0.15s;`;

        el.innerHTML = `
            <a class="sidebar-link" href="homepage.html" style="${linkStyle}">
                <span class="material-symbols-outlined" style="font-size:20px;flex-shrink:0;">add_circle</span>
                <span style="opacity:0;transition:opacity 0.2s;" class="sidebar-label">New Scan</span>
            </a>
            <div style="width:70%;height:1px;background:var(--color-border);margin:4px 0;"></div>
            <a class="sidebar-link" href="AnalysisDashboard.html" style="${linkStyle}">
                <span class="material-symbols-outlined" style="font-size:20px;flex-shrink:0;">dashboard</span>
                <span style="opacity:0;transition:opacity 0.2s;" class="sidebar-label">Dashboard</span>
            </a>
            <a class="sidebar-link" href="FactCheckPage.html" style="${linkStyle}">
                <span class="material-symbols-outlined" style="font-size:20px;flex-shrink:0;">shield</span>
                <span style="opacity:0;transition:opacity 0.2s;" class="sidebar-label">Fact Check</span>
            </a>
            <a class="sidebar-link" href="ReportPage.html" style="${linkStyle}">
                <span class="material-symbols-outlined" style="font-size:20px;flex-shrink:0;">description</span>
                <span style="opacity:0;transition:opacity 0.2s;" class="sidebar-label">Reports</span>
            </a>
            <style>
                .sidebar-link:hover { color: var(--color-text-main) !important; background: var(--color-bg-panel) !important; }
            </style>
        `;

        // Fade labels on hover via parent expand
        el.addEventListener('mouseenter', () => {
            el.querySelectorAll('.sidebar-label').forEach(l => l.style.opacity = '1');
        });
        el.addEventListener('mouseleave', () => {
            el.querySelectorAll('.sidebar-label').forEach(l => l.style.opacity = '0');
        });
    },

    highlightCurrentNav: function () {
        const current = window.location.pathname.split('/').pop();
        document.querySelectorAll('.nav-link').forEach(link => {
            if (link.getAttribute('href') === current) {
                link.style.color = 'var(--color-accent-success)';
                link.style.borderColor = 'rgba(71,229,188,0.3)';
                link.style.background = 'rgba(71,229,188,0.08)';
            }
        });
        document.querySelectorAll('.sidebar-link').forEach(link => {
            if (link.getAttribute('href') === current) {
                link.style.color = 'var(--color-accent-success)';
                link.style.background = 'rgba(71,229,188,0.08)';
            }
        });
    }
};

document.addEventListener('DOMContentLoaded', () => Layout.init());


// (duplicate removed - new Layout defined above)
