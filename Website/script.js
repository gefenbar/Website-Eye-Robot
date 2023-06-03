let reportsData = []
const serverUrl = 'http://109.67.30.38:3002' 

function toggleDropdown(isScanUrl) {
  const dropdown = document.querySelectorAll('.dropdown')[isScanUrl ? 0 : 1];
  dropdown.classList.toggle('select-open');
}

getReport(serverUrl)

setInterval(() => {
    getReport(serverUrl)
}, 10000)

async function ScanReport() {
  // Get the URL input field value
  try {
    const urlInput = document.querySelector('#url-input').value.trim();
    // Send the URL to the server for scanning
    fetch(`${serverUrl}/report`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: urlInput })
    }).then(()=> {
      document.getElementById("scan").reset();
      enableScanBtn(false)
    })

  }
  catch (e) {
    console.log(e)
  }
}

document.getElementById("scan").addEventListener("submit", (e) => {
  e.preventDefault()
  ScanReport()
})

// Get the scan report container
const scanReportContainer = document.querySelector('#report');

// Get the scan button
const scanButton = document.querySelector('.form-group button[type="submit"]');

// Get the URL input field
const urlInput = document.querySelector('#url-input');

urlInput.addEventListener('input', () => {
  // Verify that the input is a valid website URL
  const urlPattern = /^(http|https):\/\/[a-z0-9-]+(\.[a-z0-9-]+)*(:[0-9]+)?(\/.*)?$/i;
  enableScanBtn(!urlInput.value.trim() === '' || urlPattern.test(urlInput.value.trim()))
});

const url_display = document.querySelector('h3#url')
const url_indicator = document.querySelector('#url')
if (url_indicator.innerText.length == 0) {
  url_display.style.display = 'none'
}

// Helper function to convert a string to an array buffer
function s2ab(s) {
  const buf = new ArrayBuffer(s.length);
  const view = new Uint8Array(buf);
  for (let i = 0; i < s.length; i++) view[i] = s.charCodeAt(i) & 0xff;
  return buf;
}


function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}


if (window.location.pathname === '/contact.html') {
  document.getElementById('contact-form').addEventListener('submit', (event) => {
    event.preventDefault(); // prevent the form from submitting
    sendEmail(); // call the sendEmail function to send the email
  });
}
