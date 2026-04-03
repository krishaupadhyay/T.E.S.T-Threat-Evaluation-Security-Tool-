const express = require("express");// this is call import required packages-creating express lib
const router = express.Router();//useing express make router object--This router will handle routes like /signup and /login.
const bcrypt = require("bcryptjs");//for hashing 
const User = require("../models/User");//temp user from db
const jwt = require("jsonwebtoken");
const mailer = require("../config/mailer");   

function generateOTP() {
  return Math.floor(100000 + Math.random() * 900000).toString();
}

/* ******************************************SIGNUP********************************************** */

router.post("/signup", async (req, res) => {
    const { fullName, email, password } = req.body;
    // const { fullName, role,email, password } = req.body;

    //if any field is empty then it returns ALl fields are required
    if (!fullName || !email || !password) {
        return res.json({ success: false, message: "All fields are required" });
    }

    //this chek if user already exist
    const exists = await User.findOne({ email });
    if (exists) {
        return res.json({ success: false, message: "User already exists" });
    }

    //password hashing 
    const hashpass = await bcrypt.hash(password, 10);

    await User.create({ fullName, email, password: hashpass, role: "user" });
    res.json({ success: true, message: "Signup successful" });
});

/* *********************************************** LOGIN  USER***********************************************/
router.post("/user-login", async (req, res) => {
  const { email, password } = req.body;
  if (!email || !password)
    return res.json({ success: false, message: "Email and password required" });

  const user = await User.findOne({ email });
  if (!user)
    return res.json({ success: false, message: "Invalid credentials" });

  const isMatch = await bcrypt.compare(password, user.password);
  if (!isMatch)
    return res.json({ success: false, message: "Invalid credentials" });

  if (user.role === "admin")
    return res.json({ success: false, message: "Admin credentials not allowed" });

  // generate OTP
  const otp = generateOTP();
  const otpExpiry = new Date(Date.now() + 5 * 60 * 1000); // 5 minutes

  // save OTP to DB
  user.otp = otp;
  user.otpExpiry = otpExpiry;
  await user.save();

  // send OTP email
  await mailer.sendMail({
    from: process.env.EMAIL_USER,
    to: email,
    subject: "T.E.S.T. — Your OTP Code",
    html: `
      <h2>Your OTP Code</h2>
      <p>Use this code to complete your login:</p>
      <h1 style="letter-spacing: 8px; color: #00bfff;">${otp}</h1>
      <p>This code expires in 5 minutes.</p>
    `
  });

  res.json({ success: true, message: "OTP sent to your email", email });
});


// VERIFY OTP — new route
router.post("/verify-otp", async (req, res) => {
  const { email, otp } = req.body;

  const user = await User.findOne({ email });
  if (!user)
    return res.json({ success: false, message: "User not found" });

  // check OTP
  if (user.otp !== otp)
    return res.json({ success: false, message: "Invalid OTP" });

  // check expiry
  if (new Date() > user.otpExpiry)
    return res.json({ success: false, message: "OTP expired. Please login again." });

  // clear OTP
  user.otp = null;
  user.otpExpiry = null;
  await user.save();

  // now issue token
  const token = jwt.sign(
    { id: user._id, role: user.role },
    process.env.JWT_SECRET,
    { expiresIn: "1d" }
  );

  res.cookie("token", token, {
    httpOnly: true,
    secure: false,
    sameSite: "strict"
  });

  res.json({ success: true, message: "Login successful", role: user.role, email: user.email });
});




/* ************************************************** ADMIN LOGIN ********************************************** */

// auth middleware for admin
router.post("/admin-login", async (req, res) => {
  const { email, password } = req.body;
  if (!email || !password)
    return res.json({ success: false, message: "Email and password required" });

  const user = await User.findOne({ email });
  if (!user)
    return res.json({ success: false, message: "Invalid credentials" });

  const isMatch = await bcrypt.compare(password, user.password);
  if (!isMatch)
    return res.json({ success: false, message: "Invalid credentials" });

  if (user.role !== "admin")
    return res.json({ success: false, message: "Access denied. Not an admin." });

  const otp = generateOTP();
  const otpExpiry = new Date(Date.now() + 5 * 60 * 1000);
  user.otp = otp;
  user.otpExpiry = otpExpiry;
  await user.save();

  await mailer.sendMail({
    from: process.env.EMAIL_USER,
    to: email,
    subject: "T.E.S.T. Admin — OTP Code",
    html: `
      <h2>Admin OTP Code</h2>
      <p>Your admin login OTP:</p>
      <h1 style="letter-spacing: 8px; color: #ff3e3e;">${otp}</h1>
      <p>Expires in 5 minutes.</p>
    `
  });

  res.json({ success: true, message: "OTP sent to admin email", email });
});


/*************************************** login user dashboard *****************************************   */
router.get("/me", async (req, res) => {
    try {
        const token = req.cookies.token;

        if (!token) {
            return res.json({ success: false, message: "No token" });
        }
        const decoded = jwt.verify(token, process.env.JWT_SECRET);

        const user = await User.findById(decoded.id).select("-password");

        if (!user) {
            return res.json({ success: false, message: "User not found" });
        }

        res.json({
            success: true,
            user: {
                name: user.fullName,
                role: user.role,
                email: user.email
            }
        });

    } catch (err) {
        return res.json({ success: false, message: "Invalid token" });
    }
});



/* ****************************************************logout route*******************************************************/


router.post("/logout", (req, res) => {
    res.clearCookie("token");
    res.json({ success: true, message: "Logged out successfully" });
});



module.exports = router;
