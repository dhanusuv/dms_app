document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('datasetForm');
    const tableBody = document.getElementById('datasetTableBody');

    // Fetch existing datasets and populate the table
    fetch('http://localhost:5000/datasets')
        .then(response => response.json())
        .then(data => {
            data.forEach(record => {
                addRowToTable(record);
            });
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
            addRowToTable(newRecord);
            form.reset();
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });

    function addRowToTable(record) {
        const newRow = document.createElement('tr');
        newRow.innerHTML = `
            <td>${record.dataset_name}</td>
            <td>${record.frequency}</td>
            <td>${record.source}</td>
            <td>${record.version}</td>
            <td>
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

    window.deleteRecord = function(id) {
        fetch(`http://localhost:5000/datasets/${id}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(deletedRecord => {
            const row = document.querySelector(`tr[data-id='${deletedRecord.id}']`);
            if (row) {
                row.remove();
            } else {
                console.warn(`Row with id ${deletedRecord.id} not found in the table.`);
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }
});
