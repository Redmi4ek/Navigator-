// document.getElementById('load-articles').addEventListener('click', fetchData);

// function fetchData() {
//     fetch('/achievementsbd')
//         .then(response => {
//             if (!response.ok) {
//                 throw new Error(`HTTP error! status: ${response.status}`);
//             }
//             return response.json();
//         })
//         .then(data => displayTeachers(data.achievements));
// }

// function displayTeachers(achievements) {
//     const table = document.getElementById('articles-table');

//     // Clear the table
//     while (table.rows.length > 1) {
//         table.deleteRow(1);
//     }

//     achievements.forEach(achievement => {
//         const row = table.insertRow();
//         row.insertCell().textContent = achievement.year;
//         row.insertCell().textContent = achievement.title;
//         row.insertCell().textContent = achievement.journal;
//         row.insertCell().textContent = achievement.url;

        // Add delete icon
        // const deleteCell = row.insertCell();
        // const deleteIcon = document.createElement('i');
        // deleteIcon.className = 'fas fa-trash-alt';
        // deleteIcon.style.cursor = 'pointer';
        // deleteIcon.addEventListener('click', onDelete);
        // deleteCell.appendChild(deleteIcon);
        //
        // // Add edit icon
        // const editCell = row.insertCell();
        // const editIcon = document.createElement('i');
        // editIcon.className = 'fas fa-edit';
        // editIcon.style.cursor = 'pointer';
        // editIcon.addEventListener('click', onEdit);
        // editCell.appendChild(editIcon);
//     });

// }


//в этом файле должна быть логика получения статей с бд и возможность удалять и редактировавть их

const onDelete = () => {
    const deleteButton = document.getElementById('delete_button');

    //Логика удаления
}

const onEdit = () => {
    const editButton = document.getElementById('edit_button');

    //Логика редактирования
}