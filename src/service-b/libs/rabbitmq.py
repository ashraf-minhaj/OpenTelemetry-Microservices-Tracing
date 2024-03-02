import pika

credentials = pika.PlainCredentials('auuntoo', 'auuntoo')
parameters = pika.ConnectionParameters(host="rabbitmq", port=5672, credentials=credentials, heartbeat=600)
connection = pika.BlockingConnection(parameters)
rabbitmq_client = connection.channel()
rabbitmq_client.queue_declare(queue='post_create_queue')
