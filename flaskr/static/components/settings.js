import { initializeApp } from "https://www.gstatic.com/firebasejs/10.13.2/firebase-app.js";
import { getAuth, updateEmail, EmailAuthProvider, reauthenticateWithCredential, updatePassword, updateProfile } from "https://www.gstatic.com/firebasejs/10.13.2/firebase-auth.js";
import { getStorage, ref, uploadBytes, getDownloadURL } from "https://www.gstatic.com/firebasejs/10.13.2/firebase-storage.js";
import { doc, updateDoc } from "https://www.gstatic.com/firebasejs/10.13.2/firebase-firestore.js";
import { getFirestore } from "https://www.gstatic.com/firebasejs/10.13.2/firebase-firestore.js";
import { firebaseConfig } from "./firebaseConfig.js";

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const storage = getStorage();
const db = getFirestore();

// try rewriting functions like forget.js


// Handle profile form submission
document.getElementById('profile-form').addEventListener('submit', async(event) => {
    event.preventDefault(); // Prevent default form submission

    const newUsername = document.getElementById('username').value;
    const newEmail = document.getElementById('email').value;
    const photoFile = document.getElementById('photo').files[0];

    // Update the username
    try {
        await updateProfile(auth.currentUser, { displayName: newUsername }); // add this in signup
        const userRef = doc(db, "users", auth.currentUser.uid); // check routes.py to see how you did it there. maybe session_id?
        await updateDoc(userRef, { username: newUsername }); // update db 
    } catch (error) {
        alert(`Error updating username: ${error.message}`);
    }

    // Update the email
    try {
        await updateEmail(auth.currentUser, newEmail);
        const userRef = doc(db, "users", auth.currentUser.uid);
        await updateDoc(userRef, { email: newEmail }); // update db give up for now and restructure settings to not do these features
    } catch (error) {
        alert(`Error updating email: ${error.message}`);
    }

    // Change profile photo
    if (photoFile) {
        const storageRef = ref(storage, `profile_photos/${auth.currentUser.uid}`); // update later. 
        try {
            await uploadBytes(storageRef, photoFile);
            const photoURL = await getDownloadURL(storageRef); // update db 
            await updateProfile(auth.currentUser, { photoURL });

            // Update the photoURL in Firestore
            await updateDoc(userRef, { photoURL });

            // Update the photo preview
            document.getElementById('photo-preview').src = photoURL;
            alert('Profile photo updated successfully.');
        } catch (error) {
            alert(`Error updating profile photo: ${error.message}`);
        }
    }

    alert('Profile updated successfully.');
});

// // Update Password
// document.getElementById('update-password').addEventListener('click', async () => {  // not submit
//     const newPassword = document.getElementById('new-password').value;
//     try {
//         await updatePassword(auth.currentUser, newPassword);
//         alert('Password updated successfully.');
//     } catch (error) {
//         alert(`Error updating password: ${error.message}`);
//     }
// });


// // Handle password form submission
// document.getElementById('password-form').addEventListener('submit', async (event) => {
//     event.preventDefault(); // Prevent default form submission

//     const currentPassword = document.getElementById('current-password').value;
//     const newPassword = document.getElementById('new-password').value;

//     // Reauthenticate the user
//     const user = auth.currentUser;
//     const credential = EmailAuthProvider.credential(user.email, currentPassword);

//     try {
//         await reauthenticateWithCredential(user, credential);
//         await updatePassword(user, newPassword);
//         alert('Password updated successfully.');
//     } catch (error) {
//         alert(`Error updating password: ${error.message}`);
//     }
// });

document.getElementById('password-form').addEventListener('submit', async(event) => {
    event.preventDefault(); // Prevent the form from submitting normally

    const currentPassword = document.getElementById('current-password').value;
    console.log("currentPassword: " + currentPassword);
    const newPassword = document.getElementById('new-password').value;
    console.log("newPassword: " + newPassword);
    // Get the current user
    const auth = getAuth();
    console.log("auth: " + auth);
    const user = auth.currentUser;
    console.log("user: " + user);

    if (user) {
        const credential = EmailAuthProvider.credential(user.email, currentPassword);

        try {
            // Reauthenticate the user
            await reauthenticateWithCredential(user, credential);
            console.log("credential: " + credential);
            console.log("user: " + user);
            // Update the password
            await updatePassword(user, newPassword);
            console.log("newPassword: " + newPassword);
            // Show success alert
            alert('Password updated successfully.');
        } catch (error) {
            if (error.code === 'auth/wrong-password') {
                // Show error alert if the current password is incorrect
                document.getElementById('alert').innerHTML = "<p style='color:red;'>The current password is incorrect.</p>";
            } else {
                // General error
                document.getElementById('alert').innerHTML = `<p style='color:red;'>Error updating password: ${error.message}</p>`;
            }
        }
    } else {
        document.getElementById('alert').innerHTML = "<p style='color:red;'>No user is currently logged in.</p>";
    }
});


// Change Profile Photo
// document.getElementById('update-photo').addEventListener('click', async () => {
//     const file = document.getElementById('photo').files[0];
//     if (!file) {
//         alert('Please select a photo.');
//         return;
//     }

//     const storageRef = ref(storage, `profile_photos/${auth.currentUser.uid}`);
//     try {
//         await uploadBytes(storageRef, file);
//         const photoURL = await getDownloadURL(storageRef);
//         await updateProfile(auth.currentUser, { photoURL });

//         // Update the photoURL in Firestore
//         const userRef = doc(db, "users", auth.currentUser.uid);
//         await updateDoc(userRef, { photoURL });

//         alert('Profile photo updated successfully.');
//     } catch (error) {
//         alert(`Error updating profile photo: ${error.message}`);
//     }
// });