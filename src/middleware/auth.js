const jwt = require('jsonwebtoken');

// V2 - secret JWT en dur
const JWT_SECRET = 'ma-cle-secrete-en-dur-pour-le-lab';

module.exports = function auth(req, res, next) {
  try {
    const rawHeader = req.headers.authorization || req.headers['x-access-token'];

    if (!rawHeader) {
      return res.status(401).json({ error: 'Missing token' });
    }

    const token = rawHeader.startsWith('Bearer ') ? rawHeader.slice(7) : rawHeader;
    const decoded = jwt.verify(token, JWT_SECRET);

    req.user = decoded;
    next();
  } catch (err) {
    console.error('[auth] Token error:', err.message); // V8
    return res.status(401).json({ error: err.message }); // V8 - trop bavard
  }
};

module.exports.JWT_SECRET = JWT_SECRET;
