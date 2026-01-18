function return_issue(issue_id, copy_id,requestId,dueDate,memberId) {
    // Get elements
    const statusSelect = document.getElementById(`return_issue_status${issue_id}`);
    console.log(statusSelect)
    const status = statusSelect.value.trim();
    const successMsg = document.getElementById(`return_issue_succ_msg${issue_id}`);
    const errorMsg = document.getElementById(`return_issue_err_msg${issue_id}`);
    const spinner = document.getElementById(`return_spinner_${issue_id}`);
    const btnText = document.getElementById(`text_btn${issue_id}`);

    // Reset messages
    successMsg.classList.add('d-none');
    errorMsg.classList.add('d-none');

    // Validation: only allow "returned" or "borrowed"
    if (status !== "returned" && status !== "borrowed") {
        errorMsg.textContent = "Invalid status selected.";
        errorMsg.classList.remove('d-none');
        return;
    }

    // Show spinner
    spinner.classList.remove('d-none');
    btnText.textContent = "Processing...";

    // Send data to Flask route
    fetch('/return_issue/update', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            issue_id: issue_id,
            status: status,
            copy_id: copy_id,
            request_id:requestId,
            due_date:dueDate,
            member_id:memberId
        })
    })
        .then(response => response.json())
        .then(data => {
            spinner.classList.add('d-none');
            btnText.textContent = "Return Issue";

            if (data.success) {
                successMsg.textContent = data.message || "Status updated successfully!";
                successMsg.classList.remove('d-none');
                setTimeout(() => {
                }, 1000);
            } else {
                errorMsg.textContent = data.message || "Failed to update status.";
                errorMsg.classList.remove('d-none');
            }
        })
        .catch(error => {
            spinner.classList.add('d-none');
            btnText.textContent = "Return Issue";
            errorMsg.textContent = "An error occurred. Try again.";
            errorMsg.classList.remove('d-none');
            console.error("Error:", error);
        });
}
