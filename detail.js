document.addEventListener('DOMContentLoaded', () => {
    const table = document.getElementById('sourceRVUTable');
    const tableHeaders = document.getElementById('tableHeaders');
    const tableBody = table.querySelector('tbody');

    /**
     * Helper function to get query parameters from the URL.
     * @param {string} param - The name of the parameter to retrieve.
     * @returns {string|null} - The value of the parameter or null if not found.
     */
    function getQueryParam(param) {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get(param);
    }

    /**
     * Displays an error message in the table body.
     * @param {string} message - The error message to display.
     */
    function displayError(message) {
        tableHeaders.innerHTML = ''; // Clear headers
        tableBody.innerHTML = ''; // Clear body
        const errorRow = document.createElement('tr');
        const errorCell = document.createElement('td');
        errorCell.setAttribute('colspan', '100%');
        errorCell.textContent = message;
        errorCell.style.color = 'red'; // Optional: Red text for errors
        errorRow.appendChild(errorCell);
        tableBody.appendChild(errorRow);
    }

    /**
     * Fetches and populates dataset data based on the dataset ID.
     * @param {number} id - The dataset ID.
     */
    function fetchDatasetData(id) {
        fetch(`http://localhost:5000/dataset_table/${id}`)
            .then((response) => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then((data) => {
                console.log('Fetched dataset data:', data);

                // Clear table
                tableHeaders.innerHTML = '';
                tableBody.innerHTML = '';

                if (data.error) {
                    displayError(`Error: ${data.error}`);
                    return;
                }

                if (data.data.length > 0) {
                    // Populate table headers dynamically
                    data.columns.forEach((key) => {
                        const headerCell = document.createElement('th');
                        headerCell.textContent = key;
                        tableHeaders.appendChild(headerCell);
                    });

                    // Populate table rows dynamically
                    data.data.forEach((row) => {
                        const newRow = document.createElement('tr');
                        Object.values(row).forEach((value) => {
                            const cell = document.createElement('td');
                            cell.textContent = value;
                            newRow.appendChild(cell);
                        });
                        tableBody.appendChild(newRow);
                    });
                } else {
                    displayError('No data available');
                }
            })
            .catch((error) => {
                console.error('Error fetching dataset data:', error);
                displayError('Error loading data. Please try again later.');
            });
    }

    // Retrieve dataset ID from the URL
    const datasetId = getQueryParam('id');
    if (!datasetId) {
        displayError('No dataset ID provided in the URL');
        console.error('No dataset ID provided in the URL');
        return;
    }

    // Fetch and display the dataset data
    fetchDatasetData(datasetId);
});
