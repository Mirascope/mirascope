import type { StorybookConfig } from "@storybook/react-vite";
import { resolve } from "path";

const config: StorybookConfig = {
  stories: ["../src/**/*.mdx", "../src/**/*.stories.@(js|jsx|mjs|ts|tsx)"],
  addons: ["@storybook/addon-essentials"],
  framework: {
    name: "@storybook/react-vite",
    options: {},
  },
  features: {
    viewportStoryGlobals: true, // Enable viewport persistence between story navigation
  },
  core: {
    disableTelemetry: true,
    builder: {
      name: "@storybook/builder-vite",
      options: {
        // Prevent loading the project's Vite config
        viteConfigPath: ".storybook/empty.config.js",
      },
    },
  },
  viteFinal: async (config) => {
    // Configure everything we need for Storybook
    if (config.resolve) {
      config.resolve.alias = {
        ...config.resolve.alias,
        "@": resolve(__dirname, ".."),
        "@/src": resolve(__dirname, "../src"),
      };
    }

    // Add PostCSS with Tailwind
    config.css = {
      postcss: {
        plugins: [
          require("@tailwindcss/postcss")({
            config: "./.storybook/tailwind.config.js",
          }),
          require("autoprefixer"),
        ],
      },
    };

    return config;
  },
};

export default config;
