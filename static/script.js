document.addEventListener('DOMContentLoaded', function() {
    const cityInput = document.getElementById('city');

    cityInput.addEventListener('input', function() {
        const query = cityInput.value;
        if (query.length > 2) {
            fetch(`/autocomplete?query=${query}`)
                .then(response => response.json())
                .then(data => {
                    // handle autocomplete suggestions
                });
        }
    });
});
