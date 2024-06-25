document.getElementById('registerForm').addEventListener('submit', function(event) {
    const form = document.getElementById('registerForm');
    event.preventDefault();

    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm_password').value;

    if (password !== confirmPassword) {
        swal("Passwords do not match", "", "error");
    } else {
        swal("Good job!", "Registration successful!", "success");

        setTimeout(() => {
            window.location.href = '/article_form'
        }, 1000);
        form.reset();
    }
    

    //некая логика записи в бд нового пароля и последующего входа по этому паролю
});