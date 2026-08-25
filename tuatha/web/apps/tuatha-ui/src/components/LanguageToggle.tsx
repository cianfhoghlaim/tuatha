/**
 * <LanguageToggle> — the bilingual EN + GA toggle used by every
 * realm route. Persists the choice in `localStorage` under the
 * `tuatha.language` key (default `en`).
 */

import { useCallback, useEffect, useState } from "react";
import type { Language } from "@tuatha/mastery-chart";

const STORAGE_KEY = "tuatha.language";

function readStoredLanguage(): Language {
  if (typeof window === "undefined") return "en";
  const raw = window.localStorage.getItem(STORAGE_KEY);
  return raw === "ga" ? "ga" : "en";
}

export interface LanguageToggleProps {
  readonly value?: Language;
  readonly onChange?: (next: Language) => void;
}

export function LanguageToggle({ value, onChange }: LanguageToggleProps) {
  const [stored, setStored] = useState<Language>(readStoredLanguage);
  const current = value ?? stored;

  useEffect(() => {
    if (typeof window !== "undefined") {
      window.localStorage.setItem(STORAGE_KEY, current);
    }
  }, [current]);

  const handleSelect = useCallback(
    (next: Language) => {
      setStored(next);
      onChange?.(next);
    },
    [onChange],
  );

  return (
    <div className="tuatha-language-toggle" role="group" aria-label="Language toggle">
      <button
        type="button"
        aria-pressed={current === "en"}
        data-lang="en"
        onClick={() => handleSelect("en")}
      >
        EN
      </button>
      <button
        type="button"
        aria-pressed={current === "ga"}
        data-lang="ga"
        onClick={() => handleSelect("ga")}
      >
        GA
      </button>
    </div>
  );
}

export function useLanguage(): [Language, (next: Language) => void] {
  const [stored, setStored] = useState<Language>(readStoredLanguage);
  const setLang = useCallback((next: Language) => {
    setStored(next);
  }, []);
  return [stored, setLang];
}