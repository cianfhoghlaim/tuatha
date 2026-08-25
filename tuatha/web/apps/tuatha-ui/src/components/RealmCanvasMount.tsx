/**
 * <RealmCanvasMount> — the reusable 2.5D PixiJS v8 mount
 * component used by every per-subject realm route. Boots the
 * `TuathaRealmCanvas` against a ref'd host <div>, tears it
 * down on unmount.
 *
 * NO Babylon.js. NO SpacetimeDB. NO 3D worlds.
 */

import { useEffect, useRef, useState } from "react";
import {
  TuathaRealmCanvas,
  type TuathaRealmCanvasHandle,
  type SubjectSlug,
} from "@tuatha/realm-canvas";

export interface RealmCanvasMountProps {
  readonly subject: SubjectSlug;
  readonly height?: number;
  readonly audioEnabled?: boolean;
  readonly forceWebGL?: boolean;
}

export function RealmCanvasMount({
  subject,
  height = 480,
  audioEnabled = false,
  forceWebGL = false,
}: RealmCanvasMountProps) {
  const hostRef = useRef<HTMLDivElement | null>(null);
  const canvasRef = useRef<TuathaRealmCanvas | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const host = hostRef.current;
    if (host === null) return;
    const width = host.clientWidth || host.parentElement?.clientWidth || 800;

    const canvas = new TuathaRealmCanvas(host, {
      subject,
      width,
      height,
      audioEnabled,
      forceWebGL,
    });
    canvasRef.current = canvas;

    canvas
      .mount()
      .then((handle: TuathaRealmCanvasHandle) => {
        if (!audioEnabled) {
          void handle.audio.unlock();
        }
      })
      .catch((err: unknown) => {
        const message = err instanceof Error ? err.message : String(err);
        setError(message);
      });

    return () => {
      void canvas.destroy();
      canvasRef.current = null;
    };
  }, [subject, height, audioEnabled, forceWebGL]);

  return (
    <div className="tuatha-realm-canvas" data-subject={subject} data-testid="realm-canvas-mount">
      <div ref={hostRef} style={{ width: "100%", height }} data-testid="realm-canvas-host" />
      {error === null ? null : (
        <p role="alert" className="tuatha-realm-canvas-error">
          {error}
        </p>
      )}
    </div>
  );
}