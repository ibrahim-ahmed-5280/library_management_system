function confirmCancel(requestId) {
    const alertDiv = document.getElementById(`cancelAlert${requestId}`);

    fetch(`/member/cancel_request/${requestId}`, { 
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            alertDiv.className = "alert alert-success mt-3";
            alertDiv.textContent = "Request cancelled successfully!";
        } else {
            alertDiv.className = "alert alert-danger mt-3";
            alertDiv.textContent = "Failed to cancel the request.";
        }

        // Optional: Close modal after 2 seconds
        setTimeout(() => {
            const modalEl = document.getElementById(`cancelModal${requestId}`);
            const modal = bootstrap.Modal.getInstance(modalEl);
            modal.hide();
            // Optionally remove the request row from the table
            const row = document.getElementById(`requestRow${requestId}`);
            if (row) row.remove();
        }, 2000);
    })
    .catch(err => {
        alertDiv.className = "alert alert-danger mt-3";
        alertDiv.textContent = "An error occurred!";
        console.error(err);
    });
}
