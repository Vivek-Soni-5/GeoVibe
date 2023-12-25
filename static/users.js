
  function getLocation(event) {
  
    // Prevent the default form submission behavior
    event.preventDefault();
  
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(showPosition, showError);
    } else {
        alert("Geolocation is not supported by this browser.");
    }
  }

  function getLocationN(event) {
  
    // Prevent the default form submission behavior
    event.preventDefault();
  
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(showPositionN, showError);
    } else {
        alert("Geolocation is not supported by this browser.");
    }
  }

  function getLocationL() {
  
    // Prevent the default form submission behavior
    document.forms[1].submit();
    
  }
  
  function showPosition(position) {
    document.getElementById("latitude").value = position.coords.latitude;
    document.getElementById("longitude").value = position.coords.longitude;
    // Continue with the form submission
    document.forms[2].submit(); // Submit the third form on the page
  }

  function showPositionN(position) {
    document.getElementById("Nlatitude").value = position.coords.latitude;
    document.getElementById("Nlongitude").value = position.coords.longitude;
    // Continue with the form submission
    document.forms[0].submit(); // Submit the first form on the page
  }
  
  function showError(error) {
    switch (error.code) {
        case error.PERMISSION_DENIED:
            alert("User denied the request for Geolocation.");
            break;
        case error.POSITION_UNAVAILABLE:
            alert("Location information is unavailable.");
            break;
        case error.TIMEOUT:
            alert("The request to get user location timed out.");
            break;
        case error.UNKNOWN_ERROR:
            alert("An unknown error occurred.");
            break;
    }
  }
  