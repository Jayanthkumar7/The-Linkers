document.addEventListener("DOMContentLoaded", function () {
    const requestButtons = document.querySelectorAll(".request-button");

    requestButtons.forEach((button) => {
        button.addEventListener("click", function () {
            const bloodType = this.previousElementSibling.previousElementSibling.textContent.trim();
            const urgencyCheckbox = this.previousElementSibling.querySelector(".urgency-checkbox");
            const isEmergency = urgencyCheckbox.checked;

            // Prepare request data
            const requestData = {
                blood_type: bloodType,
                emergency: isEmergency
            };

            // Send request to Flask backend
            fetch("/add_org_request", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(requestData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert(`Request for ${bloodType} submitted successfully!`);
                } else {
                    alert(`Error: ${data.error}`);
                }
            })
            .catch(error => {
                console.error("Error submitting request:", error);
                alert("Failed to submit request. Please try again.");
            });
        });
    });
});
