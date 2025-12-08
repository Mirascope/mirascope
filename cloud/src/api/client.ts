import { QueryClient } from "@tanstack/react-query";

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      retry: (failureCount, error) => {
        // Don't retry on 401 (auth errors)
        if (error instanceof Error && error.message.includes("401")) {
          return false;
        }
        return failureCount < 3;
      },
    },
  },
});
