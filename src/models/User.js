const mongoose = require('mongoose');

const userSchema = new mongoose.Schema(
  {
    username: { type: String, required: true, unique: true },
    email: { type: String, required: true },
    password: { type: String, required: true }, // V6 - MD5 côté contrôleur
    role: { type: String, default: 'user' } // V3 - rôle piloté par l'entrée utilisateur
  },
  { timestamps: true }
);

module.exports = mongoose.model('User', userSchema);
