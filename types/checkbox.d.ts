declare module "@web/core/checkbox/checkbox" {
  import { Component } from "@odoo/owl";

  export interface CheckBoxProps {
    value: boolean;
    disabled?: boolean;
    onChange?: (value: boolean) => void;
  }

  export class CheckBox extends Component<CheckBoxProps> {}
}