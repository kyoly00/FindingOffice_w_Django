document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('reservation-form');

    form.addEventListener('submit', function(event) {
        event.preventDefault();
        const formData = new FormData(form);
        const date = formData.get('date');
        const time = formData.get('time');
        const paymentMethod = formData.get('payment-method');

        // 여기서 가져온 데이터로 무언가를 할 수 있습니다 (예: 서버로 보내기)
        console.log('예약 날짜:', date);
        console.log('예약 시간:', time);
        console.log('결제 방식:', paymentMethod);
    });
});
// Get the modal
var modal = document.getElementById("myModal");

// Get the dialog
var dialog = document.getElementById("dialog");

// Get the <span> element that closes the modal and dialog
var span = document.getElementsByClassName("close");

// When the user clicks on the button, open the modal
document.getElementById("reservation-form").addEventListener("submit", function(event) {
    event.preventDefault(); // Prevent form submission
    var paymentMethod = document.getElementById("payment-method").value;
    if (paymentMethod === "credit") {
        // Show dialog for credit card info
        dialog.style.display = "block";
    } else if (paymentMethod === "paypal") {
        // Show modal for completion message
        modal.style.display = "block";
        document.getElementById("modal-text").innerText = "예약이 완료되었습니다.";
    }
});


// When the user clicks on <span> (x), close the modal and dialog
for (var i = 0; i < span.length; i++) {
  span[i].onclick = function() {
    modal.style.display = "none";
    dialog.style.display = "none";
  }
}

// When the user clicks anywhere outside of the modal or dialog, close it
window.onclick = function(event) {
  if (event.target == modal || event.target == dialog) {
    modal.style.display = "none";
    dialog.style.display = "none";
  }
}

// Submit credit card info
document.getElementById("submit-card-info").addEventListener("click", function() {
    var cardCompany = document.getElementById("card-company").value;
    var accountNumber = document.getElementById("account-number").value;
    // You can add further processing logic here, such as sending the data to a server
    // For demonstration, let's just close the dialog
    dialog.style.display = "none";
    // Show modal for completion message
    modal.style.display = "block";
    document.getElementById("modal-text").innerText = "예약이 완료되었습니다.";
});

document.getElementById("confirm-button").addEventListener("click", function() {
    // Redirect to another page
    window.location.href= redirectUrl; // 여기에 이동할 URL을 입력하세요.
});

// Initialize modal and dialog to hidden initially
modal.style.display = "none";
dialog.style.display = "none";

