document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('articleForm');

    form.addEventListener('submit', function(event) {
        event.preventDefault(); // Предотвращаем стандартное поведение формы

        // Проверяем, что все обязательные поля заполнены
        const articleYear = document.getElementById('article_year').value;
        const articleTitle = document.getElementById('article_title').value;
        const link = document.getElementById('link').value;
        const journal = document.getElementById('journal').value

        if (articleYear && articleTitle && link && journal) {
            swal("Good job!", "You've successfully posted the article!", "success");

            //*** Здесь должна быть логика добавления статьи в базу данных. Пока ее нет ***

            form.reset(); // Очистить форму после успешного заполнения
        } else {
            swal("Please, fill all the fields!", "", "error");
        }
    });
});


