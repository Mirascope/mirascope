/**
 * Country detection utilities for client-side usage
 */

// Shared interface with the Cloudflare worker
export interface CountryDetectionResponse {
  country: string | null;
  timezone: string | null;
  continent: string | null;
  timestamp: string;
}

// Cache key and duration
const CACHE_KEY = "cf-country-data";
const CACHE_DURATION_MS = 24 * 60 * 60 * 1000; // 24 hours

/**
 * Get the user's country code with caching
 */
export async function getCountryCode(): Promise<string | null> {
  if (typeof window === "undefined") return null;

  // Check cache first
  const cached = getCachedCountryData();
  if (cached?.country) {
    return cached.country;
  }

  // Fetch from API
  try {
    const response = await fetch("/cf/country-detection");
    if (!response.ok) return null;

    const data: CountryDetectionResponse = await response.json();

    if (data.country) {
      setCachedCountryData(data);
      return data.country;
    }
  } catch (error) {
    console.log("Failed to fetch country code:", error);
  }

  return null;
}

/**
 * Get full country detection data with caching
 */
export async function getCountryData(): Promise<CountryDetectionResponse | null> {
  if (typeof window === "undefined") return null;

  // Check cache first
  const cached = getCachedCountryData();
  if (cached) {
    return cached;
  }

  // Fetch from API
  try {
    const response = await fetch("/cf/country-detection");
    if (!response.ok) return null;

    const data: CountryDetectionResponse = await response.json();
    setCachedCountryData(data);
    return data;
  } catch (error) {
    console.log("Failed to fetch country data:", error);
    return null;
  }
}

/**
 * Get cached country data if still valid
 */
function getCachedCountryData(): CountryDetectionResponse | null {
  const cached = sessionStorage.getItem(CACHE_KEY);
  if (!cached) return null;

  try {
    const data: CountryDetectionResponse = JSON.parse(cached);
    const cacheTime = new Date(data.timestamp).getTime();
    const now = Date.now();

    // Check if cache is still valid
    if (now - cacheTime < CACHE_DURATION_MS) {
      return data;
    }

    // Cache expired, remove it
    sessionStorage.removeItem(CACHE_KEY);
    return null;
  } catch (error) {
    // Invalid cached data, remove it
    sessionStorage.removeItem(CACHE_KEY);
    return null;
  }
}

/**
 * Cache country data
 */
function setCachedCountryData(data: CountryDetectionResponse): void {
  sessionStorage.setItem(CACHE_KEY, JSON.stringify(data));
}
