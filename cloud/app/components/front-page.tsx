import { Button } from "@/app/components/ui/button";
import { useAuth } from "@/app/contexts/auth";
import { Link } from "@tanstack/react-router";

export function FrontPage() {
  const { user, isLoading, logout } = useAuth();

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (!user) {
    return <div>Not authenticated</div>;
  }

  return (
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
  );
}
