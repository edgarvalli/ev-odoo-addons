declare module "@web/core/registry" {
  export type Category = "services" | "effects";

  export interface RegistryType {
    category(category: Category): {
      add(serviceName: string, serviceComponent: any): void;
    };
  }

  export const registry: RegistryType;
}
