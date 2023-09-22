// Create a variable to store the chart
var chart;
var unitDataGlobal; // Global storage for unit data
var showCurrentRMS = true; // Switch to control data display

var sumChart;
var showCurrentRMSSum = true;

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

function processData(data) {
    var unit_ids = Object.keys(data.series);
    unitDataGlobal = unit_ids.map(unit_id => data.series[unit_id]);
}
function sumData(unitDataGlobal, index) {
    var length = unitDataGlobal[0].length;
    var sumData = [];
    for (var i = 0; i < length; i++) {
        var sum = 0;
        unitDataGlobal.forEach(function(unitData) {
            if (unitData[i] !== undefined && unitData[i][index] !== undefined) {
                sum += unitData[i][index] / (index == 3 ? 1000 : 1);
            }
        });
        sumData.push(sum);
    }
    // console.log(sumData)
    return sumData;
}

function updateChart() {
    if (!unitDataGlobal) return;

    var labels = unitDataGlobal[0].map(item => item[0]);
    var datasets = [];

    var datasetLabels = ['Current RMS (A)', 'Apparent Power (VA)'];
    var indices = [3, 6];

    var maxValue = 0;

    unitDataGlobal.forEach(function(unitData, unit_id) {
        var index = showCurrentRMS ? indices[0] : indices[1];
        var dataset = {
            label: 'Unit ' + (unit_id + 2) + ': ' + datasetLabels[showCurrentRMS ? 0 : 1],
            data: unitData.map(function(item) {
                var value = item[index];
                if (value === -1 || isNaN(value)) {
                    return null;
                }
                value = value / (showCurrentRMS ? 1000 : 1);
                if (value > maxValue) {
                    maxValue = value;
                }
                return value;
            }),
            fill: false,
            borderColor: colors[unit_id % colors.length],
            lineTension: 0.1
        };
        datasets.push(dataset);
    });

    if (!chart) {
        var ctx = document.getElementById('LiveData_Chart').getContext('2d');
        chart = new Chart(ctx, {
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
                        max: maxValue * 1.2,
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
                }
            }
        });

        var button = document.createElement('button');
        button.id = 'switchButton';
        button.className = 'btn btn-primary';
        button.style.marginTop = '20px';
        button.style.display = 'block';
        button.style.margin = 'auto';
        button.onclick = function() {
            showCurrentRMS = !showCurrentRMS;
            updateChart();
        };
        document.getElementById('chartContainer').appendChild(button);

        var legendSection = document.createElement('div');
        legendSection.id = 'legendSection';
        legendSection.style.marginTop = '20px';
        legendSection.style.display = 'flex';
        legendSection.style.flexWrap = 'wrap';
        document.getElementById('chartContainer').appendChild(legendSection);
    } else {
        chart.data.labels = labels;
        chart.data.datasets = datasets;
        chart.options.scales.y.max = maxValue * 1.2;
        chart.update();
    }

    document.getElementById('switchButton').innerHTML = 'Show ' + (showCurrentRMS ? 'Apparent Power (VA)' : 'Current RMS (A)');
    document.querySelector('h3.text-center').innerHTML = 'Live Readings: ' + (showCurrentRMS ? 'Current RMS (A)' : 'Apparent Power (VA)');

    var legendSection = document.getElementById('legendSection');
    legendSection.innerHTML = '';
    datasets.forEach(function(dataset, i) {
        var legendItem = document.createElement('div');
        legendItem.style.marginRight = '10px';
        legendItem.style.fontSize = '14px';
        legendItem.style.lineHeight = '1.4';
        legendItem.style.display = 'flex';
        legendItem.style.alignItems = 'center';
        legendItem.innerHTML = '<span style="background-color: ' + colors[i % colors.length] + '; width: 10px; height: 10px; display: inline-block; margin-right: 5px;"></span>' + dataset.label + ': ' + dataset.data[dataset.data.length - 1];
        legendSection.appendChild(legendItem);
    });
}

function updateSumChart() {
    if (!unitDataGlobal) return;

    var labels = unitDataGlobal[0].map(item => item[0]);
    var datasets = [];

    var datasetLabels = ['Current RMS (A)', 'Apparent Power (VA)'];
    var indices = [3, 6];

    var index = showCurrentRMSSum ? indices[0] : indices[1];
    var dataset = {
        label: 'Total ' + datasetLabels[showCurrentRMSSum ? 0 : 1],
        data: sumData(unitDataGlobal, index),
        fill: false,
        borderColor: colors[0],
        lineTension: 0.1
    };
    datasets.push(dataset);


    // console.log(unitDataGlobal)

    var maxValue = Math.max(...dataset.data);

    if (!sumChart) {
        var ctx = document.getElementById('Sum_LiveData_Chart').getContext('2d');
        sumChart = new Chart(ctx, {
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
                        // max: maxValue * 1.2,
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
                }
            }
        });

        var button = document.createElement('button');
        button.id = 'switchSumButton';
        button.className = 'btn btn-primary';
        button.style.marginTop = '20px';
        button.style.display = 'block';
        button.style.margin = 'auto';
        button.onclick = function() {
            showCurrentRMSSum = !showCurrentRMSSum;
            updateSumChart();
        };
        document.getElementById('chartContainer2').appendChild(button);

        var legendSection = document.createElement('div');
        legendSection.id = 'legendSectionSum';
        legendSection.style.marginTop = '20px';
        legendSection.style.display = 'flex';
        legendSection.style.flexWrap = 'wrap';
        document.getElementById('chartContainer2').appendChild(legendSection);
    } else {
        sumChart.data.labels = labels;
        sumChart.data.datasets = datasets;
        // sumChart.options.scales.y.max = maxValue * 1.2;
        sumChart.update();
    }

    document.getElementById('switchSumButton').innerHTML = 'Show Total ' + (showCurrentRMSSum ? 'Apparent Power (VA)' : 'Current RMS (A)');
    document.querySelector('#readingType2A').innerHTML = 'Live Readings: Total ' + (showCurrentRMSSum ? 'Current RMS (A)' : 'Apparent Power (VA)');
    document.querySelector('#readingType2B').innerHTML = 'Live Readings: Total ' + (showCurrentRMSSum ? 'Current RMS (A)' : 'Apparent Power (VA)');


    var legendSection = document.getElementById('legendSectionSum');
    legendSection.innerHTML = '';
    datasets.forEach(function(dataset, i) {
        var legendItem = document.createElement('div');
        legendItem.style.marginRight = '10px';
        legendItem.style.fontSize = '14px';
        legendItem.style.lineHeight = '1.4';
        legendItem.style.display = 'flex';
        legendItem.style.alignItems = 'center';
        legendItem.innerHTML = '<span style="background-color: ' + colors[i % colors.length] + '; ' +
            'width: 10px; height: 10px; display: inline-block; margin-right: 5px;"></span>' +
            dataset.label + ': ' + dataset.data[dataset.data.length - 1].toFixed(2);
        legendSection.appendChild(legendItem);
        // console.log(dataset.data)
    });
}

function updatePieChart() {
    if (!unitDataGlobal) return;



    var indices = [3, 6];
    var index = showCurrentRMSSum ? indices[0] : indices[1];

    var labels = unitDataGlobal.map((_, unit_id) => 'Unit ' + (unit_id + 2));
    var data = unitDataGlobal.map(unitData => unitData[unitData.length - 1][index] / (showCurrentRMSSum ? 1000 : 1));
    var backgroundColors = unitDataGlobal.map((_, unit_id) => colors[unit_id % colors.length]);

    if (!pieChart) {
        var ctx = document.getElementById('Pie_LiveData_Chart').getContext('2d');
        pieChart = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: backgroundColors,
                    hoverOffset: 4
                }]
            },
            options: {
                animation: {
                    duration: 0
                },
                responsive: true
            }
        });
    } else {
        pieChart.data.labels = labels;
        pieChart.data.datasets[0].data = data;
        pieChart.update();
    }
}


function fetchData() {
    $.getJSON('/live_data')
        .done(function(data) {
            processData(data);
            updateChart();
            updateSumChart();
            updatePieChart();
        })
        .fail(function() {
            $('#errorMessage').show().text('Data stream unavailable');
           // $('#LiveData_Chart').hide();
           //  $('#Sum_LiveData_Chart').hide();
           //  $('#Pie_LiveData_Chart').hide();
        });
}

fetchData();
// setInterval(fetchData, 1000);
updateTabs();
// setInterval(updateTabs, 1000);

// Update line charts and tabs  every second
setInterval(function() {
    fetchData();
    updateTabs();
}, 1000);
