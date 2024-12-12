const INITIAL_STOCK = 1700; // Initial stock set to 100 for comparison
const THRESHOLD_PERCENTAGE = 0.75; // 50% threshold for low stock
let fetchInterval = null, chartUpdateInterval = null,accuracyChartUpdate=null;
let isStarted = false;

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

function updateModel() {
    if (!isStarted) {
        alert("Please start first!");
        return;
    }else{
        const selectedModel = document.getElementById("modelSelector").value;
        fetch('/update-model', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ model_name: selectedModel }),
        })
        .then(response => response.json())
        .then(data => alert("Model updated to: " + data.model_name))
        .catch(error => console.error('Error:', error));
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
                }
            ],
        },
        options: {
            responsive: true,
            scales: {
                x: {
                    title: { display: true, text: 'Week Number' },
                },
                y: {
                    beginAtZero: false, // Disable automatic zero start
                    min: 800,          // Set minimum value
                    title: { display: true, text: 'Number of Orders' },
                },
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
        const selectedModel = document.getElementById("modelSelector").value;

        const modelColors = {
            sk_sarima:'rgba(255, 165, 0, 1)' ,     // Green for SARIMA
            holt_winters: 'rgba(0, 255, 0, 1)', // Blue for Holt Winters
            auto_sarima: 'rgba(255, 0, 0, 1)',      // Purple for ARIMA
        };

        const selectedColor = modelColors[selectedModel] || 'rgba(0, 0, 255, 1)'; // Default color

        // Add the current week if not already present
        if (!weeks.includes(currentWeek)) {
            weeks.push(currentWeek);

            // Ensure all datasets are padded with `null` for the new week
            foodOrdersLineChart.data.datasets.forEach((dataset) => {
                dataset.data.push(null);
            });
        }

        // Handle the actual orders dataset
        let actualOrdersDataset = foodOrdersLineChart.data.datasets.find(
            (dataset) => dataset.label === 'Actual Orders'
        );

        if (!actualOrdersDataset) {
            // Create the dataset for actual orders if it doesn't exist
            actualOrdersDataset = {
                label: 'Actual Orders',
                data: Array(weeks.length).fill(null), // Initialize with null for all weeks
                borderColor: 'rgba(0, 0, 255, 1)',    // Blue for actual orders
                backgroundColor: 'rgba(0, 0, 255, 0.2)', // Semi-transparent background
                borderWidth: 2,
            };
            foodOrdersLineChart.data.datasets.push(actualOrdersDataset);
        }

        // Update the actual orders data
        actualOrdersDataset.data[weeks.indexOf(currentWeek)] = actualOrders;

        // Handle the predicted orders dataset for the selected model
        let modelDataset = foodOrdersLineChart.data.datasets.find(
            (dataset) => dataset.label === 'Predicted Orders (' + selectedModel + ')'
        );

        if (!modelDataset) {
            // Create a new dataset for the selected model
            modelDataset = {
                label: 'Predicted Orders (' + selectedModel + ')',
                data: Array(weeks.length).fill(null), // Initialize with null for all weeks
                borderColor: selectedColor,
                backgroundColor: selectedColor.replace('1)', '0.2)'), // Semi-transparent background
                borderWidth: 2,
            };
            foodOrdersLineChart.data.datasets.push(modelDataset);
        }

        // Update the predicted orders data
        modelDataset.data[weeks.indexOf(currentWeek)] = predictedOrders;

        // Update the chart
        foodOrdersLineChart.update();
    } catch (error) {
        console.error('Error updating food orders chart:', error);
    }
}

let modelAccuracyChart = null;
let accuracyWeeks = [];  // Weeks
let accuracyData = [];   // Accuracy percentages

function createModelAccuracyLineChart() {
    const ctx = document.getElementById('model-accuracy-line-chart').getContext('2d');
    modelAccuracyChart = new Chart(ctx, {
        type: 'line',
        data: {
            // labels: accuracyWeeks,
            // datasets: [{
            //     label: 'Model Accuracy (%)',
            //     data: accuracyData,
            //     borderColor: 'rgba(54, 162, 235, 1)',
            //     backgroundColor: 'rgba(54, 162, 235, 0.2)',
            //     fill: false,
            //     tension: 0.1,
            //     borderWidth: 2,
            // }],
        },
        options: {
            responsive: true,
            scales: {
                x: {
                    title: { display: true, text: 'Week Number' },
                },
                y: {
                    beginAtZero: false,
                    min: 50,   // Set a reasonable minimum for accuracy
                    max: 100,  // Accuracy should be a percentage
                    title: { display: true, text: 'Accuracy (%)' },
                },
            },
        },
    });
}



async function updateModelAccuracyChart() {
    try {
        const response = await fetch('/mocked-data');
        const data = await response.json();

        const accuracies = data.model_accuracy; // This should be the list of accuracies
        const currentWeek = data.current_week;

        // Get the currently selected model
        const selectedModel = document.getElementById("modelSelector").value;
        console.log(`Selected Model: ${selectedModel}`);

        // Define colors for each model
        const modelColors = {
            sk_sarima:'rgba(255, 165, 0, 1)' ,     // Green for SARIMA
            holt_winters: 'rgba(0, 255, 0, 1)', // Blue for Holt Winters
            auto_sarima: 'rgba(255, 0, 0, 1)',      // Purple for ARIMA
        };

        const selectedColor = modelColors[selectedModel] || 'rgba(75, 192, 192, 1)'; // Default color

        // Check if the model is already displayed on the chart
        const existingDatasetIndex = modelAccuracyChart.data.datasets.findIndex(
            (dataset) => dataset.label === `Model Accuracy (%) - ${selectedModel}`
        );

        if (existingDatasetIndex === -1) {
            // Add a new dataset for the selected model
            const newDataset = {
                label: `Model Accuracy (%) - ${selectedModel}`,
                data: accuracies,
                borderColor: selectedColor,
                backgroundColor: selectedColor.replace('1)', '0.2)'), // Semi-transparent background
                fill: false,
                tension: 0.4, // Smooth curve
            };

            modelAccuracyChart.data.datasets.push(newDataset);
        } else {
            // Update the existing dataset for the selected model
            modelAccuracyChart.data.datasets[existingDatasetIndex].data = accuracies;
            modelAccuracyChart.data.datasets[existingDatasetIndex].borderColor = selectedColor;
            modelAccuracyChart.data.datasets[existingDatasetIndex].backgroundColor = selectedColor.replace('1)', '0.2)');
        }

        // Ensure the labels (weeks) are up-to-date
        modelAccuracyChart.data.labels = Array.from(
            { length: accuracies.length },
            (_, i) => `Week ${i + 1}`
        );

        // Update the chart
        modelAccuracyChart.update();
    } catch (error) {
        console.error('Error updating model accuracy chart:', error);
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


document.getElementById('toggle-button').addEventListener('click', () => {
    const button = document.getElementById('toggle-button');
    const modelSelection = document.getElementById('modelSelection');

    if (!fetchInterval && !chartUpdateInterval) {
        // Start state
        fetchInterval = setInterval(fetchData, 5000);
        chartUpdateInterval = setInterval(updateFoodOrdersLineChart, 5000);
        accuracyChartUpdate = setInterval(updateModelAccuracyChart, 10000);
        button.textContent = 'Stop';
        modelSelection.style.display = 'block'; // Show model selection
        isStarted = true;
    } else {
        // Stop state
        clearInterval(fetchInterval);
        clearInterval(chartUpdateInterval);
        clearInterval(accuracyChartUpdate);
        fetchInterval = null;
        chartUpdateInterval = null;
        accuracyChartUpdate = null;
        button.textContent = 'Start';
        modelSelection.style.display = 'none'; // Hide model selection
        isStarted = false;
    }
});

document.getElementById('modelSelector').addEventListener('change', () => {
    updateModelAccuracyChart();
});

// Initialize the line chart
createFoodOrdersLineChart();
createModelAccuracyLineChart();