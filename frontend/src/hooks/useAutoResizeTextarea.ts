import { useEffect, useRef } from "react";

/** Grows a textarea with its content, up to maxHeightPx, then scrolls. */
export function useAutoResizeTextarea(value: string, maxHeightPx = 200) {
  const ref = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, maxHeightPx)}px`;
  }, [value, maxHeightPx]);

  return ref;
}
