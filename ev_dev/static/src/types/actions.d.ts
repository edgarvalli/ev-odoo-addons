/**
 * Odoo 19.0 Actions Type Definitions
 * Based on: https://www.odoo.com/documentation/19.0/developer/reference/backend/actions.html
 */

export type ActionTarget = "current" | "new" | "self" | "fullscreen" | "main";

export interface BaseAction {
  id?: number;
  name?: string;
  type: string;
  xml_id?: string;
}

/**
 * Window Actions (ir.actions.act_window)
 * Opens a view for a specific model.
 */
export interface WindowAction extends BaseAction {
  type: "ir.actions.act_window";
  res_model: string;
  res_id?: number | false;
  view_mode?: string; // e.g., 'tree,form,kanban'
  views?: [number | false, string][]; // e.g., [[false, 'list'], [123, 'form']]
  target?: ActionTarget;
  domain?: string | any[];
  context?: Record<string, any>;
  help?: string;
  limit?: number;
  search_view_id?: [number, string] | false;
}

/**
 * URL Actions (ir.actions.act_url)
 * Redirects to an external or internal URL.
 */
export interface URLAction extends BaseAction {
  type: "ir.actions.act_url";
  url: string;
  target?: "new" | "self";
}

/**
 * Server Actions (ir.actions.server)
 * Executes Python code on the server.
 */
export interface ServerAction extends BaseAction {
  type: "ir.actions.server";
  model_id: number;
  model_name?: string;
  state: "code" | "object_create" | "object_write" | "multi";
  code?: string;
  child_ids?: number[];
  crud_model_id?: number;
  link_field_id?: number;
}

/**
 * Report Actions (ir.actions.report)
 * Triggers the generation of a report (PDF/HTML).
 */
export interface ReportAction extends BaseAction {
  type: "ir.actions.report";
  report_name: string; // The technical name of the report
  report_type: "qweb-pdf" | "qweb-html" | "qweb-text";
  data?: Record<string, any>;
  context?: Record<string, any>;
  display_name?: string;
  paperformat_id?: number;
}

/**
 * Client Actions (ir.actions.client)
 * Executes a specific widget or client-side logic.
 */
export interface ClientAction extends BaseAction {
  type: "ir.actions.client";
  tag: string; // The widget tag registered in the client action registry
  params?: Record<string, any>;
  target?: ActionTarget;
  context?: Record<string, any>;
}

/**
 * Union type for all possible Odoo Actions
 */
export type OdooAction =
  | WindowAction
  | URLAction
  | ServerAction
  | ReportAction
  | ClientAction;

/**
 * Common views sequence for Window Actions
 */
export type ViewMode =
  | "tree"
  | "form"
  | "kanban"
  | "calendar"
  | "pivot"
  | "graph"
  | "cohort"
  | "activity";
