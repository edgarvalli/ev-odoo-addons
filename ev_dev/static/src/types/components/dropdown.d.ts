declare module "@web/core/dropdown/dropdown" {
  import { Component } from "@odoo/owl";

  export interface DropdownProps {
    toggler?: string;
    class?: string;
    menuClass?: string;
    disabled?: boolean;
  }

  export class Dropdown extends Component<DropdownProps> {}
}

declare module "@web/core/dropdown/dropdown_item" {
  import { Component } from "@odoo/owl";

  export interface DropdownItemProps {
    onSelected?: () => void;
    disabled?: boolean;
    class?: string;
  }

  export class DropdownItem extends Component<DropdownItemProps> {}
}
