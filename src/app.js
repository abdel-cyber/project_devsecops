const express = require('express');
const cors = require('cors');
const { connectDB } = require('./config/db');
const path = require('path');
const authRoutes = require('./routes/authRoutes');
const noteRoutes = require('./routes/noteRoutes');
const Note = require('./models/Note'); // Importation du modèle pour le sabotage

const app = express();
const PORT = process.env.PORT || 3000;

// V10 - CORS trop permissif
app.use(cors({ origin: '*' }));
app.use(express.json({ limit: '5mb' }));
app.use(express.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, '..', 'public')));

app.use((req, res, next) => {
  // V8 - logs trop verbeux
  console.log(`[request] ${req.method} ${req.url}`);
  if (Object.keys(req.body || {}).length > 0) {
    // 🟢 CORRECTION : Remplacement de print par console.log pour éviter le ReferenceError
    console.log('[request] body:', req.body);
  }
  next();
});

app.get('/api', (req, res) => {
  res.json({
    app: 'SecNotes',
    mode: 'vulnerable-lab',
    endpoints: {
      register: 'POST /api/auth/register',
      login: 'POST /api/auth/login',
      notes: 'GET|POST /api/notes',
      noteById: 'GET|PUT|DELETE /api/notes/:id',
      search: 'GET /api/notes/search?q=...'
    }
  });
});

app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

 /// 🚨 SABOTAGE POUR LA SOUTENANCE (Route publique sans middleware)
app.get('/api/notes/search', async (req, res) => {
   try {
     const query = req.query.q || '';
     const Note = require('./models/Note'); // Assure-toi que le modèle est importé
     const notes = await Note.find({ title: new RegExp(query, 'i') });
     return res.status(200).json(notes);
   } catch (err) {
     return res.status(500).json({ error: err.message });
   }
});

// Routes normales sécurisées
app.use('/api/auth', authRoutes);
app.use('/api/notes', noteRoutes); 

app.use((err, req, res, next) => {
  console.error('[app] unhandled error:', err);
  res.status(500).json({
    error: err.message,
    stack: err.stack
  });
});

if (require.main === module) {
  connectDB()
    .then(() => {
      app.listen(PORT, () => {
        console.log(`[app] SecNotes listening on port ${PORT}`);
      });
    })
    .catch((err) => {
      console.error('[app] Startup failure:', err);
      process.exit(1);
    });
}

module.exports = app;