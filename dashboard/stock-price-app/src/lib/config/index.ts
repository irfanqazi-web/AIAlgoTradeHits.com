/**
 * Config Layer - Export all configurations
 * Single entry point for all SSOT configurations
 *
 * @version 5.1.0
 */

// MACRO CONFIG - Single Source of Truth (Primary)
export { default as MACRO_CONFIG } from './macro-config';
export * from './macro-config';

// Legacy exports (kept for backwards compatibility)
export * from './trading-config';
export * from './api-config';
export * from './ui-config';

// Version info
export const CONFIG_VERSION = "5.1.0";
