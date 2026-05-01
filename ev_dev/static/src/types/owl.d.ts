declare module "@odoo/owl" {
  import { StandardFieldProps } from "@web/views/fields/standard_field_props";
  export class Component<P = StandardFieldProps> {
    static template?: string;
    static xml?: string;
    static components?: Record<string, any>;
    static description: string;

    // 👇 definición (schema)
    static props?: P;

    // 👇 props reales en runtime
    props: P;

    setup(): void;
  }

  export function useState<T extends object>(state: T): T;

  export interface Ref<T = any> {
    el?: HTMLElement;
    value?: T;
  }

  export function useRef<T = any>(name?: string): Ref<T>;

  export function onMounted(fn: () => void): void;

  export function onWillStart(fn: () => void): void;

  export function onWillUnmount(fn: () => void): void;

  export function onWillUpdateProps(
    fn: (nextProps: Record<string, any>) => void,
  ): void;

  export function xml(strings: TemplateStringsArray, ...values: any[]): any;
}
