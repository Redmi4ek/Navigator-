document.getElementById('registerForm').addEventListener('submit', function(event) {
    event.preventDefault();

    //здесь вызывается isOwnPassword(), если возвращает true, то вызвается функция checkAllFields(). Если false, и выясняется что
    //юзер ввел пароль полученный по почте, то его редиректает на window.location.href = '/regist_teacher2', где он ставит свой.

    checkAllFields();
});

const checkAllFields = () => {
    //здесь просто проверяется заполнил ли юзер все поля
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;


    if (email&&password) {
        window.location.href = '/article_form'
        form.reset();
    } else {
        swal("Error", "Please fill in all fields.", "error");
    }
}
const isOwnPassword = () => {
    //некая логика которая проверяет введенный пароль с полученным на почту
    //если введенный пароль равен === паролю полученному на почте (reg_pass), то возвращает false, если не равен
    // (то есть ввел свой собственный пароль который он уже ставил на странице /regist_teacher2), возвращает true

    console.log('checks password')
}