from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.pymongo import PymongoInstrumentor
from opentelemetry.instrumentation.pika import PikaInstrumentor

def configure_tracer(service_name: str):
    trace.set_tracer_provider(
        TracerProvider(
            resource=Resource.create(
                {ResourceAttributes.SERVICE_NAME: service_name})
        )
    )

    jaeger_exporter = JaegerExporter(
        agent_host_name="jaeger",
        agent_port=6831
        # collector_endpoint="http://localhost:14268/api/traces",
    )

    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(jaeger_exporter)
    )

    RedisInstrumentor().instrument()
    Psycopg2Instrumentor().instrument()
    RequestsInstrumentor().instrument()
    PymongoInstrumentor().instrument()
    PikaInstrumentor().instrument()

    print("Tracing initialized")
