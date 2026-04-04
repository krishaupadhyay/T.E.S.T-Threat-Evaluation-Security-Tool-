//creation part

const express = require("express");//imports the Express framework.
const cors = require("cors"); //allow diff port req.. Cross-Origin Resource Sharing.---“Allow other origins to access this API.”
require("dotenv").config();//nodejslib--allow us to store sensitive info outside of source key
const cookieParser = require("cookie-parser");//to read cookies form browser
const connectDB = require("./config/db"); // fetch config->db file and run connectdb function

const app = express(); //app now represents our backend server.

// app.use(cors({
//   origin: "http://localhost:3000",
//   origin:"http://loacalhost:5000"
// }));

//implimentation
// Connect to MongoDB
connectDB();

// Middleware
// app.use(cors());
app.use(cors({
  origin: "http://localhost:8080", // your frontend
  credentials: true
}));


app.use(express.json());//req.body
app.use(cookieParser());//backend can read cookies set by browaser
// Test route /root 
app.get("/", (req, res) => {
  res.send("Backend is running!");
});

// Import routes (phing routes)
app.use("/api/phishing", require("./routes/phishing.routes"));//now this route start form api/phishing

//authentication api
app.use("/api/auth", require("./routes/auth.routes"));

app.use("/api", require("./routes/webscan.routes")); 

// Start server
// console.log("BODY:", req.body);

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});


//API = Application Programming Interface--way for fronted or other apps to talk to ur backend 