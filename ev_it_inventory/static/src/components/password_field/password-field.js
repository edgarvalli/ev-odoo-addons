import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

export class PasswordField extends Component {
  static template = "ev_it_inventory.PasswordField";
  static props = { ...standardFieldProps };

  setup() {
    this.state = useState({
      visible: false,
      value: this.props.record.data[this.props.name],
    });
  }

  toggle() {
    this.state.visible = !this.state.visible;
  }
  get value() {
    return this.props.record.data[this.props.name];
  }
  onInput(ev) {
    this.state.value = ev.target.value;
  }
}

registry.category("fields").add("password_field", { component: PasswordField });
