"use client";
import Image from "next/image";
import React from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import DOMPurify from "dompurify";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import ErrorState from "@/components/common/ErrorState";
import useJobDetail from "@/hooks/useJobDetail";
import { formatSalary } from "@/lib/utils";

export default function JobDetailPage() {
  const params = useParams();
  // In App Router, params.id is directly accessible
  const id = params?.id as string;

  const { data: job, isLoading, isError, refetch } = useJobDetail(id);

  if (isLoading) {
    return (
      <div className="max-w-6xl mx-auto p-6 space-y-6">
        <Skeleton className="h-10 w-32" />
        <div className="flex gap-4">
          <Skeleton className="h-20 w-20 rounded" />
          <div className="flex-1 space-y-2">
            <Skeleton className="h-8 w-1/2" />
            <Skeleton className="h-4 w-1/4" />
          </div>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-4">
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-64 w-full" />
          </div>
          <Skeleton className="h-48 w-full" />
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="p-6">
        <ErrorState onRetry={() => refetch()} />
      </div>
    );
  }

  if (!job) return null;

  const cleanDescription = DOMPurify.sanitize(job.description ?? "");
  const salary = formatSalary(job);

  return (
    <div>
      {/* Header wrapper */}
      <div className="bg-muted/50 py-8 px-4">
        <div className="max-w-7xl mx-auto">
          <nav className="mb-4">
            <Button variant="ghost" asChild>
              <Link href="/">← Back to Jobs</Link>
            </Button>
          </nav>

          <header className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
            <div className="flex items-center gap-5">
              {job.company?.logo_url ? (
                <Image
                  src={job.company.logo_url}
                  alt={`${job.company.name} logo`}
                  className="w-20 h-20 rounded-lg object-contain border bg-white"
                />
              ) : (
                <div className="w-20 h-20 rounded-lg bg-muted flex items-center justify-center text-muted-foreground font-bold">
                  {job.company?.name?.charAt(0) ?? "J"}
                </div>
              )}
              <div>
                <h1 className="text-3xl font-extrabold tracking-tight mb-1">
                  {job.title}
                </h1>
                <p className="text-xl text-muted-foreground font-medium mb-3">
                  {job.company?.name}
                </p>
                <div className="flex flex-wrap gap-2">
                  <Badge variant="secondary">
                    {job.location_city ?? "Location N/A"}
                  </Badge>
                  {job.is_remote && (
                    <Badge className="bg-emerald-100 text-emerald-800 hover:bg-emerald-100">
                      Remote
                    </Badge>
                  )}
                  <Badge variant="outline">{job.category ?? "General"}</Badge>
                  <Badge variant="outline">{job.job_type ?? "Full-time"}</Badge>
                </div>
              </div>
            </div>

            <Button asChild size="lg" className="w-full md:w-auto shadow-lg">
              <a href={job.job_url} target="_blank" rel="noopener noreferrer">
                Apply for this job
              </a>
            </Button>
          </header>
        </div>
      </div>

      {/* Body section */}
      <div className="max-w-7xl mx-auto px-4 py-8 grid grid-cols-1 lg:grid-cols-[1fr_320px] gap-8">
        <div>
          <h2 className="text-2xl font-bold mb-4">Job Description</h2>
          <article
            className="prose prose-slate max-w-none dark:prose-invert prose-headings:font-bold prose-a:text-primary hover:prose-a:underline"
            dangerouslySetInnerHTML={{ __html: cleanDescription }}
          />
        </div>

        <aside>
          <Card className="shadow-sm">
            <CardContent className="pt-6 space-y-5">
              <h3 className="font-bold text-lg border-b pb-2">Job Overview</h3>

              <div className="space-y-1">
                <p className="text-sm text-muted-foreground uppercase tracking-wider font-semibold">
                  Salary
                </p>
                <p className="font-medium text-lg">
                  {salary ?? "Not disclosed"}
                </p>
              </div>

              <div className="space-y-1">
                <p className="text-sm text-muted-foreground uppercase tracking-wider font-semibold">
                  Posted Date
                </p>
                <p className="font-medium">
                  {job.created_at
                    ? new Date(job.created_at).toLocaleDateString(undefined, {
                        dateStyle: "long",
                      })
                    : "Recently"}
                </p>
              </div>

              <div className="space-y-1">
                <p className="text-sm text-muted-foreground uppercase tracking-wider font-semibold">
                  Source Site
                </p>
                <p className="font-medium capitalize">
                  {job.source_site ?? "Original Board"}
                </p>
              </div>

              {job.company?.industry && (
                <div className="space-y-1">
                  <p className="text-sm text-muted-foreground uppercase tracking-wider font-semibold">
                    Industry
                  </p>
                  <p className="font-medium">{job.company.industry}</p>
                </div>
              )}
            </CardContent>
          </Card>
        </aside>
      </div>
    </div>
  );
}
