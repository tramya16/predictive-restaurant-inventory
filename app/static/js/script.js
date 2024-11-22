const INITIAL_STOCK = 1700; // Initial stock set to 100 for comparison
const THRESHOLD_PERCENTAGE = 0.25; // 25% threshold for low stock
let fetchInterval = null, chartUpdateInterval = null;

// Fetch data from the mocked API
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
    } catch (error) {
        console.error('Error fetching data:', error);
    }
}

// Function to create the line chart
let foodOrdersLineChart = null;
let weeks = [];
let actualOrdersData = [];
let predictedOrdersData = [];

function createFoodOrdersLineChart() {
    const ctx = document.getElementById('food-orders-line-chart').getContext('2d');
    foodOrdersLineChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: weeks,
            datasets: [
                {
                    label: 'Actual Orders',
                    data: actualOrdersData,
                    borderColor: 'rgba(75, 192, 192, 1)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    fill: false,
                    tension: 0.1,
                    borderWidth: 2,
                },
                {
                    label: 'Predicted Orders',
                    data: predictedOrdersData,
                    borderColor: 'rgba(255, 159, 64, 1)',
                    backgroundColor: 'rgba(255, 159, 64, 0.2)',
                    fill: false,
                    tension: 0.1,
                    borderWidth: 2,
                },
            ],
        },
        options: {
            responsive: true,
            scales: {
                x: { title: { display: true, text: 'Week Number' } },
                y: { beginAtZero: true, title: { display: true, text: 'Number of Orders' } },
            },
        },
    });
}

// Update the line chart
async function updateFoodOrdersLineChart() {
    try {
        const response = await fetch('/mocked-data');
        const data = await response.json();

        const currentWeek = data.current_week;
        const actualOrders = data.food_orders_this_week.Pasta;
        const predictedOrders = data.predicted_food_orders.Pasta;

        if (!weeks.includes(currentWeek)) {
            weeks.push(currentWeek);
            actualOrdersData.push(actualOrders);
            predictedOrdersData.push(predictedOrders);
        }

        if (foodOrdersLineChart) {
            foodOrdersLineChart.update();
        }
    } catch (error) {
        console.error('Error updating food orders chart:', error);
    }
}

// Update inventory tiles
function updateInventoryTile(ingredient, currentQuantity, restockedQuantity) {
    const tile = document.getElementById(ingredient);
    const quantityDisplay = document.getElementById(`${ingredient}-quantity`);
    const notificationPlaceholder = tile.querySelector('.restock-notification-placeholder');

    if (tile && quantityDisplay && notificationPlaceholder) {
        // Show the restocked amount temporarily
        if (restockedQuantity > 0) {
            // Temporarily add the restocked amount to stock
            quantityDisplay.textContent = `Stock: ${currentQuantity + restockedQuantity}`;

            // Update the notification
            notificationPlaceholder.textContent = `Restocked: +${restockedQuantity}`;

            // After 1 second, revert to actual stock and clear notification
            setTimeout(() => {
                quantityDisplay.textContent = `Stock: ${currentQuantity}`;
                notificationPlaceholder.textContent = ''; // Clear notification
            }, 2000); // 1 second delay
        } else {
            // If no restock, show the actual stock
            quantityDisplay.textContent = `Stock: ${currentQuantity}`;
            notificationPlaceholder.textContent = ''; // Ensure no notification
        }

        // Apply "danger" class if stock is below threshold
        const THRESHOLD_PERCENTAGE = 0.3; // Example threshold: 20%
        const INITIAL_STOCK = 100; // Replace with your actual initial stock
        if (currentQuantity < INITIAL_STOCK * THRESHOLD_PERCENTAGE) {
            tile.classList.add('danger');
        } else {
            tile.classList.remove('danger');
        }
    }
}



// Update orders with icons
// Update orders with icons and number of orders
function updatePastaOrdersUIWithIconsAndStatus(actualOrderCount, predictedOrderCount) {
    const iconContainer = document.getElementById('pasta-order-icons');
    const orderCountDisplay = document.getElementById('pasta-order-count');
    const predictedOrderCountDisplay = document.getElementById('pasta-predicted-order-count');

    // Clear existing pasta icons
    iconContainer.innerHTML = '';

        const text = document.createElement('span');
        text.textContent = ` x ${actualOrderCount}`;
        text.style.fontSize = '60px';         // Large, readable font size
        text.style.color = '#78706e';
        text.style.fontWeight = 'bold';       // Makes the text bold
        text.style.marginLeft = '15px';       // Adds space between the icon and text
        text.style.alignSelf = 'center'; // Aligns text vertically with the icon
        text.style.fontFamily = 'Arial, sans-serif'; // Sets a modern, clean font
    
        const icon = document.createElement('span');
        icon.style.fontSize = '100px';
        icon.innerHTML = '&#127837;';
        iconContainer.appendChild(icon);
        iconContainer.appendChild(text);
   

    orderCountDisplay.textContent = `Actual Orders: ${actualOrderCount}`;
    predictedOrderCountDisplay.textContent = `Predicted Orders: ${predictedOrderCount}`;
}


// Toggle button functionality
document.getElementById('toggle-button').addEventListener('click', () => {
    const button = document.getElementById('toggle-button');
    if (!fetchInterval && !chartUpdateInterval) {
        fetchInterval = setInterval(fetchData, 5000);
        chartUpdateInterval = setInterval(updateFoodOrdersLineChart, 5000);
        button.textContent = 'Stop';
    } else {
        clearInterval(fetchInterval);
        clearInterval(chartUpdateInterval);
        fetchInterval = null;
        chartUpdateInterval = null;
        button.textContent = 'Start';
    }
});

// Initialize the line chart
createFoodOrdersLineChart();
