const express = require('express');
const bodyParser = require('body-parser');
const nodemailer = require('nodemailer');
const cors = require('cors');

const app = express();

app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json());
app.use(express.static('public'));
app.use(cors());


app.post('/send-email', (req, res) => {
  const { name, email, message } = req.body;

  const transporter = nodemailer.createTransport({
    service: 'gmail',
    auth: {
      user: 'gefenbar20@gmail.com',
      pass: 'ywvzupaqnzfzjcmv'
    }
  });

  const mailOptions = {
    from: email,
    to: 'gefenbar003@gmail.com',
    subject: 'Website Eye Robot Message',
    text: `Name: ${name}\nEmail: ${email}\nMessage: ${message}`
  };

  transporter.sendMail(mailOptions, (error, info) => {
    if (error) {
      console.log(error);
      res.status(500).send('Error sending email');
    } else {
      console.log(`Email sent: ${info.response}`);
      res.header('Access-Control-Allow-Origin', '*');
      res.json({ message: 'Email sent successfully' });
    }
  });
});

app.listen(3003, () => {
  console.log('Server started on port 3003');
});

