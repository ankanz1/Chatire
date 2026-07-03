"""Receive messages from RabbitMQ and send them over the websocket."""
from gevent import monkey
monkey.patch_all()
import os
import asyncio
import websockets
import websockets.server
import pika
from json import dumps


# Monkey-patch to accept Connection: keep-alive and other non-standard connection headers
original_process_request = websockets.server.ServerProtocol.process_request

def patched_process_request(self, request):
    connection_values = request.headers.get_all("Connection")
    if not any("upgrade" in val.lower() for val in connection_values):
        if "Connection" in request.headers:
            del request.headers["Connection"]
        request.headers["Connection"] = "Upgrade"
    return original_process_request(self, request)

websockets.server.ServerProtocol.process_request = patched_process_request


async def handler(websocket):
    """Setup the WebSocket connection and stream messages from RabbitMQ."""
    # Get exchange name from path (e.g., '/31b1a70ef8264ad/' -> '31b1a70ef8264ad')
    exchange = websocket.request.path.strip('/')
    print(f"Client connected. Binding to RabbitMQ exchange: {exchange}")

    rabbitmq_url = os.environ.get('RABBITMQ_URL', 'amqp://guest:guest@localhost:5672/')
    connection = pika.BlockingConnection(
        pika.URLParameters(rabbitmq_url)
    )
    channel = connection.channel()

    channel.exchange_declare(
        exchange=exchange, exchange_type='fanout'
    )

    # exclusive means the queue should be deleted once the connection is closed
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange=exchange, queue=queue_name)

    try:
        # Stream messages from RabbitMQ to WebSocket
        while True:
            # basic_get is non-blocking in terms of thread execution,
            # allowing us to yield control back to asyncio event loop
            await asyncio.sleep(0.1)
            
            method_frame, header_frame, body = channel.basic_get(queue=queue_name)
            if method_frame:
                # Send the message to the client
                message = body.decode('utf-8')
                await websocket.send(message)
                # Acknowledge the message
                channel.basic_ack(delivery_tag=method_frame.delivery_tag)
                
            # Perform a quick non-blocking check to see if client disconnected
            try:
                # If recv() finishes or raises ConnectionClosed, it handles disconnect.
                # Since we don't expect client messages, we just check if it's closed.
                await asyncio.wait_for(websocket.recv(), timeout=0.001)
            except asyncio.TimeoutError:
                pass

    except websockets.exceptions.ConnectionClosed:
        print(f"Client disconnected from exchange: {exchange}")
    finally:
        connection.close()
        print(f"RabbitMQ connection closed for exchange: {exchange}")


async def main():
    port = int(os.environ.get("PORT", 8081))
    async with websockets.serve(handler, "0.0.0.0", port):
        print(f"WebSocket server started on ws://0.0.0.0:{port}")
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
