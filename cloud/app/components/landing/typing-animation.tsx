import { useCallback, useEffect, useRef, useState } from "react";

const WORDS = ["create", "listen", "learn", "grow"];

const TYPE_SPEED = 80;
const DELETE_SPEED = 40;
const PAUSE_ON_WORD = 2000;
const PAUSE_BETWEEN = 300;
const CURSOR_BLINK_SPEED = 530;

// Mobile timing (slightly faster)
const TYPE_SPEED_MOBILE = 60;
const PAUSE_ON_WORD_MOBILE = 1500;

type Phase = "typing" | "pausing" | "deleting" | "waiting";

function useIsMobile() {
  const [isMobile, setIsMobile] = useState(false);
  useEffect(() => {
    const mql = window.matchMedia("(max-width: 640px)");
    setIsMobile(mql.matches);
    const handler = (e: MediaQueryListEvent) => setIsMobile(e.matches);
    mql.addEventListener("change", handler);
    return () => mql.removeEventListener("change", handler);
  }, []);
  return isMobile;
}

export function TypingAnimation({ className }: { className?: string }) {
  const [wordIndex, setWordIndex] = useState(0);
  const [charIndex, setCharIndex] = useState(0);
  const [phase, setPhase] = useState<Phase>("typing");
  const [cursorVisible, setCursorVisible] = useState(true);
  const isMobile = useIsMobile();

  const typeSpeed = isMobile ? TYPE_SPEED_MOBILE : TYPE_SPEED;
  const pauseOnWord = isMobile ? PAUSE_ON_WORD_MOBILE : PAUSE_ON_WORD;

  // Cursor blink
  const cursorRef = useRef<ReturnType<typeof setInterval>>(null);
  useEffect(() => {
    if (phase === "pausing" || phase === "waiting") {
      cursorRef.current = setInterval(() => {
        setCursorVisible((v) => !v);
      }, CURSOR_BLINK_SPEED);
    } else {
      setCursorVisible(true);
      if (cursorRef.current) clearInterval(cursorRef.current);
    }
    return () => {
      if (cursorRef.current) clearInterval(cursorRef.current);
    };
  }, [phase]);

  const currentWord = WORDS[wordIndex];

  const advance = useCallback(() => {
    switch (phase) {
      case "typing":
        if (charIndex < currentWord.length) {
          setCharIndex((c) => c + 1);
        } else {
          setPhase("pausing");
        }
        break;
      case "pausing":
        setPhase("deleting");
        break;
      case "deleting":
        if (charIndex > 0) {
          setCharIndex((c) => c - 1);
        } else {
          setPhase("waiting");
        }
        break;
      case "waiting":
        setWordIndex((w) => (w + 1) % WORDS.length);
        setPhase("typing");
        break;
    }
  }, [phase, charIndex, currentWord]);

  useEffect(() => {
    let delay: number;
    switch (phase) {
      case "typing":
        delay = typeSpeed;
        break;
      case "pausing":
        delay = pauseOnWord;
        break;
      case "deleting":
        delay = DELETE_SPEED;
        break;
      case "waiting":
        delay = PAUSE_BETWEEN;
        break;
    }
    const timer = setTimeout(advance, delay);
    return () => clearTimeout(timer);
  }, [phase, charIndex, advance, typeSpeed, pauseOnWord]);

  const displayText = currentWord.slice(0, charIndex);

  return (
    <span className={className}>
      {/* Fixed-width container to prevent layout shift. Sized to fit "create" (longest at 6 chars) */}
      <span
        className="text-left text-mirple [text-shadow:0_1px_4px_rgba(0,0,0,0.15),0_2px_8px_rgba(0,0,0,0.1)]"
        style={{ minWidth: "6ch", display: "inline" }}
      >
        {displayText}
        <span
          className="inline-block w-[0.08em] translate-y-[0.05em] bg-mirple align-baseline"
          style={{
            height: "0.85em",
            opacity: cursorVisible ? 1 : 0,
            transition: "opacity 0.1s",
          }}
        />
      </span>
    </span>
  );
}
