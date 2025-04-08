"""
Simple seismic source models
----------------------------

:copyright:
    Jan Wiszniowski (jwisz@igf.edu.pl)
:license:
    GNU Lesser General Public License, Version 3
    (https://www.gnu.org/copyleft/lesser.html)
:version 0.0.1:
    2025-02-07
"""
import numpy as np
from abc import ABC, abstractmethod
from utils import SSSException


class BaseSourceModel(ABC):
    def __init__(self, source_parameters):
        self.moment_scalar = source_parameters['moment_scalar']
        self.rupture_time = source_parameters['rupture_time']

    @abstractmethod
    def _at_time(self, time):
        pass

    def time_function(self, times):
        if np.isscalar(times):
            return self._at_time(times)
        else:
            return np.array([self._at_time(t) for t in np.nditer(times)])

    def __call__(self, times):
        return self.time_function(times)


class HaskellSourceModel(BaseSourceModel):
    r"""
    Haskell source model in the time domain is described as

    .. math::
        M\left( t \right)= \begin{cases}
        0 & \text{ for } t < 0 \\
        tM_0/\tau & \text{ for } 0 \leqslant  t \leqslant \tau \\
        M_0 & \text{ for } t > \tau
        \end{cases},
        

    where :math:`M_0` is the seismic moment value, :math:`\tau` is the rupture time,
    and :math:`H(t)` is Heaviside step function.

    """
    def __init__(self, source_parameters):
        super().__init__(source_parameters)

    def _at_time(self, time):
        if time < 0.0:
            return 0.0
        elif time > self.rupture_time:
            return self.moment_scalar
        return self.moment_scalar * time / self.rupture_time


class BruneSourceModel(BaseSourceModel):
    r"""
    Brune source model in the time domain is described as

    .. math::
        M\left( t \right) = M_0\left[ 1 - \exp\left( -t/ \tau \right)\left( t/ \tau +1 \right) \right],

    where :math:`M_0` is the seismic moment value, :math:`\tau` is the rupture time,
    and :math:`H(t)` is Heaviside step function.

    """
    def __init__(self, source_parameters):
        super().__init__(source_parameters)

    def _at_time(self, time):
        if time < 0.0:
            return 0.0
        # scaled_time = 2.0 * time / self.rupture_time
        factor = time / self.rupture_time  # We assume the maximum of Brune time equals end of Haskel rupture time
        return self.moment_scalar * (1.0 - np.multiply(np.exp(-factor), factor + 1.0))


def get_time_source_model(configuration, source_parameters):
    source_model = configuration.get('source_model')
    if source_model is None:
        raise SSSException("Missing source model name")
    if source_model == 'Brune':
        return BruneSourceModel(source_parameters)
    elif source_model == 'Haskell':
        return HaskellSourceModel(source_parameters)
    else:
        raise SSSException(f"Wrong source model name '{source_model}'")
