import { initializeApp, getApp } from "https://www.gstatic.com/firebasejs/10.13.2/firebase-app.js";
import { getAuth } from "https://www.gstatic.com/firebasejs/10.13.2/firebase-auth.js";
import { getStorage, ref, uploadBytes, getDownloadURL } from "https://www.gstatic.com/firebasejs/10.13.2/firebase-storage.js";
import { getFirestore, collection, doc, setDoc, updateDoc, arrayUnion, serverTimestamp } from "https://www.gstatic.com/firebasejs/10.13.2/firebase-firestore.js";
import { firebaseConfig } from "./firebaseConfig.js";



const app = initializeApp(firebaseConfig); 
//const app = getApp(firebaseConfig);
const auth = getAuth(app);
const storage = getStorage(app, "gs://plantpals-dab2c.appspot.com"); 
const db = getFirestore(app);

document.addEventListener('DOMContentLoaded', () => {
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        const textElement = card.querySelector('.card-text');
        const titleElement = card.querySelector('.truncated-title');
        
        const fullText = textElement.textContent;
        const truncatedText = fullText.length > 280 ? fullText.substring(0, 280) + '...' : fullText;
        textElement.textContent = truncatedText;

        const fullTitle = titleElement.textContent;
        const truncatedTitle = fullTitle.length > 50 ? fullTitle.substring(0, 50) + '...' : fullTitle;
        titleElement.textContent = truncatedTitle;

        card.addEventListener('click', () => {
            if (textElement.textContent === truncatedText) {
                textElement.textContent = fullText;
            } else {
                textElement.textContent = truncatedText;
            }

            if (titleElement.textContent === truncatedTitle) {
                titleElement.textContent = fullTitle;
            } else {
                titleElement.textContent = truncatedTitle;
            }
        });
    });
});

document.getElementById('create-post-form').addEventListener('submit', async (event) => {
  event.preventDefault(); // Prevent default form submission

  const journal_id = document.getElementById('journal_id').value;
  const title = document.getElementById('title').value;
  const content = document.getElementById('content').value;
  
  
  const photoFile = document.getElementById('photo').files[0];

  console.log("photoFile: " + photoFile);
  console.log("journal_id: " + journal_id);
  console.log("title: " + title);
  console.log("content: " + content);

  const postRef = doc(collection(db, 'posts'));
  await setDoc(postRef, {
    uid: auth.currentUser.uid,
    journal_id: journal_id,
    text: content,
    doc_id: postRef.id,
    title: title,
    time_created: serverTimestamp(),
    image_url: ""
});

  const postId = postRef.id;
  console.log("Document written with ID: ", postId);

  const journalRef = doc(db, "journals", journal_id);
  
  updateDoc(journalRef, { post_ids: arrayUnion(postId) }); // append postID to post_ids
  const postRefImg = doc(db, "posts", postId);


  if (photoFile) {
      const storageRef = ref(storage, `journal/${postId}.jpg`);
      console.log("storageRef: " + storageRef);
      try {
          
          uploadBytes(storageRef, photoFile).then((snapshot) => { 
              console.log('Uploaded a blob or file!');
              
              getDownloadURL(storageRef)
                  .then((url) => {
                      console.log('Image URL:', url);
                      console.log("postsRefImg: " + postRefImg);
                      // updates db with image_url
                      updateDoc(postRefImg, { image_url: url });

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
          
          
          
          alert('Post photo updated successfully.');
          location.reload();
      } catch (error) {
          alert(`Error updating Post photo: ${error.message}`); // remove alert
      }
  }
});
