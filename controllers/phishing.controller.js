const axios = require("axios");//Axios is used to send HTTP requests.
const Scan = require("../models/Scan");

exports.analyzeEmail = async (req, res) => {
  try {
    console.log("BODY:", req.body);
    const { emailText } = req.body;

    // 🔴 VALIDATION
    if (!emailText) {
      return res.status(400).json({
        message: "emailText is required"
      });
    }
    const aiRes = await axios.post("http://127.0.0.1:5001/predict", {
  email: emailText
});

    // // 🔹 MOCK AI RESPONSE
    // const aiRes = {
    //   data: {
    //     risk: 75,
    //     label: "Phishing",
    //     explanation: "Urgent language and suspicious intent detected"
    //   }
    // };

    // ✅ SAVE MATCHING SCHEMA
    const saved = await Scan.create({
      type: "email",        // REQUIRED
      input: emailText,     // REQUIRED
      result: aiRes.data      // REQUIRED
    });
    res.status(200).json(saved);

  } catch (err) {
  console.error("ERROR 👉", err.message);
  res.status(500).json({
    message: "AI service error",
    error: err.message
  });
}
};
