/**
 * Consulting Controller - NoCodeAI.Cloud Platform
 * Handles AI consulting requests and client management
 */

const { tables, query, insertRows, getNextId } = require('../config/bigquery.config');

// Get consultants (public)
exports.getConsultants = async (req, res) => {
  try {
    // Return static consultant data
    const consultants = [
      {
        consultant_id: 1,
        name: 'Irfan Haq',
        title: 'Founder & Chief AI Strategist',
        location: 'Pakistan / Global',
        avatar: 'IH',
        bio: 'With 15+ years of experience in technology leadership and AI implementation, Irfan has helped businesses across multiple industries harness the power of artificial intelligence. His expertise spans enterprise architecture, machine learning, and strategic AI adoption.',
        skills: ['AI Strategy', 'Machine Learning', 'FinTech', 'Trading Systems', 'Google Cloud', 'Enterprise Architecture'],
        stats: {
          years_experience: 15,
          projects_completed: 50,
          value_created: '$10M+'
        },
        specializations: ['Financial AI Systems', 'Predictive Analytics', 'Enterprise Automation', 'Cloud Architecture']
      },
      {
        consultant_id: 2,
        name: 'Saleem Ahmad',
        title: 'Senior AI Solutions Architect',
        location: 'Pakistan',
        avatar: 'SA',
        bio: 'Saleem brings deep expertise in building practical AI solutions that solve real business problems. His focus on data engineering and ML operations ensures that AI implementations are not just innovative but also sustainable and scalable.',
        skills: ['Python', 'TensorFlow', 'Data Engineering', 'MLOps', 'BigQuery', 'Cloud Functions'],
        stats: {
          years_experience: 10,
          projects_completed: 35,
          value_created: '$5M+'
        },
        specializations: ['Data Pipeline Architecture', 'ML Model Deployment', 'Business Intelligence', 'Process Automation']
      }
    ];

    res.json({ success: true, consultants });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
};

// Get AI services (public)
exports.getServices = async (req, res) => {
  try {
    const services = [
      {
        service_id: 1,
        name: 'AI Strategy Consultation',
        description: 'Comprehensive assessment and roadmap for AI adoption in your organization',
        price_from: 2500,
        duration: '2-4 weeks',
        icon: 'brain',
        features: ['Current State Assessment', 'AI Opportunity Identification', 'ROI Analysis', 'Implementation Roadmap']
      },
      {
        service_id: 2,
        name: 'Custom Chatbot Development',
        description: 'Build intelligent chatbots for customer service, sales, or internal operations',
        price_from: 5000,
        duration: '4-8 weeks',
        icon: 'robot',
        features: ['Custom Training', 'Multi-platform Integration', 'Analytics Dashboard', 'Continuous Learning']
      },
      {
        service_id: 3,
        name: 'Predictive Analytics',
        description: 'Data-driven insights to forecast trends and optimize decision-making',
        price_from: 8000,
        duration: '6-12 weeks',
        icon: 'chart-line',
        features: ['Data Analysis', 'ML Model Development', 'Dashboard Creation', 'Ongoing Optimization']
      },
      {
        service_id: 4,
        name: 'Process Automation',
        description: 'Automate repetitive tasks and workflows using AI-powered solutions',
        price_from: 4000,
        duration: '3-6 weeks',
        icon: 'cogs',
        features: ['Workflow Analysis', 'Automation Design', 'Implementation', 'Training & Support']
      },
      {
        service_id: 5,
        name: 'Computer Vision Solutions',
        description: 'Image and video analysis for quality control, security, or analytics',
        price_from: 10000,
        duration: '8-16 weeks',
        icon: 'eye',
        features: ['Use Case Analysis', 'Model Training', 'Integration', 'Performance Tuning']
      },
      {
        service_id: 6,
        name: 'AI Training & Workshops',
        description: 'Upskill your team on AI concepts, tools, and best practices',
        price_from: 1500,
        duration: '1-5 days',
        icon: 'graduation-cap',
        features: ['Customized Curriculum', 'Hands-on Exercises', 'Certification', 'Follow-up Support']
      }
    ];

    res.json({ success: true, services });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
};

// Submit consulting request (public or authenticated)
exports.submitRequest = async (req, res) => {
  try {
    const {
      name,
      email,
      company,
      phone,
      service_type,
      budget_range,
      timeline,
      description,
      preferred_consultant
    } = req.body;

    if (!name || !email || !service_type || !description) {
      return res.status(400).json({
        success: false,
        message: 'Name, email, service type, and description are required'
      });
    }

    const request_id = await getNextId(tables.consultingRequests, 'request_id');
    const now = new Date().toISOString();

    // Get user_id if authenticated
    const user_id = req.user?.user_id || null;

    await insertRows('consulting_requests', [{
      request_id,
      user_id,
      name,
      email,
      company: company || '',
      phone: phone || '',
      service_type,
      budget_range: budget_range || 'not_specified',
      timeline: timeline || 'flexible',
      description,
      preferred_consultant: preferred_consultant || null,
      status: 'new',
      created_at: now,
      updated_at: now
    }]);

    res.json({
      success: true,
      message: 'Your request has been submitted. We will contact you within 24-48 hours.',
      request_id
    });
  } catch (error) {
    console.error('Submit request error:', error);
    res.status(500).json({ success: false, message: error.message });
  }
};

// Get my requests (authenticated)
exports.getMyRequests = async (req, res) => {
  try {
    const { user_id } = req.user;
    const sql = `SELECT * FROM \`${tables.consultingRequests}\` WHERE user_id = @user_id ORDER BY created_at DESC`;
    const requests = await query(sql, { user_id });

    res.json({ success: true, requests, count: requests.length });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
};

// Get all requests (admin only)
exports.getAllRequests = async (req, res) => {
  try {
    const { status, limit = 50 } = req.query;

    let sql = `SELECT * FROM \`${tables.consultingRequests}\` WHERE 1=1`;
    const params = {};

    if (status) {
      sql += ` AND status = @status`;
      params.status = status;
    }

    sql += ` ORDER BY created_at DESC LIMIT @limit`;
    params.limit = parseInt(limit);

    const requests = await query(sql, params);
    res.json({ success: true, requests, count: requests.length });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
};

// Update request status (admin only)
exports.updateRequestStatus = async (req, res) => {
  try {
    const { request_id } = req.params;
    const { status, notes, assigned_consultant } = req.body;

    if (!status) {
      return res.status(400).json({ success: false, message: 'Status is required' });
    }

    let sql = `UPDATE \`${tables.consultingRequests}\` SET status = @status, updated_at = CURRENT_TIMESTAMP()`;
    const params = { request_id: parseInt(request_id), status };

    if (notes !== undefined) {
      sql += `, admin_notes = @notes`;
      params.notes = notes;
    }
    if (assigned_consultant !== undefined) {
      sql += `, assigned_consultant = @assigned_consultant`;
      params.assigned_consultant = assigned_consultant;
    }

    sql += ` WHERE request_id = @request_id`;
    await query(sql, params);

    res.json({ success: true, message: 'Request updated successfully' });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
};

// Get request by ID
exports.getRequestById = async (req, res) => {
  try {
    const { request_id } = req.params;
    const { user_id, role } = req.user;

    let sql = `SELECT * FROM \`${tables.consultingRequests}\` WHERE request_id = @request_id`;

    // Non-admins can only see their own requests
    if (role !== 'admin') {
      sql += ` AND user_id = @user_id`;
    }

    const requests = await query(sql, { request_id: parseInt(request_id), user_id });

    if (requests.length === 0) {
      return res.status(404).json({ success: false, message: 'Request not found' });
    }

    res.json({ success: true, request: requests[0] });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
};

// Create client project (admin only)
exports.createProject = async (req, res) => {
  try {
    const {
      request_id,
      client_name,
      client_email,
      project_name,
      description,
      service_type,
      budget,
      start_date,
      estimated_end_date,
      assigned_consultant
    } = req.body;

    if (!project_name || !client_name) {
      return res.status(400).json({ success: false, message: 'Project name and client name are required' });
    }

    const project_id = await getNextId(tables.clientProjects, 'project_id');
    const now = new Date().toISOString();

    await insertRows('client_projects', [{
      project_id,
      request_id: request_id || null,
      client_name,
      client_email: client_email || '',
      project_name,
      description: description || '',
      service_type: service_type || 'general',
      budget: parseFloat(budget) || 0,
      start_date: start_date || now,
      estimated_end_date: estimated_end_date || null,
      assigned_consultant: assigned_consultant || null,
      status: 'active',
      created_at: now,
      updated_at: now
    }]);

    // Update request status if linked
    if (request_id) {
      await query(`UPDATE \`${tables.consultingRequests}\` SET status = 'converted', updated_at = CURRENT_TIMESTAMP() WHERE request_id = @request_id`,
        { request_id: parseInt(request_id) });
    }

    res.json({
      success: true,
      message: 'Project created successfully',
      project_id
    });
  } catch (error) {
    console.error('Create project error:', error);
    res.status(500).json({ success: false, message: error.message });
  }
};

// Get all projects (admin only)
exports.getAllProjects = async (req, res) => {
  try {
    const { status, limit = 50 } = req.query;

    let sql = `SELECT * FROM \`${tables.clientProjects}\` WHERE 1=1`;
    const params = {};

    if (status) {
      sql += ` AND status = @status`;
      params.status = status;
    }

    sql += ` ORDER BY created_at DESC LIMIT @limit`;
    params.limit = parseInt(limit);

    const projects = await query(sql, params);
    res.json({ success: true, projects, count: projects.length });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
};

// Get platform stats
exports.getStats = async (req, res) => {
  try {
    // Return static stats since tables might not exist yet
    const stats = {
      total_requests: 0,
      active_projects: 0,
      consultants: 2,
      services: 6
    };

    try {
      const requestsSql = `SELECT COUNT(*) as count FROM \`${tables.consultingRequests}\``;
      const requestsResult = await query(requestsSql);
      stats.total_requests = requestsResult[0]?.count || 0;

      const projectsSql = `SELECT COUNT(*) as count FROM \`${tables.clientProjects}\` WHERE status = 'active'`;
      const projectsResult = await query(projectsSql);
      stats.active_projects = projectsResult[0]?.count || 0;
    } catch (e) {
      // Tables might not exist yet
    }

    res.json({ success: true, stats });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
};
