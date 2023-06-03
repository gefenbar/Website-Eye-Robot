let loading

function render(reports, url) {
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
    if (button && loading) {
      button.innerHTML = `Loading${dots}`;
    }
  }, 500);

  const downloadBtn = document.createElement('button')
  downloadBtn.id = 'download-btn'
  if (loading) {
    downloadBtn.style.backgroundColor = '#999'
    downloadBtn.innerText = 'Loading'
  }
  else if (report.issuesFound.length === 0) {
    downloadBtn.style.backgroundColor = 'red'
    downloadBtn.innerText = 'No Issues found'
    clearInterval(interval)
  }
  else {
    downloadBtn.style.backgroundColor = '#1f8151'
    downloadBtn.innerText = 'Download Excel'
    downloadBtn.addEventListener('click', () => {
      downloadExcel(report)
    })
    clearInterval(interval)

  }
  const contentElement = document.getElementById('content')
  contentElement.innerHTML = content
  contentElement.prepend(document.createElement('br'))
  contentElement.prepend(downloadBtn)
  // Select screenshot images and add event listeners
  const screenshotImgs = document.querySelectorAll('.screenshot-img');
  screenshotImgs.forEach((screenshotImg) => {
    screenshotImg.addEventListener('mousemove', handleMouseMove);
  });
  document.querySelector(".url").style.padding = '10px'

}

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


function downloadExcel(report) {
  if (!report) return;

  const rows = [];
  // console.log(reportData)
  report?.issuesFound?.forEach((issue) => {
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

function enableScanBtn(enable) {
  const scanBtn = document.querySelector('.btn.btn-primary')
  if (loading) {
    scanBtn.style.backgroundColor = 'black';
    scanBtn.disabled = true;
    scanBtn.style.cursor = 'default'
  }
  else if (enable) {
    scanBtn.style.backgroundColor = '#4CAF50';
    scanBtn.disabled = false;
  } else {
    scanBtn.style.backgroundColor = '#f44336';
    scanBtn.disabled = true;
    scanBtn.style.cursor = 'default'
  }
}