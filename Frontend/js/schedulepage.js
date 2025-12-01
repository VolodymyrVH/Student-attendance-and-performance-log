const full_name_element = document.getElementById("full_name");
const fullNameDB = localStorage.getItem("full_name");
full_name_element.textContent = fullNameDB;

const tableBody = document.querySelector("#scheduleTable tbody");
const form = document.getElementById("lessonForm");

function toggleForm() {
    form.style.display = form.style.display === "block" ? "none" : "block";
}

async function submitLesson(event) {
    event.preventDefault();

    const teacher = document.getElementById("teacher").value;
    const subject = document.getElementById("subject").value;
    const date = document.getElementById("date").value;
    const time = document.getElementById("time").value;
    const room = document.getElementById("room").value;
    const description = document.getElementById("description").value;
    const lessonType = document.getElementById("lessonType").value;
    const groups = document.getElementById("groups").value.split(",").map(g => g.trim());

    const body = {
        teacher_name: teacher,
        subject_name: subject,
        lesson_date: date,
        time: time,
        room: room,
        topic: description,
        type: lessonType,
        groups: groups
    };

    try {
        const response = await fetch("http://127.0.0.1:8000/teacher/create_lesson", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body)
        });

        if (!response.ok) {
            alert("Не вдалося створити урок!");
            return;
        }

        await loadLessons();

        form.reset();
        form.style.display = "none";

    } catch (error) {
        console.error("Помилка створення уроку:", error);
    }
}

async function deleteRow(lessonId) {
    if (!confirm("Видалити урок?")) return;

    try {
        const response = await fetch(`http://127.0.0.1:8000/teacher/delete_lesson/${lessonId}`, {
            method: "DELETE"
        });

        if (!response.ok) {
            alert("Не вдалося видалити урок");
            return;
        }

        await loadLessons();

    } catch (error) {
        console.error("Помилка видалення:", error);
    }
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

async function loadLessons() {
    tableBody.innerHTML = "";

    try {
        const response = await fetch(`http://127.0.0.1:8000/teacher/lessons/${fullNameDB}`);

        if (!response.ok) {
            console.error("Не вдалося завантажити уроки");
            return;
        }

        const lessons = await response.json();

        lessons.forEach(lesson => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${lesson.teacher}</td>
                <td>${lesson.subject_name}</td>
                <td>${lesson.date}</td>
                <td>${lesson.time}</td>
                <td>${lesson.room}</td>
                <td>${lesson.type}</td>
                <td>${lesson.groups}</td>
                <td>${lesson.topic}</td>
                <td><button onclick="deleteRow(${lesson.lesson_id})">X</button></td>
            `;
            tableBody.appendChild(row);
        });

    } catch (error) {
        console.error("Помилка при завантаженні уроків:", error);
    }
}

window.onload = loadLessons;


const menuBtn = document.getElementById("menuBtn");
const sideMenu = document.getElementById("sideMenu");

menuBtn.addEventListener("click", () => {
    sideMenu.style.display = sideMenu.style.display === "block" ? "none" : "block";
});