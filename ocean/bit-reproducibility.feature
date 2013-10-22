Feature: Bit-Reproducible simulations
	MPAS-Ocean simulations are bit-repdoducible
	across different decompositions, and previous versions of develop.

	Scenario: 2 vs 4 procs with split explicit
		Given A "10000m" "20levs" "baroclinic_channel" "split_explicit" test
		Given A 2 processor MPAS "ocean_model" run
		Given A 4 processor MPAS "ocean_model" run
		When I compute the RMS of "temperature"
		When I compute the RMS of "layerThickness"
		Then I see "temperature" RMS of 0
		Then I see "layerThickness" RMS of 0
		Then I clean the test directory

	Scenario: 1 vs 8 procs with RK4
		Given A "10000m" "20levs" "baroclinic_channel" "RK4" test
		Given A 1 processor MPAS "ocean_model" run
		Given A 8 processor MPAS "ocean_model" run
		When I compute the RMS of "temperature"
		When I compute the RMS of "layerThickness"
		Then I see "temperature" RMS of 0
		Then I see "layerThickness" RMS of 0
		Then I clean the test directory

	Scenario: 2 vs 4 procs with split explicit
		Given A "10km" "40layer" "overflow" "split_explicit" test
		Given A 2 processor MPAS "ocean_model" run
		Given A 4 processor MPAS "ocean_model" run
		When I compute the RMS of "temperature"
		When I compute the RMS of "layerThickness"
		Then I see "temperature" RMS of 0
		Then I see "layerThickness" RMS of 0
		Then I clean the test directory

	Scenario: 1 vs 8 procs with RK4
		Given A "10km" "40layer" "overflow" "RK4" test
		Given A 1 processor MPAS "ocean_model" run
		Given A 8 processor MPAS "ocean_model" run
		When I compute the RMS of "temperature"
		When I compute the RMS of "layerThickness"
		Then I see "temperature" RMS of 0
		Then I see "layerThickness" RMS of 0
		Then I clean the test directory

	Scenario: 8 vs 8 procs with RK4 against develop
		Given A "10000m" "20levs" "baroclinic_channel" "RK4" test
		Given A 8 processor MPAS "ocean_model" run
		Given A 8 processor MPAS "ocean_model_develop" run
		When I compute the RMS of "temperature"
		When I compute the RMS of "layerThickness"
		Then I see "temperature" RMS of 0
		Then I see "layerThickness" RMS of 0
		Then I clean the test directory

	Scenario: 8 vs 8 procs with split explicit against develop
		Given A "10000m" "20levs" "baroclinic_channel" "split_explicit" test
		Given A 8 processor MPAS "ocean_model" run
		Given A 8 processor MPAS "ocean_model_develop" run
		When I compute the RMS of "temperature"
		When I compute the RMS of "layerThickness"
		Then I see "temperature" RMS of 0
		Then I see "layerThickness" RMS of 0
		Then I clean the test directory

	Scenario: 8 vs 8 procs with RK4 against develop
		Given A "10km" "40layer" "overflow" "RK4" test
		Given A 8 processor MPAS "ocean_model" run
		Given A 8 processor MPAS "ocean_model_develop" run
		When I compute the RMS of "temperature"
		When I compute the RMS of "layerThickness"
		Then I see "temperature" RMS of 0
		Then I see "layerThickness" RMS of 0
		Then I clean the test directory

	Scenario: 8 vs 8 procs with split explicit against develop
		Given A "10km" "40layer" "overflow" "split_explicit" test
		Given A 8 processor MPAS "ocean_model" run
		Given A 8 processor MPAS "ocean_model_develop" run
		When I compute the RMS of "temperature"
		When I compute the RMS of "layerThickness"
		Then I see "temperature" RMS of 0
		Then I see "layerThickness" RMS of 0
		Then I clean the test directory

