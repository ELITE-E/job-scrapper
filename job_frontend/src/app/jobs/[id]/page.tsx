"use client";

import { marked } from "marked";
import { useParams } from "next/navigation";
import { useMemo } from "react";
import Link from "next/link";
import DOMPurify from "dompurify";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { MapPin } from "lucide-react";
import { formatSalary } from "@/lib/utils";
import { useJobDetail } from "@/hooks/useJobDetail";
import { Breadcrumbs } from "@/components/common/Breadcrumbs";
import ErrorState from "@/components/common/ErrorState";

export default function JobDetailPage() {
  // 1. All hooks first (unconditionally)
  const params = useParams();
  const id = params?.id as string | undefined;
  const { data: job, isLoading, isError, refetch } = useJobDetail(id);

  // 2. Memoized values (still hooks, must be before early returns)
  //   const cleanDescription = useMemo(() => {
  //     if (!job) return "<p>No description available.</p>";
  //     const rawDescription =
  //       job.description ??
  //       (job as { description_html?: string }).description_html ??
  //       (job as { description_markdown?: string }).description_markdown ??
  //       "";
  //     if (!rawDescription) return "<p>No description available.</p>";
  //     return DOMPurify.sanitize(rawDescription);
  //   }, [job]);
  const cleanDescription = useMemo(() => {
    if (!job) return "<p>No description available.</p>";

    const rawDescription = job.description ?? "";
    if (!rawDescription) return "<p>No description available.</p>";

    // Convert Markdown to HTML
    const htmlDescription = marked.parse(rawDescription, {
      async: false,
    }) as string;

    // Sanitize the resulting HTML
    return DOMPurify.sanitize(htmlDescription);
  }, [job]);
  console.log("The job description:", job?.description);
  // 3. Conditional returns AFTER all hooks
  if (isLoading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8 space-y-6">
        <Skeleton className="h-8 w-32" />
        <Skeleton className="h-12 w-2/3" />
        <div className="grid grid-cols-1 lg:grid-cols-[1fr_320px] gap-8">
          <Skeleton className="h-64 w-full" />
          <Skeleton className="h-64 w-full" />
        </div>
      </div>
    );
  }

  if (isError || !job) {
    return <ErrorState onRetry={() => refetch()} />;
  }

  const salary = formatSalary(job);

  return (
    <div>
      <div className="bg-muted/50 py-8 px-4">
        <div className="max-w-7xl mx-auto space-y-4">
          {/* Breadcrumbs */}
          <Breadcrumbs />

          {/* Back to Jobs link */}
          <Link
            href="/jobs"
            className="text-sm text-muted-foreground hover:underline inline-block"
          >
            ← Back to Jobs
          </Link>
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <div className="text-sm text-muted-foreground">
                {job.company?.name}
              </div>
              <h1 className="text-3xl font-bold">{job.title}</h1>
              <div className="mt-2 flex flex-wrap items-center gap-2 text-sm">
                <div className="flex items-center gap-1 text-muted-foreground">
                  <MapPin className="h-4 w-4" />
                  <span>
                    {job.location_city ?? ""}
                    {job.location_state ? `, ${job.location_state}` : ""}
                  </span>
                </div>
                {job.is_remote && <Badge variant="secondary">Remote</Badge>}
                {job.job_type && (
                  <Badge variant="outline">{job.job_type}</Badge>
                )}
                {job.category?.name && <Badge>{job.category.name}</Badge>}
              </div>
            </div>
            <a href={job.job_url} target="_blank" rel="noopener noreferrer">
              <Button>Apply for this job</Button>
            </a>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8 grid grid-cols-1 lg:grid-cols-[1fr_320px] gap-8">
        <div>
          <h2 className="text-2xl font-semibold mb-4">Job Description</h2>
          <article
            className="prose prose-sm sm:prose-base lg:prose-lg max-w-none dark:prose-invert prose-headings:font-bold prose-strong:text-primary"
            dangerouslySetInnerHTML={{ __html: cleanDescription }}
          />
        </div>

        <aside>
          <Card>
            <CardHeader>
              <CardTitle>Job Details</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4 text-sm">
              <div>
                <div className="text-muted-foreground">Salary</div>
                <div className="font-medium">{salary ?? "Not disclosed"}</div>
              </div>
              <div>
                <div className="text-muted-foreground">Source</div>
                <div>{job.source_site}</div>
              </div>
              <div>
                <div className="text-muted-foreground">Job type</div>
                <div>{job.job_type ?? "-"}</div>
              </div>
              <div>
                <div className="text-muted-foreground">Remote</div>
                <div>{job.is_remote ? "Yes" : "No"}</div>
              </div>
            </CardContent>
          </Card>
        </aside>
      </div>
    </div>
  );
}
