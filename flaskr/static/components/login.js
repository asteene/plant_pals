import { getAuth, signInWithEmailAndPassword } from "https://www.gstatic.com/firebasejs/10.13.2/firebase-auth.js";

const auth = getAuth();

document.getElementById('login-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    try {
        const userCredential = await signInWithEmailAndPassword(auth, email, password);
        const idToken = await userCredential.user.getIdToken();

        // Send the token to the server for session creation
        const response = await fetch('/session', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ token: idToken })
        });

        const data = await response.json();

        if (data.status === 'success') {
            window.location.href = "/garden";
        } else {
            alert('Server authentication failed.');
        }
    } catch (error) {
        console.error("Firebase Auth Error:", error.message);

        // Handle errors here
        switch (error.code) {
            case 'auth/invalid-email':
                alert('Invalid email format.');
                break;
            case 'auth/user-disabled':
                alert('User account has been disabled.');
                break;
            case 'auth/user-not-found':
                alert('No user found with this email.');
                break;
            case 'auth/wrong-password':
                alert('Incorrect password.');
                break;
            default:
                alert(error.message);
                break;
        }
    }
});