/**
 * Build the bootstrap HTML page.
 *
 * This page sets localStorage with the gateway connection settings,
 * then redirects to the gateway's built-in Control UI.
 * The OpenClaw gateway serves its own Control UI at its HTTP port,
 * so we just need to configure localStorage and redirect there.
 */

import { gatewayToHttpUrl } from "./gateway";

export function buildBootstrapHtml(
  gatewayWsUrl: string,
  token?: string,
): string {
  const gatewayHttpUrl = gatewayToHttpUrl(gatewayWsUrl);
  const settings = JSON.stringify({
    gatewayUrl: gatewayWsUrl,
    ...(token ? { token } : {}),
  });

  return `<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Claw Debug — Connecting...</title>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      margin: 0;
      background: #1a1a2e;
      color: #e0e0e0;
    }
    .container {
      text-align: center;
      padding: 2rem;
    }
    h1 { font-size: 1.5rem; margin-bottom: 0.5rem; }
    p { color: #888; }
    code {
      background: #2d2d44;
      padding: 0.2em 0.5em;
      border-radius: 4px;
      font-size: 0.9em;
    }
    .fallback {
      margin-top: 2rem;
      padding: 1.5rem;
      background: #2d2d44;
      border-radius: 8px;
    }
    .fallback a {
      color: #6c9fff;
      text-decoration: none;
    }
    .fallback a:hover { text-decoration: underline; }
  </style>
</head>
<body>
  <div class="container">
    <h1>🔌 Connecting to Gateway...</h1>
    <p>Gateway: <code>${escapeHtml(gatewayWsUrl)}</code></p>
    <div class="fallback" id="fallback" style="display:none">
      <p>If you're not redirected automatically:</p>
      <p><a href="${escapeHtml(gatewayHttpUrl)}" id="gateway-link">Open Gateway Control UI →</a></p>
    </div>
  </div>
  <script>
    (function() {
      // Configure the OpenClaw Control UI localStorage settings
      var key = "openclaw.control.settings.v1";
      localStorage.setItem(key, ${JSON.stringify(settings)});

      // Redirect to the gateway's built-in Control UI
      var gatewayUrl = ${JSON.stringify(gatewayHttpUrl)};
      window.location.href = gatewayUrl;

      // Show fallback link after 2 seconds if redirect doesn't work
      setTimeout(function() {
        document.getElementById("fallback").style.display = "block";
      }, 2000);
    })();
  </script>
</body>
</html>`;
}

function escapeHtml(s: string): string {
  return s
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}
