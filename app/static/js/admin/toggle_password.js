function togglePassword(input_id,id="") {
    const password = document.getElementById(input_id);
    const icon = document.getElementById("eye_icon"+id);

    if (password.type === "password") {
        password.type = "text";
        icon.classList.replace("uil-eye", "uil-eye-slash");
    } else {
        password.type = "password";
        icon.classList.replace("uil-eye-slash", "uil-eye");
    }
}