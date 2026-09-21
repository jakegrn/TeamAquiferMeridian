# Meridian numerical core.
# Built with gfortran since 2011; originally f77 on the HP-UX box.
FC      = gfortran
FFLAGS  = -O2 -std=legacy -ffixed-line-length-72 -w
F90FLAGS= -O2 -w

all: cropmod

cropmod: cropmod.o waterbal.o growth.o
	$(FC) -o cropmod cropmod.o waterbal.o growth.o

cropmod.o: cropmod.f
	$(FC) $(FFLAGS) -c cropmod.f

waterbal.o: waterbal.f
	$(FC) $(FFLAGS) -c waterbal.f

growth.o: growth.f90
	$(FC) $(F90FLAGS) -c growth.f90

clean:
	rm -f *.o cropmod MERIDIAN.OUT
