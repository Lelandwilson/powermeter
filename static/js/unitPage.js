// Create a variable to store the chart
var linechart;
var pieChart;
var colors = [
  'rgb(255, 99, 132)',
  'rgb(75, 192, 192)',
  'rgb(255, 205, 86)',
  'rgb(201, 203, 207)',
  'rgb(54, 162, 235)',
  'rgb(153, 102, 255)', // Purple
  'rgb(255, 159, 64)',  // Orange
  'rgb(255, 99, 255)',  // Magenta
  'rgb(75, 0, 130)',    // Indigo
  'rgb(128, 0, 0)'      // Maroon
];


function updateDataSection(unitData) {
  var table = document.getElementById('dataSection');
  table.innerHTML = '';

  var rowData = [
    'Frequency: ' + unitData[unitData.length-1][0] + " Hz",
    'Samples per second: ' + unitData[unitData.length-1][1],
    'RMS Voltage: ' + unitData[unitData.length-1][2] + " V",
    'RMS Current: ' + unitData[unitData.length-1][3] + " mA",
    'Current Crest Factor: ' + unitData[unitData.length-1][4] + " CCF",
    'Theta: ' + unitData[unitData.length-1][5] + "°",
    'Apparent Power: ' + unitData[unitData.length-1][6] + " VA",
    'Real Power: ' + unitData[unitData.length-1][7] + " W",
    'Reactive Power: ' + unitData[unitData.length-1][8] + " VAR",
    'Power Factor: ' + unitData[unitData.length-1][9]
  ];

  rowData.forEach(function(row) {
    var tr = document.createElement('tr');
    var td = document.createElement('td');
    td.textContent = row;
    tr.appendChild(td);
    table.appendChild(tr);
  });
}


function updateChart() {
    var unit_id = window.location.pathname.split('/').pop();

    $.getJSON('/live_data')
        .done(function(data) {
            var unitData = data.series[unit_id-2];
            if (!unitData) {
                $('#LiveData_Chart').hide();
                $('#errorMessage').show().text('Data for Unit ' + unit_id + ' unavailable');
                console.log("No unit data: " + unit_id);
                return;
            }

            updateDataSection(unitData);

            var labels = data.labels;
            var datasets = [];

            var datasetLabels = ['Voltage RMS (V)', 'Current RMS (A)', 'Apparent Power (VA)', 'Real Power (W)', 'Reactive Power (VAR)'];

            var indices = [2, 3, 6, 7, 8];
            var maxValue = -Infinity;

            indices.forEach(function(index, i) {
                var dataset = {
                    label: datasetLabels[i],
                    data: unitData.map(function(item) {
                        var value;
                        if (datasetLabels[i] === 'Current RMS (A)') {
                            value = item[index] / 1000;
                        } else {
                            value = item[index];
                        }
                        if (value === -1 || isNaN(value)) {
                            return null;
                        }
                        return value;
                    }),
                    fill: false,
                    borderColor: colors[i],
                    lineTension: 0.1
                };
                datasets.push(dataset);

                var datasetMax = Math.max.apply(null, dataset.data.filter(value => value !== null));
                if (datasetMax > maxValue) {
                    maxValue = datasetMax;
                }
            });

            var adjustedMaxValue = maxValue * 1.2;

            if (!linechart) {
                var ctx = document.getElementById('LiveData_Chart').getContext('2d');
                linechart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: labels,
                        datasets: datasets
                    },
                    options: {
                        animation: {
                            duration: 0
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                max: adjustedMaxValue,
                                title: {
                                    display: false,
                                    text: 'Value'
                                }
                            },
                            x: {
                                display: false,
                                beginAtZero: true,
                                max: 100,
                                title: {
                                    display: true,
                                    text: 'Time (s)'
                                }
                            }
                        },
                        plugins: {
                            annotation: {
                                annotations: [{
                                    type: 'line',
                                    mode: 'vertical',
                                    scaleID: 'x',
                                    value: labels[labels.length - 1],
                                    borderColor: 'rgba(0,0,0,0.5)',
                                    borderWidth: 2,
                                    label: {
                                        content: datasetLabels.map(function(label, index) {
                                            return label + ': ' + datasets[index].data[datasets[index].data.length - 1];
                                        }).join('\n'),
                                        enabled: true,
                                        position: 'top'
                                    }
                                }]
                            }
                        }
                    }
                });

                var legendSection = document.createElement('div');
                legendSection.id = 'legendSection';
                legendSection.style.marginTop = '20px';
                legendSection.style.display = 'flex';
                legendSection.style.flexWrap = 'wrap';
                document.getElementById('chartContainer').appendChild(legendSection);
            } else {
                linechart.data.labels = labels;
                linechart.data.datasets = datasets;
                linechart.options.scales.y.max = adjustedMaxValue;
                linechart.update();
            }

            var legendSection = document.getElementById('legendSection');
            legendSection.innerHTML = '';
            datasets.forEach(function(dataset, i) {
                var legendItem = document.createElement('div');
                legendItem.style.marginRight = '10px';
                legendItem.style.fontSize = '14px';
                legendItem.style.lineHeight = '1.4';
                legendItem.style.display = 'flex';
                legendItem.style.alignItems = 'center';
                legendItem.innerHTML = '<span style="background-color: ' + colors[i] + '; width: 10px; height: 10px; display: inline-block; margin-right: 5px;"></span>' + datasetLabels[i] + ': ' + dataset.data[dataset.data.length - 1];
                legendSection.appendChild(legendItem);
            });
        })
        .fail(function() {
            $('#errorMessage').show().text('Data stream unavailable');
        });
}

function updatePieChart() {
    // Extract the unit_id from the URL
    var unit_id = window.location.pathname.split('/').pop();

    // Fetch the data for the specific unit_id
    $.getJSON('/live_data')
        .done(function(data) {
            // Prepare the data for the specific unit_id
            var unitData = data.series[unit_id-2]; //fix the indexing issue, where unit 2 is indexed 0

            if (!unitData) {
                // Handle the case when data for the unit is not available
                console.log("No unit data: " + unit_id);
                return;
            }

            // Prepare the chart data
            var labels = ['Real Power', 'Reactive Power'];
            var indices = [7, 8];

            // Fetch the necessary data for the pie chart
            var pieData = indices.map(index => unitData[unitData.length-1][index]);

            if (!pieChart) {
                var ctx = document.getElementById('LiveData_PieChart').getContext('2d');
                pieChart = new Chart(ctx, {
                    type: 'pie',
                    data: {
                        labels: labels,
                        datasets: [{
                            data: pieData,
                            backgroundColor: ['rgb(201, 203, 207)', 'rgb(54, 162, 235)']
                        }]
                    },
                    options: {
                        responsive: true,
                        animation: {
                            duration: 0 // turn off animation
                        }
                    }
                });
            } else {
                // If the chart already exists, update its data
                pieChart.data.datasets[0].data = pieData;
                pieChart.update();
            }
        })
        .fail(function() {
            // If the request fails, display an error message
            $('#errorMessage').show().text('Data stream unavailable');
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

updateChart();
updateTabs();
updatePieChart();

// Update line chart and pie chart every second
setInterval(function() {
    updateChart();
    updatePieChart();
    updateTabs();
}, 1000);
