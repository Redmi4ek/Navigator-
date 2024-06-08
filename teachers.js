document.addEventListener("DOMContentLoaded", function() {
    // примеры
    const exampleTeachers = [
        {
            first_name: "John",
            last_name: "Doe",
            telegram_id: "@johndoe",
            school: "St. Mary's High School",
            phone_number: "1234567890"
        },
        {
            first_name: "Jane",
            last_name: "Smith",
            telegram_id: "@janesmith",
            school: "Greenwood Elementary",
            phone_number: "0987654321"
        },
        {
            first_name: "Alice",
            last_name: "Johnson",
            telegram_id: "@alicejohnson",
            school: "Maplewood Middle School",
            phone_number: "6789012345"
        }
    ];

    // Функция для отображения учителей тут с бд как нить подумайте))
    function displayTeachers(teachers) {
        const table = document.getElementById('teachers-table');
        teachers.forEach(teacher => {
            const row = table.insertRow();
            const firstNameCell = row.insertCell(0);
            const lastNameCell = row.insertCell(1);
            const telegramIdCell = row.insertCell(2);
            const schoolCell = row.insertCell(3);
            const phoneNumberCell = row.insertCell(4);

            firstNameCell.textContent = teacher.first_name;
            lastNameCell.textContent = teacher.last_name;
            telegramIdCell.textContent = teacher.telegram_id;
            schoolCell.textContent = teacher.school;
            phoneNumberCell.textContent = teacher.phone_number;
        });
    }

    displayTeachers(exampleTeachers);
});
