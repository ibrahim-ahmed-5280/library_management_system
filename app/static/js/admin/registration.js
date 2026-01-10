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

function showSucess(message) {
    const succ_msg = document.getElementById('succ_msg');
    succ_msg.innerHTML = message;
    succ_msg.style.display = 'block';
}

function showError(message) {
    const error_msg = document.getElementById('err_msg');
    error_msg.innerHTML = message;
    error_msg.style.display = 'block';
}

function hideError() {
    const error_msg = document.getElementById('err_msg');
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
function validateConfirmPassword(confirm,password, input, errorDiv) {
    resetInput(input, errorDiv);

    if (confirm != password) {
        setInvalid(input, errorDiv, "Confirm password must be same as password.");
        return false;
    }

    setValid(input);
    return true;
}


/* ===================== REGISTER ADMIN ===================== */
function register_admin() {
    hideError();
    const name = admin_name.value.trim();
    const email = admin_email.value.trim();
    const password = admin_password.value.trim();
    const confirm = confirm_password.value.trim();
    let error = false;

    if (!validateFullName(name, admin_name, admin_name_error)) error = true;
    if (!validateEmail(email, admin_email, admin_email_error)) error = true;
    if (!validatePassword(password, admin_password, admin_password_error)) error = true;
    if (!validateConfirmPassword(confirm,password, confirm_password, confirm_password_error)) error = true;

    if (error) return;

    disableForm(admin_form, admin_btn, admin_spinner, admin_btn_text, "Registering...");

    fetch("/admin/add_admin", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, email, password,confirm })
    })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                showSucess(data.message);
                setTimeout(function () {
                    location.reload();
                }, 1000); // <-- Set your desired delay here
                admin_form.reset();
            }
            else showError(data.message);
        })
        .finally(() => {
            enableForm(admin_form, admin_btn, admin_spinner, admin_btn_text, "Register Admin");
        });
}

/* ===================== REGISTER LIBRARIAN ===================== */
function register_librarian() {
    hideError();
    const name = lib_name.value.trim();
    const email = lib_email.value.trim();
    const password = lib_password.value.trim();
    const confirm = lib_confirm.value.trim();

    let error = false;

    if (!validateFullName(name, lib_name, lib_name_error)) error = true;
    if (!validateEmail(email, lib_email, lib_email_error)) error = true;
    if (!validatePassword(password, lib_password, lib_password_error)) error = true;
    if (!validateConfirmPassword(confirm,password, lib_confirm, lib_confirm_error)) error = true;

    if (error) return;

    disableForm(librarian_form, lib_btn, lib_spinner, lib_btn_text, "Registering...");

    fetch("/admin/add_librarian", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, email, password,confirm })
    })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                showSucess(data.message);
                setTimeout(function () {
                    location.reload();
                }, 1000); // <-- Set your desired delay here
                librarian_form.reset();
            }
            else showError(data.message);
        })
        .finally(() => {
            enableForm(librarian_form, lib_btn, lib_spinner, lib_btn_text, "Register Librarian");
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
    if (!validateConfirmPassword(confirm,password, member_confirm, member_confirm_error)) error = true;

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

/* ===================== REGISTER POLICY ===================== */
function register_policy() {

    // ---------- FORM ----------
    const form = document.getElementById("policy_form");

    // ---------- INPUTS ----------
    const nameInput  = document.getElementById("policy_name");
    const keyInput   = document.getElementById("policy_key");
    const valueInput = document.getElementById("policy_value");
    const descInput  = document.getElementById("description");

    // ---------- ERRORS ----------
    const nameError  = document.getElementById("policy_name_error");
    const keyError   = document.getElementById("policy_key_error");
    const valueError = document.getElementById("policy_value_error");
    const descError  = document.getElementById("description_error");

    // ---------- BUTTON ----------
    const btn     = document.getElementById("policy_btn");
    const spinner = document.getElementById("policy_spinner");
    const btnText = document.getElementById("policy_btn_text");

    hideError();

    const name  = nameInput.value.trim();
    const key   = keyInput.value.trim();
    const value = valueInput.value.trim();
    const desc  = descInput.value.trim();

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

    // Policy Key (snake_case recommended)
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
    disableForm(form, btn, spinner, btnText, "Registering...");

    fetch("/admin/add_policy", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            policy_name: name,
            policy_key: key,
            policy_value: value,
            description: desc
        })
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            showSucess(data.message);
            setTimeout(() => location.reload(), 1000);
            form.reset();
        } else {
            showError(data.message);
        }
    })
    .finally(() => {
        enableForm(form, btn, spinner, btnText, "Register Policy");
    });
}



