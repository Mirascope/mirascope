import type { BaseLogoProps } from "./logoUtils";
import { MirascopeLogo, LilypadLogo, useProduct } from "@/src/components/core";

/**
 * Reusable Logo component with customizable size and text display
 * Automatically swaps between Mirascope and Lilypad logos based on
 * product context.
 */
const ProductLogo: React.FC<BaseLogoProps> = (props) => {
  const product = useProduct();

  switch (product.name) {
    case "lilypad":
      return <LilypadLogo {...props} />;
    case "mirascope":
      return <MirascopeLogo {...props} />;
    default:
      throw new Error(`Unknown product: ${product.name}`);
  }
};

export default ProductLogo;
