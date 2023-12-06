# tracer.py
"""
This module is for using the uptrace tracer.
"""
import os
import uptrace
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
)

uptrace.configure_opentelemetry(
    dsn=os.getenv("UPTRACE_DSN"),
    service_name="back-snapmsg",
    service_version="1.0.0",
)

provider = TracerProvider()
processor = BatchSpanProcessor(ConsoleSpanExporter())
provider.add_span_processor(processor)

# Sets the global default tracer provider
trace.set_tracer_provider(provider)

# Creates a tracer from the global tracer provider
tracer = trace.get_tracer("back-snapmsg")
