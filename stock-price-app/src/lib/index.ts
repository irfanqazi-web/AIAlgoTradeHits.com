/**
 * Lib Index - Export all library modules
 * Single entry point for config, engines, services, and hooks
 *
 * @version 3.0.0
 */

// Config Layer (SSOT)
export * from './config';

// Engine Layer (Pure Calculations)
export * from './engines';

// Service Layer (Orchestration)
export * from './services';

// Hooks Layer (React Integration)
export * from './hooks';

// Library version
export const LIB_VERSION = "3.0.0";
