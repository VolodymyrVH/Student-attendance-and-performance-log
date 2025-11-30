const tableBody = document.querySelector("#scheduleTable tbody");
    const form = document.getElementById("lessonForm");

    window.onload = function() {
        const saved = localStorage.getItem("schedule");
        if (saved) {
            tableBody.innerHTML = saved;
        }
    };

    function toggleForm() {
        form.style.display = form.style.display === "block" ? "none" : "block";
    }

    function submitLesson(event) {
        event.preventDefault();

        const teacher = document.getElementById("teacher").value;
        const subject = document.getElementById("subject").value;
        const date = document.getElementById("date").value;
        const time = document.getElementById("time").value;
        const room = document.getElementById("room").value;
        const description = document.getElementById("description").value;
        const lessonType = document.getElementById("lessonType").value;
        const groups = document.getElementById("groups").value;

        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${teacher}</td>
            <td>${subject}</td>
            <td>${date}</td>
            <td>${time}</td>
            <td>${room}</td>
            <td>${lessonType}</td>
            <td>${groups}</td>
            <td>${description}</td>
            <td><button onclick="deleteRow(this)">X</button></td>
        `;

        tableBody.appendChild(row);

        form.reset();
        form.style.display = "none";
    }

    function deleteRow(btn) {
        btn.parentElement.parentElement.remove();
    }

    function saveSchedule() {
        localStorage.setItem("schedule", tableBody.innerHTML);
        alert("Збережено!");
    }

    function clearSchedule() {
        if (confirm("Очистити розклад повністю?")) {
            tableBody.innerHTML = "";
            localStorage.removeItem("schedule");
        }
    }

    const menuBtn = document.getElementById("menuBtn");
    const sideMenu = document.getElementById("sideMenu");

    menuBtn.addEventListener("click", () => {
        sideMenu.style.display =
            sideMenu.style.display === "block" ? "none" : "block";
    });