const express = require("express");
const router = express.Router();
const { protect, adminOnly } = require("../middleware/auth");
const { analyzeEmail, getScans, getAllScans } = require("../controllers/phishing.controller");

router.post("/analyze", protect, analyzeEmail);
router.get("/scans",     protect,            getScans);
router.get("/all-scans", protect, adminOnly, getAllScans);

module.exports = router;