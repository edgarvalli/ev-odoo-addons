import { Component, useState, onMounted } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

/**
 * @typedef {import("@web/views/fields/standard_field_props").StandardFieldProps} StandardFieldProps
 */


/**
 * @typedef {Object} StateType
 * @property {import("../../types/models/user").User} users
 */

export default class UserList extends Component {
  static template = "ev_dev.UserList";
  static props = { ...standardFieldProps };

  /**@type {StateType} */
  state = {};

  /**@type {StandardFieldProps} */
  props = {};

  setup() {
    this.state = useState({
      users: [],
    });
    this.orm = useService("orm");

    onMounted(() => {
      this.getUsers();
    });
  }

  get value() {
    return this.props.record.data[this.props.name];
  }

  async getUsers() {
    const users = await this.orm.searchRead("res.users", [], ["id", "name","email"]);

    if (users) {
      this.state.users = users;
    }
  }
}
