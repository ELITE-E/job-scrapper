"use client";

import React from "react";
import { XCircle } from "lucide-react";
import { Button } from "@/components/ui/button";

interface Props {
  onRetry: () => void;
}

export function ErrorState({ onRetry }: Props) {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-center">
      <XCircle className="w-12 h-12 text-destructive mb-4" />
      <h3 className="text-lg font-semibold">Something went wrong</h3>
      <p className="text-sm text-muted-foreground mt-2">
        An error occurred while loading jobs.
      </p>
      <div className="mt-4">
        <Button onClick={onRetry}>Retry</Button>
      </div>
    </div>
  );
}

export default ErrorState;
