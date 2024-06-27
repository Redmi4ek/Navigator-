document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("registerForm").addEventListener("submit", async function (event) {
        event.preventDefault();

        const firstName = document.getElementById("first_name").value;
        const lastName = document.getElementById("last_name").value;
        const email = document.getElementById("email").value;
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
                email: email,
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
