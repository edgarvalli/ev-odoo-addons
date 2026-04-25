declare module "@odoo/owl" {
  export class Component<P = any> {
    static props?: P;
    static template?: string;
    static xml?: string;
    static componets?: Record<string, any>;
    
    setup(): void;
  }

  export function useState<T>(state: T): T;

  export interface Ref<T = any> {
    el?: HTMLElement;
    value?: T;
  }

  export function useRef<T = any>(name?: string): Ref<T>;

  export function onMounted(fn: () => void): void;

  export function xml(strings: TemplateStringsArray, ...values: any[]): any;
}
