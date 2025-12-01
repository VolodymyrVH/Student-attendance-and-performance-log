console.log("Test");

const form = document.getElementById("login-form");

form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const fullName = document.querySelector('input[name="full_name"]').value;
    const password = document.querySelector('input[name="password"]').value;

    const body = {
        full_name: fullName,
        password: password
    };

    try {
        const response = await fetch("http://127.0.0.1:8000/auth/login", {
            method: "POST",
            headers: { 
                "Content-Type": "application/json"
            },
            body: JSON.stringify(body)
        });

        if (!response.ok) {
            alert("Невірний логін або пароль");
            return;
        }

        const data = await response.json();

        localStorage.setItem("full_name", data.full_name);
        localStorage.setItem("token", data.token);
        localStorage.setItem("role", data.role);
        localStorage.setItem("user_id", data.user_id);

        window.location.href = "mainpage.html";

    } catch (error) {
        console.error(error);
        alert("Помилка з’єднання з сервером");
    }
});
