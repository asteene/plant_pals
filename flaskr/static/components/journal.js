document.addEventListener('DOMContentLoaded', () => {
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        const textElement = card.querySelector('.card-text');
        const fullText = textElement.textContent;
        const truncatedText = fullText.length > 100 ? fullText.substring(0, 100) + '...' : fullText;

        textElement.textContent = truncatedText; 

        card.addEventListener('click', () => {
            if (textElement.textContent === truncatedText) {
                textElement.textContent = fullText; 
            } else {
                textElement.textContent = truncatedText; 
            }
        });
    });
});