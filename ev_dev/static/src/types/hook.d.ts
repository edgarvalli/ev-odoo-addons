declare module "@web/core/utils/hooks" {
  // ---------------------------------------
  // BASE TYPES
  // ---------------------------------------

  export interface EventBus {
    on(event: string, callback: (...args: any[]) => void): void;
    off(event: string, callback: (...args: any[]) => void): void;
    trigger(event: string, payload?: any): void;
  }

  export interface Ref<T = HTMLElement> {
    el: T | null;
  }

  // ---------------------------------------
  // useAutofocus
  // ---------------------------------------
  export function useAutofocus<T extends HTMLElement = HTMLElement>(): Ref<T>;

  // ---------------------------------------
  // useBus
  // ---------------------------------------
  export function useBus(
    bus: EventBus,
    eventName: string,
    callback: (event: any) => void
  ): void;

  // ---------------------------------------
  // usePager
  // ---------------------------------------
  export interface PagerState {
    offset: number;
    limit: number;
    total: number;
  }

  export interface PagerProps extends PagerState {
    onUpdate: (newState: Partial<PagerState>) => void;
  }

  export function usePager(
    getPagerProps: () => PagerProps
  ): void;

  // ---------------------------------------
  // usePosition
  // ---------------------------------------
  export type PositionDirection = "top" | "bottom" | "left" | "right";

  export type PositionVariant = "start" | "middle" | "end" | "fit";

  export type PositionValue =
    | PositionDirection
    | `${PositionDirection}-${PositionVariant}`;

  export interface PositioningSolution {
    direction: PositionDirection;
    variant: PositionVariant;
    top: number;
    left: number;
  }

  export interface UsePositionOptions {
    popper?: string;
    container?: HTMLElement;
    margin?: number;
    position?: PositionValue;
    onPositioned?: (
      el: HTMLElement,
      solution: PositioningSolution
    ) => void;
  }

  export function usePosition(
    reference: HTMLElement | (() => HTMLElement | null),
    options?: UsePositionOptions
  ): void;

  // ---------------------------------------
  // useSpellCheck
  // ---------------------------------------
  export interface SpellCheckOptions {
    refName?: string;
  }

  export function useSpellCheck<T extends HTMLElement = HTMLElement>(
    options?: SpellCheckOptions
  ): Ref<T>;

  // ---------------------------------------
  // EXTRA: useAssets (otro módulo)
  // ---------------------------------------
}

declare module "@web/core/assets" {
  export interface UseAssetsOptions {
    cssLibs?: string[];
    jsLibs?: string[];
    bundles?: string[];
  }

  export function useAssets(options: UseAssetsOptions): Promise<void>;
}

declare module "@web/search/pager_hook" {
  export { usePager } from "@web/core/utils/hooks";
}