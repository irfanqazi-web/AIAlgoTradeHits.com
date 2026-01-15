/**
 * Invention Controller - YouInvent.Tech Platform
 * Handles invention submissions, viewing, and management
 */

const { tables, query, insertRows, getNextId } = require('../config/bigquery.config');

// Get all inventions (public)
exports.getAllInventions = async (req, res) => {
  try {
    const { category, status, limit = 50 } = req.query;

    let sql = `SELECT * FROM \`${tables.inventions}\` WHERE 1=1`;
    const params = {};

    if (category) {
      sql += ` AND category = @category`;
      params.category = category;
    }
    if (status) {
      sql += ` AND status = @status`;
      params.status = status;
    }

    sql += ` ORDER BY submitted_at DESC LIMIT @limit`;
    params.limit = parseInt(limit);

    const inventions = await query(sql, params);
    res.json({ success: true, inventions, count: inventions.length });
  } catch (error) {
    console.error('Get inventions error:', error);
    res.status(500).json({ success: false, message: error.message });
  }
};

// Get invention by ID
exports.getInventionById = async (req, res) => {
  try {
    const { invention_id } = req.params;
    const sql = `SELECT * FROM \`${tables.inventions}\` WHERE invention_id = @invention_id`;
    const inventions = await query(sql, { invention_id: parseInt(invention_id) });

    if (inventions.length === 0) {
      return res.status(404).json({ success: false, message: 'Invention not found' });
    }

    res.json({ success: true, invention: inventions[0] });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
};

// Get inventions by user (authenticated)
exports.getMyInventions = async (req, res) => {
  try {
    const { user_id } = req.user;
    const sql = `SELECT * FROM \`${tables.inventions}\` WHERE inventor_id = @user_id ORDER BY submitted_at DESC`;
    const inventions = await query(sql, { user_id });

    res.json({ success: true, inventions, count: inventions.length });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
};

// Submit new invention (authenticated)
exports.submitInvention = async (req, res) => {
  try {
    const { user_id, email } = req.user;
    const {
      title,
      category,
      description,
      problem_solved,
      development_stage,
      investment_needed,
      unique_features,
      patent_status,
      prototype_ready
    } = req.body;

    if (!title || !category || !description) {
      return res.status(400).json({ success: false, message: 'Title, category, and description are required' });
    }

    const invention_id = await getNextId(tables.inventions, 'invention_id');
    const now = new Date().toISOString();

    await insertRows('inventions', [{
      invention_id,
      title,
      category,
      description,
      problem_solved: problem_solved || '',
      development_stage: development_stage || 'concept',
      investment_needed: parseInt(investment_needed) || 0,
      unique_features: unique_features || '',
      patent_status: patent_status || 'none',
      prototype_ready: prototype_ready || false,
      inventor_id: user_id,
      inventor_email: email,
      status: 'pending',
      views: 0,
      submitted_at: now,
      updated_at: now
    }]);

    res.json({
      success: true,
      message: 'Invention submitted successfully',
      invention_id
    });
  } catch (error) {
    console.error('Submit invention error:', error);
    res.status(500).json({ success: false, message: error.message });
  }
};

// Update invention (owner only)
exports.updateInvention = async (req, res) => {
  try {
    const { user_id } = req.user;
    const { invention_id } = req.params;
    const updates = req.body;

    // Verify ownership
    const checkSql = `SELECT inventor_id FROM \`${tables.inventions}\` WHERE invention_id = @invention_id`;
    const existing = await query(checkSql, { invention_id: parseInt(invention_id) });

    if (existing.length === 0) {
      return res.status(404).json({ success: false, message: 'Invention not found' });
    }
    if (existing[0].inventor_id !== user_id) {
      return res.status(403).json({ success: false, message: 'Not authorized to update this invention' });
    }

    const allowedFields = ['title', 'category', 'description', 'problem_solved', 'development_stage',
                          'investment_needed', 'unique_features', 'patent_status', 'prototype_ready'];

    const setClause = allowedFields
      .filter(f => updates[f] !== undefined)
      .map(f => `${f} = @${f}`)
      .join(', ');

    if (!setClause) {
      return res.status(400).json({ success: false, message: 'No valid fields to update' });
    }

    const sql = `UPDATE \`${tables.inventions}\` SET ${setClause}, updated_at = CURRENT_TIMESTAMP() WHERE invention_id = @invention_id`;
    await query(sql, { ...updates, invention_id: parseInt(invention_id) });

    res.json({ success: true, message: 'Invention updated successfully' });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
};

// Delete invention (owner only)
exports.deleteInvention = async (req, res) => {
  try {
    const { user_id, role } = req.user;
    const { invention_id } = req.params;

    // Verify ownership or admin
    const checkSql = `SELECT inventor_id FROM \`${tables.inventions}\` WHERE invention_id = @invention_id`;
    const existing = await query(checkSql, { invention_id: parseInt(invention_id) });

    if (existing.length === 0) {
      return res.status(404).json({ success: false, message: 'Invention not found' });
    }
    if (existing[0].inventor_id !== user_id && role !== 'admin') {
      return res.status(403).json({ success: false, message: 'Not authorized to delete this invention' });
    }

    const sql = `DELETE FROM \`${tables.inventions}\` WHERE invention_id = @invention_id`;
    await query(sql, { invention_id: parseInt(invention_id) });

    res.json({ success: true, message: 'Invention deleted successfully' });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
};

// Get invention categories
exports.getCategories = async (req, res) => {
  try {
    const categories = [
      { id: 'technology', name: 'Technology & Software', icon: 'laptop' },
      { id: 'healthcare', name: 'Healthcare & Medical', icon: 'heartbeat' },
      { id: 'agriculture', name: 'Agriculture & Food', icon: 'leaf' },
      { id: 'energy', name: 'Energy & Environment', icon: 'bolt' },
      { id: 'manufacturing', name: 'Manufacturing', icon: 'industry' },
      { id: 'consumer', name: 'Consumer Products', icon: 'shopping-bag' },
      { id: 'education', name: 'Education', icon: 'graduation-cap' },
      { id: 'transportation', name: 'Transportation', icon: 'car' },
      { id: 'other', name: 'Other', icon: 'lightbulb' }
    ];
    res.json({ success: true, categories });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
};

// Get invention stats
exports.getStats = async (req, res) => {
  try {
    const statsSql = `
      SELECT
        COUNT(*) as total_inventions,
        COUNT(DISTINCT inventor_id) as total_inventors,
        SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) as approved_inventions,
        SUM(investment_needed) as total_investment_sought
      FROM \`${tables.inventions}\`
    `;
    const stats = await query(statsSql);

    res.json({ success: true, stats: stats[0] || {} });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
};
