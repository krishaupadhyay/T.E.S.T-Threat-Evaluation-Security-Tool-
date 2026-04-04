const axios = require("axios");
const Scan = require("../models/Scan");

exports.analyzeEmail = async (req, res) => {
  try {
    const { email, deepScan, email_headers } = req.body;
    const deepScanBool = deepScan === "true" || deepScan === true;

    const hasBody = email && email.trim() !== "";
    const hasHeaders = email_headers && email_headers.trim() !== "";

    if (!hasBody && !hasHeaders) {
      return res.status(400).json({ message: "Provide email body or headers" });
    }

    const ipAddress = req.headers["x-forwarded-for"]?.split(",")[0].trim()
      || req.socket.remoteAddress || "";

    // call Flask AI
    const aiRes = await axios.post("http://127.0.0.1:5001/predict", {
      email: email || "",
      deep_scan: deepScanBool,
    });

    // save to DB — including userEmail
    const saved = await Scan.create({
      userId: req.user._id,
      userEmail: req.user.email,    // ← store user's email per scan
      type: "email",
      input: email || "",
      headers: email_headers || "",
      deepScan: deepScanBool,
      ipAddress,
      result: {
        label: aiRes?.data?.result || "Unknown",
        confidence: aiRes?.data?.confidence || 0,
        flags: Array.isArray(aiRes?.data?.flags) ? aiRes.data.flags : [],
        explanation: aiRes?.data?.explanation || ""
      }
    });

    res.status(200).json(saved);   // ← this was missing before

  } catch (err) {
    console.error("ERROR:", err.message);
    res.status(500).json({ message: "AI service error", error: err.message });
  }
};

exports.getScans = async (req, res) => {
  try {
    const scans = await Scan.find({ userId: req.user._id })
      .sort({ createdAt: -1 })
      .limit(20);
    res.status(200).json(scans);
  } catch (err) {
    res.status(500).json({ message: "Error fetching scans", error: err.message });
  }
};

// ── ADMIN ONLY ─────────────────────────────────────────────────────────────
// Returns all scans across every user, sorted newest first (max 50)
exports.getAllScans = async (req, res) => {
  try {
    const scans = await Scan.find({})
      .sort({ createdAt: -1 })
      .limit(50);
    res.status(200).json(scans);
  } catch (err) {
    res.status(500).json({ message: "Error fetching all scans", error: err.message });
  }
};