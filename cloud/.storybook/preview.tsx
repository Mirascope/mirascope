import type { Preview } from "@storybook/react";
import {
  RouterProvider,
  createMemoryHistory,
  createRootRoute,
  createRouter,
} from "@tanstack/react-router";
import { withProductTheme } from "./ProductThemeDecorator";
import "../src/styles/styles.css"; // This imports all other CSS files including themes.css and nav.css

type Viewport = {
  name: string;
  styles: {
    width: string;
    height: string;
  };
};

// Define responsive viewport presets - canonical source of truth for all stories
export const VIEWPORT_PRESETS: Record<string, Viewport> = {
  desktop: {
    name: "Desktop",
    styles: {
      width: "1440px",
      height: "800px",
    },
  },
  tablet: {
    name: "Tablet",
    styles: {
      width: "768px",
      height: "1024px",
    },
  },
  mobile: {
    name: "Mobile",
    styles: {
      width: "375px",
      height: "667px",
    },
  },
  mobileSmall: {
    name: "Mobile Small",
    styles: {
      width: "320px",
      height: "568px",
    },
  },
};

const preview: Preview = {
  parameters: {
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
    },
    backgrounds: {
      disable: true, // Disable default backgrounds since we're using our custom themes
    },
    layout: "fullscreen", // Use full screen layout for all stories by default
    viewport: {
      viewports: VIEWPORT_PRESETS,
      defaultViewport: "desktop",
    },
    docs: {
      story: {
        inline: false, // Make story embeds use the full width
        height: "300px", // Minimum height for docs mode stories
      },
    },
  },
  globalTypes: {
    product: {
      name: "Product",
      description: "Product theme to use",
      defaultValue: "mirascope",
      toolbar: {
        icon: "paintbrush",
        items: [
          { value: "mirascope", title: "Mirascope", right: "🟣" },
          { value: "lilypad", title: "Lilypad", right: "🟢" },
        ],
      },
    },
    theme: {
      name: "Theme",
      description: "Color theme to use",
      defaultValue: "light",
      toolbar: {
        icon: "circlehollow",
        items: [
          { value: "light", title: "Light", icon: "sun" },
          { value: "dark", title: "Dark", icon: "moon" },
        ],
      },
    },
    landingPage: {
      name: "Landing Page",
      description: "Toggle landing page styling",
      defaultValue: false,
      toolbar: {
        icon: "home",
        items: [
          { value: false, title: "Regular Page" },
          { value: true, title: "Landing Page" },
        ],
      },
    },
    viewport: {
      name: "Viewport",
      description: "Viewport size for responsive testing",
      defaultValue: "desktop",
      toolbar: {
        icon: "mobile",
        items: [
          { value: "desktop", title: "Desktop (1440px)" },
          { value: "tablet", title: "Tablet (768px)" },
          { value: "mobile", title: "Mobile (375px)" },
          { value: "mobileSmall", title: "Mobile Small (320px)" },
        ],
      },
    },
  },
  decorators: [
    // First wrap in TanStack Router provider to handle router dependencies
    (Story) => {
      // Create a root route with our Story as the component
      const RootRoute = createRootRoute({
        component: () => <Story />,
      });

      // Create router with memory history
      const router = createRouter({
        routeTree: RootRoute,
        history: createMemoryHistory({
          initialEntries: ["/"], // Start at the root path
        }),
      });
      return <RouterProvider router={router} />;
    },

    // Then apply theme decorator
    (Story, context) => {
      // Use story parameters if provided, otherwise use toolbar globals
      const product = context.parameters.product || context.globals.product;
      const theme = context.parameters.theme || context.globals.theme;
      const landingPage =
        context.parameters.landingPage !== undefined
          ? context.parameters.landingPage
          : context.globals.landingPage;

      // Apply viewport based on the global type or story parameter
      if (context.globals.viewport && context.viewMode !== "docs") {
        const viewportKey =
          context.parameters.viewport?.defaultViewport || context.globals.viewport;
        const viewportValue = VIEWPORT_PRESETS[viewportKey];

        if (viewportValue) {
          // Set viewport dimensions based on the selected option
          const { width, height } = viewportValue.styles;
          if (context.containerRef?.current) {
            context.containerRef.current.style.width = width;
            context.containerRef.current.style.height = height;
          }
        }
      }

      return withProductTheme(product, theme, landingPage)(Story);
    },
  ],
};

export default preview;
