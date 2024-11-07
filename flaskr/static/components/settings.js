import { initializeApp, getApp } from "https://www.gstatic.com/firebasejs/10.13.2/firebase-app.js";
import { getAuth, updateEmail, EmailAuthProvider, reauthenticateWithCredential, updatePassword, updateProfile } from "https://www.gstatic.com/firebasejs/10.13.2/firebase-auth.js";
import { getStorage, ref, uploadBytes, getDownloadURL } from "https://www.gstatic.com/firebasejs/10.13.2/firebase-storage.js";
import { doc, updateDoc } from "https://www.gstatic.com/firebasejs/10.13.2/firebase-firestore.js";
import { getFirestore } from "https://www.gstatic.com/firebasejs/10.13.2/firebase-firestore.js";
import { firebaseConfig } from "./firebaseConfig.js";



const app = initializeApp(firebaseConfig); // getApp instead
//const app = getApp(firebaseConfig);
const auth = getAuth(app);
const storage = getStorage(app, "gs://plantpals-dab2c.appspot.com"); // not sure if i can put this in github
const db = getFirestore(app);

// try rewriting functions like forget.js
// even though code looks somewhat valid, there is no change on firebase db or even storage. 


// Handle profile form submission
document.getElementById('profile-form').addEventListener('submit', async (event) => {
    event.preventDefault(); // Prevent default form submission
    console.log("hello");
    const newUsername = document.getElementById('username').value;
    const newEmail = document.getElementById('email').value;
    const photoFile = document.getElementById('photo').files[0];

    console.log("newUsername: " + newUsername);
    console.log("newEmail: " + newEmail);
    console.log("photoFile: " + photoFile);

    // Update the username - works
    try {
        await updateProfile(auth.currentUser, { displayName: newUsername }); 
        const userRef = doc(db, "users", auth.currentUser.uid); 
        await updateDoc(userRef, { username: newUsername }); 
        
        console.log("userRef: " + userRef);
        console.log("uid: " + auth.currentUser.uid);
        
    } catch (error) {
        alert(`Error updating username: ${error.message}`);
    }

    // Update the email - wont work because of email verification
    await updateEmail(auth.currentUser, newEmail);
    const userRef = doc(db, "users", auth.currentUser.uid);
    await updateDoc(userRef, { email: newEmail });
    // try {
    //     await updateEmail(auth.currentUser, newEmail);
    //     const userRef = doc(db, "users", auth.currentUser.uid);
    //     await updateDoc(userRef, { email: newEmail }); // update db give up for now and restructure settings to not do these features
    // } catch (error) {
    //     alert(`Error updating email: ${error.message}`);
    // }

    // Change profile photo - works
    if (photoFile) {
        const storageRef = ref(storage, `profile_photos/${auth.currentUser.uid}.jpg`);// is this path meant to be of where i want the image to be in the cloud or where it is on my local
        console.log("storageRef: " + storageRef);
        try {
            //await uploadBytes(storageRef, photoFile);
            // there is an alert error fix it. 
            uploadBytes(storageRef, photoFile).then((snapshot) => { //Blob
                console.log('Uploaded a blob or file!');
                
                getDownloadURL(storageRef)
                    .then((url) => {
                        console.log('Image URL:', url);
                        console.log("userRef: " + userRef);
                        // updates db with photoURL
                        updateDoc(userRef, { photoURL: url });
                        
                        // This is for downloading the image and displaying it on the page
                        // const xhr = new XMLHttpRequest();
                        // xhr.responseType = 'blob';
                        // xhr.onload = (event) => {
                        //     const blob = xhr.response;
                        // };
                        // xhr.open('GET', url);
                        // xhr.send();

                        // Update the photo preview
                        const img = document.getElementById('photo-preview'); // document.getElementById('photo-preview').src = url;
                        img.setAttribute('src', url);
                    })
                    .catch((error) => {
                        switch (error.code) {
                        case 'storage/object-not-found':
                            // File doesn't exist
                            break;
                        case 'storage/unauthorized':
                            // User doesn't have permission to access the object
                            break;
                        case 'storage/canceled':
                            // User canceled the upload
                            break;
                        // ...
                        case 'storage/unknown':
                            // Unknown error occurred, inspect the server response
                            break;
                        }
                    });

                    
              });
            
            
            
            alert('Profile photo updated successfully.');
        } catch (error) {
            alert(`Error updating profile photo: ${error.message}`); // remove alert
        }
    }
});

// Handle password form submission - works
document.getElementById('password-form').addEventListener('submit', async (event) => {
    event.preventDefault(); 

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
