import { Link } from "@tanstack/react-router";
import { useEffect } from "react";

import { useHomeLink } from "@/app/hooks/use-home-link";

import { WatercolorBackground } from "./watercolor-background";

export function NotFound() {
  const homeLink = useHomeLink();

  // Ensure watercolor-page class is on the HTML element for nav styling
  useEffect(() => {
    document.documentElement.classList.add("watercolor-page");
    return () => {
      document.documentElement.classList.remove("watercolor-page");
    };
  }, []);

  return (
    <>
      <WatercolorBackground />
      <div className="fixed inset-0 z-50 flex flex-col items-center justify-center px-4 text-center">
        <img
          src="/assets/404.webp"
          alt="Two lobsters ridden by purple frogs jousting with sticks in the ocean"
          className="mb-8 w-full max-w-sm rounded-xl shadow-lg"
        />
        <h1 className="text-4xl font-bold tracking-tight text-white drop-shadow-lg">
          Not Found
        </h1>
        <p className="mt-2 text-lg text-white/90 drop-shadow">
          We're not sure what you're looking for. We hope you like what you
          found.
        </p>
        <div className="mt-6 flex items-center gap-3">
          <button
            onClick={() => window.history.back()}
            className="rounded-md bg-white/70 px-4 py-2 text-sm font-semibold text-gray-700 backdrop-blur transition hover:bg-white/90"
          >
            Go back
          </button>
          <Link
            to={homeLink}
            className="rounded-md bg-purple-600 px-4 py-2 text-sm font-semibold text-white shadow transition hover:bg-purple-700"
          >
            Dashboard
          </Link>
        </div>
      </div>
    </>
  );
}
