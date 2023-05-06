
async function getReport() {
  const response = await fetch('http://127.0.0.1:3036/report', {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' }
  })
  document.querySelector('.lds-hourglass').style.display = 'none'
  if (response.status === 404) return
  const result = await response.json()
  const url = Object.keys(result)[0]
  const content = result[url]
  document.getElementById('content').innerHTML = content
  document.getElementById('url').innerHTML = url
}
getReport()
function ScanReport() {
  // Get the URL input field value
  try {
    const urlInput = document.querySelector('#url-input').value.trim();
    document.querySelector('.lds-hourglass').style.display = 'block'
    // Send the URL to the server for scanning
    fetch('http://127.0.0.1:3036/report', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: urlInput })
    })
    setTimeout(() => {
      getReport()
    }, 30000)
  }
  catch (e) {
    console.log(e)
  }

}

document.getElementById("scan").addEventListener("submit", (e) => {
  e.preventDefault()
  ScanReport()
})

async function sendEmail() {
  try {
    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const message = document.getElementById('message').value;

    const response = await fetch('http://localhost:3003/send-email', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ name, email, message })
    });

    const data = await response.json();
    console.log(data.message);

    // Show success message to the user
    alert('Email sent successfully!');
  } catch (error) {
    console.error(error);
    // Show error message to the user
    alert('Error sending email. Please try again later.');
  }
};

if (window.location.pathname === '/contact.html') {
  document.getElementById('contact-form').addEventListener('submit', (event) => {
    event.preventDefault(); // prevent the form from submitting
    sendEmail(); // call the sendEmail function to send the email
  });
}

// Get the scan report container
const scanReportContainer = document.querySelector('#report');

// Get the scan button
const scanButton = document.querySelector('.form-group button[type="submit"]');

// Get the URL input field
const urlInput = document.querySelector('#url-input');

urlInput.addEventListener('input', () => {
  // Verify that the input is a valid website URL
  const urlPattern = /^(http|https):\/\/[a-z0-9-]+(\.[a-z0-9-]+)*(:[0-9]+)?(\/.*)?$/i;
  if (urlInput.value.trim() === '' || !urlPattern.test(urlInput.value.trim())) {
    // Set the button color to red if the input is empty or not valid
    scanButton.style.backgroundColor = '#f44336';
    console.log(scanButton.style.backgroundColor);
    console.log("1");
    scanButton.disabled = true;
  } else {
    // Set the button color to green if the input is valid
    scanButton.style.backgroundColor = '#4CAF50';
    console.log(scanButton.style.backgroundColor);
    console.log("2");
    scanButton.disabled = false;
  }
});

const url_display = document.querySelector('h3#url')

if (url_display.innerText.length <= 1) {
  url_display.style.display = 'none'
}




