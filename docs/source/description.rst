.. _methodology_head:

Methodology
###########

The goal of this programme was the assessment of the near and intermediate field influence on the seismic signal parameters,
like maximum displacement amplitude of specific phases.
The assessment is based on a very simple seismic signal simulation.
The assumption point source, homogeneous and isotropic medium, simple Haskell :cite:`Haskell1964` source time function,
and a double couple mechanism was taken.
Additionally, the Brune model :cite:`Brune1970`, :cite:`Brune1971`
and Knopoff and Gillbert :cite:`KnopoffGillbert1959` 
are analysed to check the source time function impact on the estimates.
Knopoff and Gillbert source time function is tested only in the frequency domain.
The the radial component of displacement is analyzed, which partially equals the signal of the P wave
and was used for moment tensor estimation in many anthropogenic seismicity cases for the moment tensor estimation
e.g. :cite:`Wiejacz1992`, :cite:`Lizurek2017`.

Source time functions
=====================

For simplicity the Haskell :cite:`Haskell1964` source time function is tested
and, additionally, for comparison, the Brune model :cite:`Brune1970`, :cite:`Brune1971`
source time function is applied and the Knopoff and Gillbert :cite:`KnopoffGillbert1959`
model only in the frequency domain.

The Haskell source time function is

.. math::
   :label: eq_b1

   M\left( t \right)= \begin{cases}
   0 & \text{ for } t < 0 \\
   tM_0/\tau & \text{ for } 0 \leqslant  t \leqslant \tau \\
   M_0 & \text{ for } t > \tau
   \end{cases},
	
where :math:`M_0` is the moment, and :math:`\tau` is the rupture time. 
The alternative form of :eq:`eq_b1` is 

.. math::
   M\left( t \right) = \frac{M_0}{\tau}\left[ tH\left( t \right)-\left( t-\tau \right)H\left( t-\tau \right) \right]
	
where :math:`H\left( t \right)` is Heaviside step function.
	
In the frequency domain, Haskell source function is

.. math::
   :label: eq_b2

   M\left( \omega \right) = \frac{M_0}{\tau\omega^2}\left[ \exp\left( -j\omega\tau \right)-1 \right],

where :math:`\omega=2\pi f`.

The Brune source time function is

.. math::
   :label: eq_b3

   M\left( t \right) = M_0\left[ 1 - \exp\left( -t/ \tau \right)\left( t/ \tau +1 \right) \right].
	
In the frequency domain, Brune source function is

.. math::
   :label: eq_b4

   M\left( \omega \right) = \frac{M_0\omega_0^2}{j\omega\left( \omega_0^2-\omega^2  \right)},

where :math:`\omega_0=1 / \tau`.

The simplest Knopoff and Gillbert model well displays the near and intermediate effect
in the frequency domain, because
  
.. math::
   :label: eq_b5

   M\left( \omega \right) = M_0.

Displacement calculation
========================

With assumptions that simplify the model, we use the total displacement in homogeneous and isotropic medium
caused by the point double couple formula :cite:`AkiRichards2002`

.. math::
   :label: eq_a0

   \begin{matrix}
   \mathbf{u}\left ( \mathbf{r},t \right ) &
   =9\sin2\theta\cos\phi\mathbf{R} &
   -6\left(\cos2\theta\cos\phi\mathbf{\Theta} - \cos\theta\sin\phi\mathbf{\Phi}  \right)  &
   \frac{1}{4\pi\rho r^4}\int_{r/v_p}^{r/v_s}\tau M\left( t-\tau \right)d\tau  \\ &
   +4 \sin2\theta\cos\phi\mathbf{R} &
   -2 \left(\cos2\theta\cos\phi\mathbf{\Theta} - \cos\theta\sin\phi\mathbf{\Phi}  \right)  &
   \frac{1}{4\pi\rho v_p^2 r^2}M\left( t-r/v_p \right)  \\ &
   -3 \sin2\theta\cos\phi\mathbf{R} &
   +3 \left(\cos2\theta\cos\phi\mathbf{\Theta} - \cos\theta\sin\phi\mathbf{\Phi}  \right)  &
   \frac{1}{4\pi\rho v_s^2 r^2}M\left( t-r/v_s \right)  \\ &
   + \sin2\theta\cos\phi\mathbf{R} & &
   \frac{1}{4\pi\rho v_p^3 r}\dot{M}\left( t-r/v_p \right)  \\ & &
   + \left(\cos2\theta\cos\phi\mathbf{\Theta} - \cos\theta\sin\phi\mathbf{\Phi}  \right)  &
   \frac{1}{4\pi\rho v_s^3 r}\dot{M}\left( t-r/v_s \right),  \\
   \end{matrix}


where :math:`\theta` and :math:`\phi` are ratiation angles,
:math:`\mathbf{R}` is the unit vector of the source-receiver radial direction,
:math:`\mathbf{\Phi}` is the perpendicular to the radial direction horizontal unit vector,
and :math:`\mathbf{\Theta}` is the unit vector completing the coordinate system.

We will organize the formula :eq:`eq_a0` algorithmically as follows:

.. math::
   :label: eq_a1

   \mathbf{u}\left ( \mathbf{r},t \right )=
   \mathbf{u}_R\left ( \mathbf{r},t \right )+
   \mathbf{u_T}\left ( \mathbf{r},t \right ),

where :math:`u_R` is the radial part of the displacement, :math:`u_T` is the transversal part of the displacement.

.. math::
   :label: eq_a2

   \mathbf{\mathbf{u}}_* \left(r, t \right) =
   \frac{\mathbf{R}^{N*}}{4\pi\rho r^4}\int_{r/v_p}^{r/v_s}\tau M\left( t-\tau \right)d\tau
   + \left[ \frac{\mathbf{R}^{I*P}}{v_p^2} + \frac{\mathbf{R}^{I*S}}{v_s^2} \right]
   \frac{1}{4\pi\rho r^2}M\left( t \right)
   +\frac{\mathbf{R}^{F*}}{4\pi\rho v_*^3 r } \dot{M}\left( t \right),
	
where :math:`*` means either a radial (:math:`R`) or transversal (:math:`T`) member of :eq:`eq_a1`,
:math:`v_*=v_p` for radial component and :math:`v_*=v_s` for transversal component.
radiation patterns of the near and intermediate fields depend on the far field radiation patterns according to
:math:`\mathbf{R}^{IRP}= 4\mathbf{R}^{FR}`, :math:`\mathbf{R}^{IRS}= -3\mathbf{R}^{FR}`,
:math:`\mathbf{R}^{ITP}= -2\mathbf{R}^{FT}`, :math:`\mathbf{R}^{ITS}= 3\mathbf{R}^{FT}`,
:math:`\mathbf{R}^{NR}= 9\mathbf{R}^{FT}`, :math:`\mathbf{R}^{NT}= -6\mathbf{R}^{FT}`.
Far field patterns exact description,
which depend on the direction angles :cite:`AkiRichards2002`,
has no significance for our research.

The assessment of the near field displacement required the calculation of
:math:`\int_{r/v_p}^{r/v_s}\tau M\left( t-\tau \right)d\tau`,
which in the time domain is the convolution of the source time function
:math:`M\left( t \right)` and the function described by the formula

.. math::
   :label: eq_a3

   G\left( t \right) = t(H(t-r/v_p) - H(t-r/v_s)),
	
where :math:`H\left( t \right)` is Heaviside step function.
In the frequency domain, the calculation of the near field displacement required the multiplication of
source complex function in the frequency domain :math:`M\left( \omega \right)` and the function

.. math::
   :label: eq_a4

   G\left( \omega \right) = \frac{\left(j\omega r/v_s+1\right)exp\left(-j\omega r/v_s\right)
   -\left(j\omega r/v_p+1\right)exp\left(-j\omega r/v_p\right)}{\omega ^2}

where :math:`\omega=2\pi f` and :math:`j=\sqrt{-1}` is.

The assessment of the far field displacement required the differentiate
of source time function.  
