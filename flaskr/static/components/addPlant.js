// import { initializeApp } from "https://www.gstatic.com/firebasejs/10.13.2/firebase-app.js";
import { getFirestore, doc, getDoc, setDoc, updateDoc, arrayUnion, collection, serverTimestamp } from "https://www.gstatic.com/firebasejs/10.13.2/firebase-firestore.js";
import { getAuth } from "https://www.gstatic.com/firebasejs/10.13.2/firebase-auth.js";

// import { firebaseConfig } from "./firebaseConfig.js";

// Initialize Firebase
// const app = initializeApp(firebaseConfig);
// const db = getFirestore(app);

import { getAuth } from "https://www.gstatic.com/firebasejs/10.13.2/firebase-auth.js";

// Initialize Firebase Firestore
const db = getFirestore();
const auth = getAuth();

// API base URL (replace this with the actual API URL you are using)
const API_BASE_URL = 'https://trefle.io/api/v1/species'; // fill in with token
const API_TOKEN = process.env.API_KEY; // API_KEY is the name of the env variable for the token 

// Function to fetch plant data from the API
async function fetchPlantData(plantID) { // update with Alec once he has established the api in routes and reference that instead.
    const response = await fetch(`${API_BASE_URL}/${plantID}?token=${API_TOKEN}`);
    if (!response.ok) {
        throw new Error('Failed to fetch plant data');
    }
    const data = await response.json();
    return data;
}

// Function to add plant to Firestore and user's garden
async function addPlantToGarden(plantID) {
    try {
        const user = auth.currentUser;
        if (!user) {
            console.error('No user is currently logged in.');
            return;
        }

        // Firestore references
        const plantsCollection = collection(db, 'plants');
        const userDocRef = doc(db, 'users', user.uid);

        // Check if the plant already exists in the plants collection
        const plantDocRef = doc(plantsCollection, plantID);
        const plantDocSnap = await getDoc(plantDocRef);

        if (!plantDocSnap.exists()) {
            // Fetch plant data from the API if it doesn't exist
            const plantData = await fetchPlantData(plantID);

            // Add plant to Firestore
            const plantDetails = {
                commonName: plantData.common_name || 'Unknown',
                scientificName: plantData.scientific_name || 'Unknown',
                id: plantData.id || 'Unknown',
                imageURL: plantData.image || '',
            };
            await setDoc(plantDocRef, plantDetails);
            console.log(`Plant ${plantData.common_name} added to Firestore.`);
        } else {
            console.log(`Plant ${plantData.common_name} already exists in Firestore.`);
        }

        // Add plant to user's garden (array in user document)
        await updateDoc(userDocRef, {
            plants: arrayUnion(plantID) // Add the plant to the user's garden array
        });
        console.log(`Plant ${plantID} added to user's garden.`);
        /*
        // Create or update the user's journal for the plant
        const journalCollectionRef = collection(userDocRef, 'journals');
        const journalDocRef = doc(journalCollectionRef, plantName); // Use the plant name as the document ID for the journal

        // Create the journal for the plant if it doesn't exist
        const journalDocSnap = await getDoc(journalDocRef);
        if (!journalDocSnap.exists()) {
            const journalData = {
                title: plantName,
                tags: [], // Placeholder for tags array
                created_at: serverTimestamp(), // Timestamp when the journal is created
            };
            await setDoc(journalDocRef, journalData);
            console.log(`Journal for plant ${plantName} created.`);
        } else {
            console.log(`Journal for plant ${plantName} already exists.`);
        }

        // Add a temporary post to the journal's posts collection
        const postsCollectionRef = collection(journalDocRef, 'posts');
        const tempPostRef = doc(postsCollectionRef); // Auto-generate post ID
        const postData = {
            title: 'First Post for ' + plantName, // Placeholder title
            description: 'This is a temporary post for the plant.', // Placeholder description
            created_at: serverTimestamp(), // Timestamp when the post is created
            image_url: plantDocSnap.data().imageURL || '' // Use the image URL from the plant doc
        };

        // Add the post to the posts collection under the journal
        await setDoc(tempPostRef, postData);
        console.log(`Post added to journal for plant ${plantName}.`);
        */
    } catch (error) {
        console.error("Error adding plant to garden:", error.message);
    }
}

// Event listener for the plant selection (example, assuming there's a form)
document.getElementById('add-plant-form').addEventListener('submit', async(event) => {
    event.preventDefault();

    // Get the plant name from the form input
    const plantName = document.getElementById('plant-name').value;

    // Call the function to add plant to Firestore and user's garden
    await addPlantToGarden(plantName);
});

$('#plantModal').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget); // Button that triggered the modal
    var plantId = button.data('id'); // Extract info from data-* attributes
    var plantName = button.data('name');
    var plantDescription = button.data('description');

    // Update the modal's content
    var modal = $(this);
    modal.find('#modal-plant-id').val(plantId);
    modal.find('#plant-title').val(plantName);
    modal.find('#plant-description').val(plantDescription);
});

function submitPlantForm() {
    document.getElementById('plantForm').submit();
}