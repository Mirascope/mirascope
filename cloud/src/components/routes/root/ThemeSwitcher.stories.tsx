import type { Meta, StoryObj } from "@storybook/react";
import ThemeSwitcher from "./ThemeSwitcher";

const meta = {
  title: "Root/ThemeSwitcher",
  component: ThemeSwitcher,
  parameters: {
    layout: "fullscreen",
  },
  tags: ["autodocs"],
  argTypes: {},
} satisfies Meta<typeof ThemeSwitcher>;

export default meta;
type Story = StoryObj<typeof meta>;

export const LandingLight: Story = {
  parameters: {
    product: "mirascope",
    theme: "light",
    landingPage: true,
  },
};

export const LandingDark: Story = {
  parameters: {
    product: "mirascope",
    theme: "dark",
    landingPage: true,
  },
};

export const MirascopeLight: Story = {
  parameters: {
    product: "mirascope",
    theme: "light",
    landingPage: false,
  },
};

export const MirascopeDark: Story = {
  parameters: {
    product: "mirascope",
    theme: "dark",
    landingPage: false,
  },
};

export const LilypadLight: Story = {
  parameters: {
    product: "lilypad",
    theme: "light",
    landingPage: false,
  },
};

export const LilypadDark: Story = {
  parameters: {
    product: "lilypad",
    theme: "dark",
    landingPage: false,
  },
};
