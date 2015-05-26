
from fibermodes import Mode, ModeFamily
from .simulator import Simulator
from multiprocessing import Pool, Pipe
from functools import partial
from collections import deque


def _neff(fiber, wl, mode, nfrom, nto):
    lowbound = min((t.recv() for t in nto), default=None)
    neff = fiber.neff(mode, wl, lowbound=lowbound)
    for f in nfrom:
        f.send(neff)
    return neff


def _sync_cache(fct, fiber, args, pipe):
    r = fct(*args)
    mode = args[0]
    ne_cache = {}
    for wl, modes in fiber._solver.ne_cache.items():
        if mode in modes:
            ne_cache[wl] = modes[mode]
    co_cache = fiber._solver.co_cache.get(mode, None)
    pipe.send((ne_cache, co_cache))

    return r


class PSimulator(Simulator):

    """

    """

    def __init__(self, *args, **kwargs):
        self.pool = Pool()
        super().__init__(*args, **kwargs)

    def __del__(self):
        self.pool.terminate()
        self.pool.join()

    def terminate(self):
        self.pool.terminate()
        self.pool.join()
        self.pool = Pool()

    def set_wavelengths(self, wavelengths):
        self.terminate()
        super().set_wavelengths(wavelengths)

    def set_factory(self, factory):
        self.terminate()
        super().set_factory(factory)

    def _apply_to_modes(self, fct, idx, args=()):
        modes = self._modes(idx)
        fiber = self.fibers[idx[0]]
        r = {}
        for m in modes:
            arg = (m,) + args
            re, se = Pipe(False)
            r[m] = self.pool.apply_async(
                _sync_cache,
                (fct, fiber, arg, se),
                callback=partial(self._update_cache,
                                 fiber=fiber, mode=m, pipe=re))
            # r[m] = self.pool.apply_async(fct, arg)
        return r

    def neff(self, fidx=None, wlidx=None):
        modes = {}
        nfrom = {}
        nto = {}
        for f, w in self._idx_iter(fidx, wlidx):
            for m in self._modes((f, w)):
                modes[(f, w, m)] = None
                nfrom[(f, w, m)] = []
                nto[(f, w, m)] = []
        ml = deque(modes.keys())

        for idx in ml:
            for d in self._depends_on(*idx):
                t, f = Pipe(False)
                nfrom[d].append(f)
                nto[idx].append(t)

        while ml:
            idx = ml.popleft()
            deps = self._depends_on(*idx)
            for d in deps:
                if modes[d] is None:
                    ml.append(idx)
                    break
            else:
                modes[idx] = self.pool.apply_async(
                    _neff,
                    (
                        self.fibers[idx[0]],
                        self.wavelengths[idx[1]],
                        idx[2],
                        nfrom[idx],
                        nto[idx]
                    ),
                    callback=partial(self._set_ne_cache, idx=idx))

        if isinstance(fidx, int) and isinstance(wlidx, int):
            return {m: modes[(fidx, wlidx, m)]
                    for m in self._modes((fidx, wlidx))}
        return ({m: modes[(f, w, m)] for m in self._modes((f, w))}
                for f, w in self._idx_iter(fidx, wlidx))

    def _update_cache(self, x, fiber, mode, pipe):
        ce_cache, co_cache = pipe.recv()
        for wl, neff in ce_cache.items():
            fiber._solver.set_ne_cache(wl, mode, neff)
        if co_cache is not None:
            fiber._solver.co_cache[mode] = co_cache
        pipe.close()

    def _set_ne_cache(self, neff, idx):
        fiber = self.fibers[idx[0]]
        wl = self.wavelengths[idx[1]]
        fiber._solver.set_ne_cache(wl, idx[2], neff)

    def _depends_on(self, fnum, wlnum, mode):
        s = []
        if wlnum > 0:
            s.append((fnum, wlnum-1, mode))

        pm = None
        if mode.family is ModeFamily.HE:
            if mode.m > 1:
                pm = Mode(ModeFamily.EH, mode.nu, mode.m - 1)
        elif mode.family is ModeFamily.EH:
            pm = Mode(ModeFamily.HE, mode.nu, mode.m)
        elif mode.m > 1:
            pm = Mode(mode.family, mode.nu, mode.m - 1)
        if pm:
            s.append((fnum, wlnum, pm))

        return s
