
from fibermodes import Mode, ModeFamily
from .simulator import Simulator
from functools import partial
from threading import Thread, Lock
from multiprocessing import Pool
from multiprocessing.pool import ApplyResult
from queue import Queue
import logging


def wrapper(fct, *args, **kwargs):
    r = fct(*args, **kwargs)
    return r, fct.__self__


class PoolThread(Thread):

    logger = logging.getLogger(__name__)

    def __init__(self, simulator):
        super().__init__()
        self.simulator = simulator
        self.jobmap = Queue()
        self.cache = {}
        self.pool = Pool()
        self.cachelock = Lock()
        self.runcache = {}
        self.runcache_lock = Lock()

    def apply_async(self, fname, idx, mode):
        f = ApplyResult(self.cache, None, None)
        self.jobmap.put((fname, idx, mode, f))
        return f

    def get_neff(self, idx, mode):
        cache = self.simulator.fibers[idx[0]]._solver.ne_cache
        wl = self.simulator.wavelengths[idx[1]]

        # First look if already in cache
        if wl in cache and mode in cache[wl]:
            return cache[wl][mode]

        # If not, look if it is already running
        # with self.runcache_lock:
        if ("neff", idx, mode) in self.runcache:
            neff, fiber = self.runcache[("neff", idx, mode)].get()
            return neff

        # Else, get it now
        lowbound = self.get_lowbound(idx, mode)
        # Call it on another process to avoid blocking thread
        return self.pool.apply(
            self.simulator.fibers[idx[0]].neff,
            (mode, wl),
            {'delta': self.simulator.delta, 'lowbound': lowbound})

    def get_deps(self, idx, mode):
        """Generator that gives modes with higher neff than current mode"""
        wlnum = idx[1]

        if wlnum > 0:
            yield ((idx[0], wlnum-1), mode)

        pm = None
        if mode.family is ModeFamily.HE:
            if mode.m > 1:
                pm = Mode(ModeFamily.EH, mode.nu, mode.m - 1)
        elif mode.family is ModeFamily.EH:
            pm = Mode(ModeFamily.HE, mode.nu, mode.m)
        elif mode.m > 1:
            pm = Mode(mode.family, mode.nu, mode.m - 1)
        if pm:
            yield (idx, pm)

        if (mode.family is ModeFamily.LP and mode.nu > 0) or mode.nu > 1:
            pm = Mode(mode.family, mode.nu-1, mode.m)
            yield (idx, pm)

    def get_lowbound(self, idx, mode):
        return min((self.get_neff(i, m)
                    for (i, m) in self.get_deps(idx, mode)),
                   default=None)

    def run(self):
        self.logger.debug("Thread started")
        while True:
            fname, idx, mode, f = self.jobmap.get()
            lowbound = self.get_lowbound(idx, mode)
            fct = getattr(self.simulator.fibers[idx[0]], fname)
            wl = self.simulator.wavelengths[idx[1]]
            with self.runcache_lock:
                self.runcache[(fname, idx, mode)] = self.pool.apply_async(
                    wrapper,
                    (fct, mode, wl),
                    {'delta': self.simulator.delta, 'lowbound': lowbound},
                    callback=partial(
                        self.callback, fname=fname, idx=idx, mode=mode, f=f),
                    error_callback=self.ecallback)
        self.logger.debug("Thread stopped")

    def callback(self, result, fname, idx, mode, f):
        r, rfiber = result
        fnum = idx[0]
        fiber = self.simulator.fibers[fnum]

        f._set(None, (True, r))

        # update cache
        with self.cachelock:
            for w, cache in rfiber._solver.ne_cache.items():
                if w in fiber._solver.ne_cache:
                    fiber._solver.ne_cache[w].update(cache)
                else:
                    fiber._solver.ne_cache[w] = cache
        with self.runcache_lock:
            del self.runcache[(fname, idx, mode)]

    def ecallback(self, error):
        raise error


class PSimulator(Simulator):

    def __init__(self, np=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reset_thread()

    def reset_thread(self):
        self.thread = PoolThread(self)
        self.thread.start()

    def _apply_to_modes(self, fct, idx):
        modes = self._modes(idx)
        return {mode: self.thread.apply_async(fct.__name__, idx, mode)
                for mode in sorted(modes)}

    def _apply_cutoff_to_modes(self, fct, idx):
        modes = self._modes(idx)
        return {mode: self.thread.pool.apply_async(fct, (mode,))
                for mode in modes}

    def modes(self, fidx=None, wlidx=None):
        if isinstance(fidx, int) and isinstance(wlidx, int):
            return self._modes((fidx, wlidx))
        else:
            futures = (self.thread.pool.apply_async(self._modes, (f, wl))
                       for (f, wl) in self._idx_iter(fidx, wlidx))
            return (f.get() for f in futures)




# def _neff(fiber, wl, mode, nfrom, nto):
#     lowbound = min((t.recv() for t in nto), default=None)
#     neff = fiber.neff(mode, wl, lowbound=lowbound)
#     for f in nfrom:
#         f.send(neff)
#     return neff


# def _sync_cache(fct, fiber, args, pipe):
#     r = fct(*args)
#     mode = args[0]
#     ne_cache = {}
#     for wl, modes in fiber._solver.ne_cache.items():
#         if mode in modes:
#             ne_cache[wl] = modes[mode]
#     co_cache = fiber._solver.co_cache.get(mode, None)
#     pipe.send((ne_cache, co_cache))

#     return r


# class PSimulator(Simulator):

#     """

#     """

#     def __init__(self, *args, **kwargs):
#         self.pool = Pool()
#         super().__init__(*args, **kwargs)

#     def terminate(self):
#         self.pool.terminate()
#         self.pool.join()
#         self.pool = Pool()

#     def set_wavelengths(self, wavelengths):
#         self.terminate()
#         super().set_wavelengths(wavelengths)

#     def set_factory(self, factory):
#         self.terminate()
#         super().set_factory(factory)

#     def _apply_to_modes(self, fct, idx, args=()):
#         modes = self._modes(idx)
#         fiber = self.fibers[idx[0]]
#         r = {}
#         for m in modes:
#             arg = (m,) + args
#             re, se = Pipe(False)
#             r[m] = self.pool.apply_async(
#                 _sync_cache,
#                 (fct, fiber, arg, se),
#                 callback=partial(self._update_cache,
#                                  fiber=fiber, mode=m, pipe=re))
#             # r[m] = self.pool.apply_async(fct, arg)
#         return r

#     def neff(self, fidx=None, wlidx=None):
#         modes = {}
#         nfrom = {}
#         nto = {}
#         for f, w in self._idx_iter(fidx, wlidx):
#             for m in self._modes((f, w)):
#                 modes[(f, w, m)] = None
#                 nfrom[(f, w, m)] = []
#                 nto[(f, w, m)] = []
#         ml = deque(modes.keys())

#         for idx in ml:
#             for d in self._depends_on(*idx):
#                 t, f = Pipe(False)
#                 nfrom[d].append(f)
#                 nto[idx].append(t)

#         while ml:
#             idx = ml.popleft()
#             deps = self._depends_on(*idx)
#             for d in deps:
#                 if modes[d] is None:
#                     ml.append(idx)
#                     break
#             else:
#                 modes[idx] = self.pool.apply_async(
#                     _neff,
#                     (
#                         self.fibers[idx[0]],
#                         self.wavelengths[idx[1]],
#                         idx[2],
#                         nfrom[idx],
#                         nto[idx]
#                     ),
#                     callback=partial(self._set_ne_cache, idx=idx))

#         if isinstance(fidx, int) and isinstance(wlidx, int):
#             return {m: modes[(fidx, wlidx, m)]
#                     for m in self._modes((fidx, wlidx))}
#         return ({m: modes[(f, w, m)] for m in self._modes((f, w))}
#                 for f, w in self._idx_iter(fidx, wlidx))

#     def _update_cache(self, x, fiber, mode, pipe):
#         ce_cache, co_cache = pipe.recv()
#         for wl, neff in ce_cache.items():
#             fiber._solver.set_ne_cache(wl, mode, neff)
#         if co_cache is not None:
#             fiber._solver.co_cache[mode] = co_cache
#         pipe.close()

#     def _set_ne_cache(self, neff, idx):
#         fiber = self.fibers[idx[0]]
#         wl = self.wavelengths[idx[1]]
#         fiber._solver.set_ne_cache(wl, idx[2], neff)


