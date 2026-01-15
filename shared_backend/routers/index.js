/**
 * Unified API Router
 * Routes for all platforms: KaamyabPakistan, YouInvent, HomeFranchise, NoCodeAI
 */

const express = require('express');
const router = express.Router();

// Controllers
const userController = require('../controllers/user.controller');
const projectController = require('../controllers/project.controller');
const statsController = require('../controllers/stats.controller');
const inventionController = require('../controllers/invention.controller');
const franchiseController = require('../controllers/franchise.controller');
const consultingController = require('../controllers/consulting.controller');

// ==================== AUTH ROUTES (Shared) ====================
router.post('/auth/signup', userController.signup);
router.post('/auth/signin', userController.signin);
router.post('/auth/login', userController.signin); // Alias

// Profile (requires auth)
router.get('/profile', userController.authMiddleware, userController.getProfile);
router.put('/profile', userController.authMiddleware, userController.updateProfile);
router.post('/change-password', userController.authMiddleware, userController.changePassword);

// ==================== KAAMYABPAKISTAN ROUTES ====================

// Projects (Public)
router.get('/get/all/mainprojects', projectController.getAllMainProjects);
router.get('/get/project/:project_id', projectController.getMainProjectById);
router.get('/get/subproject/:project_id', projectController.getSubProjectsByMainId);
router.get('/get/subpro/:sub_id', projectController.getSubProjectById);
router.get('/get/all/subprojects', projectController.getAllSubProjects);
router.get('/get/subproject/des/:sub_id', projectController.getSubProjectDescription);
router.get('/get/subproject/description/:sub_id', projectController.getSubProjectDescription);

// Stats and Data (Public)
router.get('/stats', statsController.getDashboardStats);
router.get('/categories', statsController.getCategories);
router.get('/opportunities', statsController.getOpportunities);
router.get('/programs', statsController.getPrograms);
router.get('/success-stories', statsController.getSuccessStories);
router.get('/search', statsController.searchProjects);
router.get('/investor-types', statsController.getInvestorTypes);
router.post('/investor-interest', statsController.registerInvestorInterest);

// Projects Admin Routes
router.post('/create/mainproject', userController.authMiddleware, userController.adminMiddleware, projectController.createMainProject);
router.put('/update/mainproject', userController.authMiddleware, userController.adminMiddleware, projectController.updateMainProject);
router.delete('/delete/mainproject/:project_id', userController.authMiddleware, userController.adminMiddleware, projectController.deleteMainProject);
router.post('/create/subproject', userController.authMiddleware, userController.adminMiddleware, projectController.createSubProject);
router.put('/update/subproject', userController.authMiddleware, userController.adminMiddleware, projectController.updateSubProject);
router.delete('/delete/subproject/:sub_id', userController.authMiddleware, userController.adminMiddleware, projectController.deleteSubProject);
router.post('/create/subprojectdes', userController.authMiddleware, userController.adminMiddleware, projectController.createSubProjectDescription);
router.put('/update/subprojectdes', userController.authMiddleware, userController.adminMiddleware, projectController.updateSubProjectDescription);

// ==================== YOUINVENT ROUTES ====================

// Inventions (Public)
router.get('/inventions', inventionController.getAllInventions);
router.get('/inventions/categories', inventionController.getCategories);
router.get('/inventions/stats', inventionController.getStats);
router.get('/inventions/:invention_id', inventionController.getInventionById);

// Inventions (Authenticated)
router.get('/my-inventions', userController.authMiddleware, inventionController.getMyInventions);
router.post('/inventions', userController.authMiddleware, inventionController.submitInvention);
router.put('/inventions/:invention_id', userController.authMiddleware, inventionController.updateInvention);
router.delete('/inventions/:invention_id', userController.authMiddleware, inventionController.deleteInvention);

// ==================== HOMEFRANCHISE ROUTES ====================

// Franchises (Public)
router.get('/franchises', franchiseController.getAllFranchises);
router.get('/franchises/categories', franchiseController.getCategories);
router.get('/franchises/stats', franchiseController.getStats);
router.get('/franchises/:franchise_id', franchiseController.getFranchiseById);

// Franchises (Authenticated - Franchiser)
router.get('/my-franchises', userController.authMiddleware, franchiseController.getMyFranchises);
router.post('/franchises', userController.authMiddleware, franchiseController.createFranchise);
router.put('/franchises/:franchise_id', userController.authMiddleware, franchiseController.updateFranchise);
router.delete('/franchises/:franchise_id', userController.authMiddleware, franchiseController.deleteFranchise);
router.get('/franchises/:franchise_id/applications', userController.authMiddleware, franchiseController.getFranchiseApplications);

// Franchises (Authenticated - Franchisee)
router.post('/franchises/:franchise_id/apply', userController.authMiddleware, franchiseController.applyForFranchise);
router.get('/my-applications', userController.authMiddleware, franchiseController.getMyApplications);

// ==================== NOCODEAI ROUTES ====================

// Consulting (Public)
router.get('/consultants', consultingController.getConsultants);
router.get('/ai-services', consultingController.getServices);
router.get('/consulting/stats', consultingController.getStats);
router.post('/consulting/request', consultingController.submitRequest);

// Consulting (Authenticated)
router.get('/my-requests', userController.authMiddleware, consultingController.getMyRequests);
router.get('/consulting/requests/:request_id', userController.authMiddleware, consultingController.getRequestById);

// Consulting Admin Routes
router.get('/consulting/all-requests', userController.authMiddleware, userController.adminMiddleware, consultingController.getAllRequests);
router.put('/consulting/requests/:request_id/status', userController.authMiddleware, userController.adminMiddleware, consultingController.updateRequestStatus);
router.post('/consulting/projects', userController.authMiddleware, userController.adminMiddleware, consultingController.createProject);
router.get('/consulting/projects', userController.authMiddleware, userController.adminMiddleware, consultingController.getAllProjects);

module.exports = router;
