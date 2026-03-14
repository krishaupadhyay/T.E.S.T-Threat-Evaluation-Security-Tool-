const express = require("express");// this is call import required packages-creating express lib
const router = express.Router();//useing express make router object--This router will handle routes like /signup and /login.
const bcrypt = require("bcryptjs");//for hashing 
const User = require("../models/User");//

/* SIGNUP */

router.post("/signup", async (req, res) => {
    const { fullName,email, password } = req.body;
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
const hashpass= await bcrypt.hash(password,10);

    await User.create({ fullName,email, password:hashpass, role:"user" });
    res.json({ success: true, message: "Signup successful" });
});

/* LOGIN  USER*/
router.post("/user-login", async (req, res) => {
    const { email, password } = req.body;  // fetch data form mongo 

    if (!email || !password) {
        return res.json({ success: false, message: "Email and password required" });
    }

    //find user by email only 
    const user = await User.findOne({email});
    if(!user){
        return res.json({success:false,message:"INvalid credentials "});
    }
//compare  enterd password with hashed password 
const isMatch=await bcrypt.compare(password,user.password);
if (!isMatch) {
        return res.json({ success: false, message: "Invalid credentials" });
    }
    if(user.role==='admin')
{
      return res.json({ success: false, message: "Admin credentials not allowed" });
}
    res.json({success:true,message:"Login succesfull",role:user.role,email:user.email})

});

/* ADMIN LOGIN */
// auth middleware for admin

router.post("/admin-login", async (req, res) => {
    const { email, password } = req.body;

    if (!email || !password) {
        return res.json({ success: false, message: "Email and password required" });
    }

    const user = await User.findOne({ email });

    if (!user) {
        return res.json({ success: false, message: "Invalid credentials for Admin" });
    }

    const isMatch = await bcrypt.compare(password, user.password);

    if (!isMatch) {
        return res.json({ success: false, message: "Invalid credentials" });
    }

    // 🔴 CHECK ROLE HERE
    if (user.role !== "admin") {
        return res.json({ success: false, message: "Access denied. Not an admin." });
    }

    res.json({
        success: true,
        message: "Admin login successful",
        role: user.role,
        email: user.email
    });
});


module.exports = router;
