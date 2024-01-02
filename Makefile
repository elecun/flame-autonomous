
incabin_camera_monitor:
	@python ./app/incabin_camera_monitor.py --config ./config/camera.cfg

series_analyzer:
	@python ./app/series_analyzer.py --config ./config/mro.cfg

surface_defect_monitor:
	@python ./app/surface_defect_monitor.py --config ./config/sdd.cfg