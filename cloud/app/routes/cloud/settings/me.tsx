import { createFileRoute } from "@tanstack/react-router";
import { useAuth } from "@/app/contexts/auth";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/app/components/ui/card";
import { Input } from "@/app/components/ui/input";
import { Label } from "@/app/components/ui/label";

function MyDetailsSettingsPage() {
  const { user, isLoading } = useAuth();

  const header = (
    <div className="mb-6">
      <h1 className="text-2xl font-semibold">My Details</h1>
      <p className="text-muted-foreground mt-1">Your personal information</p>
    </div>
  );

  if (isLoading) {
    return (
      <div className="max-w-2xl">
        {header}
        <div className="flex justify-center pt-12">
          <div className="text-muted-foreground">Loading...</div>
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="max-w-2xl">
        {header}
        <div className="flex justify-center pt-12">
          <div className="text-muted-foreground">
            Please sign in to continue
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl">
      {header}

      <Card>
        <CardHeader>
          <CardTitle>Account Information</CardTitle>
          <CardDescription>Your account details</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="user-name">Name</Label>
            <Input
              id="user-name"
              value={user.name ?? ""}
              readOnly
              className="bg-muted"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="user-email">Email</Label>
            <Input
              id="user-email"
              value={user.email}
              readOnly
              className="bg-muted"
            />
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

export const Route = createFileRoute("/cloud/settings/me")({
  component: MyDetailsSettingsPage,
});
