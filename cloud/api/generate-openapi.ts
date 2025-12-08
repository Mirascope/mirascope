import { OpenApi } from "@effect/platform";
import { MirascopeCloudApi } from "./router";

const baseSpec = OpenApi.fromApi(MirascopeCloudApi);
const spec = {
  ...baseSpec,
  info: {
    ...baseSpec.info,
    title: "Mirascope Cloud API",
    version: "0.1.0",
    description: "Complete API documentation for Mirascope Cloud",
  },
  servers: [
    {
      url: "https://v2.mirascope.com",
      description: "Production server",
      "x-fern-server-name": "production",
    },
    {
      url: "https://staging.mirascope.com",
      description: "Staging server",
      "x-fern-server-name": "staging",
    },
    {
      url: "http://localhost:3000",
      description: "Local development server",
      "x-fern-server-name": "local",
    },
  ],
};

console.log(JSON.stringify(spec, null, 2));
