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

function uploadImage() {
  const form = document.getElementById("imageUploadForm");
  const formData = new FormData(form);

  fetch('{{ url_for("main.upload_image") }}', {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.status === "success") {
        document.getElementById("imageUrl").value = data.image_url;
        alert("Image uploaded successfully!");
      } else {
        alert("Image upload failed: " + data.message);
      }
    })
    .catch((error) => {
      console.error("Error uploading image:", error);
    });
}