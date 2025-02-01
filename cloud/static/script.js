// Login validation function
document.getElementById('loginForm').addEventListener('submit', async function(event) {
    event.preventDefault();

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    const response = await fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
    });

    if (response.redirected) {
        window.location.href = response.url;  // Redirect to dashboard if successful
    } else {
        const result = await response.json();
        alert(result.message);  // Show error message
    }
});


// Registration validation function
function validateRegistration(event) {
    event.preventDefault();

    const firstName = document.getElementById('firstName').value;
    const lastName = document.getElementById('lastName').value;
    const phone = document.getElementById('phone').value;
    const email = document.getElementById('email').value;
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const errorMessage = document.getElementById('errorMessage');

    fetch('/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ first_name: firstName, last_name: lastName, phone, email, username, password }),
    })
    .then(response => {
        if (response.ok) {
            alert('Registration successful!');
            window.location.href = "azure_credentials.html"; 
        } else {
            return response.json().then(data => {
                errorMessage.textContent = data.message;
            });
        }
    });
}

// Tab functionality for charts
$(document).ready(function() {
    $("#tabs ul li").on("click", function() {
        $("#tabs ul li").removeClass("font-bold text-blue-500").addClass("text-gray-500");
        $(this).addClass("font-bold text-blue-500");
        var activeTab = $(this).attr("id");
        if (activeTab === "tab1") {
            $("#tab-1").show();
            $("#tab-2").hide();
        } else {
            $("#tab-1").hide();
            $("#tab-2").show();
        }
    });

    // Slider functionality
    var slider = document.getElementById('slider');
    noUiSlider.create(slider, {
        start: [10],
        connect: [true, false],
        range: {
            'min': 1,
            'max': 100
        }
    });

    // Mock CPU and Network Data
    var cpuData = [12, 19, 3, 5, 2, 8, 10, 15, 6];
    var networkInData = [1200, 1500, 1100, 900, 1600, 1700, 1450, 1300, 1500];
    var networkOutData = [1000, 1300, 900, 850, 1400, 1550, 1350, 1100, 1400];

    // CPU Usage Chart with Anomalies
    var anomalyThresholdCPU = 80;
    var cpuAnomalies = cpuData.map(value => value > anomalyThresholdCPU ? value : null);

    var ctx1 = document.getElementById('cpuUsageChart').getContext('2d');
    var cpuUsageChart = new Chart(ctx1, {
        type: 'line',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep'],
            datasets: [{
                label: 'CPU Usage (%)',
                data: cpuData,
                borderColor: 'rgba(54, 162, 235, 1)',
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderWidth: 2,
                pointRadius: cpuAnomalies.map(val => val ? 6 : 0),
                pointBackgroundColor: cpuAnomalies.map(val => val ? 'red' : 'rgba(54, 162, 235, 1)')
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) { return value + "%" }
                    }
                }
            },
            title: {
                display: true,
                text: 'CPU Usage Over Time with Anomalies'
            }
        }
    });

    // Network I/O Chart with Anomalies
    var anomalyThresholdNetwork = 1600;
    var networkInAnomalies = networkInData.map(value => value > anomalyThresholdNetwork ? value : null);
    var networkOutAnomalies = networkOutData.map(value => value > anomalyThresholdNetwork ? value : null);

    var ctx2 = document.getElementById('networkChart').getContext('2d');
    var networkChart = new Chart(ctx2, {
        type: 'line',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep'],
            datasets: [{
                label: 'Network In (Bytes)',
                data: networkInData,
                borderColor: 'rgba(75, 192, 192, 1)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderWidth: 2,
                pointRadius: networkInAnomalies.map(val => val ? 6 : 0),
                pointBackgroundColor: networkInAnomalies.map(val => val ? 'red' : 'rgba(75, 192, 192, 1)')
            }, {
                label: 'Network Out (Bytes)',
                data: networkOutData,
                borderColor: 'rgba(255, 159, 64, 1)',
                backgroundColor: 'rgba(255, 159, 64, 0.2)',
                borderWidth: 2,
                pointRadius: networkOutAnomalies.map(val => val ? 6 : 0),
                pointBackgroundColor: networkOutAnomalies.map(val => val ? 'red' : 'rgba(255, 159, 64, 1)')
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                }
            },
            title: {
                display: true,
                text: 'Network I/O Over Time with Anomalies'
            }
        }
    });

    // Anomaly Message Functionality
    function updateAnomalyMessage(anomalies) {
        const anomalyMessage = document.getElementById('anomalyMessage');
        if (anomalies.some(value => value !== null)) {
            anomalyMessage.classList.remove('hidden');
        } else {
            anomalyMessage.classList.add('hidden');
        }
    }

    // Update anomaly message based on CPU anomalies
    updateAnomalyMessage(cpuAnomalies);
});

f// Fetch data from the Flask API
fetch('http://127.0.0.1:5000/get-data')
    .then(response => response.json())
    .then(data => {
        console.log(data);  // Log data to check if it is received correctly

        // Extract CPU and Network data from the response
        const cpuData = data.map(item => item.cpu_usage);
        const networkInData = data.map(item => item.network_in);
        const networkOutData = data.map(item => item.network_out);

        // Generate the CPU Usage Chart
        const ctx1 = document.getElementById('cpuUsageChart').getContext('2d');
        const cpuUsageChart = new Chart(ctx1, {
            type: 'line',
            data: {
                labels: cpuData.map((_, index) => index + 1),
                datasets: [{
                    label: 'CPU Usage (%)',
                    data: cpuData,
                    borderColor: 'rgba(54, 162, 235, 1)',
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                title: {
                    display: true,
                    text: 'CPU Usage Over Time',
                    fontSize: 18,
                    fontColor: '#333'
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) { return value + "%" }
                        }
                    }
                }
            }
        });

        // Generate the Network I/O Chart
        const ctx2 = document.getElementById('networkChart').getContext('2d');
        const networkChart = new Chart(ctx2, {
            type: 'line',
            data: {
                labels: networkInData.map((_, index) => index + 1),
                datasets: [
                    {
                        label: 'Network In (Bytes)',
                        data: networkInData,
                        borderColor: 'rgba(75, 192, 192, 1)',
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        borderWidth: 2
                    },
                    {
                        label: 'Network Out (Bytes)',
                        data: networkOutData,
                        borderColor: 'rgba(255, 159, 64, 1)',
                        backgroundColor: 'rgba(255, 159, 64, 0.2)',
                        borderWidth: 2
                    }
                ]
            },
            options: {
                responsive: true,
                title: {
                    display: true,
                    text: 'Network I/O Over Time',
                    fontSize: 18,
                    fontColor: '#333'
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    })
    .catch(error => console.error('Error fetching data:', error));
