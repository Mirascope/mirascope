import type { Meta, StoryObj } from "@storybook/react";
import { userEvent, within } from "@storybook/test";
import Header from "./Header";
import { VIEWPORT_PRESETS } from "@/.storybook/preview";

async function openSearchBar(canvasElement: HTMLElement) {
  // Wait for the canvas to be fully rendered
  // Get the canvas containing the rendered story
  const canvas = within(canvasElement);

  // Find the search container using the data-testid attribute
  const searchContainer = canvas.getByTestId("search-input");

  // Click on the search input to open it
  await userEvent.click(searchContainer);
}

const meta = {
  title: "Root/Header",
  component: Header,
  parameters: {
    layout: "fullscreen",
    // Make the viewports available to all stories
    viewport: {
      viewports: VIEWPORT_PRESETS,
      defaultViewport: "desktop",
    },
  },
} satisfies Meta<typeof Header>;

export default meta;
type Story = StoryObj<typeof Header>;

// Default header in light mode and Mirascope product
export const Default: Story = {
  name: "Desktop (Default)",
  parameters: {
    product: "mirascope",
    theme: "light",
  },
  args: {
    showProductSelector: false,
  },
};

// Header in dark mode
export const DarkMode: Story = {
  name: "Desktop (Dark Mode)",
  parameters: {
    product: "mirascope",
    theme: "dark",
  },
  args: {
    showProductSelector: false,
  },
};

// Header with product selector for docs pages
export const WithProductSelector: Story = {
  name: "Desktop with Product Selector",
  parameters: {
    product: "mirascope",
    theme: "light",
  },
  args: {
    showProductSelector: true,
  },
};

// Lilypad product
export const LilypadProduct: Story = {
  name: "Desktop (Lilypad Product)",
  parameters: {
    product: "lilypad",
    theme: "light",
  },
  args: {
    showProductSelector: false,
  },
};

// Landing page header
export const LandingPage: Story = {
  name: "Desktop (Landing Page)",
  parameters: {
    product: "mirascope",
    theme: "light",
    landingPage: true,
  },
  args: {
    showProductSelector: false,
  },
};

// Responsive stories - Adding clearer names for autodocs
export const TabletView: Story = {
  name: "Tablet (768px)",
  parameters: {
    product: "mirascope",
    theme: "light",
    viewport: {
      defaultViewport: "tablet",
    },
  },
  args: {
    showProductSelector: true,
  },
};

export const MobileView: Story = {
  name: "Mobile (375px)",
  parameters: {
    product: "mirascope",
    theme: "light",
    viewport: {
      defaultViewport: "mobile",
    },
  },
  args: {
    showProductSelector: false,
  },
};

export const MobileSmallView: Story = {
  name: "Mobile Small (320px)",
  parameters: {
    product: "mirascope",
    theme: "light",
    viewport: {
      defaultViewport: "mobileSmall",
    },
  },
  args: {
    showProductSelector: false,
  },
};

export const MobileMenuOpen: Story = {
  name: "Mobile with Menu Open",
  parameters: {
    product: "mirascope",
    theme: "light",
    viewport: {
      defaultViewport: "mobile",
    },
  },
  args: {
    showProductSelector: false,
  },
  play: async () => {
    // Open the mobile menu for this story
    if (typeof document !== "undefined") {
      setTimeout(() => {
        const menuButton = document.querySelector('button[aria-label="Toggle menu"]');
        if (menuButton instanceof HTMLElement) {
          menuButton.click();
        }
      }, 300); // Small delay to ensure DOM is ready
    }
  },
};

export const TabletWithProductSelector: Story = {
  name: "Tablet with Product Selector",
  parameters: {
    product: "mirascope",
    theme: "light",
    viewport: {
      defaultViewport: "tablet",
    },
  },
  args: {
    showProductSelector: true,
  },
};

// Mobile with dark theme
export const MobileDarkMode: Story = {
  name: "Mobile in Dark Mode",
  parameters: {
    product: "mirascope",
    theme: "dark",
    viewport: {
      defaultViewport: "mobile",
    },
  },
  args: {
    showProductSelector: false,
  },
};

// Landing page on mobile
export const LandingPageMobile: Story = {
  name: "Mobile Landing Page",
  parameters: {
    product: "mirascope",
    theme: "light",
    landingPage: true,
    viewport: {
      defaultViewport: "mobile",
    },
  },
  args: {
    showProductSelector: false,
  },
};

// Stories for search bar - one for each viewport size
export const DesktopSearchOpen: Story = {
  name: "Desktop with Search Open",
  parameters: {
    product: "mirascope",
    theme: "light",
    viewport: {
      defaultViewport: "desktop",
    },
  },
  args: {
    showProductSelector: false,
  },
  play: async ({ canvasElement }) => openSearchBar(canvasElement),
};

export const TabletSearchOpen: Story = {
  name: "Tablet with Search Open",
  parameters: {
    product: "mirascope",
    theme: "light",
    viewport: {
      defaultViewport: "tablet",
    },
  },
  args: {
    showProductSelector: false,
  },
  play: async ({ canvasElement }) => openSearchBar(canvasElement),
};

export const MobileSearchOpen: Story = {
  name: "Mobile with Search Open",
  parameters: {
    product: "mirascope",
    theme: "light",
    viewport: {
      defaultViewport: "mobile",
    },
  },
  args: {
    showProductSelector: false,
  },
  play: async ({ canvasElement }) => openSearchBar(canvasElement),
};

export const MobileSmallSearchOpen: Story = {
  name: "Mobile Small with Search Open",
  parameters: {
    product: "mirascope",
    theme: "light",
    viewport: {
      defaultViewport: "mobileSmall",
    },
  },
  args: {
    showProductSelector: false,
  },
  play: async ({ canvasElement }) => openSearchBar(canvasElement),
};
