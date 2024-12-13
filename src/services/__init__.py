import asyncio
from abc import abstractmethod, ABC

from loguru import logger


class Service(ABC):
    """Common abstract service"""

    def __init__(self, name: str = "Service"):
        self._name = name
        self._required_init = True
        self._service_initialize = asyncio.Event()
        self.stopping = False
        self.task = asyncio.create_task(self._loop(), name=name)
        self.task.add_done_callback(self.main_task_done_callback)

    @property
    def name(self):
        return self.task.get_name() or self._name

    @abstractmethod
    async def _run(self):
        raise NotImplementedError

    @abstractmethod
    async def _initialize_logic(self):
        raise NotImplementedError

    @abstractmethod
    async def cleanup(self):
        raise NotImplementedError

    def main_task_done_callback(self, task: asyncio.Task):
        try:
            logger.warning(f"Result of {self._name} main task {task.result()}")
        except asyncio.CancelledError:
            logger.info(f"Cancelling {self._name}...")
        except Exception as e:
            logger.error(f"Main {self._name} task finished with {e}")

    async def initialize(self):
        logger.info(f"Start initializing service {self._name}")
        await self._initialize_logic()
        logger.info(f"Service {self._name} initialize successfully")
        self._service_initialize.set()

    @staticmethod
    async def _handling_exception(e: Exception):
        """For handling custom exceptions
        you can change self._required_init here or do smth else
        return True on handled
        """
        logger.warning(f"There is no handler for {e} [{type(e)}]")
        return False

    async def _loop(self):
        while True:
            try:
                if self._required_init:
                    self._service_initialize.clear()
                    await self.initialize()
                logger.info(f"Run {self._name} service")
                await self._run()
            except asyncio.CancelledError:
                await self.cancelled()
                logger.info(f"Stopping service {self._name}")
                raise
            except asyncio.TimeoutError:
                logger.error("Timeout error occurred!")
                continue
            except Exception as e:
                is_handled = await self._handling_exception(e)
                if not is_handled:
                    logger.warning(f"There is no handler for {e} [{type(e)}]")
                continue
            finally:
                logger.info(f"Cleaning up after {self._name} service")
                await self.cleanup()
                await asyncio.sleep(1)

    async def stop(self, timeout=10):
        if not self.stopping:
            self.stopping = True
            self._service_initialize.clear()
            self.task.cancel()
            done, _ = await asyncio.wait([self.task], timeout=timeout)
            if not done:
                logger.warning("Couldn't cleanly stop task:%s", self.task)

    async def cancelled(self):
        logger.info(f"Task {self._name} stopping")
