"""
==============================================================================
Orbital Sentinel - Kafka Streaming Service
Confluent Kafka integration for real-time data streaming
==============================================================================
"""

import asyncio
import json
from datetime import datetime
from typing import Optional, Callable, Any
from loguru import logger

try:
    from confluent_kafka import Producer, Consumer, KafkaError, KafkaException
    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False
    logger.warning("confluent-kafka not installed, using simulation mode")

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.models import EnvironmentData, StreamMessage
from configs.config import get_config


class KafkaProducer:
    """
    Kafka producer for sending environmental data to Confluent Cloud.
    Falls back to in-memory queue when Kafka is not configured.
    """
    
    def __init__(self):
        """Initialize Kafka producer"""
        self.config = get_config().kafka
        self.producer = None
        self._initialized = False
        self._fallback_queue = []  # In-memory fallback
        
        if KAFKA_AVAILABLE and self.config.api_key and self.config.api_secret:
            try:
                producer_config = {
                    'bootstrap.servers': self.config.bootstrap_servers,
                    'security.protocol': 'SASL_SSL',
                    'sasl.mechanisms': 'PLAIN',
                    'sasl.username': self.config.api_key,
                    'sasl.password': self.config.api_secret,
                    'client.id': 'orbital-sentinel-producer',
                }
                self.producer = Producer(producer_config)
                self._initialized = True
                logger.info("Kafka producer initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Kafka producer: {e}")
                self._initialized = False
        else:
            logger.warning("Kafka not configured, using in-memory fallback")
    
    @property
    def is_available(self) -> bool:
        """Check if Kafka producer is available"""
        return self._initialized
    
    def _delivery_callback(self, err, msg):
        """Callback for message delivery reports"""
        if err:
            logger.error(f"Message delivery failed: {err}")
        else:
            logger.debug(f"Message delivered to {msg.topic()} [{msg.partition()}]")
    
    async def send(
        self,
        data: EnvironmentData,
        topic: Optional[str] = None
    ) -> bool:
        """
        Send environmental data to Kafka topic.
        
        Args:
            data: Environmental data to send
            topic: Optional topic override
            
        Returns:
            True if successful, False otherwise
        """
        target_topic = topic or self.config.topic
        
        try:
            # Create stream message
            message = StreamMessage(
                message_id=f"env-{datetime.utcnow().timestamp()}",
                timestamp=datetime.utcnow(),
                event_type="environment_data",
                payload=data.model_dump(),
                source="orbital-sentinel"
            )
            
            message_json = json.dumps(message.model_dump(), default=str)
            
            if self._initialized and self.producer:
                # Send to Kafka
                self.producer.produce(
                    topic=target_topic,
                    key=str(data.location.region or "unknown"),
                    value=message_json,
                    callback=self._delivery_callback
                )
                self.producer.poll(0)  # Trigger delivery callbacks
                return True
            else:
                # Fallback to in-memory queue
                self._fallback_queue.append(message.model_dump())
                if len(self._fallback_queue) > 1000:
                    self._fallback_queue = self._fallback_queue[-1000:]
                logger.debug(f"Message added to fallback queue (size: {len(self._fallback_queue)})")
                return True
                
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return False
    
    def flush(self, timeout: float = 10.0):
        """Flush pending messages"""
        if self.producer:
            self.producer.flush(timeout)
    
    def get_fallback_messages(self, limit: int = 100) -> list:
        """Get messages from fallback queue"""
        return self._fallback_queue[-limit:]


class KafkaConsumer:
    """
    Kafka consumer for receiving environmental data from Confluent Cloud.
    Falls back to reading from producer's fallback queue when not configured.
    """
    
    def __init__(self, producer: Optional[KafkaProducer] = None):
        """
        Initialize Kafka consumer.
        
        Args:
            producer: Optional producer instance for fallback mode
        """
        self.config = get_config().kafka
        self.consumer = None
        self._initialized = False
        self._running = False
        self._producer = producer  # For fallback mode
        
        if KAFKA_AVAILABLE and self.config.api_key and self.config.api_secret:
            try:
                consumer_config = {
                    'bootstrap.servers': self.config.bootstrap_servers,
                    'security.protocol': 'SASL_SSL',
                    'sasl.mechanisms': 'PLAIN',
                    'sasl.username': self.config.api_key,
                    'sasl.password': self.config.api_secret,
                    'group.id': self.config.group_id,
                    'auto.offset.reset': 'latest',
                    'enable.auto.commit': True,
                }
                self.consumer = Consumer(consumer_config)
                self._initialized = True
                logger.info("Kafka consumer initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Kafka consumer: {e}")
                self._initialized = False
        else:
            logger.warning("Kafka not configured, using fallback mode")
    
    @property
    def is_available(self) -> bool:
        """Check if Kafka consumer is available"""
        return self._initialized
    
    async def subscribe(self, topics: Optional[list] = None):
        """Subscribe to topics"""
        if self.consumer:
            target_topics = topics or [self.config.topic]
            self.consumer.subscribe(target_topics)
            logger.info(f"Subscribed to topics: {target_topics}")
    
    async def consume(
        self,
        callback: Callable[[dict], Any],
        poll_timeout: float = 1.0
    ):
        """
        Start consuming messages.
        
        Args:
            callback: Function to call with each message
            poll_timeout: Timeout for polling in seconds
        """
        self._running = True
        
        if self._initialized and self.consumer:
            logger.info("Starting Kafka consumer loop")
            
            while self._running:
                try:
                    msg = self.consumer.poll(poll_timeout)
                    
                    if msg is None:
                        continue
                    
                    if msg.error():
                        if msg.error().code() == KafkaError._PARTITION_EOF:
                            continue
                        else:
                            raise KafkaException(msg.error())
                    
                    # Parse and process message
                    message_data = json.loads(msg.value().decode('utf-8'))
                    await callback(message_data)
                    
                except Exception as e:
                    logger.error(f"Consumer error: {e}")
                    await asyncio.sleep(1)
        else:
            # Fallback mode - read from producer's queue
            logger.info("Starting fallback consumer loop")
            processed_count = 0
            
            while self._running:
                if self._producer:
                    messages = self._producer.get_fallback_messages(10)
                    for msg in messages[processed_count:]:
                        await callback(msg)
                        processed_count += 1
                
                await asyncio.sleep(poll_timeout)
    
    def stop(self):
        """Stop consuming messages"""
        self._running = False
        if self.consumer:
            self.consumer.close()
        logger.info("Consumer stopped")


class StreamingService:
    """
    High-level streaming service combining producer and consumer.
    Provides a simple interface for streaming environmental data.
    """
    
    def __init__(self):
        """Initialize streaming service"""
        self.producer = KafkaProducer()
        self.consumer = KafkaConsumer(self.producer)
        self._message_handlers = []
        
        logger.info("Streaming service initialized")
    
    @property
    def is_available(self) -> bool:
        """Check if streaming service is available"""
        return self.producer.is_available or True  # Always available with fallback
    
    async def publish(self, data: EnvironmentData) -> bool:
        """
        Publish environmental data to the stream.
        
        Args:
            data: Environmental data to publish
            
        Returns:
            True if successful
        """
        return await self.producer.send(data)
    
    def add_handler(self, handler: Callable[[dict], Any]):
        """
        Add a message handler.
        
        Args:
            handler: Function to call with each message
        """
        self._message_handlers.append(handler)
    
    async def _dispatch_message(self, message: dict):
        """Dispatch message to all handlers"""
        for handler in self._message_handlers:
            try:
                await handler(message)
            except Exception as e:
                logger.error(f"Handler error: {e}")
    
    async def start_consuming(self):
        """Start consuming messages from the stream"""
        await self.consumer.subscribe()
        await self.consumer.consume(self._dispatch_message)
    
    def stop(self):
        """Stop the streaming service"""
        self.consumer.stop()
        self.producer.flush()


# Singleton instance
_streaming_service = None


def get_streaming_service() -> StreamingService:
    """Get or create the singleton streaming service instance"""
    global _streaming_service
    if _streaming_service is None:
        _streaming_service = StreamingService()
    return _streaming_service
