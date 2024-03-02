from flask import Flask, jsonify, request
from random import randint
import json
from opentelemetry import trace, context
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from tracer import configure_tracer

configure_tracer(service_name="service-b")
tracer = trace.get_tracer(__name__)

from libs.redis import redis_client
from threading import Thread
from libs.rabbitmq import rabbitmq_client
from libs.pg import get_pg_connection
from libs.mongo import get_mongo_collection

app = Flask(__name__)

@app.route('/api/feed/<customer_id>', methods=['GET'])
def get_customer_by_id(customer_id):
    tracer = trace.get_tracer(__name__)

    propagator = TraceContextTextMapPropagator()
    ctx = propagator.extract(carrier=request.headers)

    with tracer.start_as_current_span("getting_feed_service-b", context=ctx) as main_span:
        try:
            user_posts = [
                {
                    'id': 1,
                    'title': 'Post 1',
                    'content': 'Content 1'
                },
                {
                    'id': 2,
                    'title': 'Post 2',
                    'content': 'Content 2'
                },
                {
                    'id': 3,
                    'title': 'Post 3',
                    'content': 'Content 3'
                }
            ]
            return jsonify(user_posts)
        except Exception as e:
            main_span.record_exception(e)
            main_span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))

            return jsonify({'error': str(e)}), 500
        finally:
            main_span.end()

def handle_post_create_event(ch, method, properties, body):
        message = json.loads(body)
        print("Received message:", message)

        tracer = trace.get_tracer(__name__)

        with tracer.start_as_current_span("handle_post_create_event") as main_span:
            try:
              print("Saving user to database")
              
            except Exception as e:
                main_span.record_exception(e)
                main_span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            finally:
                main_span.end()

def consume_messages():
    rabbitmq_client.basic_consume(queue='post_create_queue',
                          on_message_callback=handle_post_create_event,
                          auto_ack=True)

    print('Waiting for messages. To exit press CTRL+C')

    rabbitmq_client.start_consuming()

if __name__ == '__main__':
    consumer_thread = Thread(target=consume_messages)
    consumer_thread.start()
    app.run(host='0.0.0.0', port=5002)
