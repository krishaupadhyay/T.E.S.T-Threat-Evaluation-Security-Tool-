const express = require('express');
const router = express.Router();
const axios = require('axios');
const WebScan = require('../models/webscan');
const { protect } = require('../middleware/auth');

// Run scan + save to DB
router.post('/webscan', protect, async (req, res) => {
  const { targetUrl } = req.body;

  if (!targetUrl) {
    return res.status(400).json({ error: 'targetUrl is required in request body' });
  }

  if (!targetUrl.startsWith('http://') && !targetUrl.startsWith('https://')) {
    return res.status(400).json({ error: 'URL must include http:// or https://' });
  }

  try {
    const pythonRes = await axios.post('http://localhost:5002/scan', {
      url: targetUrl
    });

    const { total_score, results, llm_analysis } = pythonRes.data;

    const scan = new WebScan({
      userId: req.user.id,
      userEmail: req.user.email,   // ← fix: populate actual user email
      targetUrl,
      totalScore: total_score,
      vulnerabilities: results,
      llmAnalysis: llm_analysis
    });

    await scan.save();

    res.json({
      success: true,
      results: results,
      total_score: total_score,
      llm_analysis: llm_analysis
    });

  } catch (err) {
    console.error('WebScan error:', err.response?.data || err.message);
    res.status(500).json({ error: 'Scan failed. Is Flask running on port 5002?' });
  }
});

// Get all past scans for logged-in user
router.get('/webscans', protect, async (req, res) => {
  try {
    const scans = await WebScan.find({ userId: req.user.id }).sort({ createdAt: -1 });
    res.json(scans);
  } catch (err) {
    res.status(500).json({ error: 'Could not fetch scans' });
  }
});

module.exports = router;