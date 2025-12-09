import { Button } from "@/src/components/ui/button";
import { useAuth } from "@/src/contexts/auth";
import { Link } from "@tanstack/react-router";

export function HomePage() {
  const { user, isLoading, logout } = useAuth();

  if (isLoading) {
    return (
      <div className="w-full min-h-[calc(60vh-var(--header-height))] flex items-center justify-center p-8">
        <div>Loading...</div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="w-full min-h-[calc(60vh-var(--header-height))] flex items-center justify-center p-8">
        <div>Not authenticated</div>
      </div>
    );
  }

  return (
    <div className="w-full min-h-[calc(60vh-var(--header-height))] flex items-center justify-center p-8">
      <div className="max-w-md text-center">
        <div className="space-y-2">
          <h1 className="text-3xl font-semibold">
            {user.name ? `Welcome, ${user.name.split(" ")[0]}!` : "Welcome!"}
          </h1>
          <div className="text-muted-foreground">{user.email}</div>
        </div>
        <div className="flex gap-3 justify-center mt-6">
          <Link to="/organizations">
            <Button>Organizations</Button>
          </Link>
          <Button variant="outline" onClick={() => void logout()}>
            Logout
          </Button>
        </div>
      </div>
    </div>
  );
}
