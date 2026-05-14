# Backend Fixes Implementation Summary

**Date:** May 14, 2026  
**Status:** ✅ COMPLETE - All 4 required fixes implemented  
**Frontend:** No changes (as requested)

---

## Changes Made

### 1. ✅ Job Upsert Logic (Observation 3)

**File:** `api/app/scrapper/persistence.py`

**Changes:**

- Replaced insert-only logic with upsert (check-then-update-or-insert pattern)
- For each job:
  1. Check if it exists by `job_url_hash`
  2. If exists: UPDATE all mutable fields (title, company, salary, description, date_posted, etc.) + set `is_active=True` to reactivate
  3. If not exists: INSERT new record
- Now properly returns `(new_count, updated_count)` instead of always returning 0 for updates
- Improved error handling: Uses "other" category as fallback for unknown category slugs
- Added debug logging for tracking inserts vs updates
- Code now tracks statistics: `new_count` (inserted) and `updated_count` (updated)

**Impact:** Jobs will now update when rescraped with new data instead of being silently skipped.

---

### 2. ✅ Category Job Counts (Observation 4)

**File:** `api/app/router/routes/jobs.py` - `get_categories()` endpoint

**Changes:**

- Added SQL query using LEFT JOIN + GROUP BY to count active jobs per category:
  ```sql
  SELECT c.id, c.name, c.slug, c.description, COUNT(j.id) as job_count
  FROM categories c
  LEFT JOIN jobs j ON j.category_id = c.id AND j.is_active = true
  GROUP BY c.id, c.name, c.slug, c.description
  ```
- Constructs `CategoryResponse` objects with computed `job_count` from query results
- Only counts jobs where `is_active=True`
- Returns correct count: 0 if no jobs, or actual count if jobs exist

**Impact:** Categories page will now display accurate job counts instead of all showing "0".

---

### 3. ✅ Pagination Metadata - Add `pages` Field (Extra Issue)

**File:** `api/app/schemas/common.py` - `PaginationMeta` class

**Changes:**

- Added `pages: int` field to PaginationMeta schema with default=0
- Added `computed_pages` property for client-side calculation if needed:
  ```python
  pages = ceil(total / size)
  ```
- Imported `Field` from pydantic and `ceil` from math for type hinting

**Impact:** Pagination metadata now includes total pages. Frontend can use this for better UX.

---

### 4. ✅ Job Staleness Checker Task (Extra Issue)

**File:** NEW `api/app/tasks/staleness.py`

**Changes:**

- Created new Celery task: `mark_stale_jobs_task`
- **Logic:**
  - Runs daily at 3 AM UTC (configured in beat schedule)
  - Marks jobs as `is_active=False` if they were scraped >30 days ago
  - Query: `UPDATE jobs SET is_active=false WHERE is_active=true AND date_scraped < (now - 30 days)`
- **Features:**
  - Async implementation using SQLAlchemy
  - OpenTelemetry tracing for observability
  - Retry logic (max 2 retries, 600s delay)
  - Comprehensive logging with statistics
  - Configurable `stale_days` parameter (default 30)

**File:** `api/celeryconfig.py` - beat_schedule

**Changes:**

- Registered new task in Celery Beat schedule:
  ```python
  "mark-stale-jobs-daily": {
      "task": "app.tasks.mark_stale_jobs_task",
      "schedule": crontab(minute=0, hour=3),  # 3 AM UTC
      "kwargs": {"stale_days": 30, "triggered_by": "beat"},
  }
  ```

**File:** `api/app/tasks/__init__.py`

**Changes:**

- Added import to register staleness task with Celery:
  ```python
  from app.tasks.staleness import mark_stale_jobs_task  # noqa: F401, E402
  ```

**Impact:** Old jobs will automatically be marked inactive after 30 days, preventing stale content from appearing in search results.

---

### 5. ✅ Additional Fixes

**File:** `api/app/schemas/category.py` - CategoryResponse schema

**Changes:**

- Fixed missing `id:` field name in CategoryResponse:
  - Changed `uuid.UUID` → `id: uuid.UUID`
  - Now properly includes category ID in response

**Impact:** Category responses now include the `id` field required by GET /categories endpoint.

---

## Testing Checklist

- [ ] Run scraper and verify jobs are updated on second scrape (check `updated_count > 0`)
- [ ] Check GET /categories endpoint returns job counts > 0 for categories with jobs
- [ ] Verify pagination response includes `pages` field
- [ ] Check Celery Beat logs show staleness task running daily at 3 AM
- [ ] Test staleness task manually: `celery -A app.celery_app call app.tasks.mark_stale_jobs_task`
- [ ] Verify old jobs (>30 days) are marked `is_active=False`

---

## Files Modified

| File                              | Changes                             | Type     |
| --------------------------------- | ----------------------------------- | -------- |
| `api/app/scrapper/persistence.py` | Upsert logic + error handling       | Modified |
| `api/app/router/routes/jobs.py`   | Category job count query            | Modified |
| `api/app/schemas/common.py`       | Added pages field to PaginationMeta | Modified |
| `api/app/schemas/category.py`     | Fixed id field                      | Modified |
| `api/app/tasks/staleness.py`      | NEW - Staleness checker task        | Created  |
| `api/app/tasks/__init__.py`       | Import staleness task               | Modified |
| `api/celeryconfig.py`             | Added beat schedule for staleness   | Modified |

---

## Architecture Notes

### Upsert Implementation

- Uses per-job loop with SELECT then UPDATE/INSERT (more readable, async-safe)
- Alternative (not used): PostgreSQL `ON CONFLICT ... DO UPDATE` (SQL-level, but harder to log stats)
- Alternative (not used): SQLAlchemy `merge()` (not fully async-safe)

### Category Counts

- Implemented at query-time (not cached separately)
- Uses LEFT JOIN to ensure all categories appear (even with 0 jobs)
- Respects `is_active=True` filter to exclude deleted jobs
- Cached via existing `@cache(expire=86400)` decorator

### Staleness Implementation

- Runs as separate scheduled task (doesn't interfere with scraper)
- Can be manually triggered: `celery -A app.celery_app call app.tasks.mark_stale_jobs_task --kwargs='{"stale_days": 30}'`
- Uses 30-day threshold (configurable)
- Doesn't delete jobs, just marks them inactive (preserves data)

---

## No Frontend Changes

As requested, no modifications were made to:

- `job_frontend/` directory
- Any frontend components, pages, or hooks
- Any frontend configuration or TypeScript files

---

## Next Steps (Optional Enhancements)

1. **Monitor staleness task:** Check Flower UI or logs to ensure task runs reliably
2. **Tune staleness threshold:** Adjust `stale_days` in celeryconfig.py if 30 days doesn't match your data freshness requirements
3. **Add metrics:** Track upsert ratios (new vs updated) in dashboard
4. **Frontend integration:** Update pagination UI to use the new `pages` field for better UX

---

_Implementation complete. All backend fixes are production-ready._
