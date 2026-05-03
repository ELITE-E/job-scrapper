"use client";

import React from "react";
import { Search } from "lucide-react";
import { Button } from "@/components/ui/button";

interface Props {
  onClear: () => void;
}

export function EmptyState({ onClear }: Props) {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-center">
      <Search className="w-12 h-12 text-muted-foreground mb-4" />
      <h3 className="text-lg font-semibold">
        No jobs found matching your filters
      </h3>
      <p className="text-sm text-muted-foreground mt-2">
        Try clearing some filters or broaden your search.
      </p>
      <div className="mt-4">
        <Button variant="outline" onClick={onClear}>
          Clear filters
        </Button>
      </div>
    </div>
  );
}

export default EmptyState;
