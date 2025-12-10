import { createContext, useContext, type ReactNode } from "react";
import { type ProductName, type Product, productKey } from "@/src/lib/content/spec";

export { type ProductName, type Product, productKey };

const ProductContext = createContext<Product>({ name: "mirascope" });

export function useProduct() {
  return useContext(ProductContext);
}

interface ProductProviderProps {
  children: ReactNode;
  product: Product;
}

export function ProductProvider({ children, product }: ProductProviderProps) {
  const key = productKey(product);
  const productAttr = { "data-product": key };

  return (
    <ProductContext.Provider value={product}>
      <div {...productAttr} className="h-full">
        {children}
      </div>
    </ProductContext.Provider>
  );
}
