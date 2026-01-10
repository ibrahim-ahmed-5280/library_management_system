// login.js

function login() {
    // 🐛 FIX 1: Corrected form ID to match the HTML
    const form = document.getElementById('login_admin_form'); 
    
    // Check if the form exists before continuing
    if (!form) {
        console.error("Form with ID 'login_admin_form' not found.");
        return;
    }

    // Use querySelector to find inputs/buttons within the form
    const inputs = form.querySelectorAll('input, button');
    
    // Get values
    const email = document.getElementById('emailaddress').value.trim();
    const password = document.getElementById('password').value.trim();

    // Get error/state elements
    // NOTE: Ensure 'email_error' and 'pass_error' DIVs are present in your HTML (they are now)
    const emailError = document.getElementById('email_error');
    const passError = document.getElementById('pass_error');
    const button = form.querySelector('button');
    const spinner = document.getElementById('spinner');
    const btnText = document.getElementById('btnText');

    // Reset error messages and form opacity
    [emailError, passError].forEach(err => {
        err.style.opacity = 0;
        err.innerHTML = "";
    });
    form.style.opacity = 1;

    // error message
    error_msg = document.getElementById('error_msg');
    error_msg.style.display = 'none';
    let hasError = false;

    // --- VALIDATION ---
    const emailPattern = /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/;
    if (!emailPattern.test(email)) {
        emailError.style.opacity = 1;
        emailError.innerHTML = "Please enter a valid email address.";
        hasError = true;
    }

    if (!password || password.length < 6) {
        passError.style.opacity = 1;
        passError.innerHTML = "Password must be at least 6 characters.";
        hasError = true;
    }

    if (hasError) return;

    // --- Disable inputs during submission (Loading State) ---
    button.disabled = true;
    spinner.classList.remove('d-none'); // Show spinner
    btnText.textContent = 'Logging...';
    form.style.opacity = 0.8;
    inputs.forEach(input => input.disabled = true);
    console.log(email, password)
    // --- Send data to backend ---
    fetch('/librarian/login_librarian', { // Use relative path
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
    })
    .then(res => {
        // Check if response is successful before trying to parse JSON
        if (!res.ok) {
            throw new Error(`Server responded with status: ${res.status}`);
        }
        return res.json();
    })
    .then(data => {
        if (data.success) {
            // Success: Redirect to admin dashboard
            window.location.href = '/librarian/dashboard_page';
        } else {
            // Failure: Display backend error messages
            // 💡 ENHANCEMENT: Use a single generic error for improved security
            if (data.error === 'invalid_email' || data.error === 'invalid_pass' || data.error === 'invalid_credentials') {
                // Display error message under the password field for generic credential errors
                error_msg.style.display = 'block'; 
                error_msg.innerHTML = data.message;
            } else {
                alert(data.message || "Login failed. Please try again.");
            }
        }
    })
    .catch(err => {
        console.error('Fetch Error:', err);
        alert('A network error occurred. Please check your connection.');
    })
    .finally(() => {
        // --- Always reset UI state ---
        button.disabled = false;
        spinner.classList.add('d-none'); // Hide spinner
        btnText.textContent = 'Log In';
        form.style.opacity = 1;
        inputs.forEach(input => input.disabled = false);
    });
}