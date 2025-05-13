// GraphQL endpoint
const GRAPHQL_URL = '/graphql';

// Global chart reference
let dataChart = null;

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
                sensor_count
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
        option.textContent = `${location.name} (${location.sensor_count})`;
        locationSelect.appendChild(option);
    });
}

// Load sensors list
async function loadSensors() {
    const query = `
        query {
            sensors {
                sensor_id
                sensor_type
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
        option.value = sensor.sensor_id;
        option.textContent = sensor.sensor_id;
        sensorIdSelect.appendChild(option);
    });
    
    // Populate sensors list
    const sensorsContainer = document.getElementById('sensors-container');
    sensorsContainer.innerHTML = '';
    
    const sensorsByType = {};
    data.data.sensors.forEach(sensor => {
        if (!sensorsByType[sensor.sensor_type]) {
            sensorsByType[sensor.sensor_type] = [];
        }
        sensorsByType[sensor.sensor_type].push(sensor);
    });
    
    for (const [type, sensors] of Object.entries(sensorsByType)) {
        const typeHeader = document.createElement('li');
        typeHeader.innerHTML = `<strong>${type.charAt(0).toUpperCase() + type.slice(1)} Sensors</strong>`;
        sensorsContainer.appendChild(typeHeader);
        
        sensors.forEach(sensor => {
            const sensorItem = document.createElement('li');
            sensorItem.textContent = `${sensor.sensor_id} (${sensor.location})`;
            sensorItem.addEventListener('click', () => {
                document.getElementById('sensor-type').value = sensor.sensor_type;
                document.getElementById('location').value = sensor.location;
                document.getElementById('sensor-id').value = sensor.sensor_id;
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
            sensor_readings(
                sensor_type: $sensorType,
                location: $location,
                sensor_id: $sensorId,
                start_time: $startTime,
                end_time: $endTime,
                limit: 100
            ) {
                sensor_id
                sensor_type
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
    if (!data || !data.data || !data.data.sensor_readings) return;
    
    const readings = data.data.sensor_readings;
    
    // Update table
    updateReadingsTable(readings);
    
    // Update chart
    updateChart(readings);
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
            <td>${reading.sensor_id}</td>
            <td>${reading.sensor_type}</td>
            <td>${reading.location}</td>
            <td>${reading.value}</td>
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
        if (!datasetsBySensorId[reading.sensor_id]) {
            datasetsBySensorId[reading.sensor_id] = {
                label: `${reading.sensor_id} (${reading.location})`,
                data: [],
                borderColor: getRandomColor(),
                backgroundColor: 'transparent',
                borderWidth: 2,
                tension: 0.1
            };
        }
        
        datasetsBySensorId[reading.sensor_id].data.push({
            x: new Date(reading.timestamp),
            y: reading.value
        });
    });
    
    // Get unit from any reading if available
    const unit = readings.length > 0 ? readings[0].unit : '';
    const sensorType = readings.length > 0 ? readings[0].sensor_type : 'Sensor';
    
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

// Generate random color for chart lines
function getRandomColor() {
    const colors = [
        '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
        '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
    ];
    return colors[Math.floor(Math.random() * colors.length)];
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
        loadReadings();
    });
    
    // Auto-refresh every 30 seconds
    setInterval(() => {
        loadReadings();
    }, 30000);
});
