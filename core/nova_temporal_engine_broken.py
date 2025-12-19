#!/usr/bin/env python3

import asyncio
from temporalio import workflow

@workflow.defn
class NovaLifecycle:
    @workflow.run
    async def run(self):
        while True:
            await asyncio.sleep(5)
            workflow.logger.info("Heartbeat")

if __name__ == "__main__":
    asyncio.run(NovaLifecycle().run())
