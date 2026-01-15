/**
 * Franchise Controller - HomeFranchise.Biz Platform
 * Handles franchise listings and applications
 */

const { tables, query, insertRows, getNextId } = require('../config/bigquery.config');

// Get all franchises (public)
exports.getAllFranchises = async (req, res) => {
  try {
    const { category, investment_range, limit = 50 } = req.query;

    let sql = `SELECT * FROM \`${tables.franchises}\` WHERE status = 'active'`;
    const params = {};

    if (category) {
      sql += ` AND category = @category`;
      params.category = category;
    }

    sql += ` ORDER BY created_at DESC LIMIT @limit`;
    params.limit = parseInt(limit);

    const franchises = await query(sql, params);
    res.json({ success: true, franchises, count: franchises.length });
  } catch (error) {
    console.error('Get franchises error:', error);
    res.status(500).json({ success: false, message: error.message });
  }
};

// Get franchise by ID
exports.getFranchiseById = async (req, res) => {
  try {
    const { franchise_id } = req.params;
    const sql = `SELECT * FROM \`${tables.franchises}\` WHERE franchise_id = @franchise_id`;
    const franchises = await query(sql, { franchise_id: parseInt(franchise_id) });

    if (franchises.length === 0) {
      return res.status(404).json({ success: false, message: 'Franchise not found' });
    }

    res.json({ success: true, franchise: franchises[0] });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
};

// Get my franchises (franchiser)
exports.getMyFranchises = async (req, res) => {
  try {
    const { user_id } = req.user;
    const sql = `SELECT * FROM \`${tables.franchises}\` WHERE owner_id = @user_id ORDER BY created_at DESC`;
    const franchises = await query(sql, { user_id });

    res.json({ success: true, franchises, count: franchises.length });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
};

// Create franchise listing (franchiser)
exports.createFranchise = async (req, res) => {
  try {
    const { user_id, email } = req.user;
    const {
      business_name,
      category,
      description,
      investment_min,
      investment_max,
      franchise_fee,
      royalty_percent,
      locations_available,
      training_provided,
      support_provided,
      requirements,
      contact_email,
      contact_phone,
      website
    } = req.body;

    if (!business_name || !category || !description) {
      return res.status(400).json({ success: false, message: 'Business name, category, and description are required' });
    }

    const franchise_id = await getNextId(tables.franchises, 'franchise_id');
    const now = new Date().toISOString();

    await insertRows('franchises', [{
      franchise_id,
      business_name,
      category,
      description,
      investment_min: parseInt(investment_min) || 0,
      investment_max: parseInt(investment_max) || 0,
      franchise_fee: parseInt(franchise_fee) || 0,
      royalty_percent: parseFloat(royalty_percent) || 0,
      locations_available: parseInt(locations_available) || 1,
      training_provided: training_provided || '',
      support_provided: support_provided || '',
      requirements: requirements || '',
      contact_email: contact_email || email,
      contact_phone: contact_phone || '',
      website: website || '',
      owner_id: user_id,
      owner_email: email,
      status: 'active',
      views: 0,
      applications_count: 0,
      created_at: now,
      updated_at: now
    }]);

    res.json({
      success: true,
      message: 'Franchise listing created successfully',
      franchise_id
    });
  } catch (error) {
    console.error('Create franchise error:', error);
    res.status(500).json({ success: false, message: error.message });
  }
};

// Update franchise (owner only)
exports.updateFranchise = async (req, res) => {
  try {
    const { user_id } = req.user;
    const { franchise_id } = req.params;
    const updates = req.body;

    // Verify ownership
    const checkSql = `SELECT owner_id FROM \`${tables.franchises}\` WHERE franchise_id = @franchise_id`;
    const existing = await query(checkSql, { franchise_id: parseInt(franchise_id) });

    if (existing.length === 0) {
      return res.status(404).json({ success: false, message: 'Franchise not found' });
    }
    if (existing[0].owner_id !== user_id) {
      return res.status(403).json({ success: false, message: 'Not authorized to update this franchise' });
    }

    const allowedFields = ['business_name', 'category', 'description', 'investment_min', 'investment_max',
                          'franchise_fee', 'royalty_percent', 'locations_available', 'training_provided',
                          'support_provided', 'requirements', 'contact_email', 'contact_phone', 'website', 'status'];

    const setClause = allowedFields
      .filter(f => updates[f] !== undefined)
      .map(f => `${f} = @${f}`)
      .join(', ');

    if (!setClause) {
      return res.status(400).json({ success: false, message: 'No valid fields to update' });
    }

    const sql = `UPDATE \`${tables.franchises}\` SET ${setClause}, updated_at = CURRENT_TIMESTAMP() WHERE franchise_id = @franchise_id`;
    await query(sql, { ...updates, franchise_id: parseInt(franchise_id) });

    res.json({ success: true, message: 'Franchise updated successfully' });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
};

// Delete franchise (owner only)
exports.deleteFranchise = async (req, res) => {
  try {
    const { user_id, role } = req.user;
    const { franchise_id } = req.params;

    // Verify ownership or admin
    const checkSql = `SELECT owner_id FROM \`${tables.franchises}\` WHERE franchise_id = @franchise_id`;
    const existing = await query(checkSql, { franchise_id: parseInt(franchise_id) });

    if (existing.length === 0) {
      return res.status(404).json({ success: false, message: 'Franchise not found' });
    }
    if (existing[0].owner_id !== user_id && role !== 'admin') {
      return res.status(403).json({ success: false, message: 'Not authorized to delete this franchise' });
    }

    const sql = `DELETE FROM \`${tables.franchises}\` WHERE franchise_id = @franchise_id`;
    await query(sql, { franchise_id: parseInt(franchise_id) });

    res.json({ success: true, message: 'Franchise deleted successfully' });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
};

// Apply for franchise (franchisee)
exports.applyForFranchise = async (req, res) => {
  try {
    const { user_id, email } = req.user;
    const { franchise_id } = req.params;
    const {
      applicant_name,
      phone,
      city,
      investment_capacity,
      experience,
      message
    } = req.body;

    if (!applicant_name || !phone || !city) {
      return res.status(400).json({ success: false, message: 'Name, phone, and city are required' });
    }

    // Check if franchise exists
    const checkSql = `SELECT franchise_id, business_name FROM \`${tables.franchises}\` WHERE franchise_id = @franchise_id`;
    const franchises = await query(checkSql, { franchise_id: parseInt(franchise_id) });

    if (franchises.length === 0) {
      return res.status(404).json({ success: false, message: 'Franchise not found' });
    }

    const application_id = await getNextId(tables.franchiseApplications, 'application_id');
    const now = new Date().toISOString();

    await insertRows('franchise_applications', [{
      application_id,
      franchise_id: parseInt(franchise_id),
      applicant_id: user_id,
      applicant_email: email,
      applicant_name,
      phone,
      city,
      investment_capacity: parseInt(investment_capacity) || 0,
      experience: experience || '',
      message: message || '',
      status: 'pending',
      created_at: now,
      updated_at: now
    }]);

    // Update applications count
    await query(`UPDATE \`${tables.franchises}\` SET applications_count = applications_count + 1 WHERE franchise_id = @franchise_id`,
      { franchise_id: parseInt(franchise_id) });

    res.json({
      success: true,
      message: 'Application submitted successfully',
      application_id
    });
  } catch (error) {
    console.error('Apply franchise error:', error);
    res.status(500).json({ success: false, message: error.message });
  }
};

// Get my applications (franchisee)
exports.getMyApplications = async (req, res) => {
  try {
    const { user_id } = req.user;
    const sql = `
      SELECT a.*, f.business_name, f.category
      FROM \`${tables.franchiseApplications}\` a
      JOIN \`${tables.franchises}\` f ON a.franchise_id = f.franchise_id
      WHERE a.applicant_id = @user_id
      ORDER BY a.created_at DESC
    `;
    const applications = await query(sql, { user_id });

    res.json({ success: true, applications, count: applications.length });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
};

// Get applications for my franchise (franchiser)
exports.getFranchiseApplications = async (req, res) => {
  try {
    const { user_id } = req.user;
    const { franchise_id } = req.params;

    // Verify ownership
    const checkSql = `SELECT owner_id FROM \`${tables.franchises}\` WHERE franchise_id = @franchise_id`;
    const existing = await query(checkSql, { franchise_id: parseInt(franchise_id) });

    if (existing.length === 0) {
      return res.status(404).json({ success: false, message: 'Franchise not found' });
    }
    if (existing[0].owner_id !== user_id) {
      return res.status(403).json({ success: false, message: 'Not authorized' });
    }

    const sql = `SELECT * FROM \`${tables.franchiseApplications}\` WHERE franchise_id = @franchise_id ORDER BY created_at DESC`;
    const applications = await query(sql, { franchise_id: parseInt(franchise_id) });

    res.json({ success: true, applications, count: applications.length });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
};

// Get franchise categories
exports.getCategories = async (req, res) => {
  try {
    const categories = [
      { id: 'food', name: 'Food & Beverage', icon: 'utensils' },
      { id: 'retail', name: 'Retail', icon: 'store' },
      { id: 'services', name: 'Services', icon: 'concierge-bell' },
      { id: 'health', name: 'Health & Fitness', icon: 'dumbbell' },
      { id: 'education', name: 'Education & Training', icon: 'graduation-cap' },
      { id: 'automotive', name: 'Automotive', icon: 'car' },
      { id: 'technology', name: 'Technology', icon: 'laptop' },
      { id: 'real-estate', name: 'Real Estate', icon: 'building' },
      { id: 'other', name: 'Other', icon: 'briefcase' }
    ];
    res.json({ success: true, categories });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
};

// Get franchise stats
exports.getStats = async (req, res) => {
  try {
    const statsSql = `
      SELECT
        COUNT(*) as total_franchises,
        COUNT(DISTINCT owner_id) as total_franchisers,
        SUM(applications_count) as total_applications,
        AVG(investment_min) as avg_investment_min
      FROM \`${tables.franchises}\`
      WHERE status = 'active'
    `;
    const stats = await query(statsSql);

    res.json({ success: true, stats: stats[0] || {} });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
};
