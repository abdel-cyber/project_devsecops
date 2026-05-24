const mongoose = require('mongoose');

// V2 - secret / URI en dur + log verbeux
const DEFAULT_MONGO_URI = process.env.MONGO_URI || 'mongodb://localhost:27017/secnotes';
let currentUri = DEFAULT_MONGO_URI;

async function connectDB() {
  if (mongoose.connection.readyState === 1) {
    return;
  }

  console.log('[db] Connecting to MongoDB with URI:', currentUri);
  await mongoose.connect(currentUri, {
    autoIndex: true
  });
  console.log('[db] MongoDB connected');
}

async function disconnectDB() {
  if (mongoose.connection.readyState !== 0) {
    await mongoose.disconnect();
  }
}

function setMongoUri(uri) {
  currentUri = uri;
}

module.exports = {
  connectDB,
  disconnectDB,
  setMongoUri,
  DEFAULT_MONGO_URI
};
