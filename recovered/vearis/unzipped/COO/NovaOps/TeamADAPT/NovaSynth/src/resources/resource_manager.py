"""
NovaSynth Resource Manager

Manages resource allocation, optimization, and sharing between frameworks. The resource
manager ensures efficient use of system resources while enabling natural framework
evolution and synthesis.

Created by Cosmos
Version: 0.1.0
"""

from typing import Dict, List, Optional, Set, Union, Any
from dataclasses import dataclass
from datetime import datetime
import asyncio
import logging
import uuid

from pydantic import BaseModel
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ResourceAllocation:
    """Resource allocation for a framework."""
    allocation_id: str
    framework_id: str
    resource_type: str
    allocated: Dict[str, float]
    limits: Dict[str, float]
    usage: Dict[str, float]
    timestamp: datetime
    metadata: Dict

class ResourceRequest(BaseModel):
    """Request for resource allocation."""
    request_id: str
    framework_id: str
    resource_type: str
    requirements: Dict[str, float]
    priority: int
    flexibility: float  # 0-1, how flexible the request is
    timestamp: datetime
    metadata: Dict

class ResourceMetrics(BaseModel):
    """Metrics for resource usage and efficiency."""
    allocation_efficiency: float
    usage_efficiency: float
    resource_balance: float
    adaptation_rate: float
    timestamp: datetime

class ResourceManager:
    """Manages framework resource allocation and optimization."""

    def __init__(self):
        self.allocations: Dict[str, ResourceAllocation] = {}
        self.requests: Dict[str, ResourceRequest] = {}
        self.resource_pools: Dict[str, Dict[str, float]] = {
            "compute": {"total": 100.0, "available": 100.0},
            "memory": {"total": 100.0, "available": 100.0},
            "network": {"total": 100.0, "available": 100.0}
        }
        self.allocation_history: List[Dict] = []
        self.metrics_history: List[ResourceMetrics] = []
        logger.info("Resource Manager initialized")

    async def request_resources(
        self, framework_id: str,
        resource_type: str,
        requirements: Dict[str, float],
        priority: int = 1,
        flexibility: float = 0.5
    ) -> ResourceRequest:
        """Request resources for a framework."""
        request = ResourceRequest(
            request_id=str(uuid.uuid4()),
            framework_id=framework_id,
            resource_type=resource_type,
            requirements=requirements,
            priority=priority,
            flexibility=flexibility,
            timestamp=datetime.utcnow(),
            metadata={}
        )

        self.requests[request.request_id] = request
        logger.info(f"Resource request from {framework_id}: {request.request_id}")
        return request

    async def allocate_resources(
        self, request: ResourceRequest
    ) -> Optional[ResourceAllocation]:
        """Allocate resources based on request."""
        # Check resource availability
        if not await self._check_availability(request):
            logger.warning(f"Insufficient resources for request: {request.request_id}")
            return None

        # Calculate allocation
        allocation = await self._calculate_allocation(request)
        if not allocation:
            return None

        # Update resource pools
        await self._update_pools(allocation)

        # Record allocation
        self.allocations[allocation.allocation_id] = allocation
        self.allocation_history.append({
            "timestamp": datetime.utcnow(),
            "allocation_id": allocation.allocation_id,
            "framework_id": request.framework_id,
            "allocated": allocation.allocated
        })

        logger.info(f"Resources allocated: {allocation.allocation_id}")
        return allocation

    async def optimize_resources(self) -> None:
        """Optimize resource allocation across frameworks."""
        while True:
            # Calculate current metrics
            metrics = await self.calculate_metrics()
            self.metrics_history.append(metrics)

            # Check for optimization opportunities
            if metrics.allocation_efficiency < 0.8:
                await self._rebalance_allocations()

            # Adapt to usage patterns
            if metrics.usage_efficiency < 0.7:
                await self._adapt_allocations()

            await asyncio.sleep(5)  # Optimization interval

    async def _check_availability(
        self, request: ResourceRequest
    ) -> bool:
        """Check if requested resources are available."""
        pool = self.resource_pools[request.resource_type]

        # Check each requested resource
        for resource, amount in request.requirements.items():
            if resource not in pool or pool[resource] < amount:
                return False

        return True

    async def _calculate_allocation(
        self, request: ResourceRequest
    ) -> Optional[ResourceAllocation]:
        """Calculate resource allocation based on request."""
        allocated = {}
        limits = {}

        # Calculate allocation for each resource
        for resource, amount in request.requirements.items():
            available = self.resource_pools[request.resource_type][resource]

            # Apply flexibility
            min_allocation = amount * (1 - request.flexibility)
            max_allocation = amount * (1 + request.flexibility)

            # Calculate actual allocation
            if available >= min_allocation:
                allocated[resource] = min(available, max_allocation)
                limits[resource] = max_allocation
            else:
                return None

        return ResourceAllocation(
            allocation_id=str(uuid.uuid4()),
            framework_id=request.framework_id,
            resource_type=request.resource_type,
            allocated=allocated,
            limits=limits,
            usage={resource: 0.0 for resource in allocated},
            timestamp=datetime.utcnow(),
            metadata={"request_id": request.request_id}
        )

    async def _update_pools(
        self, allocation: ResourceAllocation
    ) -> None:
        """Update resource pools after allocation."""
        pool = self.resource_pools[allocation.resource_type]

        # Update available resources
        for resource, amount in allocation.allocated.items():
            pool[resource] -= amount

    async def _rebalance_allocations(self) -> None:
        """Rebalance resource allocations for efficiency."""
        # Get all current allocations
        current_allocations = list(self.allocations.values())

        # Sort by usage efficiency
        current_allocations.sort(
            key=lambda x: sum(x.usage.values()) / sum(x.allocated.values())
        )

        # Redistribute resources from least to most efficient
        for i in range(len(current_allocations) - 1):
            source = current_allocations[i]
            target = current_allocations[i + 1]

            # Calculate redistribution
            for resource in source.allocated:
                if resource in target.allocated:
                    # Calculate amount to redistribute
                    usage_ratio = source.usage[resource] / source.allocated[resource]
                    if usage_ratio < 0.5:  # Low usage
                        redistribution = source.allocated[resource] * 0.2  # 20% reduction

                        # Update allocations
                        source.allocated[resource] -= redistribution
                        target.allocated[resource] += redistribution

                        logger.info(
                            f"Redistributed {redistribution} of {resource} from "
                            f"{source.framework_id} to {target.framework_id}"
                        )

    async def _adapt_allocations(self) -> None:
        """Adapt allocations based on usage patterns."""
        for allocation in self.allocations.values():
            for resource, usage in allocation.usage.items():
                allocated = allocation.allocated[resource]
                usage_ratio = usage / allocated

                # Adjust allocation based on usage
                if usage_ratio > 0.9:  # High usage
                    # Try to increase allocation
                    increase = allocated * 0.2  # 20% increase
                    if self.resource_pools[allocation.resource_type][resource] >= increase:
                        allocation.allocated[resource] += increase
                        self.resource_pools[allocation.resource_type][resource] -= increase
                        logger.info(
                            f"Increased {resource} allocation for "
                            f"{allocation.framework_id} by {increase}"
                        )

                elif usage_ratio < 0.3:  # Low usage
                    # Decrease allocation
                    decrease = allocated * 0.2  # 20% decrease
                    allocation.allocated[resource] -= decrease
                    self.resource_pools[allocation.resource_type][resource] += decrease
                    logger.info(
                        f"Decreased {resource} allocation for "
                        f"{allocation.framework_id} by {decrease}"
                    )

    async def update_usage(
        self, allocation_id: str,
        usage: Dict[str, float]
    ) -> None:
        """Update resource usage for an allocation."""
        if allocation_id not in self.allocations:
            logger.warning(f"Unknown allocation: {allocation_id}")
            return

        allocation = self.allocations[allocation_id]
        allocation.usage = usage
        allocation.metadata["last_usage_update"] = datetime.utcnow().isoformat()

    async def calculate_metrics(self) -> ResourceMetrics:
        """Calculate current resource metrics."""
        if not self.allocations:
            return ResourceMetrics(
                allocation_efficiency=1.0,
                usage_efficiency=1.0,
                resource_balance=1.0,
                adaptation_rate=1.0,
                timestamp=datetime.utcnow()
            )

        # Calculate allocation efficiency
        total_allocated = sum(
            sum(a.allocated.values())
            for a in self.allocations.values()
        )
        total_available = sum(
            sum(p.values())
            for p in self.resource_pools.values()
        )
        allocation_efficiency = 1.0 - (total_allocated / total_available)

        # Calculate usage efficiency
        usage_ratios = [
            sum(a.usage.values()) / sum(a.allocated.values())
            for a in self.allocations.values()
        ]
        usage_efficiency = sum(usage_ratios) / len(usage_ratios)

        # Calculate resource balance
        allocations_per_framework = {}
        for allocation in self.allocations.values():
            if allocation.framework_id not in allocations_per_framework:
                allocations_per_framework[allocation.framework_id] = 0
            allocations_per_framework[allocation.framework_id] += sum(allocation.allocated.values())

        if allocations_per_framework:
            min_allocation = min(allocations_per_framework.values())
            max_allocation = max(allocations_per_framework.values())
            resource_balance = min_allocation / max_allocation if max_allocation > 0 else 1.0
        else:
            resource_balance = 1.0

        # Calculate adaptation rate
        if len(self.metrics_history) > 1:
            last_metrics = self.metrics_history[-1]
            adaptation_rate = abs(
                usage_efficiency - last_metrics.usage_efficiency
            )
        else:
            adaptation_rate = 1.0

        return ResourceMetrics(
            allocation_efficiency=allocation_efficiency,
            usage_efficiency=usage_efficiency,
            resource_balance=resource_balance,
            adaptation_rate=adaptation_rate,
            timestamp=datetime.utcnow()
        )

    async def start(self) -> None:
        """Start the resource manager."""
        optimization_task = asyncio.create_task(self.optimize_resources())
        await optimization_task

# Example usage:
async def main():
    # Initialize resource manager
    manager = ResourceManager()

    # Request resources
    request = await manager.request_resources(
        "framework_a",
        "compute",
        {"cpu": 10.0, "memory": 20.0},
        priority=2,
        flexibility=0.3
    )

    # Allocate resources
    allocation = await manager.allocate_resources(request)

    # Start resource management
    await manager.start()

if __name__ == "__main__":
    asyncio.run(main())