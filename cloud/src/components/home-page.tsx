import { Button } from "@/src/components/ui/button";
import { useAuth } from "@/src/contexts/auth";
import { Link } from "@tanstack/react-router";

export function HomePage() {
  const { user, isLoading, logout } = useAuth();

  if (isLoading) {
    return (
      <div className="w-screen h-screen flex items-center justify-center">
        <div>Loading...</div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="w-screen h-screen flex items-center justify-center">
        <div>Not authenticated</div>
      </div>
    );
  }

  return (
    <div className="w-screen h-screen flex flex-col">
      <div className="flex-1 flex flex-col gap-y-6 justify-center items-center p-8">
        <div className="flex flex-col gap-y-2 items-center">
          <h1 className="text-3xl font-semibold">
            {user.name ? `Welcome, ${user.name.split(" ")[0]}!` : "Welcome!"}
          </h1>
          <div className="text-muted-foreground">{user.email}</div>
        </div>
        <div className="flex gap-3">
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
