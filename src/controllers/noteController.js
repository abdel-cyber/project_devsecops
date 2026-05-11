const Note = require('../models/Note');

exports.listNotes = async (req, res) => {
  try {
    // V4 - trop permissif : tous les utilisateurs voient toutes les notes
    const notes = await Note.find().populate('author', 'username email role');
    res.json(notes);
  } catch (err) {
    console.error('[listNotes] error:', err);
    res.status(500).json({ error: err.message, stack: err.stack });
  }
};

exports.createNote = async (req, res) => {
  try {
    console.log('[createNote] payload:', req.body); // V8

    // V3 - aucune validation, V4 - isPublic laissé libre
    const note = await Note.create({
      title: req.body.title,
      content: req.body.content,
      isPublic: req.body.isPublic !== undefined ? req.body.isPublic : true,
      author: req.user.id
    });

    res.status(201).json(note);
  } catch (err) {
    console.error('[createNote] error:', err);
    res.status(500).json({ error: err.message, stack: err.stack });
  }
};

exports.getNoteById = async (req, res) => {
  try {
    // V4 - IDOR : aucune vérification que la note appartient à l'utilisateur courant
    const note = await Note.findById(req.params.id).populate('author', 'username email role');

    if (!note) {
      return res.status(404).json({ error: 'Note not found' });
    }

    res.json(note);
  } catch (err) {
    console.error('[getNoteById] error:', err);
    res.status(500).json({ error: err.message, stack: err.stack });
  }
};

exports.updateNote = async (req, res) => {
  try {
    // V4 - IDOR : mise à jour sans contrôle d'autorisation
    const note = await Note.findByIdAndUpdate(req.params.id, req.body, {
      new: true,
      runValidators: false
    });

    if (!note) {
      return res.status(404).json({ error: 'Note not found' });
    }

    res.json(note);
  } catch (err) {
    console.error('[updateNote] error:', err);
    res.status(500).json({ error: err.message, stack: err.stack });
  }
};

exports.deleteNote = async (req, res) => {
  try {
    // V4 - IDOR
    const note = await Note.findByIdAndDelete(req.params.id);

    if (!note) {
      return res.status(404).json({ error: 'Note not found' });
    }

    res.json({ message: 'Note deleted', note });
  } catch (err) {
    console.error('[deleteNote] error:', err);
    res.status(500).json({ error: err.message, stack: err.stack });
  }
};

exports.searchNotes = async (req, res) => {
  try {
    const rawQuery = req.query.q || '';
    let titleFilter;

    try {
      // V1 - NoSQL injection via JSON.parse depuis la query string
      titleFilter = JSON.parse(rawQuery);
    } catch (e) {
      titleFilter = { $regex: rawQuery, $options: 'i' };
    }

    const notes = await Note.find({ title: titleFilter }).populate('author', 'username email role');
    res.json(notes);
  } catch (err) {
    console.error('[searchNotes] error:', err);
    res.status(500).json({ error: err.message, stack: err.stack });
  }
};
