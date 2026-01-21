import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/app/components/ui/card";
import { Skeleton } from "@/app/components/ui/skeleton";

interface TopItem {
  name: string;
  count: number;
}

interface TopItemsListProps {
  title: string;
  items: TopItem[];
  isLoading?: boolean;
}

export function TopItemsList({ title, items, isLoading }: TopItemsListProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="space-y-2">
            {Array.from({ length: 5 }, (_, i) => (
              <Skeleton key={i} className="h-6 w-full" />
            ))}
          </div>
        ) : items.length === 0 ? (
          <p className="text-sm text-muted-foreground">No data available</p>
        ) : (
          <div className="space-y-2">
            {items.slice(0, 5).map((item, index) => (
              <div
                key={item.name}
                className="flex items-center justify-between"
              >
                <span className="text-sm truncate flex-1">
                  {index + 1}. {item.name}
                </span>
                <span className="text-sm font-medium ml-2">
                  {item.count.toLocaleString()}
                </span>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
