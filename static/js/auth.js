// Import Firebase modules
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js";
import { getAuth, createUserWithEmailAndPassword, signInWithEmailAndPassword, signOut } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js";

// Firebase configuration (Replace with your actual config)
const firebaseConfig = {
    apiKey: "AIzaSyBVn1oNO_f2e9jcR2IDEFLId0uAfvKgoJA",
    authDomain: "bananagame-ff85b.firebaseapp.com",
    projectId: "bananagame-ff85b",
    storageBucket: "bananagame-ff85b.firebasestorage.app",
    messagingSenderId: "708378566695",
    appId: "1:708378566695:web:33e55c963fecf762c12e02"
  };

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

// 🔹 Signup function
document.getElementById("signup-form")?.addEventListener("submit", (e) => {
  e.preventDefault();
  const email = document.getElementById("signup-email").value;
  const password = document.getElementById("signup-password").value;

  createUserWithEmailAndPassword(auth, email, password)
    .then((userCredential) => {
      alert("Signup successful!");
      window.location.href = "/"; // Redirect to home
    })
    .catch((error) => {
      alert(error.message);
    });
});

// 🔹 Login function
document.getElementById("login-form")?.addEventListener("submit", (e) => {
  e.preventDefault();
  const email = document.getElementById("login-email").value;
  const password = document.getElementById("login-password").value;

  signInWithEmailAndPassword(auth, email, password)
    .then((userCredential) => {
      alert("Login successful!");
      window.location.href = "/"; // Redirect to home
    })
    .catch((error) => {
      alert(error.message);
    });
});

// 🔹 Logout function
document.getElementById("logout-btn")?.addEventListener("click", () => {
  signOut(auth)
    .then(() => {
      alert("Logged out successfully!");
      window.location.href = "/login"; // Redirect to login page
    })
    .catch((error) => {
      alert(error.message);
    });
});
