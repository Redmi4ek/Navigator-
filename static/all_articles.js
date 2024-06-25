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
//     });
// }

//в этом файле должна быть логика получения статей с бд