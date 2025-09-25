"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import { useState } from "react";
import { AxiosError } from "axios"; // Import AxiosError for typing

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 5 * 60 * 1000, // 5 minutes
            gcTime: 10 * 60 * 1000, // 10 minutes
            retry: (failureCount: number, error: unknown) => {
              // Narrow error to AxiosError
              if (error && (error as AxiosError).response) {
                const status = (error as AxiosError).response?.status;
                if (status === 401 || status === 403) {
                  return false; // don't retry on auth errors
                }
              }
              return failureCount < 3; // retry up to 3 times for other errors
            },
          },
          mutations: {
            retry: false,
          },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      {process.env.NODE_ENV === "development" && <ReactQueryDevtools />}
    </QueryClientProvider>
  );
}
