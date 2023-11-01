
const closeDialogButton = document.getElementById('close-dialog');
const send_email_btn = document.getElementById('send_email');
const dialog = document.getElementById('my-dialog');
dialog.showModal();

function processData(data, cur_user)
{
    const msg = {
        'email':cur_user,
        'data':data
    }
    fetch('/send_email', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(msg)
    })
    .then(response => response.json())
    .then(data => {
        // Process the response from the Python method
        hideLoader();
        alert(data);
        console.log(data);
    })
    .catch(error => {
        hideLoader();
        alert(error);
        console.error('Error:', error);
    });
}

function hideLoader() {
    document.getElementById('loader').style.display = 'none';
}

function addLoader() {
    var loaderDiv = document.createElement("div");
    loaderDiv.id = "loader";
    loaderDiv.className = "loader";
    document.getElementById("content").appendChild(loaderDiv);
}



