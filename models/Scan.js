const mongoose = require("mongoose");

const ScanSchema = new mongoose.Schema({
  type: { type: String, required: true }, // "web", "email", "file"
  input: { type: String, required: true }, // URL, email, filename
  result: { type: Object, required: true }, // JSON result
  createdAt: { type: Date, default: Date.now }
});

// Use the exact same name here
module.exports = mongoose.model("Scan", ScanSchema);
