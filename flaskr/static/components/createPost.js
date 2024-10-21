import { getFirestore, doc, collection, addDoc, getDocs, serverTimestamp } from "https://www.gstatic.com/firebasejs/10.13.2/firebase-firestore.js";
import { getStorage, ref, uploadBytes, getDownloadURL } from "https://www.gstatic.com/firebasejs/10.13.2/firebase-storage.js";
import { getAuth } from "https://www.gstatic.com/firebasejs/10.13.2/firebase-auth.js";

// Initialize Firebase Firestore and Storage
const db = getFirestore();
const storage = getStorage();
const auth = getAuth();

// Function to fetch the user's journals (plants) from Firestore
async function fetchUserJournals() {
    const user = auth.currentUser;
    if (!user) {
        console.error("No user is logged in.");
        return [];
    }

    const journalsCollectionRef = collection(db, 'users', user.uid, 'journals');
    const querySnapshot = await getDocs(journalsCollectionRef);

    const journals = [];
    querySnapshot.forEach((doc) => {
        journals.push({ id: doc.id, ...doc.data() });
    });

    return journals;
}

// Function to upload an image to Firebase Storage and return the download URL
async function uploadImage(file) {
    const user = auth.currentUser;
    if (!user) {
        console.error('No user is currently logged in.');
        return;
    }

    const storageRef = ref(storage, `users/${user.uid}/posts/${file.name}`);
    const snapshot = await uploadBytes(storageRef, file);
    const downloadURL = await getDownloadURL(snapshot.ref);
    return downloadURL;
}

// Function to create a post for the selected journal (plant)
async function createPost(plantName, description, images) {
    const user = auth.currentUser;
    if (!user) {
        console.error("No user is logged in.");
        return;
    }

    const journalDocRef = doc(db, 'users', user.uid, 'journals', plantName);
    const postsCollectionRef = collection(journalDocRef, 'posts');

    // Upload images and get their URLs
    const imageURLs = [];
    for (const image of images) {
        const imageURL = await uploadImage(image);
        imageURLs.push(imageURL);
    }

    // Create post document in Firestore
    const postData = {
        title: `Post for ${plantName}`,
        description: description,
        created_at: serverTimestamp(),
        image_urls: imageURLs
    };

    await addDoc(postsCollectionRef, postData);
    console.log(`Post added to journal for plant ${plantName}.`);
}

// Event listener for the form submission
document.getElementById('create-post-form').addEventListener('submit', async (event) => {
    event.preventDefault();

    const plantName = document.getElementById('plant-select').value;
    const description = document.getElementById('description').value;
    const imageFiles = document.getElementById('image-upload').files;

    if (plantName && description && imageFiles.length > 0) {
        await createPost(plantName, description, imageFiles);
        console.log('Post created successfully!');
    } else {
        console.error('Please fill out all fields and upload an image.');
    }
});

// Function to populate the plant dropdown with user's journals
async function populatePlantDropdown() {
    const plantSelect = document.getElementById('plant-select');
    const journals = await fetchUserJournals();

    journals.forEach(journal => {
        const option = document.createElement('option');
        option.value = journal.id;
        option.text = journal.title;
        plantSelect.appendChild(option);
    });
}

// Call populatePlantDropdown when the page loads
window.onload = populatePlantDropdown;
