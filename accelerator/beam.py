"""Accelerator Beam"""
import logging
from typing import List, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Ellipse

from .sampling import bigaussian
from .utils import complete_twiss, compute_twiss_clojure, to_twiss


class Beam:
    def __init__(
        self,
        number: int = 1,
        energy: float = 6500.0,
        n_particles: int = 1e3,
        emittance: Union[Tuple[float, float], float] = 3.5e-6,
        sampling: str = "bigaussian",
    ):
        """Represents one beam.

        Args:
            number (optional): Beam number, either 1 or 2.
            energy (optional): Beam energy in GeV.
            n_particles (optional): number of particles in the beam.
            emittance (optional): beam emittance in meters, to specify horizontal
                and vertical emittances use a tuple.

        Examples:
            Beam with even emittances:
            >>> Beam(beam=1, n_particles=100, emittance=2.5)

            Beam with uneven emittances:
            >>> Beam(beam=1, n_particles=100, emittance=(3.5, 2.5))
        """
        sampling_map = {"bigaussian": bigaussian}
        if not isinstance(emittance, tuple):
            emittance = (emittance, emittance)
        self.number = number
        self.energy = energy
        self.emittance_h = emittance[0]
        self.emittance_v = emittance[1]
        self.n_particles = n_particles
        self.sampling = sampling_map[sampling]
        self._sampling_str = sampling
        self._log = logging.getLogger(__name__)

    def phasespace(
        self,
        twiss: List[float],
        plane: str = "h",
        closure_tol: float = 1e-9,
        n_angles: int = 1e3,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Vizualize the beam phase space given the twiss parameters.

        Args:
            twiss: twiss parameters, beta[m], alpha[rad], gamma[m^-1], one
                twiss parameter can be None.
            plane (optional): Phase space plane of interest, either 'h' or 'v'.
            closure_tol (optional): Numerical tolerance on the closure condition.
            n_angles (optional): Number of angles for which to compute the ellipse.

        Returns:
            u, u_prime: position and angle phase space coordrinates of the ellipse.
        """
        twiss = to_twiss(twiss)
        beta = twiss[0][0]
        alpha = twiss[1][0]
        gamma = twiss[2][0]
        closure = compute_twiss_clojure(twiss)
        # self._log.debug(f"beta={beta}")
        # self._log.debug(f"alpha={alpha}")
        # self._log.debug(f"gamma={gamma}")
        # self._log.debug(f"closure={closure}")
        if not (closure >= 1.0 - closure_tol and closure <= 1.0 + closure_tol):
            raise ValueError(
                f"Closure condition not met: beta * gamma - alpha**2 = {closure} != 1"
            )
        plane_map = {"h": self.emittance_h, "v": self.emittance_v}
        emit = plane_map[plane.lower()]
        angles = np.linspace(0, 2 * np.pi, int(n_angles))
        # TODO: make sure these equations are correct
        u = np.sqrt(emit * beta) * np.cos(angles)
        u_prime = -(alpha / beta) * u - np.sqrt(emit / beta) * np.sin(angles)
        return u, u_prime

    def __repr__(self) -> str:
        args = {
            "number": self.number,
            "energy": self.energy,
            "emittance": (self.emittance_h, self.emittance_v),
            "n_particles": self.n_particles,
            "sampling": self._sampling_str,
        }
        arg_str = ",\n".join([f"{key}={repr(value)}" for key, value in args.items()])
        return f"Beam(\n{arg_str})"