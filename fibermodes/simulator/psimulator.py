
from .simulator import Simulator
from multiprocessing import Pool
from functools import partial


def applyf(fsim, name):
    fct = getattr(fsim, name)
    return fct(), fsim.__self__._fiber.ne_cache


class PSimulator(Simulator):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pool = None

    def __getattr__(self, name):
        def wrapper():
            if self.pool is not None:
                self.pool.join()
            self.pool = Pool()

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



# from fibermodes import Mode, ModeFamily
# from .simulator import Simulator
# from functools import partial
# from threading import Thread, Lock, Event
# from multiprocessing import Pool
# from multiprocessing.pool import ApplyResult
# from queue import Queue, Empty
# import logging


# def wrapper(fct, *args, **kwargs):
#     r = fct(*args, **kwargs)
#     return r, fct.__self__


# class PoolThread(Thread):

#     logger = logging.getLogger(__name__)

#     def __init__(self, simulator):
#         super().__init__()
#         self.simulator = simulator
#         self.jobmap = Queue()
#         self.cache = {}
#         self.pool = Pool()
#         self.cachelock = Lock()
#         self.runcache = {}
#         # self.runcache_lock = Lock()
#         self.running = Event()
#         self.running.set()

#     def stop(self, force=False):
#         self.running.clear()
#         self.pool.close()
#         if force:
#             self.pool.terminate()
#         else:
#             self.pool.join()
#         self.join()

#     def apply_async(self, fname, idx, mode):
#         f = ApplyResult(self.cache, None, None)
#         self.jobmap.put((fname, idx, mode, f))
#         return f

#     def get_neff(self, idx, mode):
#         print(" neff for", idx, mode)
#         cache = self.simulator.fibers[idx[0]].ne_cache
#         wl = self.simulator.wavelengths[idx[1]]

#         # First look if already in cache
#         if wl in cache and mode in cache[wl]:
#             print("  neff: in cache", idx, mode)
#             return cache[wl][mode]

#         # If not, look if it is already running
#         # with self.runcache_lock:
#         if ("neff", idx, mode) in self.runcache:
#             try:
#                 print("  neff: waiting for result")
#                 neff, fiber = self.runcache[("neff", idx, mode)].get(5)
#                 print("    neff: got result", idx, mode)
#                 return neff
#             except TimeoutError:
#                 print("  Timout getting", idx, mode)

#         return None

#         # Else, get it now
#         lowbound = self.get_lowbound(idx, mode)
#         # Call it on another process to avoid blocking thread
#         print("  neff: calculating now!", idx, mode)
#         neff = self.pool.apply(
#             self.simulator.fibers[idx[0]].neff,
#             (mode, wl),
#             {'delta': self.simulator.delta, 'lowbound': lowbound})
#         print("    neff: caculation done", idx, mode)
#         with self.cachelock:
#             self.simulator.fibers[idx[0]].set_ne_cache(wl, mode, neff)
#         return neff

#     def get_deps(self, idx, mode):
#         """Generator that gives modes with higher neff than current mode"""
#         wlnum = idx[1]

#         if wlnum > 0:
#             yield ((idx[0], wlnum-1), mode)

#         pm = None
#         if mode.family is ModeFamily.HE:
#             if mode.m > 1:
#                 pm = Mode(ModeFamily.EH, mode.nu, mode.m - 1)
#         elif mode.family is ModeFamily.EH:
#             pm = Mode(ModeFamily.HE, mode.nu, mode.m)
#         elif mode.m > 1:
#             pm = Mode(mode.family, mode.nu, mode.m - 1)
#         if pm:
#             yield (idx, pm)

#         if (mode.family is ModeFamily.LP and mode.nu > 0) or mode.nu > 1:
#             pm = Mode(mode.family, mode.nu-1, mode.m)
#             yield (idx, pm)

#     def get_lowbound(self, idx, mode):
#         print(" Lowbound for", idx, mode)
#         return min(filter(lambda x: x is not None,
#                           (self.get_neff(i, m)
#                            for (i, m) in self.get_deps(idx, mode))),
#                    default=None)

#     def run(self):
#         self.logger.debug("Thread started")
#         self.running.wait()
#         self.logger.debug("Thread loop started")
#         while self.running.is_set():
#             try:
#                 fname, idx, mode, f = self.jobmap.get(True, 1)
#                 print("Next job:", fname, idx, mode)

#                 if fname == "neff":
#                     fiber = self.simulator.fibers[idx[0]]
#                     wl = self.simulator.wavelengths[idx[1]]
#                     if wl in fiber.ne_cache and mode in fiber.ne_cache[wl]:
#                         f._set(None, (True, fiber.ne_cache[wl][mode]))
#                         print("Already in cache!")
#                         continue

#                 lowbound = self.get_lowbound(idx, mode)
#                 fct = getattr(self.simulator.fibers[idx[0]], fname)
#                 wl = self.simulator.wavelengths[idx[1]]
#                 r = self.pool.apply_async(
#                         wrapper,
#                         (fct, mode, wl),
#                         {'delta': self.simulator.delta, 'lowbound': lowbound},
#                         callback=partial(
#                             self.callback, fname=fname, idx=idx,
#                             mode=mode, f=f),
#                         error_callback=self.ecallback)
#                 self.runcache[(fname, idx, mode)] = r
#             except Empty:
#                 pass
#         self.logger.debug("Thread stopped")

#     def callback(self, result, fname, idx, mode, f):
#         r, rfiber = result
#         fnum = idx[0]
#         fiber = self.simulator.fibers[fnum]

#         f._set(None, (True, r))

#         # update cache
#         with self.cachelock:
#             for w, cache in rfiber.ne_cache.items():
#                 if w in fiber.ne_cache:
#                     fiber.ne_cache[w].update(cache)
#                 else:
#                     fiber.ne_cache[w] = cache
#         del self.runcache[(fname, idx, mode)]

#     def ecallback(self, error):
#         raise error


# class PSimulator(Simulator):

#     logger = logging.getLogger(__name__)

#     def __init__(self, np=None, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.thread = None
#         self.reset_thread()

#     def __del__(self):
#         self.thread.stop(True)

#     def reset_thread(self):
#         if self.thread is not None:
#             self.thread.stop(True)
#         self.thread = PoolThread(self)
#         self.thread.start()

#     def stop_thread(self, force=False):
#         self.thread.stop(True)
#         self.thread = None

#     def _apply_to_modes(self, fct, idx):
#         modes = self._modes(idx)
#         return {mode: self.thread.apply_async(fct.__name__, idx, mode)
#                 for mode in sorted(modes)}

#     def _apply_cutoff_to_modes(self, fct, idx):
#         modes = self._modes(idx)
#         return {mode: self.thread.pool.apply_async(fct, (mode,))
#                 for mode in modes}

#     def modes(self, fidx=None, wlidx=None):
#         if isinstance(fidx, int) and isinstance(wlidx, int):
#             return self._modes((fidx, wlidx))
#         else:
#             futures = (self.thread.pool.apply_async(self._modes, (f, wl))
#                        for (f, wl) in self._idx_iter(fidx, wlidx))
#             return (f.get() for f in futures)
