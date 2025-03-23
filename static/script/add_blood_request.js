document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector(".request-form");
    
    form.addEventListener("submit", async function (event) {
        event.preventDefault();
        
        const formData = {
            requester_name: document.querySelector("input[placeholder='Full Name']").value,
            rel_patient: document.querySelector(".rel-patient").value,
            patient_name: document.querySelector("input[placeholder=\"Patient's Name\"]").value,
            patient_age: document.querySelector("input[placeholder=\"Patient's Age\"]").value,
            blood_type: document.querySelector(".blood-group").value,
            reason: document.querySelector("input[placeholder='Reason for Blood Requirement']").value,
            is_emergency: document.querySelector("input[type='checkbox']").checked,
            hospital_name: document.querySelector("input[placeholder='Hospital Name']").value
        };
        
        try {
            const response = await fetch("/request_blood_details", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(formData)
            });
            
            const result = await response.json();
            if (response.ok) {
                alert("Blood request submitted successfully! Request ID: " + result.request_id);
                form.reset();
            } else {
                alert("Error: " + result.error);
            }
        } catch (error) {
            console.error("Request failed", error);
            alert("An error occurred while submitting your request.");
        }
    });
});
