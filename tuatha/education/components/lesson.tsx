// tuatha.education.components.lesson — the per-Lesson chamber surface.
import { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Phase5RoutingDecision } from "../routing";

export function Lesson({ student_id, subject, lo_code }: {
  student_id: string; subject: string; lo_code: string;
}) {
  const [lesson, setLesson] = useState<any>(null);
  useEffect(() => {
    (async () => {
      // Production: GET /api/curriculum/{jurisdiction}?subject={subject}&lo={lo_code}
      const r = await fetch(`/api/curriculum/${encodeURIComponent("Ireland")}`);
      const d = await r.json();
      const rows = (d.data ?? []).filter((x: any) =>
        x.subject === subject && x.source_url.includes(lo_code));
      setLesson(rows[0] ?? null);
    })();
  }, [subject, lo_code]);
  if (!lesson) return <em>loading lesson {lo_code}…</em>;
  return (
    <div>
      <h3>lesson: {lo_code}</h3>
      <p>rung 1: {lesson.source_url} p.{lesson.source_page}</p>
      <p>rung 2: rung {lesson.rung} loaded</p>
      <button>open chamber</button>
    </div>
  );
}
