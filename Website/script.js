let loading = false
let reportsData = []
const serverUrl = 'http://109.67.30.38:3002'
const select = document.querySelector('#urls')
// const spinnerText = document.querySelector('#loading-spinner__text')
let selected = false

// Spinner()
function toggleDropdown() {
  var dropdown = document.querySelector('.dropdown');
  dropdown.classList.toggle('select-open');
}

function setLoadingState(isLoading) {
  if (isLoading) {
    // Spinner.show();
    // spinnerText.innerText = "Report is being made"
  } else {
    // spinnerText.innerText = ""
    // Spinner.hide()
  }
  loading = isLoading
}

async function loadingStatus() {
  try {
    const response = await fetch(`${serverUrl}/`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' }
    })
    setLoadingState(response.status > 200)

    console.log(response.status)
  } catch (e) {
    setLoadingState(true)
    return true
  }
}

async function getReport() {
  await loadingStatus();
  const response = await fetch(`${serverUrl}/reports`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' }
  })

  if (response.status === 404) return
  reportsData = await response.json()

  const { alive, reports } = reportsData

  setLoadingState(alive);

  const sortedReports = reports.sort((a, b) => a.lastUpdated > b.lastUpdated ? 1 : -1)
  render(reports, sortedReports[0].webpageUrl)
  select.innerHTML = ''
  for (const report of sortedReports) {
    select.innerHTML += `<option value="${report.webpageUrl}">${report.webpageUrl}</option>`
  }

  select.addEventListener('change', (e) => {
    selected = true
    render(reports, e.target.value)
  })
}

function render(reports, url) {
  let indicator;
  let content = ''
  const report = reports.filter(r => r.webpageUrl === url)[0]
  content = `<h3 class="url">${report.webpageUrl}</h3>`
  for (const issue of report.issuesFound) {
    content += `
          <div class="report-card">
          <div class="card-header">
            <h3>${issue['scannerName']}</h3>
            <p> page url -> 
            <a href="${issue['pageUrl']}"> ${issue['pageUrl']}</a>
            </p>
            <p>resolution -> <span>${issue['resolution']}</span></p>
            </div>
              <div class="card-screenshot">
                <a>
                  <img class="screenshot-img" src='${issue['img']}'></img>
                </a>
              </div>
            </div>`
  }
  let dots = '';
  let numDots = 0;

  const interval = setInterval(() => {
    numDots = (numDots + 1) % 4;
    dots = '.'.repeat(numDots);
    const button = document.getElementById('download-btn');
    if (button) {
      button.innerHTML = `Loading${dots}`;
    }
  }, 500);
  if (loading) {
    indicator = '<button id="download-btn" style="background-color:#999;">Loading</button><br/>'
  }
  else if (report.issuesFound.length === 0) {
    indicator = '<button id="download-btn" style="background-color: red;">No Issues found</button><br/>'
    clearInterval(interval)
  }
  else {
    indicator = '<button id="download-btn" style="background-color:#1f8151;" onclick="downloadExcel()">Download Excel</button><br/>'
    clearInterval(interval)

  }

  document.getElementById('content').innerHTML = indicator + content
  // Select screenshot images and add event listeners
  const screenshotImgs = document.querySelectorAll('.screenshot-img');
  screenshotImgs.forEach((screenshotImg) => {
    screenshotImg.addEventListener('mousemove', handleMouseMove);
  });
  document.querySelector(".url").style.padding = '10px'

}
getReport()

setInterval(() => {
    getReport()
}, 20000)

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

async function ScanReport() {
  const isLoading = await loadingStatus()
  // await sleep(250)
  console.log(isLoading)
  if (isLoading) {
    alert('Scanner is currently working! please wait for it to finish!')
    return;
  }
  selected = false
  // Get the URL input field value
  try {
    const urlInput = document.querySelector('#url-input').value.trim();
    // Send the URL to the server for scanning
    fetch(`${serverUrl}/report`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: urlInput })
    })
  }
  catch (e) {
    console.log(e)
  }
  urlInput.innerText = ''
  await sleep(250)
  getReport()
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
if (url_indicator.innerText.length == 0) {
  url_display.style.display = 'none'
}

function downloadExcel() {
  if (reportsData.length < 1) return;
  const reportData = reportsData.slice(-1)[0]

  const rows = [];
  // console.log(reportData)
  reportData?.issuesFound?.forEach((issue) => {
    const name = issue.scannerName;
    const pageUrl = issue.pageUrl;
    const resolution = issue.resolution;
    const image = issue.img;
    rows.push({ 'Issue Name': name, 'Page URL': pageUrl, 'Resolution': resolution, 'Image': image });
  });
  // console.log(rows)

  // Sort the rows array by the 'Issue Name' field
  rows.sort((a, b) => a['Issue Name'].localeCompare(b['Issue Name']));
  // Create a new workbook
  const workbook = XLSX.utils.book_new();

  // Convert the data to a worksheet
  const worksheet = XLSX.utils.json_to_sheet(rows);
  worksheet['!cols'] = [
    { wch: 20 }, // "Issue Name" column
    { wch: 50 }, // "Page URL" column
    { wch: 20 }, // "Resolution" column
    { wch: 50 }, // "Image" column
  ];
  // Add the worksheet to the workbook
  XLSX.utils.book_append_sheet(workbook, worksheet, "Sheet1");

  // Generate a binary string from the workbook
  const wbout = XLSX.write(workbook, { bookType: 'xlsx', type: 'binary' });

  // Create a Blob from the binary string
  const blob = new Blob([s2ab(wbout)], { type: 'application/octet-stream' });

  // Create a temporary link element
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = 'report.xlsx'; // Set the desired filename for the downloaded file

  // Append the link to the document body
  document.body.appendChild(link);

  // Trigger the download by simulating a click on the link
  link.click();

  // Cleanup: remove the temporary link from the document
  document.body.removeChild(link);
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



// Create a new div element for the magnifying glass
const magnifyingGlass = document.createElement('div');
magnifyingGlass.className = 'magnifying-glass';
document.body.appendChild(magnifyingGlass);

// Update the position of the magnifying glass based on the mouse movement
document.addEventListener('mousemove', (event) => {
  const x = event.clientX;
  const y = event.clientY;

  // Set the position of the magnifying glass
  magnifyingGlass.style.left = x + 'px';
  magnifyingGlass.style.top = y + 'px';
});

// Hide the default mouse cursor
document.body.style.cursor = 'none';

// Override cursor styles for specific elements
const overrideCursorStyle = (element) => {
  element.style.cursor = 'none';
};

// Apply the cursor style override to anchors, buttons, and other clickable elements
const clickableElements = document.querySelectorAll('a, button, [role="button"]');
clickableElements.forEach((element) => {
  overrideCursorStyle(element);
});

// Apply the cursor style override to URLs
const urlElements = document.querySelectorAll('[href]');
urlElements.forEach((element) => {
  overrideCursorStyle(element);
});