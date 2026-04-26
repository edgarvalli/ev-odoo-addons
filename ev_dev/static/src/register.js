import { registry } from "@web/core/registry";
import EVUserList from "./widgets/ev_user_list/user_list";

registry.category("fields").add("ev_user_list", {component: EVUserList});
