const INITIAL_STOCK = 100;  // Initial stock set to 100 for comparison
const THRESHOLD_PERCENTAGE = 0.25;  // 25% threshold for low stock
let accuracyChart = null;
let accuracyData = [];

let fetchInterval = null, timeInterval = null;

async function fetchData() {
    try {
        const response = await fetch('/mocked-data');
        const data = await response.json();

        // Update current week
        document.getElementById('current-week-number').textContent = data.current_week;

        // Update inventory quantities and check for danger
        updateInventoryTile('egg', data.inventory.eggs);
        updateInventoryTile('spaghetti', data.inventory.spaghetti);
        updateInventoryTile('bread', data.inventory.bread);
        updateInventoryTile('tomato_sauce', data.inventory.tomato_sauce);

        // Update predicted and simulated orders
        document.getElementById('egg-predicted').textContent = data.predicted_food_orders.eggs;
        document.getElementById('spaghetti-predicted').textContent = data.predicted_food_orders.spaghetti;
        document.getElementById('bread-predicted').textContent = data.predicted_food_orders.bread;
        document.getElementById('tomato_sauce-predicted').textContent = data.predicted_food_orders.tomato_sauce;

        document.getElementById('egg-simulated').textContent = data.simulated_food_orders.eggs;
        document.getElementById('spaghetti-simulated').textContent = data.simulated_food_orders.spaghetti;
        document.getElementById('bread-simulated').textContent = data.simulated_food_orders.bread;
        document.getElementById('tomato_sauce-simulated').textContent = data.simulated_food_orders.tomato_sauce;

        // Update orders by category
        document.getElementById('orders-Pasta').textContent = `Pasta: ${data.orders_by_category.Pasta}`;
        document.getElementById('orders-Omlette').textContent = `Omlette: ${data.orders_by_category.Omlette}`;
        document.getElementById('orders-GarlicBread').textContent = `Garlic Bread: ${data.orders_by_category.GarlicBread}`;

        // Update model accuracy data for the graph
        accuracyData = data.model_accuracy;  // Receive all accuracy data

        // Update model accuracy chart
        updateAccuracyChart();


    } catch (error) {
        console.error('Error fetching data:', error);
    }
}

function updateAccuracyChart() {
    const ctx = document.getElementById('accuracy-chart-canvas').getContext('2d');

    if (accuracyChart) {
accuracyChart.destroy();
        }
        accuracyChart =new Chart(ctx, {
        type: 'line',
        data: {
            labels: Array.from({ length: accuracyData.length }, (_, index) => `Week ${index + 1}`),
            datasets: [{
                label: 'Model Accuracy (%)',
                data: accuracyData,
                borderColor: '#28a745',
                backgroundColor: 'rgba(40, 167, 69, 0.2)',
                fill: true,
                tension: 0.4,
                pointRadius: 5
            }]
        },
        options: {
            responsive: true,
            plugins: {
    legend: {
        labels: {
            usePointStyle: true,
            boxWidth: 0 
        }
    }
},
            scales: {
                y: {
                    min: 0,
                    max: 100,
                    title: {
                        display: true,
                        text: 'Accuracy (%)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Week'
                    }
                }
            }
        }
    });

    console.log("Chart Updates");
}

function updateInventoryTile(food, stock) {
    const tile = document.getElementById(food);
    const stockElement = document.getElementById(`${food}-quantity`);
    stockElement.textContent = stock;

    if (stock < INITIAL_STOCK * THRESHOLD_PERCENTAGE) {
        tile.classList.add('danger');
    } else {
        tile.classList.remove('danger');
    }
}

function updateCurrentTime() {
        const now = new Date();
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        const seconds = String(now.getSeconds()).padStart(2, '0');
        const formattedTime = `${hours}:${minutes}:${seconds}`;
        
        document.getElementById('current-time-display').textContent = formattedTime;

    }

//  setInterval(fetchData, 1000);  // Fetch data every 3 seconds
//  setInterval(updateCurrentTime, 1000);  // Update current time every second

// Toggle button functionality
document.getElementById('toggle-button').addEventListener('click', () => {
    const button = document.getElementById('toggle-button');
    if (!fetchInterval && !timeInterval) {
        // Start intervals
        fetchInterval = setInterval(fetchData, 1000);
        timeInterval = setInterval(updateCurrentTime, 1000);
        button.textContent = 'Stop';
    } else {
        // Stop intervals
        clearInterval(fetchInterval);
        clearInterval(timeInterval);
        fetchInterval = null;
        timeInterval = null;
        button.textContent = 'Start';
    }
});
