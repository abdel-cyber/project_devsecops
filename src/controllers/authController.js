const md5 = require('md5');
const jwt = require('jsonwebtoken');
const User = require('../models/User');
const { JWT_SECRET } = require('../middleware/auth');

exports.register = async (req, res) => {
  try {
    console.log('[register] payload:', req.body); // V8
    // V3 - aucune validation, V6 - hashage MD5 faible, V3 - rôle libre
    const user = await User.create({
      username: req.body.username,
      email: req.body.email,
      password: md5(req.body.password || ''),
      role: req.body.role || 'user'
    });

    return res.status(201).json({
      message: 'User created',
      user
    });
  } catch (err) {
    console.error('[register] error:', err);
    return res.status(500).json({
      error: err.message,
      stack: err.stack // V8
    });
  }
};

exports.login = async (req, res) => {
  try {
    console.log('[login] incoming payload:', req.body); // V8

    // V1 - NoSQL injection : si username ou password sont des objets, ils sont injectés tels quels
    const passwordCriteria =
      typeof req.body.password === 'string' ? md5(req.body.password) : req.body.password;

    const query = {
      username: req.body.username,
      password: passwordCriteria
    };

    const user = await User.findOne(query);

    if (!user) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    const token = jwt.sign(
      { id: user._id, username: user.username, role: user.role },
      JWT_SECRET,
      { expiresIn: '8h' }
    );

    console.log(`[login] success for ${user.username} with token: ${token}`); // V8

    return res.json({
      message: 'Login successful',
      token,
      user
    });
  } catch (err) {
    console.error('[login] error:', err);
    return res.status(500).json({
      error: err.message,
      stack: err.stack // V8
    });
  }
};
