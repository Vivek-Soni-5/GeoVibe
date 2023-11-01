

function getLocation() {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(showPosition);
  } else { 
    alert("Geolocation is not supported by this browser.");
  }
}

function showPosition(position) {
    document.getElementById("longitude").value = position.coords.longitude;
    document.getElementById("latitude").value = position.coords.latitude;
}

// document.getElementById('current_location_btn').addEventListener('click', function(event) {
//     event.preventDefault(); // Prevent the default form submission behavior
//     // You can add additional code here for this button's behavior if needed
// });