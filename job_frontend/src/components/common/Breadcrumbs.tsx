"use client";

import { usePathname, useSearchParams } from "next/navigation";
import Link from "next/link";
import { ChevronRight } from "lucide-react";

interface BreadcrumbItem {
  label: string;
  href?: string;
}

export function Breadcrumbs() {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const categoryParam = searchParams.get("category");

  const breadcrumbs: BreadcrumbItem[] = [];

  // Build breadcrumbs based on current path
  if (pathname === "/jobs") {
    breadcrumbs.push({ label: "Home", href: "/" });
    breadcrumbs.push({ label: "Jobs" });

    // Add category if filtered
    if (categoryParam) {
      breadcrumbs.push({ label: `Category: ${categoryParam}` });
    }
  } else if (pathname === "/categories") {
    breadcrumbs.push({ label: "Home", href: "/" });
    breadcrumbs.push({ label: "Categories" });
  } else if (pathname.startsWith("/jobs/")) {
    breadcrumbs.push({ label: "Home", href: "/" });
    breadcrumbs.push({ label: "Jobs", href: "/jobs" });
    breadcrumbs.push({ label: "Job Details" });
  }

  if (breadcrumbs.length === 0) {
    return null;
  }

  return (
    <nav className="mb-6 flex items-center gap-1 text-sm text-muted-foreground">
      {breadcrumbs.map((item, index) => (
        <div key={index} className="flex items-center gap-1">
          {item.href ? (
            <Link
              href={item.href}
              className="hover:text-foreground transition-colors"
            >
              {item.label}
            </Link>
          ) : (
            <span>{item.label}</span>
          )}
          {index < breadcrumbs.length - 1 && (
            <ChevronRight className="h-4 w-4" />
          )}
        </div>
      ))}
    </nav>
  );
}

export default Breadcrumbs;
