async function sendEmail(serverUrl) {
    try {
      const name = document.getElementById('name').value;
      const email = document.getElementById('email').value;
      const message = document.getElementById('message').value;
  
      const response = await fetch(`${serverUrl}/send-email`, {
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