const select = document.querySelector('#urls')

async function getLoadingStatus(serverUrl) {
  try {
    const response = await fetch(`${serverUrl}/`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' }
    })
    return response.body
  } catch (e) {

  }
}

async function getReport(serverUrl, reportToRender) {
  const { alive, reports } = await getFromServer(serverUrl)
  loading = alive
  const sortedReports = reports.sort((a, b) => a.lastUpdated > b.lastUpdated ? 1 : -1)
  select.innerHTML = ''
  for (const report of sortedReports) {
    const option = document.createElement('p')
    option.className = 'dropdown-option'
    option.innerText = report.webpageUrl
    option.addEventListener('click', (e) => {
      render(reports, e.target.innerText)
      document.querySelector('.dropdown-toggle').click()
    })
    select.appendChild(option)
  }
  if(reportToRender || sortedReports.length > 0)
    render(reports, reportToRender || sortedReports[0].webpageUrl)
}

async function getFromServer(serverUrl) {
  const response = await fetch(`${serverUrl}/reports`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' }
  })

  reportsData = await response.json()

  return reportsData
}