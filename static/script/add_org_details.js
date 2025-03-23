document.addEventListener("DOMContentLoaded", function () {
    document.querySelector(".registration-form").addEventListener("submit", async function (event) {
        event.preventDefault(); // Prevent default form submission

        // Collect form data
        const institutionName = document.querySelector("input[placeholder='Institution Name']").value.trim();
        const registrationNumber = document.querySelector("input[placeholder='Registration Number']").value.trim();
        const email = document.querySelector("input[placeholder='Email Address']").value.trim();
        const phone = document.querySelector("input[placeholder='Phone Number']").value.trim();
        const location = document.querySelector("input[placeholder='Location']").value.trim();
        const address = document.querySelector("input[placeholder='Address']").value.trim();
        const city = document.querySelector("input[placeholder='City']").value.trim();
        const pincode = document.querySelector("input[placeholder='Pincode']").value.trim();
        const orgType = document.querySelector(".org-type-select").value;
        const password = document.querySelector("input[placeholder='Set Password']").value.trim();
        const confirmPassword = document.querySelector("input[placeholder='Confirm Password']").value.trim();
        const termsChecked = document.querySelector("#terms").checked;

        // Basic validation
        if (!institutionName || !registrationNumber || !email || !phone || !location || !address || 
            !city || !pincode || !orgType || !password || !confirmPassword) {
            alert("Please fill in all fields.");
            return;
        }

        // Email validation
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailPattern.test(email)) {
            alert("Please enter a valid email address.");
            return;
        }

        // Phone number validation (only digits, length between 10-15)
        const phonePattern = /^[0-9]{10,15}$/;
        if (!phonePattern.test(phone)) {
            alert("Please enter a valid phone number (10-15 digits).");
            return;
        }

        // Pincode validation (only 6-digit numbers)
        const pincodePattern = /^[0-9]{6}$/;
        if (!pincodePattern.test(pincode)) {
            alert("Please enter a valid 6-digit pincode.");
            return;
        }

        // Password validation
        if (password.length < 6) {
            alert("Password must be at least 6 characters long.");
            return;
        }

        if (password !== confirmPassword) {
            alert("Passwords do not match.");
            return;
        }

        // Ensure terms are accepted
        if (!termsChecked) {
            alert("You must agree to the Terms and Conditions.");
            return;
        }

        // Prepare data for sending
        const formData = {
            institution_name: institutionName,
            registration_number: registrationNumber,
            email: email,
            phone: phone,
            location: location,
            address: address,
            city: city,
            pincode: pincode,
            org_type: orgType,
            password: password
        };

        try {
            // Send data to Flask backend
            const response = await fetch("/add_org_details", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(formData)
            });

            const result = await response.json();

            if (result.status === "success") {
                alert(result.message);
                window.location.href = result.url; // Redirect to login page
            } else {
                alert(result.message);
            }
        } catch (error) {
            console.error("Error:", error);
            alert("Registration failed. Please try again later.");
        }
    });
});
