document.getElementById('load-teachers').addEventListener('click', fetchData);

function fetchData() {
    fetch('/teachersbd')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => displayTeachers(data.teachers));
}

function displayTeachers(teachers) {
    const table = document.getElementById('teachers-table');

    // Clear the table
    while (table.rows.length > 1) {
        table.deleteRow(1);
    }

    teachers.forEach(teacher => {
        const row = table.insertRow();
        row.insertCell().textContent = teacher.first_name;
        row.insertCell().textContent = teacher.last_name;
        row.insertCell().textContent = teacher.telegram_id;
        row.insertCell().textContent = teacher.school;
        row.insertCell().textContent = teacher.phone_number;
    });
}
