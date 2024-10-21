// forget.js
// Your Firebase configuration
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.13.2/firebase-app.js";
import { getAuth, sendPasswordResetEmail } from "https://www.gstatic.com/firebasejs/10.13.2/firebase-auth.js";
import { firebaseConfig } from "./firebaseConfig.js";

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);


// Function to send password reset email
document.getElementById('forgot-password-form').addEventListener('submit', function (e) {
    e.preventDefault();

    const email = document.getElementById('email').value;

    sendPasswordResetEmail(auth, email)
        .then(() => {
            // Show success alert
            document.getElementById('alert').innerHTML = "<p style='color:green;'>Password reset email sent! Check your inbox.</p>";

            // Wait a few seconds before redirecting to login page
            setTimeout(() => {
                window.location.href = '/login'; // Adjust this URL if needed
            }, 2000); // Redirect after 2 seconds
        })
        .catch((error) => {
            if (error.code === 'auth/user-not-found') {
                // Show error alert if email not found
                document.getElementById('alert').innerHTML = "<p style='color:red;'>No account found with this email address.</p>";
            } else {
                // General error
                document.getElementById('alert').innerHTML = "<p style='color:red;'>An error occurred. Please try again.</p>";
            }
        });
});