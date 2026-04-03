const nodemailer = require("nodemailer");

const transporter = nodemailer.createTransport({
  service: "gmail",
  auth: {
    user: process.env.EMAIL_USER,     // your gmail
    pass: process.env.EMAIL_PASS      // gmail app password
  }
});

module.exports = transporter;