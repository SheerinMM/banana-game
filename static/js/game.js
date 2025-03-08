let currentQuestionId = null;
let lives = 3;
let score = 0;
let currentQuestion = 0;
const maxQuestions = 3; // Limit per level
let difficulty = "easy"; // Default difficulty
let startTime = Date.now(); // Timer to track response time
let timerInterval; // Timer reference
let secondsElapsed = 0;


function startTimer() {
    clearInterval(timerInterval); // Stop any existing timer
    secondsElapsed = 0;

    // Update timer every second
    timerInterval = setInterval(() => {
        secondsElapsed++;
        let minutes = Math.floor(secondsElapsed / 60);
        let seconds = secondsElapsed % 60;
        document.getElementById("timer").innerText = 
            (minutes < 10 ? "0" : "") + minutes + ":" + (seconds < 10 ? "0" : "") + seconds;
    }, 1000);
}


// ⏹️ Stop Timer
function stopTimer() {
    clearInterval(timerInterval);
}
 // Track start time

// Fetch a question from the backend
async function fetchQuestion(level) {
    try {
        const response = await fetch(`/api/questions?difficulty=${level}`);
        const data = await response.json();

        if (response.ok) {
            // Set the question_id dynamically
            document.getElementById("question_id").value = data.question_id;
            document.getElementById("question-img").src = data.image_url;

            console.log("Fetched question:", data);

            startTime = Date.now(); // Start timer for scoring
            startTimer(); // 🕒 Start the timer when a new question is fetched
        } else {
            alert("Failed to fetch question");
        }
    } catch (error) {
        console.error("Error fetching question:", error);
    }
}


// Submit the user's answer
async function submitAnswer() {
    const answer = document.getElementById("answer").value;
    const question_id = document.getElementById("question_id").value; // Get the question_id

    if (answer.trim() === "") {
        alert("Please enter an answer!");
        return;
    }

    if (!question_id) {
        alert("Question ID is missing!");
        return;
    }

    try {
        // POST request to check the answer
        const response = await fetch("/check_answer", {
            method: "POST",
            body: new URLSearchParams({
                answer: answer,
                question_id: question_id, // Send the question_id as well
            }),
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
            },
        });

        const data = await response.json();
        const logMessages = document.getElementById("log-messages");

        if (response.ok) {
            const timeTaken = Math.floor((Date.now() - startTime) / 1000); // Calculate time taken
            if (data.message.includes("Correct")) {
                score += 100 - timeTaken * 2; // Scoring logic
                logMessages.innerHTML += `<p style="color:green;">✅ Well done! Correct Answer. +${100 - timeTaken * 2} points</p>`;
            } else {
                decreaseLives();
                logMessages.innerHTML += `<p style="color:red;">❌ Wrong answer, try again!</p>`;
            }
        } else {
            logMessages.innerHTML += `<p style="color:orange;">⚠️ ${data.error || "An error occurred"}</p>`;
        }

        currentQuestion++;
        if (currentQuestion < maxQuestions && lives > 0) {
            fetchQuestion(difficulty);
            document.getElementById("answer").value = ""; // Clear input
        } else if (lives === 0) {
            logMessages.innerHTML += `<p style="color:red;">💀 Game Over! You ran out of lives!</p>`;
        } else {
            showScoreboard();
        }
    } catch (error) {
        console.error("Error:", error);
        alert("An error occurred. Please try again.");
    }
}

// Decrease hearts if the answer is wrong
function decreaseLives() {
    lives -= 1;
    let heartsContainer = document.getElementById("lives");
    heartsContainer.innerHTML = "❤️ ".repeat(lives);

    if (lives === 0) {
        alert("Game Over! Try again.");
        resetGame();
    }
}

// Update logs section
function updateLog(message) {
    let logContainer = document.getElementById("log-messages");
    logContainer.innerHTML += `<p>${message}</p>`;
}

// Fetch next question
function nextQuestion() {
    fetchQuestion(difficulty);
    document.getElementById("answer").value = "";
}

// Reset the game
function resetGame() {
    lives = 3;
    score = 0;
    currentQuestion = 0;
    document.getElementById("lives").innerHTML = "❤️ ❤️ ❤️";
    document.getElementById("log-messages").innerHTML = "";
    fetchQuestion(difficulty);
}

// Show scoreboard
function showScoreboard() {
    alert(`🎉 Level Complete! Your score: ${score}`);
    saveScore();
}

// Save score to the server
async function saveScore() {
    await fetch("/save_score", {
        method: "POST",
        body: new URLSearchParams({ difficulty: difficulty, score: score }),
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });
}

// Load first question on page load
document.addEventListener("DOMContentLoaded", () => {
    fetchQuestion(difficulty);
});


async function submitScore(score, difficulty, timeTaken) {
    try {
        const response = await fetch("/submit_score", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ score: score, difficulty: difficulty, time_taken: timeTaken })
        });

        const data = await response.json();
        if (response.ok) {
            console.log("Score submitted:", data.message);
        } else {
            console.error("Error:", data.error);
        }
    } catch (error) {
        console.error("Error submitting score:", error);
    }
}

// Call this function when the level ends
submitScore(50, "medium", 120);  // Example: Player scored 50 on Medium in 120 seconds

async function refreshScoreboard() {
    try {
        const response = await fetch("/scoreboard");
        const scoresHTML = await response.text();
        document.getElementById("scoreboard-container").innerHTML = scoresHTML;
    } catch (error) {
        console.error("Error refreshing scoreboard:", error);
    }
}

// Call this when scores are submitted
submitScore(50, "medium", 120).then(refreshScoreboard);
