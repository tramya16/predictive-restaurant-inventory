const INITIAL_STOCK = 50; // Initial stock set to 100 for comparison
const THRESHOLD_PERCENTAGE = 0.25; // 25% threshold for low stock
let accuracyChart = null;
let accuracyData = [];
let weekLabels = [];

let fetchInterval = null, timeInterval = null;

async function fetchData() {
    try {
        const response = await fetch('/mocked-data');
        const data = await response.json();

        // Update current week
        const currentWeek = data.current_week;
        document.getElementById('current-week-number').textContent = currentWeek;

        // Update inventory quantities and check for danger
        updateInventoryTile('tomato', data.inventory.tomato, data.restocked_ingredients.tomato);
        updateInventoryTile('spaghetti', data.inventory.spaghetti, data.restocked_ingredients.spaghetti);
        updateInventoryTile('cheese', data.inventory.cheese, data.restocked_ingredients.cheese);
        updateInventoryTile('basil', data.inventory.basil, data.restocked_ingredients.basil);

        // Update orders by Food Items
        updatePastaOrdersUIWithIconsAndStatus(data.food_orders_this_week.Pasta, data.predicted_food_orders.Pasta);

        // Update model accuracy data for the graph
        const latestAccuracy = data.model_accuracy; // Get accuracy for the current week
        console.log(latestAccuracy)
        updateAccuracyChart(currentWeek, latestAccuracy);

    } catch (error) {
        console.error('Error fetching data:', error);
    }
}

function updateAccuracyChart(currentWeek, latestAccuracy) {
    if (!accuracyChart) {
        console.error('Chart not initialized.');
        return;
    }

    // Initialize weekLabels and accuracyData if it's the first update
    if (weekLabels.length === 0) {
        weekLabels.push('Week 1');  // Add the first week label
        accuracyData.push(latestAccuracy);  // Add the accuracy data for Week 1
    }

    // Ensure the weekLabels and accuracyData arrays have enough entries for the current week
    while (weekLabels.length < currentWeek) {
        weekLabels.push(`Week ${weekLabels.length + 1}`);  // Add more weeks as needed
        accuracyData.push(null);  // Add placeholder data for missing weeks
    }

    // Validate latestAccuracy and update only the current week's accuracy
    if (latestAccuracy !== undefined && latestAccuracy !== null) {
        console.log(latestAccuracy);
        
        // Update the accuracy value for the current week
        accuracyData[currentWeek - 1] = latestAccuracy;
    } else {
        console.warn(`Invalid accuracy for week ${currentWeek}:`, latestAccuracy);
    }

    // Update the chart data
    accuracyChart.data.labels = weekLabels;
    accuracyChart.data.datasets[0].data = accuracyData;

    // Update the chart with the latest data
    accuracyChart.update();
}

function initializeAccuracyChart() {
    const ctx = document.getElementById('accuracy-chart-canvas').getContext('2d');
    
    accuracyChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: weekLabels, // Dynamic week labels
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
}

function updateInventoryTile(food, stock, restockedAmount) {
    const tile = document.getElementById(food);
    const stockElement = document.getElementById(`${food}-quantity`);
    stockElement.textContent = stock;

    // Create restock amount animation inside the tile
    if (restockedAmount > 0) {
        const restockNotification = document.createElement('span');
        restockNotification.classList.add('restock-notification');
        restockNotification.textContent = `+${restockedAmount}`;

        // Append the notification to the tile's quantity element for animation
        stockElement.appendChild(restockNotification);

        // Animate the restock notification
        setTimeout(() => {
            restockNotification.classList.add('show');
        }, 100); // Delay to ensure it's visible for animation

        // Clean up the notification after a short delay
        setTimeout(() => {
            restockNotification.classList.remove('show');
            setTimeout(() => {
                restockNotification.remove();
            }, 500); // Wait for the fade-out animation to finish
        }, 2000); // Show restock for 2 seconds
    }

    const percentage = stock / INITIAL_STOCK;

    if (percentage < THRESHOLD_PERCENTAGE) {
        tile.classList.add('danger');
        tile.classList.remove('warning', 'success');
    } else if (percentage < 0.7) {
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

    iconContainer.innerHTML = '';

    for (let i = 0; i < actualOrderCount; i++) {
        const icon = document.createElement('span');
        icon.style.fontSize = '100px';
        icon.innerHTML = '&#127837;';
        iconContainer.appendChild(icon);
    }

    orderCountDisplay.textContent = `Actual Orders: ${actualOrderCount}`;
    predictedOrderCountDisplay.textContent = `Predicted Orders: ${predictedOrderCount}`;
}

function updateCurrentTime() {
    const now = new Date();
    const formattedTime = now.toLocaleTimeString('en-US', { hour12: false });
    document.getElementById('current-time-display').textContent = formattedTime;
}

// Toggle button functionality
document.getElementById('toggle-button').addEventListener('click', () => {
    const button = document.getElementById('toggle-button');
    if (!fetchInterval && !timeInterval) {
        fetchInterval = setInterval(fetchData, 1000);
        timeInterval = setInterval(updateCurrentTime, 1000);
        button.textContent = 'Stop';
    } else {
        clearInterval(fetchInterval);
        clearInterval(timeInterval);
        fetchInterval = null;
        timeInterval = null;
        button.textContent = 'Start';
    }
});

// Initialize the chart when the page loads
document.addEventListener('DOMContentLoaded', () => {
    initializeAccuracyChart();
});
