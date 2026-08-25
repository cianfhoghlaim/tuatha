/**
 * <RealmPage> — the shared per-subject realm page layout.
 *
 * Composes:
 * - the `<RealmCanvasMount>` (PixiJS v8 2.5D background)
 * - the `<LanguageToggle>` (EN + GA)
 * - the `<QuestList>` (real Convex query against `questPacks`)
 * - the subject header (bilingual EN + GA from the realm
 *   descriptor)
 *
 * The 8 per-subject routes are thin wrappers that pass in
 * the `subject` slug. NO Babylon.js, NO SpacetimeDB.
 */

import { useCallback, useState } from "react";
import { loadRealmDescriptor, type SubjectSlug } from "@tuatha/realm-canvas";
import type { Language } from "@tuatha/mastery-chart";
import { LanguageToggle } from "./LanguageToggle";
import { QuestList } from "./QuestList";
import { RealmCanvasMount } from "./RealmCanvasMount";

export interface RealmPageProps {
  readonly subject: SubjectSlug;
}

export function RealmPage({ subject }: RealmPageProps) {
  const descriptor = loadRealmDescriptor(subject);
  const [language, setLanguage] = useState<Language>("en");
  const [activeQuestId, setActiveQuestId] = useState<string | null>(null);

  const handleStart = useCallback((questId: string) => {
    setActiveQuestId(questId);
  }, []);

  const title = language === "ga" ? descriptor.title.ga : descriptor.title.en;
  const tagline = language === "ga" ? descriptor.tagline.ga : descriptor.tagline.en;

  return (
    <main className="tuatha-realm-page" data-subject={subject} data-language={language}>
      <header className="tuatha-realm-header">
        <h1 data-testid="realm-title">{title}</h1>
        <p className="tuatha-realm-tagline">{tagline}</p>
        <LanguageToggle value={language} onChange={setLanguage} />
      </header>
      <RealmCanvasMount subject={subject} />
      <section className="tuatha-realm-quests" aria-label={language === "ga" ? "Taiscéalacha" : "Quests"}>
        <h2>{language === "ga" ? "Taiscéalacha" : "Quests"}</h2>
        <QuestList subject={subject} language={language} onStart={handleStart} />
        {activeQuestId === null ? null : (
          <p className="tuatha-realm-active-quest" data-active-quest-id={activeQuestId}>
            {language === "ga" ? "Tasc gníomhach" : "Active quest"}: {activeQuestId}
          </p>
        )}
      </section>
    </main>
  );
}