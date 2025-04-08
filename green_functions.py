"""
Green function in the time domain
---------------------------------

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


class BaseGreenFunction(ABC):
    """
    The base class of Green function classes. It required in derived classes definitions of three functions:

    * near(self, source_model, distance, vp, vs, times)
    * intermediate(self, source_model, distance, vp, vs, times)
    * far(self, source_model, distance, vp, vs, times)

    They return radial and transversal displacement responses.

    :param dt: The time sampling step for integration and differentiation calculations,
    :param density: The density at the source,
    :param transversal_radiation: The transversal_radiation pattern in the far field,
    :param radial_radiation: The radial radiation pattern in the far field.

    """
    def __init__(self, dt, density, transversal_radiation=1.0, radial_radiation=0.52):
        self.dt = dt
        self.density = density
        self.transversal_radiation = transversal_radiation
        self.radial_radiation = radial_radiation
        pass

    @abstractmethod
    def near(self, source_model, distance, vp, vs, times):
        """
        Compute the near part of the displacement

        :param source_model: The source model object,
        :param distance: The hypocentral distance,
        :param vp: The P wave velocity,
        :param vs: The S wave velocity,
        :param times: Time samples. The samples steps must equal dt,
        :return: The radial and transversal displacement in the far field,
        
        """
        pass

    @abstractmethod
    def intermediate(self, source_model, distance, vp, vs, times, phase='P'):
        """
        Compute the intermediate part of the displacement

        :param source_model: The source model object,
        :param distance: The hypocentral distance,
        :param vp: The P wave velocity,
        :param vs: The S wave velocity,
        :param times: Time samples. The samples steps must equal dt,
        :param phase: The phase name: 'P' or 'S',
        :return: The radial and transversal displacement in the far field,
        
        """
        pass

    @abstractmethod
    def far(self, source_model, distance, vp, vs, times, phase='P'):
        """
        Compute the far part of the displacement

        :param source_model: The source model object,
        :param distance: The hypocentral distance,
        :param vp: The P wave velocity,
        :param vs: The S wave velocity,
        :param times: Time samples. The samples steps must equal dt,
        :param phase: The phase name: 'P' or 'S',
        :return: The radial and transversal displacement in the far field,
        
        """
        pass


def _phases_function(tp, ts, time):
    if tp <= time <= ts:
        return time
    else:
        return 0.0


class HomogeneousGreenFunction(BaseGreenFunction):
    """
    The Green function in the homogeneous and isotropic medium

    :param dt: The time sampling step for integration and differentiation calculations
    :param density: The density at the source
    :param transversal_radiation: The transversal_radiation pattern in the far field
    :param radial_radiation: The radial radiation pattern in the far field

    """
    def __init__(self, dt, density, transversal_radiation=1.0, radial_radiation=0.52):
        """

        :param dt: The time sampling step for integration and differentiation calculations
        :param density: The density at the source
        :param transversal_radiation: The transversal_radiation pattern in the far field
        :param radial_radiation: The radial radiation pattern in the far field
        """
        super().__init__(dt, density, transversal_radiation=transversal_radiation,
                         radial_radiation=radial_radiation)
        pass

    def near(self, source_model, distance, vp, vs, times):
        r"""
        Compute the near part of the displacement
        of the Green function in the homogeneous and isotropic medium.

        .. math::
            u_* \left(r, t \right) = \frac{R^{N*}}{4\pi\rho r^4}\int_{r/v_p}^{r/v_s}\tau M\left( t-\tau \right)d\tau,

        where * means radial or transversal part, :math:`u \left(r, t \right)` is the displacement,
        :math:`R^{N*}` is the radiation of radial or transversal near field pattern
        :math:`R^{NR}= 9R^{FR}` and :math:`R^{NT}= -6R^{FT}` (see far field radiation),
        :math:`r` is the hypocentral distance, :math:`\rho` is the density at the source,
        :math:`v_p` and :math:`v_s` are P and S velocities at the source,
        :math:`M\left( t \right)` is the source time function.
        The integration is realised by the convolution of the source time function nad the signal
        :math:`t(H(t-r/v_p) - H(t-r/v_s))`, where :math:`H(t)` is Heaviside step function.
            
        :param source_model: The source model object.
        :param distance: The hypocentral distance
        :param vp: The P wave velocity.
        :param vs: The S wave velocity.
        :param times: Time samples. The samples steps must equal dt 
        :return: The radial and transversal displacement in the near field

        """
        tp = distance / vp
        ts = distance / vs
        phases_function = np.array([_phases_function(tp, ts, t+tp) for t in np.nditer(times)])
        convolution = np.convolve(phases_function, source_model(times)) * self.dt
        factor = convolution / (4.0 * np.pi * self.density * distance ** 4)
        radial = 9.0 * self.radial_radiation * factor
        transversal = -6.0 * self.transversal_radiation * factor
        return radial, transversal

    def intermediate(self, source_model, distance, vp, vs, times, phase='P'):
        r"""
        Compute the intermediate part of the displacement
        of the Green function in the homogeneous and isotropic medium.

        .. math::
            u_* \left(r, t \right) = \frac{R^{I*}}{4\pi\rho v^2 r^2} M\left( t \right),

        where :math * means radial or transversal part,
        :math:`u \left(r, t \right)` is the displacement,
        :math:`R^{I*}` is the radiation of radial or transversal near field pattern,
        :math:`r` is the hypocentral distance, :math:`\rho` is the density at the source,
        :math:`v` is the P or S velocity,
        :math:`M\left( t \right)` is the source time function.
        For P wave :math:`R^{IR}= 4R^{FR}` and :math:`R^{IT}= -2R^{FT}` (see far field radiation),
        for S wave :math:`R^{IR}= -3R^{FR}` and :math:`R^{IT}= 3R^{FT}` (see far field radiation).

        :param source_model: The source model object.
        :param distance: The hypocentral distance
        :param vp: The P wave velocity.
        :param vs: The S wave velocity.
        :param times: Time samples. The samples steps must equal dt
        :param phase: The phase name: 'P' or 'S'
        :return: The radial and transversal displacement in the near field

        """
        source_times = source_model(times)
        factor = source_times / (4.0 * np.pi * self.density * distance ** 2 * vp ** 2)
        if phase == 'P':
            radial = 4.0 * self.radial_radiation * factor
            transversal = -2.0 * self.transversal_radiation * factor
        else:
            radial = -3.0 * self.radial_radiation * factor
            transversal = 3.0 * self.transversal_radiation * factor
        return radial, transversal

    def far(self, source_model, distance, vp, vs, times, phase='P'):
        r"""
        Compute the far part of the displacement
        of the Green function in the homogeneous and isotropic medium.

        .. math::
            u_* \left(r, t \right) = \frac{R^{I*}}{4\pi\rho v^3 r } \dot{M}\left( t \right),

        where :math * means radial or transversal part, which in the case of far field is equivalent of the P or S wave,
        :math:`u \left(r, t \right)` is the displacement,
        :math:`R^{F*}` is the radiation of radial or transversal near field pattern,
        :math:`r` is the hypocentral distance, :math:`\rho` is the density at the source,
        :math:`v` is the P or S velocity,
        :math:`\dot{M}\left( t \right)` is the time derivative of source time function.

        :param source_model: The source model object.
        :param distance: The hypocentral distance
        :param vp: The P wave velocity.
        :param vs: The S wave velocity.
        :param times: Time samples. The samples steps must equal dt.
        :param phase: The phase name: 'P' or 'S'
        :return: The radial and transversal displacement in the near field

        """
        source_diff = np.diff(source_model(times)) / self.dt
        factor = source_diff / (4.0 * np.pi * self.density * distance * vp ** 3)
        if phase == 'P':
            radial = factor * self.radial_radiation
            return radial, np.zeros(radial.size)
        else:
            transversal = factor * self.transversal_radiation
        return np.zeros(transversal.size), transversal


def get_green_function(configuration, dt, density, transversal_radiation=1.0, radial_radiation=0.52):
    green_function = configuration.get('green_function', 'homogeneous')
    if green_function == 'homogeneous':
        return HomogeneousGreenFunction(dt, density, transversal_radiation=transversal_radiation,
                                        radial_radiation=radial_radiation)
    else:
        raise SSSException(f"Wrong Green function name '{green_function}'")
