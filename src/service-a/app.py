from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
import requests
from flask import Flask, jsonify, request
from random import randint
import json
from opentelemetry import trace
from datetime import datetime

from tracer import configure_tracer
configure_tracer(service_name="service-a")

from libs.rabbitmq import rabbitmq_client
from libs.mongo import get_mongo_collection
from libs.redis import redis_client
from libs.pg import pg_client   

tracer = trace.get_tracer(__name__)

URL_SVC_B = 'http://localhost:5002'

app = Flask(__name__)


@app.route('/api/feed/<customer_id>', methods=['GET'])
def get_feed_by_user_id(customer_id):
    page = request.args.get('page', default=1, type=int)
    limit = request.args.get('limit', default=10, type=int)

    with tracer.start_as_current_span("getting_feed_service-a") as main_span:
        try:

            headers = {}
            propagator = TraceContextTextMapPropagator()
            propagator.inject(carrier=headers)

            customer_data_response = requests.get(
                f'{URL_SVC_B}/api/feed/{customer_id}?page={page}&limit={limit}', headers=headers)
            customer_data = customer_data_response.json()

            return jsonify(customer_data)
        except Exception as e:
            main_span.record_exception(e)
            main_span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))

            return jsonify({'error': str(e)}), 500
        finally:
            main_span.end()


@app.route('/api/<customer_id>/post', methods=['POST'])
def insert_user(customer_id):
    with tracer.start_as_current_span("create_new_post") as main_span:
        try:
            request_data = request.get_json()
            post_data = {
                'content': request_data.get('content'),
                'title': request_data.get('title'),
                'customer_id': customer_id
            }

            main_span.set_attribute('customer_id', customer_id)

            rabbitmq_client.basic_publish(
                exchange='', routing_key='post_create_queue', body=json.dumps(post_data))

            return jsonify({'message': 'Post is creating'})
        except Exception as e:
            main_span.record_exception(e)
            main_span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))

            return jsonify({'error': str(e)}), 500
        finally:
            main_span.end()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
