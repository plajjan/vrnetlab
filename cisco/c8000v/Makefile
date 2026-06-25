VENDOR=cisco
NAME=c8000v
IMAGE_FORMAT=qcow2
IMAGE_GLOB=*.qcow2

# Extract version from filename (e.g. c8000v-17.11.01a.qcow2)
# If not in filename, extract from qcow2 metadata
VERSION=$(shell V=$$(echo $(IMAGE) | sed -n 's/.*[^0-9]\([0-9]\+\.[0-9]\+\.[0-9]\+[a-z]\?\).*/\1/p'); \
	[ -n "$$V" ] && echo "$$V" || strings $(IMAGE) | awk -F= '/RELVER/{print $$2; exit}')

-include ../../makefile-sanity.include
-include ../../makefile.include
-include ../../makefile-install.include

# Pass MODE to docker build
docker-build: MODE?=autonomous
docker-build: docker-build-common
	(cd docker; docker build --build-arg MODE=$(MODE) -t $(REGISTRY)$(IMG_VENDOR)_$(IMG_NAME):$(VERSION) .)
	$(MAKE) docker-clean-build
	@if [ "$(MODE)" = "autonomous" ]; then \
		echo "Running install step for autonomous mode..."; \
		docker run --cidfile cidfile --privileged $(REGISTRY)$(IMG_VENDOR)_$(IMG_NAME):$(VERSION) --trace --install; \
		docker commit --change='ENTRYPOINT ["uv", "run", "/launch.py"]' $$(cat cidfile) $(REGISTRY)$(IMG_VENDOR)_$(IMG_NAME):$(VERSION); \
		docker rm -f $$(cat cidfile); \
		rm -f cidfile; \
	else \
		echo "Skipping install step for $(MODE) mode (serial-enabled image)"; \
	fi

# Override default to build the autonomous, controller and ztp mode variants.
# The controller and ztp variants both skip the autonomous install step, so they
# stay pristine (empty startup-config) -- ztp needs that to enter day-zero ZTP.
# Because MODE is the very last layer in the Dockerfile (after the qcow2 and the
# *.py), and ENV is a metadata-only instruction, the controller and ztp tags
# share every filesystem layer (base + qcow2 + launch.py) and add zero extra
# bytes -- the qcow2 is stored on disk only once.
docker-image:
	for IMAGE in $(IMAGES); do \
		echo "Building autonomous mode variant for $$IMAGE"; \
		$(MAKE) IMAGE=$$IMAGE MODE=autonomous docker-build; \
		$(MAKE) IMAGE=$$IMAGE docker-clean-build; \
		echo "Building controller mode variant for $$IMAGE"; \
		VER=$$($(MAKE) -s IMAGE=$$IMAGE print-version); \
		$(MAKE) IMAGE=$$IMAGE VERSION=controller-$$VER MODE=controller docker-build; \
		$(MAKE) IMAGE=$$IMAGE docker-clean-build; \
		echo "Building ztp mode variant for $$IMAGE"; \
		VER=$$($(MAKE) -s IMAGE=$$IMAGE print-version); \
		$(MAKE) IMAGE=$$IMAGE VERSION=ztp-$$VER MODE=ztp docker-build; \
		$(MAKE) IMAGE=$$IMAGE docker-clean-build; \
	done

print-version:
	@echo $(VERSION)
