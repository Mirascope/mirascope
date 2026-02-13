import type { ReactNode } from "react";

import { useNavigate } from "@tanstack/react-router";
import { BarChart3, Bot, Shield, Zap } from "lucide-react";

import { Button } from "@/app/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/app/components/ui/card";
import { WatercolorBackground } from "@/app/components/watercolor-background";
import { useAuth } from "@/app/contexts/auth";
import { useSunsetTime } from "@/app/hooks/sunset-time";

interface GithubButtonProps {
  iconSize?: number;
  children?: ReactNode;
  onClick?: () => void;
}

// todo(seb): leverage shared component
function GitHubLoginButton({
  iconSize = 24,
  children,
  onClick,
}: GithubButtonProps) {
  return (
    <Button
      variant="outline"
      onClick={onClick}
      className="w-72 h-12 font-sans rounded-lg border-black/20 hover:bg-black/5 dark:border-white/30 dark:hover:bg-white/10"
    >
      <svg
        fill="currentColor"
        role="img"
        viewBox="0 0 24 24"
        width={iconSize}
        height={iconSize}
        xmlns="http://www.w3.org/2000/svg"
        className="mr-3 flex-shrink-0 text-black dark:text-white"
      >
        <path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12" />
      </svg>
      <span className="text-black dark:text-white font-medium">{children}</span>
    </Button>
  );
}

interface GoogleButtonProps {
  iconSize?: number;
  children?: ReactNode;
  onClick?: () => void;
}

// todo(seb): leverage shared component
function GoogleLoginButton({
  iconSize = 24,
  children,
  onClick,
}: GoogleButtonProps) {
  return (
    <Button
      variant="outline"
      onClick={onClick}
      className="w-72 h-12 font-sans rounded-lg border-black/20 hover:bg-black/5 dark:border-white/30 dark:hover:bg-white/10"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 48 48"
        width={iconSize}
        height={iconSize}
        className="mr-3 flex-shrink-0"
      >
        <path
          fill="#EA4335"
          d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"
        />
        <path
          fill="#4285F4"
          d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"
        />
        <path
          fill="#FBBC05"
          d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"
        />
        <path
          fill="#34A853"
          d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"
        />
      </svg>
      <span className="text-black dark:text-white font-medium">{children}</span>
    </Button>
  );
}

export function LoginPage() {
  useSunsetTime();
  const { user, isLoading, loginWithGitHub, loginWithGoogle } = useAuth();
  const navigate = useNavigate();

  if (!isLoading && user) {
    void navigate({ to: "/cloud", replace: true });
  }

  const features = [
    {
      icon: Bot,
      title: "Deploy AI bots instantly",
      description: "Go from idea to live bot with one click",
    },
    {
      icon: BarChart3,
      title: "Built-in observability",
      description: "Traces, logs, and analytics out of the box",
    },
    {
      icon: Zap,
      title: "Powered by top models",
      description: "Claude Haiku, Sonnet, and Opus built in",
    },
    {
      icon: Shield,
      title: "Free tier included",
      description: "Start building today at no cost",
    },
  ];

  return (
    <>
      <WatercolorBackground />
      <div className="flex min-h-[calc(100vh-var(--header-height))] items-center justify-center p-6 sm:p-8">
        <div className="flex flex-col lg:flex-row items-center gap-10 lg:gap-16">
          <Card className="flex flex-col h-fit w-fit p-2 bg-card text-black dark:text-white border-black/10 dark:border-white/10">
            <CardHeader className="mb-2 text-center">
              <CardTitle className="text-2xl">Mirascope Cloud</CardTitle>
            </CardHeader>
            <CardContent className="flex flex-col justify-center items-center gap-y-3">
              <GitHubLoginButton onClick={loginWithGitHub}>
                Sign in with GitHub
              </GitHubLoginButton>
              <GoogleLoginButton onClick={loginWithGoogle}>
                Sign in with Google
              </GoogleLoginButton>
            </CardContent>
          </Card>
          <Card className="flex flex-col h-fit w-fit p-6 bg-background/80 backdrop-blur-sm text-black dark:text-white border-black/10 dark:border-white/10">
            <h2 className="text-3xl font-bold tracking-tight mb-8">
              Your AI bot in 30 seconds
            </h2>
            <div className="space-y-6">
              {features.map((feature) => (
                <div key={feature.title} className="flex items-start gap-4">
                  <feature.icon className="size-6 text-mirple mt-0.5 shrink-0" />
                  <div className="text-left">
                    <p className="font-semibold">{feature.title}</p>
                    <p className="text-sm text-muted-foreground">
                      {feature.description}
                    </p>
                  </div>
                </div>
              ))}
            </div>
            <p className="mt-10 text-sm text-muted-foreground">
              Free to start. No credit card required.
            </p>
          </Card>
        </div>
      </div>
    </>
  );
}
