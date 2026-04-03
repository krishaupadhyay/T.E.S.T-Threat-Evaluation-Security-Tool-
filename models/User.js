const mongoose = require("mongoose");

const userSchema = new mongoose.Schema({
  fullName: { type: String, required: true },
  email: { type: String, required: true, unique: true },
  password: { type: String, required: true },
  role: { type: String, enum: ["user", "admin"], default: "user" },

  // MFA fields
  otp: { type: String, default: null },
  otpExpiry: { type: Date, default: null }
});

module.exports = mongoose.model("User", userSchema);