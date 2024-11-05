document.addEventListener("DOMContentLoaded", function () {
    const toggleButton = document.getElementById("dark-mode-toggle");
    const body = document.body;

    // Check for saved user preference
    const darkModePreference = localStorage.getItem("darkMode");

    if (darkModePreference === "enabled") {
        body.classList.add("dark-mode");
        toggleButton.textContent = "Light Mode";
    } else {
        toggleButton.textContent = "Dark Mode";
    }

    // Toggle dark mode on button click
    toggleButton.addEventListener("click", function () {
        body.classList.toggle("dark-mode");
        const isDarkModeEnabled = body.classList.contains("dark-mode");

        // Save user preference
        if (isDarkModeEnabled) {
            localStorage.setItem("darkMode", "enabled");
            toggleButton.textContent = "Light Mode";
        } else {
            localStorage.setItem("darkMode", "disabled");
            toggleButton.textContent = "Dark Mode";
        }
    });
});
