import { useMemo } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "convex/react";
import { api } from "../../../../convex/_generated/api";
import {
  MasteryChart,
  topSubject,
  type MasterySeries,
} from "@tuatha/mastery-chart";
import { LanguageToggle, useLanguage } from "../../../components/LanguageToggle";
import {
  buildEmblemKey,
  defaultEmblemSeed,
  emblemSrc,
  isEmblemCacheFresh,
  type EmblemCacheEntry,
} from "../../../lib/emblem";

export const Route = createFileRoute("/student/$id/mastery" as never)({
  component: StudentMastery,
});

interface BadgeRow {
  readonly _id: string;
  readonly studentId: string;
  readonly subject: string;
  readonly competencyCode: string;
  readonly dateEarned: number;
}

function useMasterySeries(studentId: string, language: "en" | "ga"): MasterySeries | null {
  const badges = useQuery(api.badge_query.listBadgesByStudent as never, { studentId } as never);

  return useMemo<MasterySeries | null>(() => {
    if (badges === undefined) return null;
    const counts = new Map<string, number>();
    for (const row of badges as BadgeRow[]) {
      counts.set(row.subject, (counts.get(row.subject) ?? 0) + 1);
    }
    const points = Array.from(counts.entries()).map(([subject, count]) => {
      const score = Math.min(100, count * 20);
      return { subject: subject as MasterySeries["points"][number]["subject"], score };
    });
    return {
      studentId,
      language,
      points,
    };
  }, [badges, studentId, language]);
}

function StudentMastery() {
  const { id } = Route.useParams();
  const [language, setLanguage] = useLanguage();
  const series = useMasterySeries(id, language);

  if (series === null) {
    return (
      <main className="tuatha-mastery-page tuatha-mastery-loading" data-student-id={id}>
        <p>{language === "ga" ? "Ag lódáil…" : "Loading mastery…"}</p>
      </main>
    );
  }

  const seed = defaultEmblemSeed(id);
  const top = topSubject(series);
  const key = buildEmblemKey(id, top, seed);
  const cached = useQuery(api.emblem.getEmblem as never, key as never);

  return (
    <main className="tuatha-mastery-page" data-student-id={id} data-language={language}>
      <header className="tuatha-mastery-header">
        <h1 data-testid="mastery-title">
          {language === "ga" ? "Máistreacht" : "Mastery"}: {id}
        </h1>
        <LanguageToggle value={language} onChange={setLanguage} />
      </header>
      <section className="tuatha-mastery-chart-section">
        <MasteryChart series={series} />
      </section>
      <section
        className="tuatha-mastery-emblem-section"
        aria-label={language === "ga" ? "Suaitheantas" : "Emblem"}
      >
        <h2>{language === "ga" ? "Suaitheantas an Dalta" : "Student Emblem"}</h2>
        <p>
          {language === "ga" ? "Príomhábhar" : "Top subject"}: <strong>{top}</strong>
        </p>
        {isEmblemCacheFresh(cached ?? null, key) && cached !== undefined ? (
          <img
            className="tuatha-mastery-emblem"
            src={emblemSrc(cached as EmblemCacheEntry)}
            alt={language === "ga" ? `Suaitheantas do ${id}` : `Emblem for ${id}`}
            data-testid="mastery-emblem"
          />
        ) : (
          <div className="tuatha-mastery-emblem-placeholder" data-testid="mastery-emblem-placeholder">
            {language === "ga" ? "Gan suaitheantas fós" : "No emblem cached yet"}
          </div>
        )}
      </section>
    </main>
  );
}