interface CloudflareRequest extends Request {
  cf?: {
    country?: string;
    timezone?: string;
    continent?: string;
    city?: string;
    region?: string;
    [key: string]: any;
  };
}

import type { CountryDetectionResponse } from "@/src/lib/services/country-detection";

export function countryDetectionHandler(request: Request): Response {
  const cfRequest = request as CloudflareRequest;
  const cf = cfRequest.cf;

  const countryCode = cf?.country || null;
  const timezone = cf?.timezone || null;
  const continent = cf?.continent || null;

  const response: CountryDetectionResponse = {
    country: countryCode,
    timezone: timezone,
    continent: continent,
    timestamp: new Date().toISOString(),
  };

  console.log(`Country detection result: ${JSON.stringify(response)}`);

  return new Response(JSON.stringify(response), {
    status: 200,
    headers: {
      "Content-Type": "application/json",
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET",
      "Cache-Control": "no-cache",
    },
  });
}
