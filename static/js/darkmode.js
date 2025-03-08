// Function to apply dark mode if it's enabled in localStorage
function applyDarkMode() {
    const darkMode = localStorage.getItem('darkMode') === 'enabled';
    document.body.classList.toggle('dark-mode', darkMode);
}

// Apply dark mode on page load
document.addEventListener("DOMContentLoaded", function () {
    applyDarkMode();

    // Dark Mode Toggle Button
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    darkModeToggle.addEventListener('click', function () {
        const darkMode = document.body.classList.toggle('dark-mode');
        localStorage.setItem('darkMode', darkMode ? 'enabled' : 'disabled');
    });
});
