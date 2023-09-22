function updateTabs(){
    $.ajax({
        url: '/live_data',
        async: true, // Updated here
        dataType: 'json',
        success: function(data) {

            // Get the unit_ids from the data
            var unit_ids = Object.keys(data.series);

            // Fetch the updated labels
            $.get('/api/unit-labels', function(unit_labels) {

                // Sort the unit_ids in ascending order
                unit_ids.sort(function(a, b) {
                    return a - b;
                });

                // Clear the existing buttons
                var buttonContainer = document.getElementById('UnitbuttonContainer');
                buttonContainer.innerHTML = '';
                // Create a new button for each unit
                for (var i = 0; i < unit_ids.length; i++) {
                    (function (unit_id) {
                        // Add 2 to the unit ID
                        var updatedUnitID = parseInt(unit_id) + 2;
                        var button = document.createElement('button');
                        button.className = 'unitlinks';
                        button.id = 'unit' + unit_id + '_btn';
                        // Check if a custom label exists for this unit, else use default
                        var label = unit_labels[unit_id] ? unit_labels[unit_id] : 'Unit ' + updatedUnitID;
                        button.innerHTML = label;
                        button.onclick = function () {
                            window.location.href = '/unit/' + updatedUnitID;
                        };
                        buttonContainer.appendChild(button);
                    })(unit_ids[i]);
                }
            });
        }
    });
}

    document.getElementById('exportButton').addEventListener('click', function() {
        exportTableToCSV('table.csv');
    });

    function exportTableToCSV(filename) {
        var csv = [];
        var rows = document.querySelectorAll('table tr');

        for (var i = 0; i < rows.length; i++) {
            var row = [], cols = rows[i].querySelectorAll('td, th');

            for (var j = 0; j < cols.length; j++)
                row.push(cols[j].innerText);

            csv.push(row.join(','));
        }

        // Generate CSV file and trigger download
        var csvContent = csv.join('\n');
        var blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        var link = document.createElement('a');
        if (link.download !== undefined) {
            var url = URL.createObjectURL(blob);
            link.setAttribute('href', url);
            link.setAttribute('download', filename);
            link.style.visibility = 'hidden';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    }

updateTabs();

// Update line chart and pie chart every second
setInterval(function() {
    updateTabs();
}, 1000);
