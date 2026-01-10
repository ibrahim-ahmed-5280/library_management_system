function delete_copy(copy_id) {
    succ_msg = document.getElementById(`succ${copy_id}`)
    error_msg = document.getElementById(`error${copy_id}`)
    succ_msg.style.display = 'none';
    error_msg.style.display = 'none';

    // Get spinner and button if you have them
    const btn = document.getElementById(`delete_btn_${copy_id}`);
    const spinner = document.getElementById(`delete_spinner_${copy_id}`);
    btn_text = document.getElementById(`text_btn${copy_id}`)
    spinner.classList.remove('d-none');
    btn_text.textContent = 'Deleting...';

    fetch('/copies/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ copy_id: copy_id })
    })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                succ_msg.textContent = data.message;
                succ_msg.style.display = 'block';

                // Remove the row from table
                const row = document.getElementById(`copy_row_${copy_id}`);
                if (row) row.remove();

                // Close modal after 1 second
                setTimeout(() => {
                    const modalEl = document.getElementById(`deleteCopyModal${copy_id}`);
                    const modal = bootstrap.Modal.getInstance(modalEl);
                    if (modal) modal.hide();
                }, 1000);

            } else {
                error_msg.textContent = data.message;
                error_msg.style.display = 'block';
            }
        })
        .catch(() => {
            alert('Network error. Please try again.');
        })
        .finally(() => {
            spinner.classList.add('d-none');
            btn_text.textContent = 'Delete';
        });
}

function clearErrors(form) {
    form.querySelectorAll('.invalid-feedback').forEach(el => el.textContent = '');
    form.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
}

function showError(input, errorId, message) {
    input.classList.add('is-invalid');
    document.getElementById(errorId).textContent = message;
}

function update_copy_status(copy_id) {
    const form = document.getElementById(`status_copy_change${copy_id}`);
    clearErrors(form);

    const statusSelect = document.getElementById(`copy_status${copy_id}`);
    const statusValue = statusSelect.value.trim().toLowerCase();

    const succ_msg = document.getElementById(`copy_succ_msg${copy_id}`);
    const error_msg = document.getElementById(`copy_err_msg${copy_id}`);

    succ_msg.classList.add('d-none');
    error_msg.classList.add('d-none');

    let hasError = false;

    // ---------- Validation ----------
    const allowedStatuses = ['available', 'lost', 'damaged', 'maintenance'];

    if (!allowedStatuses.includes(statusValue)) {
        showError(statusSelect, `copy_status_error${copy_id}`, 'Please select a valid status.');
        hasError = true;
    }

    if (hasError) return;

    // ---------- Submit ----------
    fetch('/copies/update-status', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            copy_id: copy_id,
            status: statusValue
        })
    })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                succ_msg.textContent = data.message;
                succ_msg.classList.remove('d-none');

                // Update UI (optional: table row)
                const cell = document.getElementById(`copy_status_cell_${copy_id}`);
                if (cell) cell.textContent = statusValue.charAt(0).toUpperCase() + statusValue.slice(1);

                // Close modal after 1s
                setTimeout(() => {
                    const modalEl = document.getElementById(`updateCopyModal${copy_id}`);
                    const modal = bootstrap.Modal.getInstance(modalEl);
                    if (modal) modal.hide();
                }, 1000);
            } else {
                error_msg.textContent = data.message;
                error_msg.classList.remove('d-none');
            }
        })
        .catch(() => {
            error_msg.textContent = 'Network error. Please try again.';
            error_msg.classList.remove('d-none');
        });
}
