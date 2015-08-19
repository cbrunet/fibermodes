
from .simulator import Simulator
from multiprocessing import Pool
from functools import partial
import os


def applyf(fsim, name):
    fct = getattr(fsim, name)
    return fct(), fsim.__self__._fiber.ne_cache


class PSimulator(Simulator):

    def __init__(self, *args, **kwargs):
        self.pool = None
        self.numProcs = kwargs.pop("processes", 0) or os.cpu_count()

        super().__init__(*args, **kwargs)

    def __getattr__(self, name):
        def wrapper():
            if self.pool is not None:
                self.terminate()
            self.pool = Pool(self.numProcs)

            r = self.pool.imap(partial(applyf, name=name), self._fsims)
            for i, (res, ne_cache) in enumerate(r):
                self.fibers[i].ne_cache = ne_cache
                yield res
            self.pool.close()
            self.pool.join()
            self.pool = None

        return wrapper

    def terminate(self):
        if self.pool is not None:
            self.pool.terminate()
            self.pool.join()
            self.pool = None
