declare module "@web/core/colorlist/colorlist" {
  import { Component } from "@odoo/owl";

  export interface Color {
    id: number;
    [key: string]: any;
  }

  export interface ColorListProps {
    canToggle?: boolean;
    colors: Color[];
    forceExpanded?: boolean;
    isExpanded?: boolean;
    selectedColor?: number;
    onColorSelected?: (colorId: number) => void;
  }

  export class ColorList extends Component<ColorListProps> {}
}