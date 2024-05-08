
incabin_camera_monitor:
	@python3 ./app/incabin_camera_monitor.py --config ./config/camera.cfg

series_analyzer:
	@python3 ./app/series_analyzer.py --config ./config/mro.cfg

surface_defect_monitor:
	@python3 ./app/surface_defect_monitor.py --config ./config/sdd.cfg