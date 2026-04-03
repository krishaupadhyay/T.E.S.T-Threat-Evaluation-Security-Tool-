const express = require("express");
const router = express.Router();
const auth = require("../middleware/auth");
const { analyzeEmail, getScans } = require("../controllers/phishing.controller");

router.post("/analyze", auth, analyzeEmail);
router.get("/scans", auth, getScans);

module.exports = router;