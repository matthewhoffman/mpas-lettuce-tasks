Feature: Reproduce Halfar analytic solution
        In order to perform simulations that are accurate
        As an MPAS Developer
        I want MPAS-Land Ice simulations to reproduce the Halfar analytic solution across different decompositions.

	Scenario: 1 procs with dome shallow-ice
		Given A "dome" "sia" test
		Given A 1 processor MPAS "landice_model" run
		When I compute the Halfar RMS
		Then I see Halfar RMS of <20
#		Then I clean the test directory

	Scenario: 4 procs with dome shallow-ice
		Given A "dome" "sia" test
		Given A 4 processor MPAS "landice_model" run
		When I compute the Halfar RMS
		Then I see Halfar RMS of <20
#		Then I clean the test directory

