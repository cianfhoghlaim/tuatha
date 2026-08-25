/**
 * <QuestList> — the per-realm quest list. Real Convex query
 * against the `questPacks` table (no hardcoded item counts).
 *
 * The component renders a loading shimmer while the query is
 * in flight, an empty state when the query returns zero rows,
 * and a clickable row for every quest the query returns.
 */

import { useQuery } from "convex/react";
import { api } from "../../convex/_generated/api";
import type { Language } from "@tuatha/mastery-chart";

export interface QuestListProps {
  readonly subject: string;
  readonly language: Language;
  readonly onStart: (questId: string) => void;
}

interface QuestPackRow {
  readonly _id: string;
  readonly titleEn: string;
  readonly titleGa: string;
}

interface QuestRowProps {
  readonly questId: string;
  readonly titleEn: string;
  readonly titleGa: string;
  readonly language: Language;
  readonly onStart: (questId: string) => void;
}

function QuestRow({ questId, titleEn, titleGa, language, onStart }: QuestRowProps) {
  const title = language === "ga" && titleGa !== "" ? titleGa : titleEn;
  return (
    <li className="tuatha-quest-row" data-quest-id={questId}>
      <span className="tuatha-quest-title">{title}</span>
      <button
        type="button"
        className="tuatha-quest-start"
        onClick={() => onStart(questId)}
        data-testid="quest-start"
      >
        {language === "ga" ? "Tosaigh" : "Start"}
      </button>
    </li>
  );
}

export function QuestList({ subject, language, onStart }: QuestListProps) {
  const data = useQuery(api.quest_query.listQuestPacksBySubject as never, { subject } as never) as
    | QuestPackRow[]
    | undefined;

  if (data === undefined) {
    return (
      <div className="tuatha-quest-list-loading" role="status" aria-live="polite">
        <span>{language === "ga" ? "Ag lódáil…" : "Loading quests…"}</span>
      </div>
    );
  }

  if (data.length === 0) {
    return (
      <div className="tuatha-quest-list-empty">
        <p>{language === "ga" ? "Níl aon taiscéalacha fós." : "No quests yet."}</p>
      </div>
    );
  }

  return (
    <ul className="tuatha-quest-list" data-subject={subject} data-language={language}>
      {data.map((row) => (
        <QuestRow
          key={row._id}
          questId={row._id}
          titleEn={row.titleEn}
          titleGa={row.titleGa}
          language={language}
          onStart={onStart}
        />
      ))}
    </ul>
  );
}