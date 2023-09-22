var pauseUpdates = false;

$(document).ready(function(){
    $("form").submit(function(event){
        event.preventDefault(); // Prevent the form from being submitted normally
        var formData = $(this).serialize(); // Get the form data
        $.ajax({
            type: 'POST',
            url: '/settings',
            data: formData,
            success: function(response){
                // If the request was successful, update the tabs
                updateTabs();
            }
        });
    });

    // Event handler for the pause button
    $('#pauseButton').click(function() {
        // Toggle the state of the pauseUpdates variable
        pauseUpdates = !pauseUpdates;

        // Change the text of the button to reflect the current state
        if (pauseUpdates) {
            $('#pauseButton').text('Resume');
        } else {
            $('#pauseButton').text('Pause');
        }
    });
});

function dataStream() {
    if (pauseUpdates) {
        // If updates are paused, don't do anything
        return;
    }
    $.get('/basicDataStream')
        .done(function (data) {
            // Check if the text box already has more than 100 lines
            var oldText = $('#liveDataBox').val();
            var oldTextLines = oldText.split('\n');
            if (oldTextLines.length >= 100) {
                // If the text box already has 100 lines,
                // remove the first line (the oldest one) before adding the new data
                oldTextLines.shift();
                oldText = oldTextLines.join('\n');
            }

            // Append the new data to the old text with a newline character in between
            var newText = oldText + '\n' + data;

            // Update the text box with the new data
            $('#liveDataBox').val(newText);

            // Scroll to the bottom of the text area
            $('#liveDataBox').scrollTop($('#liveDataBox')[0].scrollHeight);
        });
}

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



dataStream();
// Update line charts and tabs  every second
setInterval(function() {
    dataStream();
    updateTabs();
}, 1000);
