"use client";

import React from "react";
//import Link from "next/link";
import {
  Card,
  CardHeader,
  CardContent,
  CardFooter,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { MapPin, Building } from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import { formatSalary } from "@/lib/utils";
import type { JobDetail } from "@/types/job";

interface Props {
  //job: Job;
  job: JobDetail;
}

export function JobCard({ job }: Props) {
  const salary = formatSalary(job);

  return (
    <Card className="flex flex-col h-full">
      <CardHeader>
        <div className="flex items-start justify-between gap-4">
          <div className="min-w-0">
            <CardTitle>
              <a
                href={job.job_url}
                target="_blank"
                rel="noreferrer"
                className="text-lg font-bold block line-clamp-2"
              >
                {job.title}
              </a>
            </CardTitle>

            <div className="mt-2 flex items-center gap-3 text-sm text-muted-foreground">
              <div className="flex items-center gap-2">
                {job.company?.logo_url ? (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img
                    src={job.company.logo_url}
                    alt={job.company.name}
                    className="w-8 h-8 rounded-md object-cover"
                  />
                ) : (
                  <Building className="w-5 h-5 text-muted-foreground" />
                )}
                <span>{job.company?.name ?? "Unknown company"}</span>
              </div>

              <div className="flex items-center gap-1">
                <MapPin className="w-4 h-4" />
                <span>
                  {job.location_city ?? ""}
                  {job.location_state ? `, ${job.location_state}` : ""}
                </span>
              </div>

              {job.is_remote && <Badge variant="secondary">Remote</Badge>}

              {job.job_type && <Badge variant="outline">{job.job_type}</Badge>}

              {job.category?.name && <Badge>{job.category.name}</Badge>}
            </div>
          </div>
        </div>
      </CardHeader>

      <CardContent className="flex-1">
        <div className="text-sm text-muted-foreground mb-2">
          {salary && <div className="font-medium">{salary}</div>}
        </div>
        <div className="text-sm text-muted-foreground">
          {job.description ? job.description.slice(0, 240) : ""}
        </div>
      </CardContent>

      <CardFooter>
        <div className="flex items-center w-full gap-4">
          <div className="text-sm text-muted-foreground">
            {job.date_posted
              ? formatDistanceToNow(new Date(job.date_posted), {
                  addSuffix: true,
                })
              : ""}
          </div>

          <div className="ml-auto">
            <Button asChild>
              <a href={`/jobs/${job.id}`}>View Details</a>
            </Button>
          </div>
        </div>
      </CardFooter>
    </Card>
  );
}

export default JobCard;
