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
from bson import json_util
import json

app = Flask(__name__)

@app.route('/api/feed/<customer_id>', methods=['GET'])
def get_customer_by_id(customer_id):
    page = request.args.get('page', default=1, type=int)
    limit = request.args.get('limit', default=10, type=int)
    skip = (page - 1) * limit

    propagator = TraceContextTextMapPropagator()
    ctx = propagator.extract(carrier=request.headers)

    with tracer.start_as_current_span("getting_feed_service-b", context=ctx) as main_span:
        try:
            cached = redis_client.get(f'customer:{customer_id}:posts:{page}:{limit}')
            if cached:
                return jsonify(json.loads(cached))
            collection = get_mongo_collection('user_posts')
            user_posts = list(collection.find({'customer_id': customer_id}).skip(skip).limit(limit))
            user_posts_list = []
            for post in user_posts:
                post['_id'] = str(post['_id']) 
                user_posts_list.append(post)

            redis_client.set(f'customer:{customer_id}:posts:{page}:{limit}', json.dumps(user_posts_list), ex=60)

            return jsonify(user_posts_list)
        except Exception as e:
            main_span.record_exception(e)
            main_span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))

            return jsonify({'error': str(e)}), 500
        finally:
            main_span.end()

def handle_post_create_event(ch, method, properties, body):
        message = json.loads(body)

        with tracer.start_as_current_span("handle_post_create_event") as main_span:
            try:
                with tracer.start_as_current_span("inserting_post_to_mongo_for_read") as mongo_span:
                    collection = get_mongo_collection('user_posts')
                    collection.insert_one(message)

                    mongo_span.end()

                with tracer.start_as_current_span("inserting_post_to_pg_for_analytics") as pg_span:
                    conn = get_pg_connection()
                    cur = conn.cursor()
                    cur.execute("INSERT INTO user_posts (customer_id, title, content) VALUES (%s, %s, %s)", (message['customer_id'], message['title'], message['content']))
                    conn.commit()
                    cur.close()

                    pg_span.end()

                
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
