const mongoose = require('mongoose');

const noteSchema = new mongoose.Schema(
  {
    title: { type: String, required: true },
    content: { type: String, required: true },
    author: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
    isPublic: { type: Boolean, default: true } // V3/V4 - trop permissif par défaut
  },
  { timestamps: true }
);

module.exports = mongoose.model('Note', noteSchema);
