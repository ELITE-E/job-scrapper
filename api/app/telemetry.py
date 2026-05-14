import os

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.sampling import ALWAYS_ON, TraceIdRatioBased, ParentBased

# Instrumentation libraries
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor


# Step 2: Create a _build_resource() helper function
def _build_resource() -> Resource:
    """
    Create an OpenTelemetry Resource with service metadata.
    Returns:
        Resource: OpenTelemetry Resource with service metadata.
    """
    return Resource.create({
        SERVICE_NAME: os.environ.get("OTEL_SERVICE_NAME", "job-aggregator"),
        SERVICE_VERSION: os.environ.get("APP_VERSION", "0.1.0"),
        "deployment.environment": os.environ.get("ENVIRONMENT", "development"),
    })


# Step 3: Create a _build_sampler() helper function
def _build_sampler():
    """
    Build a sampler based on environment configuration.
    Returns:
        A Sampler instance (ALWAYS_ON or ParentBased(TraceIdRatioBased)).
    """
    sampler_name = os.environ.get("OTEL_TRACES_SAMPLER", "always_on")
    if sampler_name == "always_on":
        return ALWAYS_ON
    if sampler_name == "traceidratio":
        ratio = float(os.environ.get("OTEL_TRACES_SAMPLER_ARG", "0.1"))
        return ParentBased(root=TraceIdRatioBased(ratio))
    return ALWAYS_ON  # safe default


# Step 4: Create the _create_tracer_provider() function
def _create_tracer_provider() -> TracerProvider:
    """
    Create and configure a TracerProvider with OTLP/gRPC exporter.

    This is the core setup function. It:
    1. Calls _build_resource() and _build_sampler().
    2. Creates an OTLPSpanExporter pointing to OTEL_EXPORTER_OTLP_ENDPOINT.
    3. Wraps the exporter in a BatchSpanProcessor.
    4. Creates a TracerProvider(resource=..., sampler=...) and adds the processor.
    5. Calls trace.set_tracer_provider(provider) to register it globally.

    The BatchSpanProcessor is critical for production: it batches spans
    asynchronously in a background thread, ensuring your application code
    never blocks waiting for span export.

    Returns:
        TracerProvider: Configured tracer provider with OTLP exporter.
    """
    resource = _build_resource()
    sampler = _build_sampler()

    # Configure OTLP/gRPC exporter
    endpoint = os.environ.get(
        "OTEL_EXPORTER_OTLP_ENDPOINT",
        "http://localhost:4317"
    )
    insecure = os.environ.get(
        "OTEL_EXPORTER_OTLP_INSECURE",
        "true"
    ).lower() == "true"

    exporter = OTLPSpanExporter(
        endpoint=endpoint,
        insecure=insecure,
    )

    # Create TracerProvider with resource and sampler
    tracer_provider = TracerProvider(resource=resource, sampler=sampler)

    # Wrap exporter in BatchSpanProcessor for efficient batching
    tracer_provider.add_span_processor(
        BatchSpanProcessor(
            exporter,
            max_queue_size=int(
                os.environ.get("OTEL_BSP_MAX_QUEUE_SIZE", "2048")
            ),
            max_export_batch_size=int(
                os.environ.get("OTEL_BSP_MAX_EXPORT_BATCH_SIZE", "512")
            ),
            schedule_delay_millis=int(
                os.environ.get("OTEL_BSP_SCHEDULE_DELAY_MILLIS", "5000")
            ),
        )
    )

    # Register globally so all modules can get tracers via trace.get_tracer()
    trace.set_tracer_provider(tracer_provider)

    return tracer_provider


# Step 5: Create setup_telemetry(app) for FastAPI
def setup_telemetry(app) -> None:
    """
    Set up OpenTelemetry tracing for FastAPI application.

    This function:
    1. Calls _create_tracer_provider() to set up the global provider.
    2. Instruments FastAPI to automatically capture HTTP request/response data.
    3. Instruments httpx for automatic tracing of outbound HTTP calls (e.g., JobSpy API calls).

    Note: SQLAlchemy instrumentation is NOT handled here. It requires the engine
    instance created in app/database.py and is handled in Section 10.

    Args:
        app: FastAPI application instance.

    Example:
        from fastapi import FastAPI
        from app.telemetry import setup_telemetry

        app = FastAPI()
        setup_telemetry(app)
    """
    try:
        # Create and register global tracer provider
        _create_tracer_provider()

        # Instrument FastAPI to trace HTTP requests
        # Automatically captures request duration, HTTP methods, endpoint paths, status codes, etc.
        FastAPIInstrumentor.instrument_app(app)

        # Instrument httpx for JobSpy's outbound HTTP calls
        # Automatically traces all outbound HTTP requests made by the application
        HTTPXClientInstrumentor().instrument()

    except Exception as e:
        # Don't raise — allow app to run without tracing
        print(f"Failed to set up telemetry: {e}")


# Step 6: Create setup_worker_telemetry() for Celery
def setup_worker_telemetry() -> None:
    """
    Set up OpenTelemetry tracing for Celery worker process.

    This is a separate function called inside the Celery worker_process_init
    signal hook. It:
    1. Calls _create_tracer_provider() to set up the global provider.
    2. Instruments httpx for automatic tracing of outbound HTTP calls.

    Does NOT instrument FastAPI (not relevant in the worker process).

    Note: This must be called AFTER the Celery worker process is initialized.
    Tracing components like BatchSpanProcessor use threading and must be
    initialized after the worker fork is complete.

    Example:
        # In Celery signal handler:
        from celery.signals import worker_process_init
        from app.telemetry import setup_worker_telemetry

        @worker_process_init.connect
        def init_worker_telemetry(**kwargs):
            setup_worker_telemetry()
    """
    try:
        # Create and register global tracer provider
        _create_tracer_provider()

        # Instrument httpx for outbound HTTP calls in worker tasks
        HTTPXClientInstrumentor().instrument()

    except Exception as e:
        # Don't raise — allow worker to start without tracing
        print(f"Failed to set up worker telemetry: {e}")


tracer = trace.get_tracer(__name__)