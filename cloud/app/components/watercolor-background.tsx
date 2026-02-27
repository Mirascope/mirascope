import { cn } from "@/app/lib/utils";

import styles from "./watercolor-background.module.css";

export function WatercolorBackground() {
  return <div className={cn(styles.base, styles.landing, "watercolor-bg")} />;
}
