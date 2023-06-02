let reportsData = []
const serverUrl = 'http://109.67.30.38:3002' 
let selected = false

function toggleDropdown() {
  const dropdown = document.querySelector('.dropdown');
  dropdown.classList.toggle('select-open');
}

getReport(serverUrl)

setInterval(() => {
    getReport(serverUrl)
}, 10000)

async function ScanReport() {
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


if (window.location.pathname === '/contact.html') {
  document.getElementById('contact-form').addEventListener('submit', (event) => {
    event.preventDefault(); // prevent the form from submitting
    sendEmail(); // call the sendEmail function to send the email
  });
}
