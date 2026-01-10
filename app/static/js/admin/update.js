/* ===================== HELPERS ===================== */
function setInvalid(input, errorDiv, message) {
    input.classList.remove("is-valid");
    input.classList.add("is-invalid");
    errorDiv.innerHTML = message;
}

function setValid(input) {
    input.classList.remove("is-invalid");
    input.classList.add("is-valid");
}

function resetInput(input, errorDiv = null) {
    input.classList.remove("is-invalid", "is-valid");
    if (errorDiv) errorDiv.innerHTML = "";
}

function disableForm(form, button, spinner, btnText, text) {
    form.querySelectorAll("input, select, button").forEach(el => el.disabled = true);
    spinner.classList.remove("d-none");
    btnText.textContent = text;
    form.style.opacity = "0.7";
}

function enableForm(form, button, spinner, btnText, text) {
    form.querySelectorAll("input, select, button").forEach(el => el.disabled = false);
    spinner.classList.add("d-none");
    btnText.textContent = text;
    form.style.opacity = "1";
}

function showSucess(message, id) {
    const succ_msg = document.getElementById('succ_msg' + id);
    succ_msg.innerHTML = message;
    succ_msg.style.display = 'block';
}

function showError(message, id) {
    const error_msg = document.getElementById('err_msg' + id);
    error_msg.innerHTML = message;
    error_msg.style.display = 'block';
}

function hideError(id) {
    const error_msg = document.getElementById('err_msg' + id);
    error_msg.style.display = 'none';
}
/* ===================== COMMON VALIDATORS ===================== */
function validateFullName(name, input, errorDiv) {
    resetInput(input, errorDiv);

    const parts = name.split(" ").filter(Boolean);

    if (name.length < 9 || name.length > 60) {
        setInvalid(input, errorDiv, "Full name must be 9–60 characters.");
        return false;
    }
    if (parts.length < 3 || parts.length > 4) {
        setInvalid(input, errorDiv, "Full name must contain 3 or 4 parts.");
        return false;
    }
    if (!parts.every(p => /^[A-Za-z]{3,15}$/.test(p))) {
        setInvalid(input, errorDiv, "Each name part must be 3–15 letters only.");
        return false;
    }

    setValid(input);
    return true;
}

function validateEmail(email, input, errorDiv) {
    resetInput(input, errorDiv);
    const pattern = /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/;

    if (!pattern.test(email)) {
        setInvalid(input, errorDiv, "Enter a valid email address.");
        return false;
    }

    setValid(input);
    return true;
}

function validatePassword(password, input, errorDiv) {
    resetInput(input, errorDiv);

    if (password.length < 6 || password.length > 20) {
        setInvalid(input, errorDiv, "Password must be 6–20 characters.");
        return false;
    }

    setValid(input);
    return true;
}
function validateConfirmPassword(confirm, password, input, errorDiv) {
    resetInput(input, errorDiv);

    if (confirm != password) {
        setInvalid(input, errorDiv, "Confirm password must be same as password.");
        return false;
    }

    setValid(input);
    return true;
}


/* ===================== UPDATE LIBRARIAN AND ADMIN ===================== */
function update_user(user_id) {

    // Form
    const form = document.getElementById(`user_form${user_id}`);

    // Inputs
    const nameInput = document.getElementById(`user_name${user_id}`);
    const emailInput = document.getElementById(`user_email${user_id}`);
    const statusInput = document.getElementById(`user_status${user_id}`);

    // Errors
    const nameError = document.getElementById(`user_name_error${user_id}`);
    const emailError = document.getElementById(`user_email_error${user_id}`);
    const statusError = document.getElementById(`user_status_error${user_id}`);

    // Button elements
    const btn = document.getElementById(`user_btn${user_id}`);
    const spinner = document.getElementById(`user_spinner${user_id}`);
    const btnText = document.getElementById(`user_btn_text${user_id}`);

    hideError(user_id);

    const name = nameInput.value.trim();
    const email = emailInput.value.trim();
    const status = statusInput.value;

    let error = false;

    if (!validateFullName(name, nameInput, nameError)) error = true;
    if (!validateEmail(email, emailInput, emailError)) error = true;
    if (!['active', 'inactive'].includes(status)) {
        setInvalid(statusInput, errorDiv, "Status must be active or inactive");
        return false;
    }

    if (error) return;

    disableForm(form, btn, spinner, btnText, "Updating...");
    console.log(user_id, name, email, status)
    fetch("/admin/update_user", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            user_id: user_id,
            name: name,
            email: email,
            status: status
        })
    })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                showSucess(data.message, user_id);
                setTimeout(function () {
                    location.reload();
                }, 1000); // <-- Set your desired delay here
            } else {
                showError(data.message, user_id);
            }
        })
        .finally(() => {
            enableForm(form, btn, spinner, btnText, "Update User");
        });
}

/* ===================== UPDATE MEMBER USER ============================= */
function update_member(user_id) {

    // ---------- FORM ----------
    const form = document.getElementById(`user_form${user_id}`);

    // ---------- INPUTS ----------
    const nameInput = document.getElementById(`user_name${user_id}`);
    const emailInput = document.getElementById(`user_email${user_id}`);
    const typeInput = document.getElementById(`member_type${user_id}`);
    const startInput = document.getElementById(`member_start${user_id}`);
    const endInput = document.getElementById(`member_end${user_id}`);
    const statusInput = document.getElementById(`user_status${user_id}`);

    // ---------- ERRORS ----------
    const nameError = document.getElementById(`user_name_error${user_id}`);
    const emailError = document.getElementById(`user_email_error${user_id}`);
    const typeError = document.getElementById(`member_type_error${user_id}`);
    const startError = document.getElementById(`member_start_error${user_id}`);
    const endError = document.getElementById(`member_end_error${user_id}`);
    const statusError = document.getElementById(`user_status_error${user_id}`);

    // ---------- MESSAGES ----------
    const successMsg = document.getElementById(`succ_msg${user_id}`);
    const errorMsg = document.getElementById(`err_msg${user_id}`);

    // ---------- BUTTON ----------
    const btn = document.getElementById(`user_btn${user_id}`);
    const spinner = document.getElementById(`user_spinner${user_id}`);
    const btnText = document.getElementById(`user_btn_text${user_id}`);

    // Reset messages
    successMsg.style.display = "none";
    errorMsg.style.display = "none";

    const name = nameInput.value.trim();
    const email = emailInput.value.trim();
    const type = typeInput.value;
    const start = startInput.value;
    const end = endInput.value;
    const status = statusInput.value;

    let error = false;

    // ---------- VALIDATION ----------
    if (!validateFullName(name, nameInput, nameError)) error = true;
    if (!validateEmail(email, emailInput, emailError)) error = true;

    // Membership type
    resetInput(typeInput, typeError);
    if (!type) {
        setInvalid(typeInput, typeError, "Select membership type.");
        error = true;
    } else {
        setValid(typeInput);
    }

    // Status
    resetInput(statusInput, statusError);
    if (!['active', 'inactive'].includes(status)) {
        setInvalid(statusInput, statusError, "Status must be active or inactive.");
        error = true;
    } else {
        setValid(statusInput);
    }

    // ---------- DATE VALIDATION ----------
    resetInput(startInput, startError);
    resetInput(endInput, endError);

    const today = new Date();
    today.setHours(0, 0, 0, 0);

    const startDate = start ? new Date(start) : null;
    const endDate = end ? new Date(end) : null;

    if (!start) {
        setInvalid(startInput, startError, "Start date is required.");
        error = true;
    } else if (startDate < today) {
        setInvalid(startInput, startError, "Start date cannot be in the past.");
        error = true;
    } else {
        setValid(startInput);
    }

    if (!end) {
        setInvalid(endInput, endError, "End date is required.");
        error = true;
    } else if (endDate < today) {
        setInvalid(endInput, endError, "End date cannot be in the past.");
        error = true;
    } else {
        setValid(endInput);
    }

    if (start && end && endDate <= startDate) {
        setInvalid(endInput, endError, "End date must be after start date.");
        error = true;
    }

    if (error) return;

    // ---------- SUBMIT ----------
    disableForm(form, btn, spinner, btnText, "Updating...");

    fetch("/admin/update_member", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            user_id: user_id,
            name: name,
            email: email,
            membership_type: type,
            membership_start: start,
            membership_end: end,
            status: status
        })
    })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                successMsg.textContent = data.message;
                successMsg.style.display = "block";
                setTimeout(function () {
                    location.reload();
                }, 1000); // <-- Set your desired delay here
            } else {
                errorMsg.textContent = data.message;
                errorMsg.style.display = "block";
            }
        })
        .finally(() => {
            enableForm(form, btn, spinner, btnText, "Update User");
        });
}


function change_password_user(user_id) {

    // Form
    const form = document.getElementById(`password_form${user_id}`);

    // Inputs
    const passwordInput = document.getElementById(`user_password${user_id}`);
    const confirmInput = document.getElementById(`user_confirm${user_id}`);
    const userIdInput = document.getElementById(`id_pass${user_id}`);

    // Errors
    const passwordError = document.getElementById(`user_password_error${user_id}`);
    const confirmError = document.getElementById(`user_confirm_error${user_id}`);

    // Messages
    const successMsg = document.getElementById(`succ_msg_pass${user_id}`);
    const errorMsg = document.getElementById(`err_msg_pass${user_id}`);

    // Button elements
    const btn = document.getElementById(`user_btn_pass${user_id}`);
    const spinner = document.getElementById(`user_spinner_pass${user_id}`);
    const btnText = document.getElementById(`user_btn_pass_text${user_id}`);

    // Reset messages
    successMsg.classList.add("d-none");
    errorMsg.classList.add("d-none");

    const password = passwordInput.value.trim();
    const confirm = confirmInput.value.trim();
    const uid = userIdInput.value;

    let error = false;

    if (!validatePassword(password, passwordInput, passwordError)) error = true;
    if (!validateConfirmPassword(confirm, password, confirmInput, confirmError)) error = true;

    if (error) return;

    disableForm(form, btn, spinner, btnText, "Updating...");

    fetch("/admin/update_user_password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            user_id: uid,
            password: password,
            confirm: confirm
        })
    })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                successMsg.innerHTML = data.message;
                successMsg.classList.remove('d-none');
                setTimeout(function () {
                    location.reload();
                }, 1000); // <-- Set your desired delay here
            } else {
                errorMsg.classList.remove('d-none');
                errorMsg.innerHTML = data.message;
            }
        })
        .finally(() => {
            enableForm(form, btn, spinner, btnText, "Update Password");
        });
}


/* ===================== REGISTER MEMBER ===================== */
function register_member() {
    hideError();
    const name = member_name.value.trim();
    const email = member_email.value.trim();
    const password = member_password.value.trim();
    const confirm = member_confirm.value.trim();
    const type = member_type.value;
    const start = member_start.value;
    const end = member_end.value;

    let error = false;

    if (!validateFullName(name, member_name, member_name_error)) error = true;
    if (!validateEmail(email, member_email, member_email_error)) error = true;
    if (!validatePassword(password, member_password, member_password_error)) error = true;
    if (!validateConfirmPassword(confirm, password, member_confirm, member_confirm_error)) error = true;

    resetInput(member_type, member_type_error);
    if (!type) {
        setInvalid(member_type, member_type_error, "Select membership type.");
        error = true;
    } else setValid(member_type);

    resetInput(member_start, member_start_error);
    resetInput(member_end, member_end_error);

    // ---------------- DATE VALIDATION ----------------
    const today = new Date();
    today.setHours(0, 0, 0, 0); // normalize

    const startDate = start ? new Date(start) : null;
    const endDate = end ? new Date(end) : null;

    if (!start) {
        setInvalid(member_start, member_start_error, "Start date is required.");
        error = true;
    }
    else if (startDate < today) {
        setInvalid(member_start, member_start_error, "Start date cannot be in the past.");
        error = true;
    }
    else {
        setValid(member_start);
    }

    if (!end) {
        setInvalid(member_end, member_end_error, "End date is required.");
        error = true;
    }
    else if (endDate < today) {
        setInvalid(member_end, member_end_error, "End date cannot be in the past.");
        error = true;
    }
    else {
        setValid(member_end);
    }

    if (start && end) {
        if (endDate <= startDate) {
            setInvalid(member_end, member_end_error, "End date must be after start date.");
            error = true;
        }
    }


    if (error) return;

    disableForm(member_form, member_btn, member_spinner, member_btn_text, "Registering...");

    fetch("/admin/add_member", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            name,
            email,
            password,
            confirm,
            membership_type: type,
            membership_start: start,
            membership_end: end
        })
    })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                showSucess(data.message);
                setTimeout(function () {
                    location.reload();
                }, 1000); // <-- Set your desired delay here
                member_form.reset();
            }
            else showError(data.message);
        })
        .finally(() => {
            enableForm(member_form, member_btn, member_spinner, member_btn_text, "Register Member");
        });
}

function update_policy(policy_id) {

    // ---------- FORM ----------
    const form = document.getElementById(`policy_form${policy_id}`);

    // ---------- INPUTS ----------
    const nameInput = document.getElementById(`policy_name${policy_id}`);
    const keyInput = document.getElementById(`policy_key${policy_id}`);
    const valueInput = document.getElementById(`policy_value${policy_id}`);
    const descInput = document.getElementById(`description${policy_id}`);

    // ---------- ERRORS ----------
    const nameError = document.getElementById(`policy_name_error${policy_id}`);
    const keyError = document.getElementById(`policy_key_error${policy_id}`);
    const valueError = document.getElementById(`policy_value_error${policy_id}`);
    const descError = document.getElementById(`description_error${policy_id}`);

    // ---------- BUTTON ----------
    const btn = document.getElementById(`policy_btn${policy_id}`);
    const spinner = document.getElementById(`policy_spinner${policy_id}`);
    const btnText = document.getElementById(`policy_btn_text${policy_id}`);

    hideError(policy_id);

    const name = nameInput.value.trim();
    const key = keyInput.value.trim();
    const value = valueInput.value.trim();
    const desc = descInput.value.trim();

    let error = false;

    // ---------- VALIDATION ----------

    // Policy Name
    resetInput(nameInput, nameError);
    if (name.length < 3 || name.length > 100) {
        setInvalid(nameInput, nameError, "Policy name must be 3–100 characters.");
        error = true;
    } else {
        setValid(nameInput);
    }

    // Policy Key (snake_case)
    resetInput(keyInput, keyError);
    if (!/^[a-z_]{3,50}$/.test(key)) {
        setInvalid(
            keyInput,
            keyError,
            "Policy key must be lowercase letters and underscores only."
        );
        error = true;
    } else {
        setValid(keyInput);
    }

    // Policy Value
    resetInput(valueInput, valueError);
    if (!value) {
        setInvalid(valueInput, valueError, "Policy value is required.");
        error = true;
    } else {
        setValid(valueInput);
    }

    // Description
    resetInput(descInput, descError);
    if (desc.length < 5) {
        setInvalid(descInput, descError, "Description must be at least 5 characters.");
        error = true;
    } else {
        setValid(descInput);
    }

    if (error) return;

    // ---------- SUBMIT ----------
    disableForm(form, btn, spinner, btnText, "Updating...");

    fetch("/admin/update_policy", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            policy_id: policy_id,
            policy_name: name,
            policy_key: key,
            policy_value: value,
            description: desc
        })
    })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                showSucess(data.message,policy_id);
                setTimeout(() => location.reload(), 1000);
            } else {
                showError(data.message,policy_id);
            }
        })
        .finally(() => {
            enableForm(form, btn, spinner, btnText, "Update Policy");
        });
}



