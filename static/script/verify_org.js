document.addEventListener("DOMContentLoaded", function () {
    const loginForm = document.querySelector(".login-form");

    loginForm.addEventListener("submit", async function (event) {
        event.preventDefault();

        const emailOrRegInput = document.querySelector(".form-input[type='text']");
        const passwordInput = document.querySelector(".form-input[type='password']");

        const emailOrReg = emailOrRegInput.value.trim();
        const password = passwordInput.value.trim();

        // Input validation
        if (!emailOrReg || !password) {
            alert("Please enter both email/registration number and password.");
            return;
        }

        try {
            const response = await fetch("/check_org_details", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ email_or_reg: emailOrReg, password: password })
            });

            const result = await response.json();

            if (response.ok && result.status === "success") {
                alert("Login successful!");
                window.location.href = result.url; // Redirect to the specified page
            } else {
                alert(result.message || "Invalid credentials. Please try again.");
            }
        } catch (error) {
            console.error("Error during login:", error);
            alert("Something went wrong. Please try again later.");
        }
    });
});
