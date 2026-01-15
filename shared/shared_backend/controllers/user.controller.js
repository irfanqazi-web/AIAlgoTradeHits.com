/**
 * User Controller - Authentication and User Management
 * Shared across all platforms
 */

const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const { tables, query, insertRows, getNextId } = require('../config/bigquery.config');

const JWT_SECRET = process.env.JWT_SECRET || 'unified-platform-secret-key-2024';
const JWT_EXPIRES_IN = '7d';

exports.signup = async (req, res) => {
  try {
    const { username, email, password, role = 'user', platform = 'kaamyabpakistan' } = req.body;

    if (!username || !email || !password) {
      return res.status(400).json({ success: false, message: 'All fields required' });
    }

    // Check if user exists
    const checkSql = `SELECT user_id FROM \`${tables.users}\` WHERE email = @email`;
    const existing = await query(checkSql, { email });
    if (existing.length > 0) {
      return res.status(400).json({ success: false, message: 'Email already registered' });
    }

    // Hash password
    const password_hash = await bcrypt.hash(password, 10);
    const user_id = await getNextId(tables.users, 'user_id');
    const now = new Date().toISOString();

    await insertRows('users', [{
      user_id,
      username,
      email,
      password_hash,
      role,
      platform,
      is_active: true,
      created_at: now,
      updated_at: now
    }]);

    // Generate token
    const token = jwt.sign({ user_id, email, role, platform }, JWT_SECRET, { expiresIn: JWT_EXPIRES_IN });

    res.json({
      success: true,
      message: 'User registered successfully',
      token,
      user: { user_id, username, email, role, platform }
    });
  } catch (error) {
    console.error('Signup error:', error);
    res.status(500).json({ success: false, message: error.message });
  }
};

exports.signin = async (req, res) => {
  try {
    const { email, password } = req.body;

    if (!email || !password) {
      return res.status(400).json({ success: false, message: 'Email and password required' });
    }

    // Find user
    const sql = `SELECT * FROM \`${tables.users}\` WHERE email = @email AND is_active = true`;
    const users = await query(sql, { email });

    if (users.length === 0) {
      return res.status(401).json({ success: false, message: 'Invalid credentials' });
    }

    const user = users[0];

    // Verify password
    const validPassword = await bcrypt.compare(password, user.password_hash);
    if (!validPassword) {
      return res.status(401).json({ success: false, message: 'Invalid credentials' });
    }

    // Generate token
    const token = jwt.sign(
      { user_id: user.user_id, email: user.email, role: user.role, platform: user.platform },
      JWT_SECRET,
      { expiresIn: JWT_EXPIRES_IN }
    );

    res.json({
      success: true,
      message: 'Login successful',
      token,
      user: {
        user_id: user.user_id,
        username: user.username,
        email: user.email,
        role: user.role,
        platform: user.platform
      }
    });
  } catch (error) {
    console.error('Signin error:', error);
    res.status(500).json({ success: false, message: error.message });
  }
};

exports.getProfile = async (req, res) => {
  try {
    const { user_id } = req.user;
    const sql = `SELECT user_id, username, email, role, platform, created_at
      FROM \`${tables.users}\` WHERE user_id = @user_id`;
    const users = await query(sql, { user_id });

    if (users.length === 0) {
      return res.status(404).json({ success: false, message: 'User not found' });
    }

    res.json({ success: true, user: users[0] });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
};

exports.updateProfile = async (req, res) => {
  try {
    const { user_id } = req.user;
    const { username, email } = req.body;

    const sql = `UPDATE \`${tables.users}\`
      SET username = @username, email = @email, updated_at = CURRENT_TIMESTAMP()
      WHERE user_id = @user_id`;

    await query(sql, { user_id, username, email });
    res.json({ success: true, message: 'Profile updated' });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
};

exports.changePassword = async (req, res) => {
  try {
    const { user_id } = req.user;
    const { current_password, new_password } = req.body;

    // Get current password hash
    const sql = `SELECT password_hash FROM \`${tables.users}\` WHERE user_id = @user_id`;
    const users = await query(sql, { user_id });

    if (users.length === 0) {
      return res.status(404).json({ success: false, message: 'User not found' });
    }

    // Verify current password
    const validPassword = await bcrypt.compare(current_password, users[0].password_hash);
    if (!validPassword) {
      return res.status(401).json({ success: false, message: 'Current password incorrect' });
    }

    // Update password
    const password_hash = await bcrypt.hash(new_password, 10);
    const updateSql = `UPDATE \`${tables.users}\`
      SET password_hash = @password_hash, updated_at = CURRENT_TIMESTAMP()
      WHERE user_id = @user_id`;

    await query(updateSql, { user_id, password_hash });
    res.json({ success: true, message: 'Password changed successfully' });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
};

// Middleware to verify JWT token
exports.authMiddleware = (req, res, next) => {
  try {
    const authHeader = req.headers.authorization;
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({ success: false, message: 'No token provided' });
    }

    const token = authHeader.split(' ')[1];
    const decoded = jwt.verify(token, JWT_SECRET);
    req.user = decoded;
    next();
  } catch (error) {
    res.status(401).json({ success: false, message: 'Invalid token' });
  }
};

// Middleware to check admin role
exports.adminMiddleware = (req, res, next) => {
  if (req.user.role !== 'admin') {
    return res.status(403).json({ success: false, message: 'Admin access required' });
  }
  next();
};
