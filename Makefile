SHELL := bash

# The Pi to deploy to and test on, e.g. make test_hw HOST=pi@192.168.68.83
HOST ?= pi@vision-kit.local
# Extra install.sh options for deploy, e.g. ARGS=--streaming
ARGS ?=
# Reference still with a face (not in git; from the original card's baseline)
VIEW2 ?= vendor/baseline/view2.jpg

PY := /opt/aiy/venv/bin/python
EXAMPLES := /opt/aiy/python/src/examples/vision
# Run a test on the Pi with the Joy Detector stopped, and start it again afterwards
# even when the test fails.
ON_PI = ssh -o BatchMode=yes $(HOST) 'sudo systemctl stop joy_detection_demo; export LIBCAMERA_LOG_LEVELS="*:WARN"; cd ~; $(1); rc=$$?; sudo systemctl start joy_detection_demo; exit $$rc'

info: menu select

menu:
	echo "1 make fetch                - get Myriad firmware + models into vendor/aiy-binaries.tgz"
	echo "2 make deploy               - install/update the Pi (HOST=$(HOST), ARGS=$(ARGS))"
	echo "3 make reboot               - reboot the Pi"
	echo "4 make status               - DKMS, Myriad and Joy Detector status on the Pi"
	echo "5 make test_hw              - LEDs, buzzer, expansion pins"
	echo "6 make test_face            - Myriad + face model on a still (no camera)"
	echo "7 make test_camera          - live camera inference, 60 frames"
	echo "8 make test_stream          - protobuf stream on port 4665 (service needs --streaming)"
	echo "9 make patches              - regenerate port/drivers.patch and port/python.patch"
	echo "10 make check_docs          - check CLAUDE.md, cards and setup record"
	echo "11 make uninstall           - remove everything install.sh added from the Pi"
	echo "12 make update_phony        - update .PHONY in Makefile"

select:
	read -p ">>> " P ; "$(MAKE)" --no-print-directory menu | grep "^$$P " | cut -d ' ' -f2-3 | bash

.SILENT:

.PHONY: info menu select fetch deploy reboot status sync_tests test_hw test_face test_camera test_stream patches check_docs uninstall update_phony 

fetch:
	port/fetch-binaries.sh

deploy:
	port/deploy.sh $(HOST) $(ARGS)

reboot:
	ssh $(HOST) sudo reboot || true

status:
	ssh -o BatchMode=yes $(HOST) 'uname -r; /usr/sbin/dkms status aiy-vision-kit; sudo journalctl -k -b --no-pager | grep -q "Myriad ready" && echo "Myriad ready" || echo "Myriad: not ready"; ls -l /dev/vision_spicomm; systemctl is-active joy_detection_demo; grep -o "joy_detection_demo.py.*" /etc/systemd/system/joy_detection_demo.service'

sync_tests:
	rsync -a port/tests/ $(HOST):vision-kit-port/tests/

test_hw: sync_tests
	$(call ON_PI,$(PY) vision-kit-port/tests/hardware_check.py)

test_face:
	[[ -f "$(VIEW2)" ]] || { echo "missing $(VIEW2): set VIEW2=<a jpeg with a face>"; exit 1; }
	scp -q "$(VIEW2)" $(HOST):view2.jpg
	$(call ON_PI,$(PY) $(EXAMPLES)/face_detection.py --input ~/view2.jpg)

test_camera:
	$(call ON_PI,$(PY) $(EXAMPLES)/face_detection_camera.py --num_frames 60 | tail -3)

test_stream: sync_tests
	ssh -o BatchMode=yes $(HOST) 'for i in $$(seq 1 90); do ss -ltn | grep -q ":4665 " && break; sleep 1; done; ss -ltn | grep -q ":4665 " || { echo "nothing listens on 4665: is the service running with --streaming?"; exit 1; }; $(PY) vision-kit-port/tests/streaming_client.py --host localhost --seconds 8 --h264 /tmp/tcp.h264'

patches:
	port/make-patches.sh

check_docs:
	CHECK=$$(mktemp -d)/check-agent-docs.py; curl -fsSL https://ai.memention.net/cards/check-agent-docs.py -o "$$CHECK" && python3 -I "$$CHECK" .

uninstall:
	ssh -t $(HOST) 'cd vision-kit-port && sudo ./uninstall.sh'

update_phony:
	echo "##### Updating .PHONY targets #####"
	targets=$$(grep -E '^[a-zA-Z_][a-zA-Z0-9_-]*:' Makefile | grep -v '=' | cut -d: -f1 | tr '\n' ' '); \
	sed -i.bak "s/^\.PHONY:.*/.PHONY: $$targets/" Makefile && \
	echo "Updated .PHONY: $$targets" && \
	rm -f Makefile.bak
