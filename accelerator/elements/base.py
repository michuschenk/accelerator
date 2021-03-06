from abc import abstractmethod
from typing import List, Tuple

import matplotlib.pyplot as plt
import numpy as np

from ..transfer_matrix import TransferMatrix
from ..utils import compute_m_twiss


class BaseElement:
    """Element"""

    def __init__(self):
        """Base class of a lattice element.
        """
        self._m_h = None
        self._m_v = None

    @property
    def m_h(self) -> TransferMatrix:
        if self._m_h is None or self._m_v is None:
            ms = self.transfer_matrix()
            self._m_h = TransferMatrix(ms[0])
            self._m_v = TransferMatrix(ms[1])
        return self._m_h

    @property
    def m_v(self) -> TransferMatrix:
        if self._m_h is None or self._m_v is None:
            ms = self.transfer_matrix()
            self._m_h = TransferMatrix(ms[0])
            self._m_v = TransferMatrix(ms[1])
        return self._m_v

    @abstractmethod
    def transfer_matrix(self) -> np.ndarray:
        pass

    def plot(
        self, u_init: List[float] = [1, np.pi / 8], plane="h", *args, **kwargs,
    ) -> Tuple[plt.Figure, plt.Axes]:
        plane_map = {"h": self.m_h, "v": self.m_v}
        coord_map = {"h": "x", "v": "y"}
        coord = coord_map[plane]
        m = plane_map[plane]
        u_1 = m @ u_init
        x_axis = [0, self.length]
        fig, axes = plt.subplots(2, 1, sharex=True)
        axes[0].plot(x_axis, [u_init[0], u_1[0]], *args, label=coord, **kwargs)
        axes[0].legend()
        axes[0].set_ylabel(f"{coord} (m)")
        axes[1].plot(x_axis, [u_init[1], u_1[1]], *args, label=f"{coord}'", **kwargs)
        axes[1].legend()
        axes[1].set_ylabel(f"{coord}'")
        axes[1].set_xlabel("s (m)")
        return fig, axes
