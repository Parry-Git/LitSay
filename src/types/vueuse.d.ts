declare module "@vueuse/core" {
  export function useEventBus<T = any>(
    key: string | symbol
  ): {
    on: (listener: (event: T) => void) => void;
    once: (listener: (event: T) => void) => void;
    off: (listener?: (event: T) => void) => void;
    emit: (event: T) => void;
  };
}
