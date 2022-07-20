import os

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.botocore import BotocoreInstrumentor
from opentelemetry.instrumentation.elasticsearch import ElasticsearchInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

def post_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)
    if os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT'):
        resource = Resource.create(attributes={
            "service.name": "ProductFlaskApp"
        })

        trace.set_tracer_provider(TracerProvider(resource=resource))
        span_processor = BatchSpanProcessor(
            OTLPSpanExporter(endpoint=os.environ.get('OTEL_EXPORTER_OTLP_ENDPOINT'))
        )
        trace.get_tracer_provider().add_span_processor(span_processor)
        BotocoreInstrumentor().instrument()
        ElasticsearchInstrumentor().instrument()
        RequestsInstrumentor().instrument()
