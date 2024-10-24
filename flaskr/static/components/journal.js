document.addEventListener('DOMContentLoaded', () => {
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        const textElement = card.querySelector('.card-text');
        const titleElement = card.querySelector('.truncated-title');
        
        const fullText = textElement.textContent;
        const truncatedText = fullText.length > 100 ? fullText.substring(0, 100) + '...' : fullText;
        textElement.textContent = truncatedText;

        const fullTitle = titleElement.textContent;
        const truncatedTitle = fullTitle.length > 25 ? fullTitle.substring(0, 25) + '...' : fullTitle;
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