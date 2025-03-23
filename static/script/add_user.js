document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector(".registration-form");

    form.addEventListener("submit", async function (event) {
        event.preventDefault();

        const fullName = document.querySelector('input[placeholder="Full Name"]').value.trim();
        const email = document.querySelector('input[placeholder="Email"]').value.trim();
        const phone = document.querySelector('input[placeholder="Phone Number"]').value.trim();
        const dob = document.querySelector('input[placeholder="D.O.B"]').value;
        const gender = document.querySelector('.select-field').value;
        const bloodGroup = document.querySelector('.select-field.select-field-large').value;
        const address = document.querySelector('input[placeholder="Address"]').value.trim();
        const city = document.querySelector('input[placeholder="City"]').value.trim();
        const state = document.querySelector('input[placeholder="State"]').value.trim();
        const pin = document.querySelector('input[placeholder="Pin"]').value.trim();
        const password = document.querySelectorAll('input[placeholder="Password"]')[0].value;
        const confirmPassword = document.querySelectorAll('input[placeholder="Confirm Password"]')[0].value;
        const termsAccepted = document.getElementById("terms").checked;

        // ✅ Validate Required Fields
        if (!fullName || !email || !phone || !dob || !gender || !bloodGroup || !address || !city || !state || !pin || !password) {
            alert("All fields are required!");
            return;
        }

        // ✅ Validate Email & Password
        if (!validateEmail(email)) {
            alert("Please enter a valid email address.");
            return;
        }
        if (!validatePassword(password)) {
            alert("Password must be at least 6 characters long.");
            return;
        }
        if (password !== confirmPassword) {
            alert("Passwords do not match.");
            return;
        }
        if (!termsAccepted) {
            alert("You must accept the terms and conditions.");
            return;
        }

        // ✅ Prepare Data for Flask Route
        const userData = {
            fullName,
            email,
            phone,
            dob,
            gender,
            bloodGroup,
            address,
            city,
            state,
            pin,
            password,
        };

        try {
            const response = await fetch("/add_user", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(userData),
            });

            const result = await response.json(); // Extract JSON response

            if (response.ok && result.status === "success") {
                form.reset();
                alert("Registration successful!");
                window.location.href = result.url; // Redirect user to the next page
            } else {
                alert(`Error: ${result.message}`); // Show Flask error message
            }
        } catch (error) {
            console.error("Error submitting form:", error);
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
