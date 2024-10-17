import { initializeApp } from "https://www.gstatic.com/firebasejs/10.13.2/firebase-app.js";
import { getAuth, createUserWithEmailAndPassword } from "https://www.gstatic.com/firebasejs/10.13.2/firebase-auth.js";
import { getFirestore, doc, setDoc, serverTimestamp } from "https://www.gstatic.com/firebasejs/10.13.2/firebase-firestore.js";
import { firebaseConfig } from "./firebaseConfig.js"; 
// can you create multiple accounts with the same email? 
// store UID/document ID in document for later on in the development. 


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
        const userCredential = await createUserWithEmailAndPassword(auth, email, password);
        const user = userCredential.user;

        // Save user information in Firestore
        await setDoc(doc(db, "users", user.uid), {
            username: username,
            email: email,
            dateJoined: serverTimestamp()
        });

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