import { Link } from "@tanstack/react-router";
import React from "react";
import {
  NavigationMenu,
  NavigationMenuContent,
  NavigationMenuItem,
  NavigationMenuList,
  NavigationMenuTrigger,
  NavigationMenuLink,
} from "@/src/components/ui/navigation-menu";
import { getProductRoute } from "@/src/lib/routes";
import {
  useProduct,
  useIsLandingPage,
  useIsRouterWaitlistPage,
} from "@/src/components/core";
import { PRODUCT_CONFIGS } from "@/src/lib/constants/site";
import { type Product, productKey } from "@/src/lib/content/spec";
import { cn } from "@/src/lib/utils";
import {
  NAV_LINK_STYLES,
  PRODUCT_LINK_STYLES,
  DESKTOP_NAV_STYLES,
} from "./styles";

// Reusable navigation link component
interface NavLinkProps {
  href: string;
  children: React.ReactNode;
  className?: string;
  onClick?: () => void;
}

/**
 * ProductMenuLink component for product navigation links.
 * Retrieves product information from global config and applies appropriate styling.
 */
interface ProductMenuLinkProps {
  product: Product;
}

const ProductMenuLink = ({ product }: ProductMenuLinkProps) => {
  const config = PRODUCT_CONFIGS[product.name];

  return (
    <li>
      <NavigationMenuLink asChild>
        <Link
          to={getProductRoute(product)}
          className={PRODUCT_LINK_STYLES.desktop.container}
          data-product={productKey(product)}
        >
          <div className={PRODUCT_LINK_STYLES.desktop.title}>
            {config.title}
          </div>
          <p className={PRODUCT_LINK_STYLES.desktop.description}>
            {config.tagline}
          </p>
        </Link>
      </NavigationMenuLink>
    </li>
  );
};

const NavLink = ({ href, children, className, onClick }: NavLinkProps) => {
  return (
    <Link
      to={href}
      className={cn(NAV_LINK_STYLES.base, className)}
      onClick={onClick}
    >
      {children}
    </Link>
  );
};

interface DesktopNavigationProps {
  /**
   * Whether the search bar is open, affecting navigation visibility
   */
  isSearchOpen: boolean;
}

export default function DesktopNavigation({
  isSearchOpen,
}: DesktopNavigationProps) {
  // Get the current product
  const product = useProduct();
  const isLandingPage = useIsLandingPage();
  const isRouterWaitlistPage = useIsRouterWaitlistPage();

  return (
    <div className={DESKTOP_NAV_STYLES.container(isSearchOpen)}>
      {/* Products Menu */}
      <NavigationMenu>
        <NavigationMenuList>
          <NavigationMenuItem>
            <NavigationMenuTrigger className={DESKTOP_NAV_STYLES.menuTrigger}>
              <span className={DESKTOP_NAV_STYLES.triggerText}>
                <Link to={getProductRoute(product)} className="h-full w-full">
                  Docs
                </Link>
              </span>
            </NavigationMenuTrigger>
            <NavigationMenuContent
              className={DESKTOP_NAV_STYLES.menuContent(
                isLandingPage || isRouterWaitlistPage,
              )}
            >
              <ul className={DESKTOP_NAV_STYLES.productGrid}>
                <ProductMenuLink product={{ name: "mirascope" }} />
                <ProductMenuLink product={{ name: "lilypad" }} />
              </ul>
            </NavigationMenuContent>
          </NavigationMenuItem>
        </NavigationMenuList>
      </NavigationMenu>
      <NavLink href="/blog">Blog</NavLink>
      <NavLink href="/pricing">Pricing</NavLink>
    </div>
  );
}
