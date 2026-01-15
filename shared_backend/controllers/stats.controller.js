/**
 * Stats Controller - Dashboard and Statistics
 * Shared across platforms
 */

const { tables, query } = require('../config/bigquery.config');

// Get dashboard stats for KaamyabPakistan
exports.getDashboardStats = async (req, res) => {
  try {
    const stats = {
      total_projects: 0,
      total_opportunities: 0,
      total_users: 0,
      success_stories: 0
    };

    try {
      const projectsSql = `SELECT COUNT(*) as count FROM \`${tables.mainProjects}\``;
      const projectsResult = await query(projectsSql);
      stats.total_projects = projectsResult[0]?.count || 0;

      const usersSql = `SELECT COUNT(*) as count FROM \`${tables.users}\``;
      const usersResult = await query(usersSql);
      stats.total_users = usersResult[0]?.count || 0;
    } catch (e) {
      // Tables might not exist
    }

    res.json({ success: true, stats });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
};

// Get categories
exports.getCategories = async (req, res) => {
  try {
    const sql = `SELECT * FROM \`${tables.categories}\` ORDER BY category_id`;
    const categories = await query(sql);
    res.json({ success: true, categories });
  } catch (error) {
    // Return default categories if table doesn't exist
    const defaultCategories = [
      { category_id: 1, name: 'Agriculture', icon: 'leaf' },
      { category_id: 2, name: 'Manufacturing', icon: 'industry' },
      { category_id: 3, name: 'Services', icon: 'concierge-bell' },
      { category_id: 4, name: 'Technology', icon: 'laptop' },
      { category_id: 5, name: 'Retail', icon: 'store' }
    ];
    res.json({ success: true, categories: defaultCategories });
  }
};

// Get opportunities
exports.getOpportunities = async (req, res) => {
  try {
    const sql = `SELECT * FROM \`${tables.opportunities}\` ORDER BY created_at DESC LIMIT 20`;
    const opportunities = await query(sql);
    res.json({ success: true, opportunities });
  } catch (error) {
    res.json({ success: true, opportunities: [] });
  }
};

// Get programs
exports.getPrograms = async (req, res) => {
  try {
    const sql = `SELECT * FROM \`${tables.programs}\` ORDER BY program_id`;
    const programs = await query(sql);
    res.json({ success: true, programs });
  } catch (error) {
    res.json({ success: true, programs: [] });
  }
};

// Get success stories
exports.getSuccessStories = async (req, res) => {
  try {
    const sql = `SELECT * FROM \`${tables.successStories}\` ORDER BY created_at DESC LIMIT 10`;
    const stories = await query(sql);
    res.json({ success: true, stories });
  } catch (error) {
    res.json({ success: true, stories: [] });
  }
};

// Search projects
exports.searchProjects = async (req, res) => {
  try {
    const { q, category, limit = 20 } = req.query;

    if (!q) {
      return res.status(400).json({ success: false, message: 'Search query required' });
    }

    const sql = `
      SELECT * FROM \`${tables.projectItems}\`
      WHERE LOWER(sub_name) LIKE LOWER(@searchTerm)
         OR LOWER(sub_description) LIKE LOWER(@searchTerm)
      LIMIT @limit
    `;

    const projects = await query(sql, {
      searchTerm: `%${q}%`,
      limit: parseInt(limit)
    });

    res.json({ success: true, projects, count: projects.length });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
};

// Get investor types
exports.getInvestorTypes = async (req, res) => {
  try {
    const investorTypes = [
      {
        type_id: 'angel',
        name: 'Angel Investors',
        description: 'Individual investors who provide capital for startups',
        investment_range: '$10,000 - $500,000',
        icon: 'user-tie'
      },
      {
        type_id: 'impact',
        name: 'Impact Investors',
        description: 'Investors focused on social and environmental impact',
        investment_range: '$50,000 - $5,000,000',
        icon: 'hands-helping'
      },
      {
        type_id: 'institutional',
        name: 'Institutional Investors',
        description: 'VC firms, banks, and large investment organizations',
        investment_range: '$500,000+',
        icon: 'building'
      }
    ];

    res.json({ success: true, investorTypes });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
};

// Register investor interest
exports.registerInvestorInterest = async (req, res) => {
  try {
    const { name, email, investor_type, investment_range, interests, message } = req.body;

    if (!name || !email || !investor_type) {
      return res.status(400).json({ success: false, message: 'Name, email, and investor type are required' });
    }

    // For now, just acknowledge - actual storage can be implemented when table exists
    res.json({
      success: true,
      message: 'Thank you for your interest! Our team will contact you shortly.'
    });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
};
