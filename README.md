# Job Aggregator

A backend-focused job aggregation system that collects software engineering
job listings from multiple sources, normalizes the resulting data, removes
duplicates, and presents a unified view for easier job discovery.

## Why I Built It

Job listings are fragmented across multiple platforms and the same position
often appears on several job boards.

The project explores how to build a system that can collect listings from
different sources, normalize inconsistent data, identify duplicate postings,
and expose the resulting dataset through a single application.

## Architecture

The system is composed of several backend services responsible for:

- Job collection
- Source-specific extraction
- Data normalization
- Duplicate detection
- Background processing
- Persistence
- API access
- Task scheduling

Celery and Redis are used for asynchronous/background processing, while the
database provides persistent storage for normalized job data.

## Engineering Focus

The project gave me practical experience with:

- Python backend development
- RESTful API design
- Relational database design
- Asynchronous task processing
- Service-to-service communication
- Data normalization
- Data deduplication
- Failure handling
- Background job orchestration
- Containerized development
- Git-based development workflows

## Current Status

The core aggregation system has been implemented and tested as part of a
software engineering coding assessment.

The project is currently not deployed publicly. Deployment and further
production hardening remain future work.

## What I Learned

The interesting part of this project was not simply collecting job listings.
The harder problem was dealing with inconsistent data from different sources
and turning it into a reliable dataset.

Different sources represent the same concepts differently, and duplicate
listings cannot be identified reliably using a single field. This required
thinking about normalization, identity, matching strategies, and the
trade-offs between correctness and complexity.

## Future Improvements

Potential next steps include:

- Production deployment
- Improved duplicate detection
- More robust source adapters
- Monitoring and observability
- Retry and failure policies
- Dataset versioning
- Search and filtering improvements
- Automated testing across source adapters
