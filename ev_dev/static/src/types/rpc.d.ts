declare module "@web/core/network/rpc" {
  export function rpc<T>(
    url: string,
    params?: Record<string, any>,
    settings?: { xhr?: XMLHttpRequest; silent?: boolean },
  ): Promise<T>;
}
