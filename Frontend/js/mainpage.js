const full_name_element = document.getElementById("full_name");
const fullNameDB = localStorage.getItem("full_name");

full_name_element.textContent = fullNameDB;

const menuBtn = document.getElementById("menuBtn")
const sideMenu = document.getElementById("sideMenu");

menuBtn.addEventListener("click", () => {
    sideMenu.style.display = 
        sideMenu.style.display === "block" ? "none" : "block";
});

