import { countryDetectionHandler } from "./handlers/country-detection";
import { contentMetaCorsHandler } from "./handlers/content-meta-cors";
import { joinRouterWaitlistHandler } from "./handlers/join-router-waitlist";

export default {
  async fetch(request: Request, env: any): Promise<Response> {
    const url = new URL(request.url);
    console.log(`worker dispatch: ${url.pathname}`);

    if (url.pathname === "/cf/country-detection") {
      return countryDetectionHandler(request);
    }

    if (url.pathname.startsWith("/cf/content-meta/")) {
      return contentMetaCorsHandler(request);
    }

    if (url.pathname === "/cf/join-router-waitlist") {
      return joinRouterWaitlistHandler(request, env);
    }

    // For all other requests, return 404 (Assets will handle valid files)
    return new Response("Not Found", { status: 404 });
  },
};
