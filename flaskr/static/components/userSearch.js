const searchInput = document.getElementById('user-search');
const resultsContainer = document.getElementById('search-results');

searchInput.addEventListener('input', async () => {
    const query = searchInput.value.trim();

    // Clear results if the input is empty
    if (!query) {
        resultsContainer.innerHTML = '';
        return;
    }

    try {
        const response = await fetch(`/search_users?query=${encodeURIComponent(query)}`);
        const users = await response.json();

        resultsContainer.innerHTML = ''; // Clear previous results

        if (users.length > 0) {
            users.forEach(user => {
                const listItem = document.createElement('li');
                listItem.className = 'list-group-item d-flex justify-content-between align-items-center';
                listItem.innerHTML = `
                    ${user.username}
                    <form method="POST" action="/add_friend/${user.id}">
                        <button type="submit" class="btn btn-primary">Add as Friend</button>
                    </form>
                `;
                resultsContainer.appendChild(listItem);
            });
        } else {
            resultsContainer.innerHTML = '<li class="list-group-item text-muted">No users found.</li>';
        }
    } catch (error) {
        console.error('Error fetching users:', error);
    }
});
