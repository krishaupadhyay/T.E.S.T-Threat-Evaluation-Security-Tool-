const express = require("express");
const router = express.Router();

const { analyzeEmail } = require("../controllers/phishing.controller");

router.post("/analyze", analyzeEmail);

module.exports = router;
