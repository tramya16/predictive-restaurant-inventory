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
        updateInventoryTile('tomato', data.inventory.tomato, data.restocked_ingredients.tomato);
        updateInventoryTile('spaghetti', data.inventory.spaghetti, data.restocked_ingredients.spaghetti);
        updateInventoryTile('cheese', data.inventory.cheese, data.restocked_ingredients.cheese);
        updateInventoryTile('basil', data.inventory.basil, data.restocked_ingredients.basil);


        // Update orders by Food Items
        // Example usage - Update pasta orders dynamically (replace 10 with actual order count)
        updatePastaOrdersUIWithIconsAndStatus(data.food_orders_this_week.Pasta,data.predicted_food_orders.Pasta);

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

function updateInventoryTile(food, stock, restockedAmount) {
    const tile = document.getElementById(food);
    const stockElement = document.getElementById(`${food}-quantity`);
    const restockedNotification = document.getElementById(`${food}-restocked-notification`);

    // Update stock quantity
    stockElement.textContent = stock;

    // Show or hide the restocked notification
    if (restockedAmount > 0) {
        restockedNotification.textContent = `+${restockedAmount} Restocked`;
        restockedNotification.classList.add('show');  // Show notification with animation
    } else {
        restockedNotification.classList.remove('show');  // Hide notification
    }

    // Calculate the percentage of remaining stock
    const percentage = stock / INITIAL_STOCK;

    // Change tile color based on stock level
    if (percentage < THRESHOLD_PERCENTAGE) {
        tile.classList.add('danger');
        tile.classList.remove('warning', 'success');
    } else if (percentage < 0.7) {  // If stock is between 25% and 70%
        tile.classList.add('warning');
        tile.classList.remove('danger', 'success');
    } else {
        tile.classList.add('success');
        tile.classList.remove('danger', 'warning');
    }
}


function updatePastaOrdersUIWithIconsAndStatus(actualOrderCount, predictedOrderCount) {
    const iconContainer = document.getElementById('pasta-order-icons');
    const orderCountDisplay = document.getElementById('pasta-order-count');
    const predictedOrderCountDisplay = document.getElementById('pasta-predicted-order-count');
    const orderStatus = document.getElementById('pasta-order-status');
    
    const maxOrders = 20;  // Set your max order threshold

    // Clear previous icons
    iconContainer.innerHTML = '';

    // Add pasta icons based on actual order count
    for (let i = 0; i < actualOrderCount; i++) {
        const icon = document.createElement('span');
        icon.style.fontSize = '100px';  // Adjust the size of the emoji
        icon.innerHTML = '&#127837;';  // Pasta emoji
        iconContainer.appendChild(icon);
    }

    // Display the actual number of orders
    orderCountDisplay.textContent = `Actual Orders: ${actualOrderCount}`;

    // Display the predicted number of orders
    predictedOrderCountDisplay.textContent = `Predicted Orders: ${predictedOrderCount}`;

    // Calculate order status based on actual order count
    const orderPercentage = (actualOrderCount / maxOrders) * 100;
    if (orderPercentage < 30) {
        orderStatus.textContent = 'Low Demand';
        orderStatus.className = 'low-demand';
    } else if (orderPercentage < 70) {
        orderStatus.textContent = 'Medium Demand';
        orderStatus.className = 'medium-demand';
    } else {
        orderStatus.textContent = 'High Demand';
        orderStatus.className = 'high-demand';
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
