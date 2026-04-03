const mongoose = require("mongoose");

const ScanSchema = new mongoose.Schema({
  userId: { type: mongoose.Schema.Types.ObjectId, ref: "User", required: true },
  userEmail: { type: String, default: "" },   // ← add this
  type: { type: String, default: "email" },
  input: { type: String, default: "" },
  headers: { type: String, default: "" },
  deepScan: { type: Boolean, default: false },
  result: {
    label: { type: String, default: "" },
    confidence: { type: Number, default: 0 },
    flags: { type: [String], default: [] },
    explanation: { type: String, default: "" }
  },
  ipAddress: { type: String, default: "" },
  createdAt: { type: Date, default: Date.now }
});

module.exports = mongoose.model("Scan", ScanSchema);