function clearErrors(form) {
    form.querySelectorAll('.invalid-feedback').forEach(el => el.textContent = '');
    form.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
}

function showError(input, errorId, message) {
    input.classList.add('is-invalid');
    document.getElementById(errorId).textContent = message;
}

function update_request_status(request_id) {
    const form = document.getElementById(`request_form${request_id}`);
    clearErrors(form);

    const statusSelect = document.getElementById(`req_status${request_id}`);
    const noteField = document.getElementById(`req_note${request_id}`);
    const statusValue = statusSelect.value.trim().toLowerCase();
    const noteValue = noteField.value.trim();

    const succ_msg = document.getElementById(`req_succ_msg${request_id}`);
    const error_msg = document.getElementById(`req_err_msg${request_id}`);
    succ_msg.classList.add('d-none');
    error_msg.classList.add('d-none');

    let hasError = false;
    const allowedStatuses = ['pending','approved','rejected','reserved','completed','cancelled'];
    if (!allowedStatuses.includes(statusValue)) {
        showError(statusSelect, `req_status_error${request_id}`, 'Please select a valid status.');
        hasError = true;
    }

    if (hasError) return;

    fetch('/requests/update-status', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({
            request_id: request_id,
            status: statusValue,
            note: noteValue
        })
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            succ_msg.textContent = data.message;
            succ_msg.classList.remove('d-none');

            // update badge in table
            const cell = document.querySelector(`#request_row_${request_id} td:nth-child(5) span`);
            if (cell) cell.textContent = statusValue.charAt(0).toUpperCase() + statusValue.slice(1);

            setTimeout(()=>{
                const modalEl = document.getElementById(`updateRequestModal${request_id}`);
                const modal = bootstrap.Modal.getInstance(modalEl);
                if(modal) modal.hide();
            },1000);
        } else {
            error_msg.textContent = data.message;
            error_msg.classList.remove('d-none');
        }
    })
    .catch(()=>{
        error_msg.textContent = 'Network error. Please try again.';
        error_msg.classList.remove('d-none');
    });
}
