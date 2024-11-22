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
        

    } catch (error) {
        console.error('Error fetching data:', error);
    }
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
        }, 1000); // Show restock for 2 seconds
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
    if (!fetchInterval && !timeInterval) {
        fetchInterval = setInterval(fetchData, 1000);
        button.textContent = 'Stop';
    } else {
        clearInterval(fetchInterval);
        clearInterval(timeInterval);
        fetchInterval = null;
        timeInterval = null;
        button.textContent = 'Start';
    }
});
