(function () {
    const THEME_KEY = "theme";

    function getStoredTheme() {
        try {
            const value = localStorage.getItem(THEME_KEY);
            return value === "dark" || value === "light" ? value : null;
        } catch (e) {
            return null;
        }
    }

    function setStoredTheme(theme) {
        try {
            localStorage.setItem(THEME_KEY, theme);
        } catch (e) {
            // Ignore storage errors (private mode, blocked storage, etc.)
        }
    }

    function getPreferredTheme() {
        const stored = getStoredTheme();
        if (stored) return stored;
        return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
    }

    function applyTheme(theme) {
        const root = document.documentElement;
        if (theme === "dark") {
            root.setAttribute("data-theme", "dark");
        } else {
            root.removeAttribute("data-theme");
        }
    }

    function syncToggleState(theme) {
        const toggle = document.getElementById("themeToggle");
        if (!toggle) return;
        const emoji = toggle.querySelector(".theme-emoji");

        const isDark = theme === "dark";
        toggle.setAttribute("aria-pressed", isDark ? "true" : "false");
        toggle.title = isDark ? "Switch to light mode" : "Switch to dark mode";
        if (emoji) {
            emoji.textContent = isDark ? "🌙" : "☀️";
        }
    }

    window.initTheme = function initTheme() {
        const theme = getPreferredTheme();
        applyTheme(theme);
        syncToggleState(theme);
    };

    window.toggleTheme = function toggleTheme() {
        const current = document.documentElement.getAttribute("data-theme") === "dark" ? "dark" : "light";
        const next = current === "dark" ? "light" : "dark";
        const thumb = document.querySelector("#themeToggle .theme-toggle-thumb");

        if (thumb) {
            thumb.classList.add("is-switching");
            setTimeout(function () {
                thumb.classList.remove("is-switching");
            }, 220);
        }

        applyTheme(next);
        setStoredTheme(next);
        syncToggleState(next);
    };

    document.addEventListener("DOMContentLoaded", function () {
        window.initTheme();

        const media = window.matchMedia("(prefers-color-scheme: dark)");
        const onSystemThemeChange = function (event) {
            if (getStoredTheme()) return;
            const nextTheme = event.matches ? "dark" : "light";
            applyTheme(nextTheme);
            syncToggleState(nextTheme);
        };

        if (typeof media.addEventListener === "function") {
            media.addEventListener("change", onSystemThemeChange);
        } else if (typeof media.addListener === "function") {
            media.addListener(onSystemThemeChange);
        }
    });
})();
