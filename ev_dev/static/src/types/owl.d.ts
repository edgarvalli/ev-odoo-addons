import { StandardFieldProps } from "@web/views/fields/standard_field_props";

declare module "@odoo/owl" {
  export class Component<P = StandardFieldProps> {
    static template?: string;
    static xml?: string;
    static components?: Record<string, any>;

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

  export function xml(strings: TemplateStringsArray, ...values: any[]): any;
}