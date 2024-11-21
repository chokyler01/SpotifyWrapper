document.addEventListener("DOMContentLoaded", function () {
    const deleteAccountForm = document.getElementById("delete-account-form");
    deleteAccountForm.addEventListener("submit", function (e) {
        if (!confirm("Are you sure you want to delete your account? This action cannot be undone.")) {
            e.preventDefault();
        }
    });
});
