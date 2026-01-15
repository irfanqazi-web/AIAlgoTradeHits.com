/**
 * BigQuery Configuration for Unified Platform
 * Supports: KaamyabPakistan, YouInvent, HomeFranchise, NoCodeAI
 */

const { BigQuery } = require('@google-cloud/bigquery');

const PROJECT_ID = process.env.GCP_PROJECT_ID || 'aialgotradehits';
const DATASET_ID = process.env.BQ_DATASET || 'kaamyabpakistan_data';

const bigquery = new BigQuery({ projectId: PROJECT_ID });

const tables = {
  // Shared Users Table
  users: `${PROJECT_ID}.${DATASET_ID}.users`,

  // KaamyabPakistan Tables
  mainProjects: `${PROJECT_ID}.${DATASET_ID}.main_projects`,
  projectItems: `${PROJECT_ID}.${DATASET_ID}.project_items`,
  sublistDes: `${PROJECT_ID}.${DATASET_ID}.sublist_des`,
  subprojectVideos: `${PROJECT_ID}.${DATASET_ID}.subproject_videos`,
  subprojectBlogs: `${PROJECT_ID}.${DATASET_ID}.subproject_blogs`,
  categories: `${PROJECT_ID}.${DATASET_ID}.categories`,
  projects: `${PROJECT_ID}.${DATASET_ID}.projects`,
  opportunities: `${PROJECT_ID}.${DATASET_ID}.opportunities`,
  programs: `${PROJECT_ID}.${DATASET_ID}.programs`,
  successStories: `${PROJECT_ID}.${DATASET_ID}.success_stories`,
  investors: `${PROJECT_ID}.${DATASET_ID}.investors`,

  // YouInvent Tables
  inventions: `${PROJECT_ID}.${DATASET_ID}.inventions`,
  inventionCategories: `${PROJECT_ID}.${DATASET_ID}.invention_categories`,
  inventionInvestors: `${PROJECT_ID}.${DATASET_ID}.invention_investors`,

  // HomeFranchise Tables
  franchises: `${PROJECT_ID}.${DATASET_ID}.franchises`,
  franchiseApplications: `${PROJECT_ID}.${DATASET_ID}.franchise_applications`,
  franchiseCategories: `${PROJECT_ID}.${DATASET_ID}.franchise_categories`,

  // NoCodeAI Tables
  consultingRequests: `${PROJECT_ID}.${DATASET_ID}.consulting_requests`,
  consultants: `${PROJECT_ID}.${DATASET_ID}.consultants`,
  aiServices: `${PROJECT_ID}.${DATASET_ID}.ai_services`,
  clientProjects: `${PROJECT_ID}.${DATASET_ID}.client_projects`,
};

async function query(sql, params = {}) {
  try {
    const [rows] = await bigquery.query({ query: sql, params });
    return rows;
  } catch (error) {
    console.error('BigQuery Error:', error.message);
    throw error;
  }
}

async function insertRows(tableName, rows) {
  try {
    const datasetRef = bigquery.dataset(DATASET_ID);
    const tableRef = datasetRef.table(tableName);
    await tableRef.insert(rows);
    return { success: true, count: rows.length };
  } catch (error) {
    console.error('Insert Error:', error.message);
    throw error;
  }
}

async function getNextId(tableId, idColumn) {
  try {
    const sql = `SELECT COALESCE(MAX(${idColumn}), 0) + 1 as next_id FROM \`${tableId}\``;
    const rows = await query(sql);
    return rows[0]?.next_id || 1;
  } catch (error) {
    // Table might not exist yet, return 1
    return 1;
  }
}

async function tableExists(tableName) {
  try {
    const datasetRef = bigquery.dataset(DATASET_ID);
    const tableRef = datasetRef.table(tableName);
    const [exists] = await tableRef.exists();
    return exists;
  } catch (error) {
    return false;
  }
}

module.exports = {
  bigquery,
  tables,
  query,
  insertRows,
  getNextId,
  tableExists,
  PROJECT_ID,
  DATASET_ID
};
