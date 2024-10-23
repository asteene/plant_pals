import { initializeApp } from "https://www.gstatic.com/firebasejs/10.13.2/firebase-app.js";
import { getAuth, createUserWithEmailAndPassword } from "https://www.gstatic.com/firebasejs/10.13.2/firebase-auth.js";
import { getFirestore, doc, setDoc, serverTimestamp } from "https://www.gstatic.com/firebasejs/10.13.2/firebase-firestore.js";
import { firebaseConfig } from "./firebaseConfig.js";

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);

document.getElementById('signup-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    try {
        // Create user
        const userCredential = await createUserWithEmailAndPassword(auth, email, password); // is there a way to create user with username?
        const user = userCredential.user;// console.log this later to find more details and see if you can add display name here

        // Save user information in Firestore with expanded structure
        await setDoc(doc(db, "users", user.uid), {
            username: username,
            email: email,
            dateJoined: serverTimestamp(),
            UID: user.uid,  // Store UID as a field
            plants: [],  // Initialize an empty array for plants
            photoURL: "../static/components/signup.js" // add link to random default photo from the cloud

            // add photoURL and password
        });

        // Prepare for journals and posts in the future (optional: create a default journal document)
        // You can add this part when you're ready to initialize journal collections for users.

        // Get ID token and send it to server
        const idToken = await user.getIdToken();
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
        console.error(error.message);
        alert(error.message);
    }
});
