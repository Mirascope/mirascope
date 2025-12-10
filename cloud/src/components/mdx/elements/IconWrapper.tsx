import {
  Lightbulb,
  Users,
  Github,
  Star,
  Rocket,
  BookOpen,
  AlertCircle,
  Info,
  CheckCircle,
  ChevronDown,
  AlertTriangle,
  Heart,
  Check,
  DollarSign,
  Globe,
  Bolt,
  Search,
  BarChart,
  Edit,
  FlaskConical,
  Zap,
  // Add other icons as needed
} from "lucide-react";

// Map of icons available in the application
const ICONS: Record<string, any> = {
  lightbulb: Lightbulb,
  users: Users,
  github: Github,
  star: Star,
  rocket: Rocket,
  "book-open": BookOpen,
  "alert-circle": AlertCircle,
  info: Info,
  "check-circle": CheckCircle,
  "chevron-down": ChevronDown,
  "alert-triangle": AlertTriangle,
  heart: Heart,
  check: Check,
  "dollar-sign": DollarSign,
  globe: Globe,
  bolt: Bolt,
  search: Search,
  "bar-chart": BarChart,
  edit: Edit,
  flask: FlaskConical,
  "flask-conical": FlaskConical,
  zap: Zap,
};

interface IconWrapperProps {
  name: string;
  size?: number;
  className?: string;
  [key: string]: any;
}

export function Icon({ name, size = 24, className = "", ...props }: IconWrapperProps) {
  const LucideIcon = ICONS[name];

  if (!LucideIcon) {
    // Error so we will fail CI and ensure this gets fixed.
    throw new Error(`Icon "${name}" not found. Available icons: ${Object.keys(ICONS).join(", ")}`);
  }

  return <LucideIcon size={size} className={className} {...props} />;
}
