document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('datasetForm');
    const tableBody = document.getElementById('datasetTableBody');

    // Fetch existing datasets and populate the table
    fetch('http://localhost:5000/datasets')
        .then(response => {
            console.log('Fetching datasets...');
            return response.json();
        })
        .then(data => {
            console.log('Fetched datasets:', data);
            data.forEach(record => {
                addRowToTable(record);
            });
        })
        .catch(error => {
            console.error('Error fetching datasets:', error);
        });

    form.addEventListener('submit', (event) => {
        event.preventDefault();

        const datasetName = document.getElementById('datasetName').value;
        const frequency = document.getElementById('frequency').value;
        const source = document.getElementById('source').value;
        const version = document.getElementById('version').value;

        const data = {
            dataset_name: datasetName,
            frequency: frequency,
            source: source,
            version: version
        };

        fetch('http://localhost:5000/datasets', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(newRecord => {
            console.log('New record added:', newRecord);
            addRowToTable(newRecord);
            form.reset();
        })
        .catch(error => {
            console.error('Error posting new dataset:', error);
        });
    });

    function addRowToTable(record) {
        const newRow = document.createElement('tr');
        newRow.innerHTML = `
            <td>${record.id}</td>
            <td>${record.dataset_name}</td>
            <td>${record.frequency}</td>
            <td>${record.source}</td>
            <td>${record.version}</td>
            <td>
                <button onclick="window.location.href='details.html?id=${record.id}'">Select</button>
                <button onclick="editRecord(${record.id})">Edit</button>
                <button onclick="deleteRecord(${record.id})">Delete</button>
            </td>
        `;
        tableBody.appendChild(newRow);
    }

    window.editRecord = function(id) {
        // Implement the edit functionality if needed
        console.log('Edit record with id:', id);
    }

    window.selectRecord = function (id) {
        console.log('Select record with id:', id);
        // Open the details.html page with the record ID as a query parameter
        window.open(`details.html?id=${id}`, '_blank');
    };
    
    window.deleteRecord = function(id) {
        fetch(`http://localhost:5000/datasets/${id}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(deletedRecord => {
            console.log('Deleted record:', deletedRecord);
            const row = document.querySelector(`tr[data-id='${deletedRecord.id}']`);
            if (row) {
                row.remove();
            } else {
                console.warn(`Row with id ${deletedRecord.id} not found in the table.`);
            }
        })
        .catch(error => {
            console.error('Error deleting dataset:', error);
        });
    }

    // Method to fetch data from the PostgreSQL table and update the table on the web application page
    function fetchDataAndPopulateTable() {
        fetch('http://localhost:5000/datasets')
            .then(response => {
                console.log('Fetching datasets...');
                return response.json();
            })
            .then(data => {
                console.log('Fetched datasets:', data);
                tableBody.innerHTML = ''; // Clear existing table body
                data.forEach(record => {
                    addRowToTable(record);
                });
            })
            .catch(error => {
                console.error('Error fetching data:', error);
            });
    }

    // Call fetchDataAndPopulateTable to load data when the page loads
    fetchDataAndPopulateTable();
});
