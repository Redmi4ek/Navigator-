document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("registerForm").addEventListener("submit", async function (event) {
        event.preventDefault();
        
        const firstName = document.getElementById("firstName").value;
        const lastName = document.getElementById("lastName").value;

        const response = await fetch("http://127.0.0.1:8001/register", {  // Обновленный URL
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ first_name: firstName, last_name: lastName })
        });

        if (response.ok) {
            alert("Registration successful");
        } else {
            alert("Registration failed");
        }
    });
});
