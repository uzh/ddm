/**
 * Creates a debounced function that delays invoking the provided function
 * until after the specified wait time has elapsed since the last time it was invoked.
 *
 * @param fn - The function to debounce
 * @param wait - The number of milliseconds to delay
 * @returns A debounced version of the original function
 */
export function debounce<T extends (...args: any[]) => any>(
  fn: T,
  wait: number
): (...args: any[]) => void{
  let timer: ReturnType<typeof setTimeout> | undefined;

  return function(this: any, ...args: any[]): void {
    if(timer) {
      clearTimeout(timer);
    }

    const context = this;
    timer = setTimeout(()=>{
      fn.apply(context, args);
    }, wait);
  }
}
