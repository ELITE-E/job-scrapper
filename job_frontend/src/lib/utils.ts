import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Format salary range for display. Returns null if not available.
import type { Job } from "@/types/job";

export function formatSalary(job: Job): string | null {
  const { salary_min, salary_max, salary_currency, salary_interval } = job;

  if (salary_min == null && salary_max == null) return null;

  const formatValue = (val: number) => {
    try {
      if (salary_currency) {
        return new Intl.NumberFormat(undefined, {
          style: "currency",
          currency: salary_currency,
          maximumFractionDigits: 0,
        }).format(val);
      }
    } catch (e) {
      // fall through
    }
    return `$${new Intl.NumberFormat(undefined, { maximumFractionDigits: 0 }).format(val)}`;
  };

  if (salary_min != null && salary_max != null) {
    return `${formatValue(salary_min)} – ${formatValue(salary_max)}${salary_interval ? ` / ${salary_interval}` : ""}`;
  }

  const single = salary_min != null ? salary_min : (salary_max as number);
  return `${formatValue(single)}${salary_interval ? ` / ${salary_interval}` : ""}`;
}
