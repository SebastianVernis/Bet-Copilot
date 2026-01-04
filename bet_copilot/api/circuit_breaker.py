"""
Circuit Breaker pattern for API resilience.
Protects against cascading failures and rate limits.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Callable, Optional

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Blocking requests
    HALF_OPEN = "half_open"  # Testing recovery


class CircuitBreakerError(Exception):
    """Circuit breaker is open."""

    pass


class CircuitBreaker:
    """
    Circuit Breaker pattern implementation.
    
    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Too many failures, block all requests
    - HALF_OPEN: After timeout, allow one test request
    
    Transitions:
    - CLOSED -> OPEN: After failure_threshold failures
    - OPEN -> HALF_OPEN: After timeout expires
    - HALF_OPEN -> CLOSED: If test request succeeds
    - HALF_OPEN -> OPEN: If test request fails
    """

    def __init__(
        self,
        timeout: int = 60,
        failure_threshold: int = 3,
        success_threshold: int = 1,
    ):
        """
        Initialize circuit breaker.
        
        Args:
            timeout: Seconds to wait before trying again (OPEN -> HALF_OPEN)
            failure_threshold: Failures before opening circuit
            success_threshold: Successes needed to close from HALF_OPEN
        """
        self.timeout = timeout
        self.failure_threshold = failure_threshold
        self.success_threshold = success_threshold

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.lock = asyncio.Lock()

    def is_open(self) -> bool:
        """Check if circuit is open."""
        return self.state == CircuitState.OPEN

    def is_closed(self) -> bool:
        """Check if circuit is closed."""
        return self.state == CircuitState.CLOSED

    async def _should_attempt(self) -> bool:
        """Determine if request should be attempted."""
        async with self.lock:
            if self.state == CircuitState.CLOSED:
                return True

            if self.state == CircuitState.OPEN:
                # Check if timeout expired
                if (
                    self.last_failure_time
                    and datetime.now() - self.last_failure_time
                    >= timedelta(seconds=self.timeout)
                ):
                    logger.info("Circuit breaker transitioning to HALF_OPEN")
                    self.state = CircuitState.HALF_OPEN
                    return True
                else:
                    return False

            if self.state == CircuitState.HALF_OPEN:
                # Allow test request
                return True

            return False

    async def _record_success(self):
        """Record successful request."""
        async with self.lock:
            self.failure_count = 0

            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.success_threshold:
                    logger.info("Circuit breaker closing (recovery successful)")
                    self.state = CircuitState.CLOSED
                    self.success_count = 0

    async def _record_failure(self):
        """Record failed request."""
        async with self.lock:
            self.failure_count += 1
            self.last_failure_time = datetime.now()
            self.success_count = 0

            if self.state == CircuitState.HALF_OPEN:
                logger.warning("Test request failed, reopening circuit")
                self.state = CircuitState.OPEN

            elif self.failure_count >= self.failure_threshold:
                logger.warning(
                    f"Failure threshold reached ({self.failure_count}), opening circuit"
                )
                self.state = CircuitState.OPEN

    async def call(self, func: Callable, *args, **kwargs):
        """
        Execute function with circuit breaker protection.
        
        Args:
            func: Async function to call
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Function result
            
        Raises:
            CircuitBreakerError: If circuit is open
        """
        if not await self._should_attempt():
            time_remaining = 0
            if self.last_failure_time:
                elapsed = (datetime.now() - self.last_failure_time).total_seconds()
                time_remaining = max(0, self.timeout - elapsed)

            logger.warning(
                f"Circuit breaker is open. Retry in {time_remaining:.0f}s"
            )
            raise CircuitBreakerError(
                f"Circuit breaker is open. Retry in {time_remaining:.0f}s"
            )

        try:
            result = await func(*args, **kwargs)
            await self._record_success()
            return result

        except Exception as e:
            await self._record_failure()
            raise

    async def manual_open(self):
        """Manually open the circuit (e.g., for rate limits)."""
        async with self.lock:
            logger.warning("Manually opening circuit breaker")
            self.state = CircuitState.OPEN
            self.last_failure_time = datetime.now()

    async def manual_close(self):
        """Manually close the circuit."""
        async with self.lock:
            logger.info("Manually closing circuit breaker")
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.success_count = 0

    def get_state(self) -> dict:
        """Get current state information."""
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure": (
                self.last_failure_time.isoformat() if self.last_failure_time else None
            ),
        }
