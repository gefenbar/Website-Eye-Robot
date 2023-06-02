let loading

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
    if (button && loading) {
      button.innerHTML = `Loading${dots}`;
    }
  }, 400);


  const scanButton = document.querySelector('.btn.btn-primary')
  if (loading) {
    indicator = '<button id="download-btn" style="background-color:#999;">Loading</button><br/>'
    scanButton.disabled = 'true'
    scanButton.style.backgroundColor = 'gray'
  }
  else if (report.issuesFound.length === 0) {
    indicator = '<button id="download-btn" style="background-color: red;">No Issues found</button><br/>'
    scanButton.disabled = 'true'
    scanButton.style.backgroundColor = '#333333'
    clearInterval(interval)
  }
  else {
    indicator = '<button id="download-btn" style="background-color:#1f8151;" onclick="downloadExcel()">Download Excel</button><br/>'
    scanButton.disabled = 'true'
    scanButton.style.backgroundColor = '#333333'
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
