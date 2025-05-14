// GraphQL endpoint
const GRAPHQL_URL = '/graphql';

// Global chart references
let dataChart = null;
let aggregatedDataChart = null;

// Current data view mode
let currentDataView = 'raw'; // 'raw' or 'aggregated'

// Debug logging function
function logDebug(message, data = null) {
    const enableDebugLogging = true; // Set to false to disable all debug logs
    
    if (enableDebugLogging) {
        if (data) {
            console.log(`[DEBUG] ${message}`, data);
        } else {
            console.log(`[DEBUG] ${message}`);
        }
    }
}

// Fetch data using GraphQL
async function fetchGraphQL(query, variables = {}) {
    try {
        const response = await fetch(GRAPHQL_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query,
                variables
            }),
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        return await response.json();
    } catch (error) {
        console.error('Error fetching data:', error);
        return null;
    }
}

// Load locations for the filter dropdown
async function loadLocations() {
    const query = `
        query {
            locations {
                name
                sensorCount
            }
        }
    `;

    const data = await fetchGraphQL(query);
    if (!data || !data.data || !data.data.locations) return;

    const locationSelect = document.getElementById('location');
    
    // Clear existing options except the first one
    while (locationSelect.options.length > 1) {
        locationSelect.remove(1);
    }
    
    // Add new options
    data.data.locations.forEach(location => {
        const option = document.createElement('option');
        option.value = location.name;
        option.textContent = `${location.name} (${location.sensorCount})`;
        locationSelect.appendChild(option);
    });
}

// Load sensors list
async function loadSensors() {
    const query = `
        query {
            sensors {
                sensorId
                sensorType
                location
            }
        }
    `;

    const data = await fetchGraphQL(query);
    if (!data || !data.data || !data.data.sensors) return;

    // Populate sensor IDs dropdown
    const sensorIdSelect = document.getElementById('sensor-id');
    
    // Clear existing options except the first one
    while (sensorIdSelect.options.length > 1) {
        sensorIdSelect.remove(1);
    }
    
    // Add new options
    data.data.sensors.forEach(sensor => {
        const option = document.createElement('option');
        option.value = sensor.sensorId;
        option.textContent = sensor.sensorId;
        sensorIdSelect.appendChild(option);
    });
    
    // Populate sensors list
    const sensorsContainer = document.getElementById('sensors-container');
    sensorsContainer.innerHTML = '';
    
    const sensorsByType = {};
    data.data.sensors.forEach(sensor => {
        if (!sensorsByType[sensor.sensorType]) {
            sensorsByType[sensor.sensorType] = [];
        }
        sensorsByType[sensor.sensorType].push(sensor);
    });
    
    for (const [type, sensors] of Object.entries(sensorsByType)) {
        const typeHeader = document.createElement('li');
        typeHeader.innerHTML = `<strong>${type.charAt(0).toUpperCase() + type.slice(1)} Sensors</strong>`;
        sensorsContainer.appendChild(typeHeader);
        
        sensors.forEach(sensor => {
            const sensorItem = document.createElement('li');
            sensorItem.textContent = `${sensor.sensorId} (${sensor.location})`;
            sensorItem.addEventListener('click', () => {
                document.getElementById('sensor-type').value = sensor.sensorType;
                document.getElementById('location').value = sensor.location;
                document.getElementById('sensor-id').value = sensor.sensorId;
                document.getElementById('filter-form').dispatchEvent(new Event('submit'));
            });
            sensorItem.style.cursor = 'pointer';
            sensorItem.classList.add('sensor-item');
            sensorsContainer.appendChild(sensorItem);
        });
    }
}

// Load sensor readings
async function loadReadings() {
    const sensorType = document.getElementById('sensor-type').value;
    const location = document.getElementById('location').value;
    const sensorId = document.getElementById('sensor-id').value;
    const timeRange = document.getElementById('time-range').value;
    
    // Calculate time range
    const endTime = new Date().toISOString();
    const startTime = new Date(Date.now() - parseTimeRange(timeRange)).toISOString();
    
    const query = `
        query ($sensorType: String, $location: String, $sensorId: String, $startTime: String, $endTime: String) {
            sensorReadings(
                sensorType: $sensorType,
                location: $location,
                sensorId: $sensorId,
                startTime: $startTime,
                endTime: $endTime,
                limit: 100
            ) {
                sensorId
                sensorType
                location
                value
                unit
                timestamp
            }
        }
    `;
    
    const variables = {
        sensorType: sensorType || null,
        location: location || null,
        sensorId: sensorId || null,
        startTime,
        endTime
    };

    const data = await fetchGraphQL(query, variables);
    if (!data || !data.data || !data.data.sensorReadings) return;
    
    const readings = data.data.sensorReadings;
    
    // Update table
    updateReadingsTable(readings);
    
    // Update chart
    updateChart(readings);
}

// Load aggregated sensor readings
async function loadAggregatedReadings() {
    logDebug("Loading aggregated sensor readings");
    
    const sensorType = document.getElementById('sensor-type').value;
    const location = document.getElementById('location').value;
    const sensorId = document.getElementById('sensor-id').value;
    const timeRange = document.getElementById('time-range').value;
    
    logDebug("Filter criteria", { sensorType, location, sensorId, timeRange });
    
    // Calculate time range - use a longer range for aggregated data
    const endTime = new Date().toISOString();
    const startTime = new Date(Date.now() - parseTimeRange(timeRange) * 2).toISOString(); // Double the time range
    
    const query = `
        query ($sensorType: String, $location: String, $sensorId: String, $startTime: String, $endTime: String) {
            aggregatedReadings(
                sensorType: $sensorType,
                location: $location,
                sensorId: $sensorId,
                startTime: $startTime,
                endTime: $endTime,
                limit: 100
            ) {
                sensorId
                sensorType
                location
                mean
                min
                max
                unit
                timestamp
            }
        }
    `;
    
    const variables = {
        sensorType: sensorType || null,
        location: location || null,
        sensorId: sensorId || null,
        startTime,
        endTime
    };

    const data = await fetchGraphQL(query, variables);
    if (!data || !data.data || !data.data.aggregatedReadings) return;
    
    const readings = data.data.aggregatedReadings;
    
    // Update table
    updateAggregatedReadingsTable(readings);
    
    // Update chart
    updateAggregatedChart(readings);
}

// Parse time range string to milliseconds
function parseTimeRange(timeRange) {
    const hours = parseInt(timeRange.replace('h', ''));
    return hours * 60 * 60 * 1000;
}

// Update readings table
function updateReadingsTable(readings) {
    const tableBody = document.getElementById('readings-table');
    tableBody.innerHTML = '';
    
    if (readings.length === 0) {
        const row = document.createElement('tr');
        row.innerHTML = '<td colspan="6">No data available</td>';
        tableBody.appendChild(row);
        return;
    }
    
    readings.forEach(reading => {
        const row = document.createElement('tr');
        
        // Format timestamp
        const timestamp = new Date(reading.timestamp);
        const formattedTime = timestamp.toLocaleString();
        
        row.innerHTML = `
            <td>${reading.sensorId}</td>
            <td>${reading.sensorType}</td>
            <td>${reading.location}</td>
            <td>${reading.value}</td>
            <td>${reading.unit}</td>
            <td>${formattedTime}</td>
        `;
        
        tableBody.appendChild(row);
    });
}

// Update aggregated readings table
function updateAggregatedReadingsTable(readings) {
    const tableBody = document.getElementById('aggregated-readings-table');
    tableBody.innerHTML = '';
    
    if (readings.length === 0) {
        const row = document.createElement('tr');
        row.innerHTML = '<td colspan="8">No aggregated data available</td>';
        tableBody.appendChild(row);
        return;
    }
    
    readings.forEach(reading => {
        const row = document.createElement('tr');
        
        // Format timestamp
        const timestamp = new Date(reading.timestamp);
        const formattedTime = timestamp.toLocaleString();
        
        row.innerHTML = `
            <td>${reading.sensorId}</td>
            <td>${reading.sensorType}</td>
            <td>${reading.location}</td>
            <td>${reading.min.toFixed(2)}</td>
            <td>${reading.mean.toFixed(2)}</td>
            <td>${reading.max.toFixed(2)}</td>
            <td>${reading.unit}</td>
            <td>${formattedTime}</td>
        `;
        
        tableBody.appendChild(row);
    });
}

// Update chart
function updateChart(readings) {
    // Sort readings by timestamp
    readings.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
    
    // Group by sensor ID
    const datasetsBySensorId = {};
    
    readings.forEach(reading => {
        if (!datasetsBySensorId[reading.sensorId]) {
            datasetsBySensorId[reading.sensorId] = {
                label: `${reading.sensorId} (${reading.location})`,
                data: [],
                borderColor: getRandomColor(),
                backgroundColor: 'transparent',
                borderWidth: 2,
                tension: 0.1
            };
        }
        
        datasetsBySensorId[reading.sensorId].data.push({
            x: new Date(reading.timestamp),
            y: reading.value
        });
    });
    
    // Get unit from any reading if available
    const unit = readings.length > 0 ? readings[0].unit : '';
    const sensorType = readings.length > 0 ? readings[0].sensorType : 'Sensor';
    
    // Update chart title
    document.getElementById('chart-title').textContent = `${sensorType.charAt(0).toUpperCase() + sensorType.slice(1)} Data ${unit ? '(' + unit + ')' : ''}`;
    
    // Destroy existing chart if it exists
    if (dataChart) {
        dataChart.destroy();
    }
    
    // Create new chart
    const ctx = document.getElementById('data-chart').getContext('2d');
    dataChart = new Chart(ctx, {
        type: 'line',
        data: {
            datasets: Object.values(datasetsBySensorId)
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: 'minute',
                        displayFormats: {
                            minute: 'HH:mm'
                        },
                        tooltipFormat: 'yyyy-MM-dd HH:mm:ss'
                    },
                    title: {
                        display: true,
                        text: 'Time'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: unit
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'top',
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ${context.parsed.y} ${unit}`;
                        }
                    }
                }
            }
        }
    });
}

// Update aggregated chart
function updateAggregatedChart(readings) {
    // Sort readings by timestamp
    readings.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
    
    // Group by sensor ID
    const datasetsBySensorId = {};
    
    readings.forEach(reading => {
        const sensorId = reading.sensorId;
        
        // Create datasets for min, mean, and max
        if (!datasetsBySensorId[`${sensorId}-min`]) {
            datasetsBySensorId[`${sensorId}-min`] = {
                label: `${sensorId} (Min)`,
                data: [],
                borderColor: getRandomColor(),
                backgroundColor: 'transparent',
                borderWidth: 1,
                borderDash: [5, 5],
                tension: 0.1
            };
            
            datasetsBySensorId[`${sensorId}-mean`] = {
                label: `${sensorId} (Mean)`,
                data: [],
                borderColor: datasetsBySensorId[`${sensorId}-min`].borderColor,
                backgroundColor: 'transparent',
                borderWidth: 2,
                tension: 0.1
            };
            
            datasetsBySensorId[`${sensorId}-max`] = {
                label: `${sensorId} (Max)`,
                data: [],
                borderColor: datasetsBySensorId[`${sensorId}-min`].borderColor,
                backgroundColor: 'transparent',
                borderWidth: 1,
                borderDash: [5, 5],
                tension: 0.1
            };
        }
        
        // Add data points
        datasetsBySensorId[`${sensorId}-min`].data.push({
            x: new Date(reading.timestamp),
            y: reading.min
        });
        
        datasetsBySensorId[`${sensorId}-mean`].data.push({
            x: new Date(reading.timestamp),
            y: reading.mean
        });
        
        datasetsBySensorId[`${sensorId}-max`].data.push({
            x: new Date(reading.timestamp),
            y: reading.max
        });
    });
    
    // Get unit from any reading if available
    const unit = readings.length > 0 ? readings[0].unit : '';
    const sensorType = readings.length > 0 ? readings[0].sensorType : 'Sensor';
    
    // Update chart title
    document.getElementById('aggregated-chart-title').textContent = `Aggregated ${sensorType.charAt(0).toUpperCase() + sensorType.slice(1)} Data ${unit ? '(' + unit + ')' : ''}`;
    
    // Destroy existing chart if it exists
    if (aggregatedDataChart) {
        aggregatedDataChart.destroy();
    }
    
    // Create new chart
    const ctx = document.getElementById('aggregated-data-chart').getContext('2d');
    aggregatedDataChart = new Chart(ctx, {
        type: 'line',
        data: {
            datasets: Object.values(datasetsBySensorId)
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: 'hour',
                        displayFormats: {
                            hour: 'MM-dd HH:mm'
                        },
                        tooltipFormat: 'yyyy-MM-dd HH:mm:ss'
                    },
                    title: {
                        display: true,
                        text: 'Time'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: unit
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        filter: function(item) {
                            // Hide the range dataset from the legend
                            return !item.text.includes('Range');
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const datasetLabel = context.dataset.label || '';
                            const value = context.parsed.y.toFixed(2);
                            
                            if (datasetLabel.includes('Range')) {
                                return null; // Don't show tooltip for range dataset
                            }
                            
                            return `${datasetLabel}: ${value} ${unit}`;
                        },
                        footer: function(tooltipItems) {
                            // Find all items with the same timestamp and show min/max/mean
                            if (tooltipItems.length > 0) {
                                const sensorId = tooltipItems[0].dataset.label.split(' ')[0];
                                let min, mean, max;
                                
                                for (const item of tooltipItems) {
                                    const label = item.dataset.label;
                                    if (label.includes(sensorId)) {
                                        if (label.includes('Min')) {
                                            min = item.parsed.y.toFixed(2);
                                        } else if (label.includes('Mean')) {
                                            mean = item.parsed.y.toFixed(2);
                                        } else if (label.includes('Max')) {
                                            max = item.parsed.y.toFixed(2);
                                        }
                                    }
                                }
                                
                                if (min && mean && max) {
                                    return `Range: ${min} - ${max} ${unit}`;
                                }
                            }
                            return null;
                        }
                    }
                }
            }
        }
    });
}

// Generate random color for chart lines
function getRandomColor() {
    const colors = [
        '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
        '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
    ];
    return colors[Math.floor(Math.random() * colors.length)];
}

// Toggle between raw and aggregated data views
function toggleDataView(view) {
    const rawDataView = document.getElementById('raw-data-view');
    const aggregatedDataView = document.getElementById('aggregated-data-view');
    const rawDataTab = document.getElementById('raw-data-tab');
    const aggregatedDataTab = document.getElementById('aggregated-data-tab');
    
    currentDataView = view;
    
    if (view === 'raw') {
        rawDataView.classList.add('active');
        aggregatedDataView.classList.remove('active');
        rawDataTab.classList.add('active');
        aggregatedDataTab.classList.remove('active');
        
        // Refresh raw data view
        loadReadings();
    } else {
        rawDataView.classList.remove('active');
        aggregatedDataView.classList.add('active');
        rawDataTab.classList.remove('active');
        aggregatedDataTab.classList.add('active');
        
        // Refresh aggregated data view
        loadAggregatedReadings();
    }
}

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    // Load initial data
    loadLocations();
    loadSensors();
    loadReadings();
    
    // Handle filter form submission
    document.getElementById('filter-form').addEventListener('submit', (event) => {
        event.preventDefault();
        
        // Load data based on current view
        if (currentDataView === 'raw') {
            loadReadings();
        } else {
            loadAggregatedReadings();
        }
    });
    
    // Add event listeners for tab buttons
    document.getElementById('raw-data-tab').addEventListener('click', () => {
        toggleDataView('raw');
    });
    
    document.getElementById('aggregated-data-tab').addEventListener('click', () => {
        toggleDataView('aggregated');
    });
    
    // Auto-refresh every 30 seconds
    setInterval(() => {
        if (currentDataView === 'raw') {
            loadReadings();
        } else {
            loadAggregatedReadings();
        }
    }, 30000);
});
