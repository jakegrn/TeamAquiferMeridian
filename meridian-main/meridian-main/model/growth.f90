! ======================================================================
!  GROWTH - biomass accumulation and yield.
!  Rewritten in Fortran 90 by K. Osei, 1998-07-22, replacing the
!  original F77 routine.  The radiation use efficiency term was
!  re-fitted at that time against the 1971-1996 trial set.
!
!  Kept deliberately separate from WATBAL so the water balance can be
!  validated on its own.
! ======================================================================
subroutine growth(n, idoy, tmax, tmin, srad, sw, awc, biom, xlai, yield)
   implicit none

   integer, intent(in)  :: n
   integer, intent(in)  :: idoy(n)
   real,    intent(in)  :: tmax(n), tmin(n), srad(n), sw(n)
   real,    intent(in)  :: awc
   real,    intent(out) :: biom(n), xlai(n)
   real,    intent(out) :: yield

   integer :: i
   real    :: tavg, tt, ttcum, lai, b, db
   real    :: fint, stress, rue

   real, parameter :: TBASE   = 5.0      ! base temperature, degC
   real, parameter :: TTEMERG = 120.0    ! thermal time to emergence
   real, parameter :: TTMAT   = 1450.0   ! thermal time to maturity
   real, parameter :: KEXT    = 0.55     ! extinction coefficient
   real, parameter :: LAIMAX  = 5.2
   real, parameter :: RUE0    = 1.62     ! g MJ-1, refitted 1998
   real, parameter :: HINDEX  = 0.48     ! harvest index

   ttcum = 0.0
   b     = 0.0
   lai   = 0.0

   do i = 1, n
      tavg = 0.5 * (tmax(i) + tmin(i))
      tt   = max(tavg - TBASE, 0.0)
      ttcum = ttcum + tt

      if (ttcum < TTEMERG) then
         lai = 0.0
      else if (ttcum < TTMAT) then
         lai = LAIMAX * sin(3.14159265 * (ttcum - TTEMERG) / (TTMAT - TTEMERG))
         if (lai < 0.0) lai = 0.0
      else
         lai = 0.0
      end if

      fint = 1.0 - exp(-KEXT * lai)

      ! Water stress on assimilation.  Uses the same 50 percent
      ! threshold as WATBAL but computes the fraction differently
      ! because AWC here is per-unit-depth.  See MRD-204.
      if (awc > 0.0) then
         stress = min(sw(i) / (awc * 100.0), 1.0)
      else
         stress = 1.0
      end if
      if (stress > 0.5) then
         stress = 1.0
      else
         stress = stress / 0.5
      end if

      rue = RUE0 * stress
      db  = rue * srad(i) * fint
      b   = b + db

      biom(i) = b
      xlai(i) = lai
   end do

   yield = b * HINDEX * 0.01   ! g m-2 to t ha-1

end subroutine growth
