declare module "@web/core/action_swiper/action_swiper" {
  import { Component } from "@odoo/owl";

  export interface SwipeAction {
    action: () => void;
    icon?: string;
    bgColor?: string;
  }

  export interface ActionSwiperProps {
    onLeftSwipe?: SwipeAction;
    onRightSwipe?: SwipeAction;
  }

  export class ActionSwiper extends Component<ActionSwiperProps> {}
}
