function pay_fine(issue_id) {

    const successMsg = document.getElementById(`fine_succ_msg${issue_id}`);
    const errorMsg = document.getElementById(`fine_err_msg${issue_id}`);
    const spinner = document.getElementById(`fine_spinner_${issue_id}`);
    const btnText = document.getElementById(`fine_btn_text${issue_id}`);

    // Reset alerts
    successMsg.classList.add('d-none');
    errorMsg.classList.add('d-none');

    // Show spinner
    spinner.classList.remove('d-none');
    btnText.textContent = "Processing...";

    fetch('/librarian/pay_fine', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            issue_id: issue_id
        })
    })
    .then(response => response.json())
    .then(data => {

        spinner.classList.add('d-none');
        btnText.textContent = "Confirm";

        if (data.success) {
            successMsg.textContent = data.message || "Fine marked as paid successfully!";
            successMsg.classList.remove('d-none');

            // Refresh page to update status badge & button
            setTimeout(() => {
                window.location.reload();
            }, 800);

        } else {
            errorMsg.textContent = data.message || "Failed to mark fine as paid.";
            errorMsg.classList.remove('d-none');
        }
    })
    .catch(error => {

        spinner.classList.add('d-none');
        btnText.textContent = "Confirm";

        errorMsg.textContent = "An unexpected error occurred.";
        errorMsg.classList.remove('d-none');

        console.error("Error:", error);
    });
}
