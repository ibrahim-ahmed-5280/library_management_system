/* --- Direct Error Handling (No Bootstrap Classes) --- */

// Shows the red text below the input
function displayFieldError(errorId, message) {
    const errorDiv = document.getElementById(errorId);
    if (errorDiv) {
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
        errorDiv.style.color = '#dc3545'; // Red color
    }
}

// Hides the red text
function clearFieldError(errorId) {
    const errorDiv = document.getElementById(errorId);
    if (errorDiv) {
        errorDiv.textContent = '';
        errorDiv.style.display = 'none';
    }
}

/* --- Password Submission --- */
function submit_password_librarian() {
    const errorAlert = document.getElementById('passwordError');
    const successAlert = document.getElementById('passwordSuccess');
    const spinner = document.getElementById('spinner');
    const btnText = document.getElementById('btnText');
    const submitBtn = document.getElementById('changePasswordBtn');

    // 1. Reset everything
    errorAlert.classList.add('d-none');
    successAlert.classList.add('d-none');
    clearFieldError('oldPasswordFeedback');
    clearFieldError('newPasswordFeedback');
    clearFieldError('confirmPasswordFeedback');

    // 2. Gather values
    const oldPass = document.getElementById('oldPassword').value.trim();
    const newPass = document.getElementById('newPassword').value.trim();
    const confPass = document.getElementById('confirmPassword').value.trim();
    const librarainId = document.getElementById('librarian_id').value;

    // 3. Validation Logic
    let isValid = true;

    if (!oldPass) {
        displayFieldError('oldPasswordFeedback', 'Current password is required.');
        isValid = false;
    }
    if (newPass.length < 6) {
        displayFieldError('newPasswordFeedback', 'Minimum 6 characters required.');
        isValid = false;
    }
    if (newPass !== confPass) {
        displayFieldError('confirmPasswordFeedback', 'Passwords do not match.');
        isValid = false;
    }

    if (!isValid) return;

    // 4. UI Loading State
    spinner.classList.remove('d-none');
    btnText.textContent = 'Processing...';
    submitBtn.disabled = true;

    // 5. Fetch
    fetch('/change_password_librarian', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            librarian_id: librarainId,
            old_password: oldPass,
            new_password: newPass,
            confirm_password: confPass
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            successAlert.textContent = data.message;
            successAlert.classList.remove('d-none');
            document.getElementById('changePasswordForm').reset();
            setTimeout(() => location.reload(), 2000);
        } else {
            errorAlert.textContent = data.message;
            errorAlert.classList.remove('d-none');
            // If backend sends specific field errors
            if (data.errors) {
                if (data.errors.old_password) displayFieldError('oldPasswordFeedback', data.errors.old_password);
                if (data.errors.new_password) displayFieldError('newPasswordFeedback', data.errors.new_password);
            }
        }
    })
    .catch(err => {
        errorAlert.textContent = 'Network error.';
        errorAlert.classList.remove('d-none');
    })
    .finally(() => {
        spinner.classList.add('d-none');
        btnText.textContent = 'Change Password';
        submitBtn.disabled = false;
    });
}
function toggleFormVisibility() {
    const form = document.getElementById('formChange');
    form.classList.toggle('d-none');
}

function submit_changes() {
    const button = document.querySelector('#formChange .btn-with-spinner');
    const spinner = button.querySelector('.spinner-border');
    const buttonText = button.querySelector('.button-text');

    const succ_msg = document.getElementById("alert_success");
    const error_msg = document.getElementById("alert_error");

    // Show loading state
    spinner.classList.remove('d-none');
    buttonText.textContent = 'Processing...';
    button.disabled = true;

    succ_msg.style.display = 'none';
    error_msg.style.display = 'none';

    let isValid = true;

    // ================= Name validation =================
    const name = sanitizeInput(document.getElementById('name').value);
    if (!name) {
        showError('name', 'Name is required');
        isValid = false;
    } else {
        hideError('name');
    }

    // ================= Email validation =================
    const email = sanitizeInput(document.getElementById('type_email').value);
    if (!email) {
        showError('email', 'Email is required');
        isValid = false;
    } else if (!isValidEmail(email)) {
        showError('email', 'Please enter a valid email address');
        isValid = false;
    } else {
        hideError('email');
    }

    // Stop if validation fails
    if (!isValid) {
        spinner.classList.add('d-none');
        buttonText.textContent = 'Submit';
        button.disabled = false;
        return;
    }

    // ================= Prepare data =================
    const formData = {
        librarian_id: document.getElementById("librarian_id").value,
        name: name,
        email: email
    };

    console.log(formData);

    // ================= Send request =================
    fetch('/change_librarian_details', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status) {
            error_msg.style.display = 'none';
            succ_msg.style.display = 'block';
            succ_msg.innerHTML = data.message || 'success to update user details';

            setTimeout(() => {
                location.reload();
            }, 2000);
        } else {
            succ_msg.style.display = 'none';
            error_msg.style.display = 'block';
            error_msg.innerHTML = data.message || 'Failed to update user details';

            if (data.errors) {
                Object.entries(data.errors).forEach(([field, message]) => {
                    showError(field, message);
                });
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
        succ_msg.style.display = 'none';
        error_msg.style.display = 'block';
        error_msg.innerHTML = 'Network error occurred. Please try again.';
    })
    .finally(() => {
        spinner.classList.add('d-none');
        buttonText.textContent = 'Submit';
        button.disabled = false;
    });
}

// ================= Helpers =================
function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function sanitizeInput(input) {
    if (typeof input !== 'string') return input;

    return input.trim()
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#x27;");
}

function showError(fieldId, message) {
    const errorElement = document.getElementById(`${fieldId}Error`);
    if (errorElement) {
        errorElement.textContent = message;
        errorElement.style.display = 'block';
    }
}

function hideError(fieldId) {
    const errorElement = document.getElementById(`${fieldId}Error`);
    if (errorElement) {
        errorElement.style.display = 'none';
    }
}


