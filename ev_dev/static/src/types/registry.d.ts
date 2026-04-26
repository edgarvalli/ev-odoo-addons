declare module "@web/core/registry" {
  export interface RegistryAddOptions {
    force?: boolean;
    sequence?: number;
  }

  export class Registry<T = any> {
    add(
      key: string,
      value: T,
      options?: RegistryAddOptions
    ): this;

    get(key: string, defaultValue?: T): T;

    contains(key: string): boolean;

    getAll(): T[];

    remove(key: string): void;

    category(name: string): Registry<T>;
  }

  /**
   * Categorías comunes (no son restrictivas en Odoo realmente,
   * pero ayuda para autocompletado)
   */
  export type Category =
    | "fields"
    | "services"
    | "effects"
    | "views"
    | "formatters"
    | "parsers"
    | "main_components"
    | "systray"
    | "user_menuitems"
    | "public_components"
    | (string & {}); // permite custom categories

  export interface RootRegistry extends Registry<any> {
    category(name: Category): Registry<any>;
  }

  export const registry: RootRegistry;
}