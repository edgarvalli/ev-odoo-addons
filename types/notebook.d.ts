declare module "@web/core/notebook/notebook" {
  import { Component } from "@odoo/owl";

  export interface NotebookPage {
    id?: string;
    title: string;
    Component?: any;
    props?: any;
  }

  export interface NotebookProps {
    pages?: NotebookPage[];
    defaultPage?: string;
    orientation?: "horizontal" | "vertical";
    onPageUpdate?: (pageId: string) => void;
  }

  export class Notebook extends Component<NotebookProps> {}
}