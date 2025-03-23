  function connectRequest(button) {
      const requestId = button.getAttribute("data-request-id");
      const bloodBankId = button.getAttribute("data-blood-bank-id");

      fetch('/connect_request', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json'
          },
          body: JSON.stringify({
              request_id: requestId,
              blood_bank_id: bloodBankId
          })
      })
      .then(response => response.json())
      .then(data => {
          if (data.success) {
              alert("Request successfully sent!");
              button.innerText = "Requested"; 
              button.disabled = true;
          } else {
              alert("Error sending request!");
          }
      })
      .catch(error => console.error('Error:', error));
  }


  function filterRequests() {
    let selectedBloodGroup = document.getElementById("bloodGroupFilter").value.toLowerCase();
    let donorCards = document.querySelectorAll(".donor-card");

    donorCards.forEach(card => {
        let bloodGroupElement = card.querySelector(".donor-card__detail:nth-child(2)");
        let bloodGroup = bloodGroupElement ? bloodGroupElement.innerText.split(":")[1].trim().toLowerCase() : "";

        if (selectedBloodGroup === "" || bloodGroup === selectedBloodGroup) {
            card.style.display = "block";
        } else {
            card.style.display = "none";
        }
    });
}
