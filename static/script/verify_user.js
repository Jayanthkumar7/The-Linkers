document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector(".login-form");

    form.addEventListener("submit", async function (event) {
        event.preventDefault();

        const email = document.querySelector('input[placeholder="Email / Phone"]').value.trim();
        const password = document.querySelector('input[placeholder="Password"]').value.trim();

        // Validate inputs
        if (!validateEmail(email)) {
            alert("Please enter a valid email address.");
            return;
        }
        if (!validatePassword(password)) {
            alert("Password must be at least 6 characters long.");
            return;
        }

        const userdata = { email, password };

        try {
            const response = await fetch("/login_user", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(userdata),
            });

            const result = await response.json(); // Parse response JSON

            if (result.status === "success") {
                alert("Login Successful!");
                setTimeout(() => {
                    window.location.href = result.url; // Redirect user
                }, 1000);
            } else {
                alert("Error: Login Failed. Please try again!");
            }
        } catch (error) {
            console.error("Error Submitting form", error);
            alert("An error occurred. Please try again.");
        }
    });

    function validateEmail(email) {
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailPattern.test(email);
    }

    function validatePassword(password) {
        return password.length >= 6;
    }
});
