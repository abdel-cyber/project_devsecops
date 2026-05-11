const express = require('express');
const auth = require('../middleware/auth');
const {
  listNotes,
  createNote,
  getNoteById,
  updateNote,
  deleteNote,
  searchNotes
} = require('../controllers/noteController');

const router = express.Router();

router.use(auth);
router.get('/', listNotes);
router.post('/', createNote);
router.get('/search', searchNotes);
router.get('/:id', getNoteById);
router.put('/:id', updateNote);
router.delete('/:id', deleteNote);

module.exports = router;
