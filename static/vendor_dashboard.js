function openTab(tabName) {
    const tabs = document.querySelectorAll('.tab-content');
    tabs.forEach(tab => {
        tab.classList.remove('active');
    });
    document.getElementById(tabName).classList.add('active');    
}
function addMenuItem() {
// Display the item form
document.getElementById('addItemForm').style.display = 'block';
}

function submitItemForm() {
// Get values from the form
const itemName = document.getElementById('itemName').value;
const itemPrice = document.getElementById('itemPrice').value;
const itemImage = document.getElementById('itemImage').value;

// Validate and add the item to the list
if (itemName && itemPrice) {
    // Create a new list item
    const newItem = document.createElement('li');
    //newItem.textContent = ${itemName} - ${itemPrice};

    // Append the new item to the list
    document.getElementById('itemList').appendChild(newItem);

    // Clear the form fields
    document.getElementById('itemName').value = '';
    document.getElementById('itemPrice').value = '';
    document.getElementById('itemImage').value = '';

    // Hide the item form
    document.getElementById('addItemForm').style.display = 'none';
} else {
    alert('Please fill in all required fields (Item Name and Item Price).');
}
}