import { useState, useEffect } from "react";

import {
  useIsLandingPage,
  useIsLoginPage,
  useIsRouterWaitlistPage,
  useTheme,
} from "@/app/components/blocks/theme-provider";

// Enable this flag to see detailed logs about sunset calculations
const VERBOSE_LOGGING = false;

// Map of countries/regions to approximate latitudes for sunset calculation
const REGION_LATITUDES: Record<string, number> = {
  // Northern hemisphere (higher latitudes)
  IS: 65,
  NO: 62,
  FI: 62,
  SE: 62,
  RU: 60,
  EE: 59,
  LV: 57,
  DK: 56,
  LT: 55,
  BY: 54,
  IE: 53,
  UK: 53,
  GB: 53,
  NL: 52,
  DE: 51,
  BE: 51,
  PL: 52,
  CZ: 50,
  SK: 49,
  LU: 49,
  AT: 47,
  CH: 47,
  HU: 47,
  SI: 46,
  HR: 45,
  FR: 46,
  BA: 44,
  RO: 45,
  ME: 43,
  BG: 43,
  RS: 44,
  MK: 41,
  AL: 41,
  IT: 42,
  ES: 40,
  PT: 39,
  GR: 39,
  TR: 39,
  US: 38,
  CA: 56,
  JP: 36,
  // Southern hemisphere (higher latitudes)
  AU: -25,
  NZ: -40,
  AR: -34,
  CL: -33,
  ZA: -30,
  // Near-equatorial countries
  MX: 23,
  BR: -10,
  IN: 20,
  ID: -2,
  MY: 3,
  SG: 1,
  // Default (mid-latitude) for unknown countries
  _: 40,
};

// Calculate day of year (1-366)
function getDayOfYear(date: Date): number {
  const start = new Date(date.getFullYear(), 0, 0);
  const diff =
    date.getTime() -
    start.getTime() +
    (start.getTimezoneOffset() - date.getTimezoneOffset()) * 60 * 1000;
  const oneDay = 1000 * 60 * 60 * 24;
  return Math.floor(diff / oneDay);
}

// Calculate solar declination angle (in degrees) for a given day of year
// 23.44° is Earth's axial tilt, and the offset of 81 days aligns with the spring equinox
function getSolarDeclination(dayOfYear: number): number {
  return 23.44 * Math.sin(((2 * Math.PI) / 365) * (dayOfYear - 81));
}

// Calculate approximate sunset hour based on latitude and day of year
function estimateSunsetHour(latitude: number, dayOfYear: number): number {
  const declination = getSolarDeclination(dayOfYear);

  // Calculate the hour angle (in degrees, then converted to hours)
  // This is the angular displacement of the sun from the local meridian
  const hourAngle =
    (Math.acos(
      -Math.tan((latitude * Math.PI) / 180) *
        Math.tan((declination * Math.PI) / 180),
    ) *
      (180 / Math.PI)) /
    15;

  // Calculate sunset time (12 hours + hour angle)
  // At true noon, the sun is at the local meridian (12:00)
  // The hour angle represents the additional time until sunset
  return 12 + hourAngle;
}

// Calculate when civil twilight ends (sun is 6° below horizon)
// Returns hour in decimal form (e.g., 19.5 = 7:30 PM)
function estimateCivilTwilightEndHour(
  latitude: number,
  dayOfYear: number,
): number {
  const declination = getSolarDeclination(dayOfYear);
  const latRad = (latitude * Math.PI) / 180;
  const decRad = (declination * Math.PI) / 180;

  // Sun altitude for civil twilight end: -6 degrees
  const altitudeRad = (-6 * Math.PI) / 180;

  // Hour angle formula accounting for sun altitude below horizon:
  // cos(ω) = (sin(h) - sin(φ) × sin(δ)) / (cos(φ) × cos(δ))
  const cosHourAngle =
    (Math.sin(altitudeRad) - Math.sin(latRad) * Math.sin(decRad)) /
    (Math.cos(latRad) * Math.cos(decRad));

  // Clamp to valid range (handles extreme latitudes where twilight may not end)
  const clampedCos = Math.max(-1, Math.min(1, cosHourAngle));
  const hourAngle = (Math.acos(clampedCos) * (180 / Math.PI)) / 15;

  return 12 + hourAngle;
}

// Calculates if current time is close to sunset based on location and date
function isAroundSunsetTime(): boolean {
  const date = new Date();
  const dayOfYear = getDayOfYear(date);
  const hour = date.getHours();
  const minutes = date.getMinutes();

  // Source tracking for logging
  let locationSource = "default";

  // Get country code from meta tag if available (set by Cloudflare)
  // Fallback to estimate based on browser locale
  let countryCode = "_"; // Default

  // Try to get from Cloudflare header if available
  const cfCountryMeta = document.querySelector('meta[name="cf-ipcountry"]');
  if (cfCountryMeta) {
    const country = (cfCountryMeta.getAttribute("content") || "").toUpperCase();
    if (REGION_LATITUDES[country]) {
      countryCode = country;
      locationSource = "cloudflare";
    }
  }

  // If no country from Cloudflare, try browser language
  if (countryCode === "_") {
    // userLanguage is a legacy IE property, so we need to check for it safely
    const userLanguage =
      "userLanguage" in navigator &&
      typeof (navigator as { userLanguage?: string }).userLanguage === "string"
        ? (navigator as { userLanguage: string }).userLanguage
        : undefined;
    const browserLang: string | undefined =
      navigator.language || userLanguage || undefined;
    if (
      browserLang &&
      typeof browserLang === "string" &&
      browserLang.includes("-")
    ) {
      const langCountry = browserLang.split("-")[1]?.toUpperCase();
      if (langCountry && REGION_LATITUDES[langCountry]) {
        countryCode = langCountry;
        locationSource = "browser-locale";
      }
    }
  }

  // Get latitude for the country (or default)
  const latitude = REGION_LATITUDES[countryCode] || REGION_LATITUDES["_"];

  // Calculate approximate sunset time based on latitude and day of year
  // This is a simplified model that gives reasonable results
  const sunsetHour = estimateSunsetHour(latitude, dayOfYear);
  const sunsetMinute = Math.round((sunsetHour % 1) * 60);
  const sunsetHourInt = Math.floor(sunsetHour);

  // Format times for logging
  const formattedSunsetTime = `${sunsetHourInt}:${sunsetMinute.toString().padStart(2, "0")}`;
  const formattedCurrentTime = `${hour}:${minutes.toString().padStart(2, "0")}`;

  // Calculate civil twilight end (when it's actually dark) + small buffer
  const BUFFER_MINUTES = 10;
  const civilTwilightEndHour = estimateCivilTwilightEndHour(
    latitude,
    dayOfYear,
  );

  // Window: starts 30 min before sunset, ends when civil twilight ends + buffer
  // Convert everything to minutes since midnight for easier comparison
  const currentTimeMinutes = hour * 60 + minutes;
  const windowStartMinutes = sunsetHourInt * 60 + sunsetMinute - 30;
  const windowEndMinutes =
    Math.floor(civilTwilightEndHour) * 60 +
    Math.round((civilTwilightEndHour % 1) * 60) +
    BUFFER_MINUTES;

  // Format for logging
  const windowStartHour = Math.floor(windowStartMinutes / 60);
  const windowStartMinute = windowStartMinutes % 60;
  const windowEndHour = Math.floor(windowEndMinutes / 60);
  const windowEndMinute = windowEndMinutes % 60;

  const formattedWindowStart = `${windowStartHour}:${windowStartMinute.toString().padStart(2, "0")}`;
  const formattedWindowEnd = `${windowEndHour}:${windowEndMinute.toString().padStart(2, "0")}`;
  const formattedTwilightEnd = `${Math.floor(civilTwilightEndHour)}:${Math.round(
    (civilTwilightEndHour % 1) * 60,
  )
    .toString()
    .padStart(2, "0")}`;

  // Determine if it's sunset time
  const isSunsetTime =
    currentTimeMinutes >= windowStartMinutes &&
    currentTimeMinutes <= windowEndMinutes;

  if (VERBOSE_LOGGING) {
    console.log(
      `%cSunset Check %c${isSunsetTime ? "✅ IS SUNSET TIME" : "❌ not sunset time"}`,
      "color: orange; font-weight: bold",
      isSunsetTime ? "color: #FFB347; font-weight: bold" : "color: gray",
    );
    console.log(
      `- Location: ${countryCode} (source: ${locationSource}, latitude: ${latitude}°)
      - Current time: ${formattedCurrentTime}
      - Estimated sunset: ${formattedSunsetTime}
      - Civil twilight ends: ${formattedTwilightEnd}
      - Sunset window: ${formattedWindowStart} - ${formattedWindowEnd}
      - Day of year: ${dayOfYear}/365`,
    );
  }

  return isSunsetTime;
}

/**
 * Hook that detects if it's currently sunset time and applies/removes
 * the sunset-time class to the document when appropriate.
 *
 * @returns boolean indicating if it's currently sunset time
 */
export function useSunsetTime(): boolean {
  const [isSunsetTime, setIsSunsetTime] = useState(false);
  const { theme } = useTheme();
  const isLandingPage = useIsLandingPage();
  const isLoginPage = useIsLoginPage();
  const isRouterWaitlistPage = useIsRouterWaitlistPage();

  useEffect(() => {
    // Initial check
    const initialCheck = isAroundSunsetTime();
    if (VERBOSE_LOGGING) {
      console.log(
        `%cSunset Hook: Initial check - ${initialCheck ? "Sunset time!" : "Not sunset time"}`,
        "color: #FFA500; font-weight: bold",
      );
    }
    setIsSunsetTime(initialCheck);

    // Set up a timer to check sunset time every 30 seconds (for testing)
    // In production, use 60000 (every minute)
    const checkInterval = VERBOSE_LOGGING ? 10000 : 60000;
    const intervalId = setInterval(() => {
      const checkResult = isAroundSunsetTime();
      if (VERBOSE_LOGGING) {
        console.log(
          `%cSunset Hook: Periodic check - ${checkResult ? "Sunset time!" : "Not sunset time"}`,
          "color: #FFA500; font-weight: bold",
        );
      }
      setIsSunsetTime(checkResult);
    }, checkInterval);

    // Cleanup on unmount
    return () => {
      if (VERBOSE_LOGGING) {
        console.log("%cSunset Hook: Cleaning up interval", "color: #FFA500");
      }
      clearInterval(intervalId);
    };
  }, []);

  // Apply sunset-time class when needed (only when theme is "system")
  useEffect(() => {
    if (
      (isLandingPage || isLoginPage || isRouterWaitlistPage) &&
      isSunsetTime &&
      theme === "system"
    ) {
      if (VERBOSE_LOGGING) {
        console.log(
          "%cSunset Hook: Adding sunset-time class to document",
          "color: #FFA500; font-weight: bold",
        );
      }
      document.documentElement.classList.add("sunset-time");
      return;
    }

    if (
      VERBOSE_LOGGING &&
      document.documentElement.classList.contains("sunset-time")
    ) {
      console.log(
        "%cSunset Hook: Removing sunset-time class from document",
        "color: #FFA500",
      );
    }
    document.documentElement.classList.remove("sunset-time");
  }, [isSunsetTime, isLandingPage, isLoginPage, isRouterWaitlistPage, theme]);

  return isSunsetTime;
}
