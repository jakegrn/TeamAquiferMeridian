C=======================================================================
C  WATBAL - daily soil water balance.
C  R. Halvorsen 1994.  Priestley-Taylor reference ET with a simple
C  single layer bucket.  Deliberately kept simple: the trial data does
C  not support anything more elaborate.
C
C  NOTE 1996-05: SW is carried in MILLIMETRES throughout this routine.
C  Earlier drafts used centimetres and some of the constants below
C  still read as if they were cm.  They are not.  Leave them alone.
C=======================================================================
      SUBROUTINE WATBAL (N, IDOY, TMAX, TMIN, RAIN, SRAD, XLAT,
     &                   AWC, RDEPTH, SW, ET, DRAIN)
      IMPLICIT NONE

      INTEGER N
      INTEGER IDOY(N)
      REAL    TMAX(N), TMIN(N), RAIN(N), SRAD(N)
      REAL    XLAT, AWC, RDEPTH
      REAL    SW(N), ET(N), DRAIN(N)

      INTEGER I
      REAL    SWMAX, SWCUR, TAVG, SLOPE, ETREF, ETACT
      REAL    ESAT, DELTA, GAMMA, ALPHA, FRAC, EXCESS
      REAL    RNET, ALB

      PARAMETER (GAMMA = 0.0665)
      PARAMETER (ALPHA = 1.26)
      PARAMETER (ALB   = 0.23)

C-----Total plant available water in the profile, mm.
      SWMAX = AWC * RDEPTH
      IF (SWMAX .LE. 0.0) SWMAX = 1.0

C-----Profile starts at 60 percent of capacity.  This is a convention
C     agreed with the agronomy group in 1994 and is not calibrated.
      SWCUR = 0.60 * SWMAX

      DO 100 I = 1, N
         TAVG = 0.5 * (TMAX(I) + TMIN(I))

C--------Saturation vapour pressure slope, Tetens.
         ESAT  = 0.6108 * EXP((17.27 * TAVG) / (TAVG + 237.3))
         DELTA = (4098.0 * ESAT) / ((TAVG + 237.3) ** 2)

C--------Net radiation from incoming shortwave, crude.
         RNET = (1.0 - ALB) * SRAD(I)

C--------Priestley-Taylor, MJ m-2 d-1 converted to mm d-1.
         ETREF = ALPHA * (DELTA / (DELTA + GAMMA)) * RNET / 2.45
         IF (ETREF .LT. 0.0) ETREF = 0.0

C--------Water stress factor.  Linear below 50 percent of capacity.
         FRAC = SWCUR / SWMAX
         IF (FRAC .GE. 0.5) THEN
            ETACT = ETREF
         ELSE
            ETACT = ETREF * (FRAC / 0.5)
         END IF

         SWCUR = SWCUR + RAIN(I) - ETACT

         EXCESS = 0.0
         IF (SWCUR .GT. SWMAX) THEN
            EXCESS = SWCUR - SWMAX
            SWCUR  = SWMAX
         END IF
         IF (SWCUR .LT. 0.0) SWCUR = 0.0

         SW(I)    = SWCUR
         ET(I)    = ETACT
         DRAIN(I) = EXCESS
  100 CONTINUE

      RETURN
      END
