// config/db.js
const mongoose = require('mongoose');//This imports Mongoose from the node_modules folder.

const connectDB = async () => {
    try {
        const uri = process.env.MONGO_URI;//URI = Uniform Resource Identifier
        if (!uri) {
            throw new Error('MONGO_URI is not defined in .env');
        }
        await mongoose.connect(uri);  // no options needed in Mongoose 7+
        console.log('MongoDB connected successfully!');
    } catch (err) {
        console.error('MongoDB connection failed:', err.message);
        process.exit(1); // stop server if DB fails
    }
};

module.exports = connectDB;//"I am exporting the connectDB function so other files can use it."
