declare module "@web/core/utils/hooks" {
  export type ReadMethod =
    | "json"
    | "text"
    | "formData"
    | "blob"
    | "arrayBuffer";

  export interface HttpMethods {
    get(route: string, readMethod?: ReadMethod): Promise<any>;
    post(
      route: string,
      params: Record<string, any>,
      readMethod?: ReadMethod,
    ): Promise<any>;
  }

  export interface NotificationOptions {
    title?: string;
    type?: "warning" | "danger" | "success" | "info";
  }

  export interface Services {
    http(route: string): HttpMethods;
    notification(message: string, options?: NotificationOptions): void;
    user: any;
    cookie: any;
    title: any;
  }

  export function useService<K extends keyof Services>(
    serviceName: K,
  ): Services[K];
}
