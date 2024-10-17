import { getAuth, updateEmail, updatePassword, updateProfile } from "https://www.gstatic.com/firebasejs/10.13.2/firebase-auth.js";
import { getStorage, ref, uploadBytes, getDownloadURL } from "https://www.gstatic.com/firebasejs/10.13.2/firebase-storage.js";
import { doc, updateDoc, getDoc } from "https://www.gstatic.com/firebasejs/10.13.2/firebase-firestore.js";

const auth = getAuth();
const storage = getStorage();

// Update Username
document.getElementById('update-username').addEventListener('click', async () => {
    const newUsername = document.getElementById('username').value;
    try {
        await updateProfile(auth.currentUser, { displayName: newUsername });
        alert('Username updated successfully.');
    } catch (error) {
        alert(error.message);
    }
});

// Update Email
document.getElementById('update-email').addEventListener('click', async () => {
    const newEmail = document.getElementById('email').value;
    try {
        await updateEmail(auth.currentUser, newEmail);
        alert('Email updated successfully.');
    } catch (error) {
        alert(error.message);
    }
});

// Update Password
document.getElementById('update-password').addEventListener('click', async () => {
    const newPassword = document.getElementById('password').value;
    try {
        await updatePassword(auth.currentUser, newPassword);
        alert('Password updated successfully.');
    } catch (error) {
        alert(error.message);
    }
});

// Change Profile Photo
document.getElementById('update-photo').addEventListener('click', async () => {
    const file = document.getElementById('profile-photo').files[0];
    if (!file) {
        alert('Please select a photo.');
        return;
    }

    const storageRef = ref(storage, `profile_photos/${auth.currentUser.uid}`);
    try {
        await uploadBytes(storageRef, file);
        const photoURL = await getDownloadURL(storageRef);
        await updateProfile(auth.currentUser, { photoURL });
        alert('Profile photo updated successfully.');
    } catch (error) {
        alert(error.message);
    }
});

// Search for users
document.getElementById('search-btn').addEventListener('click', async () => {
    const searchQuery = document.getElementById('search-user').value;
    const searchResults = document.getElementById('search-results');
    searchResults.innerHTML = '';

    try {
        // Implement Firestore query to search users by username
        const usersRef = doc(db, "users", searchQuery);
        const userDoc = await getDoc(usersRef);

        if (userDoc.exists()) {
            searchResults.innerHTML = `<li>${userDoc.data().username} - ${userDoc.data().email}</li>`;
        } else {
            searchResults.innerHTML = '<li>No users found.</li>';
        }
    } catch (error) {
        alert(error.message);
    }
});