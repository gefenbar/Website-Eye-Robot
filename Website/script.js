let isLoading = false;

function setLoadingState(isLoading) {
  if (isLoading) {
    // document.getElementById("url").classList.add("loading");
  } else {
    document.getElementById("url").classList.remove("loading");
  }
}

async function getReport() {
  setLoadingState(true);
  const response = await fetch('http://127.0.0.1:3002/report', {
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
  isLoading = true
  // Get the URL input field value
  try {
    const urlInput = document.querySelector('#url-input').value.trim();
    // Send the URL to the server for scanning
    fetch('http://127.0.0.1:3002/report', {
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
  // Send a request to the server to retrieve the data
  fetch('http://localhost:3002/report', {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' }
  })
    .then((response) => {
      if (response.ok) {
        // Get the response data as JSON
        return response.json();
      } else {
        throw new Error('Failed to retrieve data from server');
      }
    })
    .then((data) => {
      // Extract the HTML string from the data
      const htmlString = data['http://127.0.0.1:3000/Website/index.html'];

      // Parse the HTML string
      const parser = new DOMParser();
      const doc = parser.parseFromString(htmlString, 'text/html');

      // Extract the relevant data from the HTML
      const reportCards = doc.querySelectorAll('.report-card');
      const rows = [];
      reportCards.forEach((reportCard) => {
        const name = reportCard.querySelector('h3').textContent;
        const pageUrl = reportCard.querySelector('a').href;
        const resolution = reportCard.querySelector('span').textContent;
        const image = reportCard.querySelector('img').src;
        rows.push([name, pageUrl, resolution, image]);
      });

      // Create a new workbook and worksheet
      const newWorkbook = XLSX.utils.book_new();
      const newWorksheet = XLSX.utils.aoa_to_sheet([
        ['Issue Name', 'Page URL', 'Resolution', 'Image'],
        ...rows,
      ]);

      // Set the width of the columns
      newWorksheet['!cols'] = [
        { wch: 20 }, // "Issue Name" column
        { wch: 50 }, // "Page URL" column
        { wch: 20 }, // "Resolution" column
        { wch: 50 }, // "Image" column
      ];

      // Add the worksheet to the workbook
      XLSX.utils.book_append_sheet(newWorkbook, newWorksheet, 'Sheet1');

      // Generate a binary string from the workbook
      const wbout = XLSX.write(newWorkbook, { bookType: 'xlsx', type: 'binary' });

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
    })
    .catch((error) => {
      console.error(error);
      // Show an error message to the user
      alert('Failed to download Excel file. Please try again later.');
    });
}

// Helper function to convert a string to an array buffer
function s2ab(s) {
  const buf = new ArrayBuffer(s.length);
  const view = new Uint8Array(buf);
  for (let i = 0; i < s.length; i++) view[i] = s.charCodeAt(i) & 0xff;
  return buf;
}