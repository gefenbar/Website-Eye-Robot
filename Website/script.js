let isLoading = false;

function setLoadingState(isLoading) {
  if (isLoading) {
    document.getElementById("url").classList.add("loading");
  } else {
    document.getElementById("url").classList.remove("loading");
  }
}

async function getReport() {
  setLoadingState(true);
  const response = await fetch('http://127.0.0.1:3013/report', {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' }
  })
  if (response.status === 404) return
  const result = await response.json()
  const url = Object.keys(result)[0]
  const content = result[url]
  document.getElementById('content').innerHTML = content
  document.getElementById('url').innerHTML = url

  // Select screenshot images and add event listeners
  const screenshotImgs = document.querySelectorAll('.screenshot-img');
  screenshotImgs.forEach((screenshotImg) => {
    screenshotImg.addEventListener('mousemove', handleMouseMove);
  });
  // document.getElementById("url").classList.remove("loading");
  setLoadingState(false);
  document.getElementById("url").style.padding = '10px'
}
getReport()

function handleMouseMove(event) {
  const { left, top, width, height } = event.target.getBoundingClientRect();
  const x = ((event.clientX - left) / width) * 150;
  const y = ((event.clientY - top) / height) * 150;
  event.target.style.transformOrigin = `${x}% ${y}%`;
  event.target.style.transform = 'scale(1.5)';


  // Reset the transform when the mouse moves away from the element
  event.target.addEventListener('mouseleave', () => {
    event.target.style.transform = 'none';
  });
}

function ScanReport() {
   isLoading=true
  // Get the URL input field value
  try {
    const urlInput = document.querySelector('#url-input').value.trim();
    // Send the URL to the server for scanning
    fetch('http://127.0.0.1:3013/report', {
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
    scanButton.disabled = true;
  } else {
    // Set the button color to green if the input is valid
    scanButton.style.backgroundColor = '#4CAF50';
    scanButton.disabled = false;
  }
});

const url_display = document.querySelector('h3#url')
const url_indicator = document.querySelector('#url')
if (url_indicator.innerText == 0) {
  url_display.style.display = 'none'
}
