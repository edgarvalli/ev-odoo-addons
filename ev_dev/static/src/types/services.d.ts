declare module "@web/core/utils/hooks" {
  // -------------------------
  // HTTP SERVICE
  // -------------------------
  export type ReadMethod =
    | "json"
    | "text"
    | "formData"
    | "blob"
    | "arrayBuffer";

  export interface HttpService {
    get(route: string, readMethod?: ReadMethod): Promise<any>;

    post(
      route: string,
      params?: Record<string, any>,
      readMethod?: ReadMethod,
    ): Promise<any>;
  }

  // -------------------------
  // NOTIFICATION SERVICE
  // -------------------------
  export interface NotificationOptions {
    title?: string;
    type?: "warning" | "danger" | "success" | "info";
    sticky?: boolean;
    className?: string;
  }

  export interface NotificationService {
    add(message: string, options?: NotificationOptions): void;
  }

  // -------------------------
  // ORM SERVICE
  // -------------------------
  export interface ORMService {
    call(
      model: string,
      method: string,
      args?: any[],
      kwargs?: Record<string, any>,
    ): Promise<any>;

    searchRead(
      model: string,
      domain?: any[],
      fields?: string[],
      kwargs?: Record<string, any>,
    ): Promise<any[]>;

    create(model: string, values: Record<string, any>): Promise<number>;

    write(
      model: string,
      ids: number[],
      values: Record<string, any>,
    ): Promise<boolean>;

    unlink(model: string, ids: number[]): Promise<boolean>;
  }

  // -------------------------
  // USER SERVICE
  // -------------------------
  export interface UserService {
    userId: number;
    isAdmin: boolean;
    name: string;
    lang: string;
    tz: string;
  }

  // -------------------------
  // COOKIE SERVICE
  // -------------------------
  export interface CookieService {
    current: Record<string, string>;

    setCookie(name: string, value: string, ttl?: number): void;

    deleteCookie(name: string): void;
  }

  // -------------------------
  // TITLE SERVICE
  // -------------------------
  export interface TitleService {
    setParts(parts: Record<string, string | null>): void;
  }

  // -------------------------
  // SERVICES MAP
  // -------------------------
  export interface Services {
    http: HttpService;
    notification: NotificationService;
    orm: ORMService;
    user: UserService;
    cookie: CookieService;
    title: TitleService;

    // permite servicios custom
    [key: string]: any;
  }

  // -------------------------
  // HOOK
  // -------------------------
  export function useService<K extends keyof Services>(
    serviceName: K,
  ): Services[K];
}
