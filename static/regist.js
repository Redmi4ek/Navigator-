document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("registerForm").addEventListener("submit", async function (event) {
        event.preventDefault();

        const firstName = document.getElementById("first_name").value;
        const lastName = document.getElementById("last_name").value;
        const telegramId = document.getElementById("telegram_id").value;
        const school = document.getElementById("school").value;
        const phoneNumber = document.getElementById("phone_number").value;

        const response = await fetch("/register", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                first_name: firstName,
                last_name: lastName,
                telegram_id: telegramId,
                school: school,
                phone_number: phoneNumber
            })
        });

        if (response.ok) {
            alert("Registration successful");
        } else {
            alert("Registration failed");
        }
    });
});
