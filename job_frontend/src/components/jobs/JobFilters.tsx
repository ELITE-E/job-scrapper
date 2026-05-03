"use client";

import React, { useState } from "react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Filter } from "lucide-react";
import {
  Sheet,
  SheetTrigger,
  SheetContent,
  SheetHeader,
  SheetFooter,
  SheetTitle,
} from "@/components/ui/sheet";
import useCategories from "@/hooks/useCategories";

interface JobFiltersProps {
  selectedCategory: string | null;
  setSelectedCategory: (v: string | null) => void;
  location: string;
  setLocation: (v: string) => void;
  isRemote: boolean | null;
  setIsRemote: (v: boolean | null) => void;
  minSalary: number | null;
  setMinSalary: (v: number | null) => void;
  maxSalary: number | null;
  setMaxSalary: (v: number | null) => void;
  clearFilters: () => void;
}

export function JobFilters({
  selectedCategory,
  setSelectedCategory,
  location,
  setLocation,
  isRemote,
  setIsRemote,
  minSalary,
  setMinSalary,
  maxSalary,
  setMaxSalary,
  clearFilters,
}: JobFiltersProps) {
  const { data: categories, isLoading } = useCategories();
  const [sheetOpen, setSheetOpen] = useState(false);

  function onMinSalaryChange(val: string) {
    const n = val === "" ? null : Number(val);
    setMinSalary(Number.isFinite(n) ? n : null);
  }

  function onMaxSalaryChange(val: string) {
    const n = val === "" ? null : Number(val);
    setMaxSalary(Number.isFinite(n) ? n : null);
  }

  return (
    <div>
      {/* Mobile: sheet trigger */}
      <div className="md:hidden mb-2">
        <Sheet open={sheetOpen} onOpenChange={setSheetOpen}>
          <div
            className="md:hidden cursor-pointer w-full"
            onClick={() => setSheetOpen(true)}
          >
            <Button variant="outline" className="w-full pointer-events-none">
              <Filter className="mr-2 h-4 w-4" /> Filters
            </Button>
          </div>
          <SheetContent side="left">
            <SheetHeader>
              <SheetTitle>Filters</SheetTitle>
            </SheetHeader>
            <div className="p-4 space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">
                  Category
                </label>
                <Select
                  value={selectedCategory ?? ""}
                  onValueChange={(v) => setSelectedCategory(v || null)}
                >
                  <SelectTrigger>
                    <SelectValue
                      placeholder={isLoading ? "Loading..." : "All categories"}
                    />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">All categories</SelectItem>
                    {isLoading ? (
                      <SelectItem value="loading" disabled>
                        Loading...
                      </SelectItem>
                    ) : (
                      categories?.map((c) => (
                        <SelectItem key={c.id} value={c.slug}>
                          {c.name}
                        </SelectItem>
                      ))
                    )}
                  </SelectContent>
                </Select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">
                  Location
                </label>
                <Input
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  placeholder="e.g. San Francisco"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Remote</label>
                <select
                  aria-label="Remote filter"
                  title="Remote filter"
                  value={isRemote === null ? "" : isRemote ? "true" : "false"}
                  onChange={(e) => {
                    const v = e.target.value;
                    if (v === "") setIsRemote(null);
                    else setIsRemote(v === "true");
                  }}
                  className="border rounded px-2 py-1"
                >
                  <option value="">Any</option>
                  <option value="true">Remote</option>
                  <option value="false">On-site</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">
                  Salary range
                </label>
                <div className="flex gap-2">
                  <Input
                    value={minSalary ?? ("" as unknown as string)}
                    onChange={(e) => onMinSalaryChange(e.target.value)}
                    placeholder="Min"
                    type="number"
                  />
                  <Input
                    value={maxSalary ?? ("" as unknown as string)}
                    onChange={(e) => onMaxSalaryChange(e.target.value)}
                    placeholder="Max"
                    type="number"
                  />
                </div>
              </div>

              <div className="flex gap-2">
                <Button variant="outline" onClick={clearFilters}>
                  Clear
                </Button>
              </div>
            </div>
            <SheetFooter>
              <div />
            </SheetFooter>
          </SheetContent>
        </Sheet>
      </div>

      {/* Desktop: persistent sidebar */}
      <aside className="hidden md:block w-64 p-4 border rounded">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Category</label>
            <Select
              value={selectedCategory ?? ""}
              onValueChange={(v) => setSelectedCategory(v || null)}
            >
              <SelectTrigger>
                <SelectValue
                  placeholder={isLoading ? "Loading..." : "All categories"}
                />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">All categories</SelectItem>
                {isLoading ? (
                  <SelectItem value="loading" disabled>
                    Loading...
                  </SelectItem>
                ) : (
                  categories?.map((c) => (
                    <SelectItem key={c.id} value={c.slug}>
                      {c.name}
                    </SelectItem>
                  ))
                )}
              </SelectContent>
            </Select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Location</label>
            <Input
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              placeholder="e.g. Remote or city"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Remote</label>
            <select
              aria-label="Remote filter"
              title="Remote filter"
              value={isRemote === null ? "" : isRemote ? "true" : "false"}
              onChange={(e) => {
                const v = e.target.value;
                if (v === "") setIsRemote(null);
                else setIsRemote(v === "true");
              }}
              className="border rounded px-2 py-1 w-full"
            >
              <option value="">Any</option>
              <option value="true">Remote</option>
              <option value="false">On-site</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">
              Salary range
            </label>
            <div className="flex gap-2">
              <Input
                value={minSalary ?? ("" as unknown as string)}
                onChange={(e) => onMinSalaryChange(e.target.value)}
                placeholder="Min"
                type="number"
              />
              <Input
                value={maxSalary ?? ("" as unknown as string)}
                onChange={(e) => onMaxSalaryChange(e.target.value)}
                placeholder="Max"
                type="number"
              />
            </div>
          </div>

          <div className="flex gap-2">
            <Button variant="outline" onClick={clearFilters}>
              Clear
            </Button>
          </div>
        </div>
      </aside>
    </div>
  );
}

export default JobFilters;
