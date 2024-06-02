document.getElementById('searchForm').addEventListener('submit', function(event) {
    event.preventDefault();

    let location = document.getElementById('location').value;
    let query = document.getElementById('query').value;

    fetch('/search', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ location: location, query: query }),
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('response').innerText = data.response;
        document.getElementById('weather').innerText = data.weather;
        document.getElementById('places').innerText = data.places;
    })
    .catch((error) => {
        console.error('Error:', error);
    });
});
