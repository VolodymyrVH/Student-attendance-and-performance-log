document.getElementById("userForm").addEventListener("submit", async function (event) {
    event.preventDefault();

    const data = {
        full_name: document.getElementById("full_name").value,
        password: document.getElementById("password").value,
        role: document.getElementById("role").value,
        group_name: document.getElementById("group_name").value || null
    };

    const response = await fetch("http://127.0.0.1:8000/admin/add_user", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    });

    const result = await response.json();
    alert(result.message || JSON.stringify(result));
});
