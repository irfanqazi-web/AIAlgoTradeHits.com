/**
 * Project Controller - KaamyabPakistan.org Platform
 * Handles projects and sub-projects
 */

const { tables, query, insertRows, getNextId } = require('../config/bigquery.config');

// Get all main projects (categories)
exports.getAllMainProjects = async (req, res) => {
  try {
    const sql = `SELECT * FROM \`${tables.mainProjects}\` ORDER BY project_id ASC`;
    const projects = await query(sql);
    res.json({ success: true, projects, count: projects.length });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
};

// Get main project by ID
exports.getMainProjectById = async (req, res) => {
  try {
    const { project_id } = req.params;
    const sql = `SELECT * FROM \`${tables.mainProjects}\` WHERE project_id = @project_id`;
    const projects = await query(sql, { project_id: parseInt(project_id) });

    if (projects.length === 0) {
      return res.status(404).json({ success: false, message: 'Project not found' });
    }

    res.json({ success: true, project: projects[0] });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
};

// Get sub-projects by main project ID
exports.getSubProjectsByMainId = async (req, res) => {
  try {
    const { project_id } = req.params;
    const sql = `SELECT * FROM \`${tables.projectItems}\` WHERE project_id = @project_id ORDER BY sub_id ASC`;
    const subprojects = await query(sql, { project_id: parseInt(project_id) });

    res.json({ success: true, subprojects, count: subprojects.length });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
};

// Get sub-project by ID
exports.getSubProjectById = async (req, res) => {
  try {
    const { sub_id } = req.params;
    const sql = `SELECT * FROM \`${tables.projectItems}\` WHERE sub_id = @sub_id`;
    const subprojects = await query(sql, { sub_id: parseInt(sub_id) });

    if (subprojects.length === 0) {
      return res.status(404).json({ success: false, message: 'Sub-project not found' });
    }

    res.json({ success: true, subproject: subprojects[0] });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
};

// Get all sub-projects
exports.getAllSubProjects = async (req, res) => {
  try {
    const sql = `SELECT * FROM \`${tables.projectItems}\` ORDER BY sub_id ASC`;
    const subprojects = await query(sql);
    res.json({ success: true, subprojects, count: subprojects.length });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
};

// Get sub-project description
exports.getSubProjectDescription = async (req, res) => {
  try {
    const { sub_id } = req.params;
    const sql = `SELECT * FROM \`${tables.sublistDes}\` WHERE sub_id = @sub_id`;
    const descriptions = await query(sql, { sub_id: parseInt(sub_id) });

    res.json({
      success: true,
      description: descriptions.length > 0 ? descriptions[0] : null
    });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
};

// Create main project (admin only)
exports.createMainProject = async (req, res) => {
  try {
    const { project_name, project_description, icon, color } = req.body;

    if (!project_name) {
      return res.status(400).json({ success: false, message: 'Project name is required' });
    }

    const project_id = await getNextId(tables.mainProjects, 'project_id');
    const now = new Date().toISOString();

    await insertRows('main_projects', [{
      project_id,
      project_name,
      project_description: project_description || '',
      icon: icon || 'folder',
      color: color || '#01796F',
      created_at: now,
      updated_at: now
    }]);

    res.json({
      success: true,
      message: 'Project created successfully',
      project_id
    });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
};

// Update main project (admin only)
exports.updateMainProject = async (req, res) => {
  try {
    const { project_id, project_name, project_description, icon, color } = req.body;

    if (!project_id) {
      return res.status(400).json({ success: false, message: 'Project ID is required' });
    }

    const sql = `UPDATE \`${tables.mainProjects}\`
      SET project_name = @project_name, project_description = @project_description,
          icon = @icon, color = @color, updated_at = CURRENT_TIMESTAMP()
      WHERE project_id = @project_id`;

    await query(sql, { project_id, project_name, project_description, icon, color });
    res.json({ success: true, message: 'Project updated successfully' });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
};

// Delete main project (admin only)
exports.deleteMainProject = async (req, res) => {
  try {
    const { project_id } = req.params;

    // Delete related sub-projects first
    await query(`DELETE FROM \`${tables.projectItems}\` WHERE main_project_id = @project_id`,
      { project_id: parseInt(project_id) });

    // Delete main project
    await query(`DELETE FROM \`${tables.mainProjects}\` WHERE project_id = @project_id`,
      { project_id: parseInt(project_id) });

    res.json({ success: true, message: 'Project deleted successfully' });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
};

// Create sub-project (admin only)
exports.createSubProject = async (req, res) => {
  try {
    const { main_project_id, sub_name, sub_description, investment_range, location } = req.body;

    if (!main_project_id || !sub_name) {
      return res.status(400).json({ success: false, message: 'Main project ID and sub-project name are required' });
    }

    const sub_id = await getNextId(tables.projectItems, 'sub_id');
    const now = new Date().toISOString();

    await insertRows('project_items', [{
      sub_id,
      main_project_id: parseInt(main_project_id),
      sub_name,
      sub_description: sub_description || '',
      investment_range: investment_range || '',
      location: location || '',
      created_at: now,
      updated_at: now
    }]);

    res.json({
      success: true,
      message: 'Sub-project created successfully',
      sub_id
    });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
};

// Update sub-project (admin only)
exports.updateSubProject = async (req, res) => {
  try {
    const { sub_id, sub_name, sub_description, investment_range, location } = req.body;

    if (!sub_id) {
      return res.status(400).json({ success: false, message: 'Sub-project ID is required' });
    }

    const sql = `UPDATE \`${tables.projectItems}\`
      SET sub_name = @sub_name, sub_description = @sub_description,
          investment_range = @investment_range, location = @location,
          updated_at = CURRENT_TIMESTAMP()
      WHERE sub_id = @sub_id`;

    await query(sql, { sub_id, sub_name, sub_description, investment_range, location });
    res.json({ success: true, message: 'Sub-project updated successfully' });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
};

// Delete sub-project (admin only)
exports.deleteSubProject = async (req, res) => {
  try {
    const { sub_id } = req.params;

    // Delete related descriptions
    await query(`DELETE FROM \`${tables.sublistDes}\` WHERE sub_id = @sub_id`,
      { sub_id: parseInt(sub_id) });

    // Delete sub-project
    await query(`DELETE FROM \`${tables.projectItems}\` WHERE sub_id = @sub_id`,
      { sub_id: parseInt(sub_id) });

    res.json({ success: true, message: 'Sub-project deleted successfully' });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
};

// Create sub-project description (admin only)
exports.createSubProjectDescription = async (req, res) => {
  try {
    const { sub_id, description_text, videos, documents } = req.body;

    if (!sub_id) {
      return res.status(400).json({ success: false, message: 'Sub-project ID is required' });
    }

    const des_id = await getNextId(tables.sublistDes, 'des_id');
    const now = new Date().toISOString();

    await insertRows('sublist_des', [{
      des_id,
      sub_id: parseInt(sub_id),
      description_text: description_text || '',
      videos: videos || '[]',
      documents: documents || '[]',
      created_at: now,
      updated_at: now
    }]);

    res.json({
      success: true,
      message: 'Description created successfully',
      des_id
    });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
};

// Update sub-project description (admin only)
exports.updateSubProjectDescription = async (req, res) => {
  try {
    const { des_id, description_text, videos, documents } = req.body;

    if (!des_id) {
      return res.status(400).json({ success: false, message: 'Description ID is required' });
    }

    const sql = `UPDATE \`${tables.sublistDes}\`
      SET description_text = @description_text, videos = @videos, documents = @documents,
          updated_at = CURRENT_TIMESTAMP()
      WHERE des_id = @des_id`;

    await query(sql, { des_id, description_text, videos, documents });
    res.json({ success: true, message: 'Description updated successfully' });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
};
