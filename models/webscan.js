const mongoose = require('mongoose');

const WebScanSchema = new mongoose.Schema({

userId: { type: mongoose.Schema.Types.ObjectId, ref: "User", required: true },
  userEmail: { type: String, default: "" },  
  targetUrl: { type: String, required: true },
  totalScore: { type: Number, default: 0 },
  vulnerabilities: { type: Array, default: [] },
  llmAnalysis: { type: String, default: 'AI analysis unavailable.' },
  createdAt: { type: Date, default: Date.now }
});

module.exports = mongoose.model('WebScan', WebScanSchema);