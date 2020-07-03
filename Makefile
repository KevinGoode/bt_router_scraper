RELEASE:=$(BUILD)
PYTHON=python3
PKGNAME=$(shell python setup.py --name)
VERSION=$(shell python setup.py --version)

ifneq ("${BUILD_COUNTER}", "")
	buildcounter:=.${BUILD_COUNTER}
else
	buildcounter:=.1
endif

subrelease:=$(shell date +"%y%m%d")${buildcounter}

all : rpm
	@echo "Generating rpm packages."

rpm:
	$(PYTHON) setup.py bdist_rpm --release ${subrelease}

clean:
	$(PYTHON) setup.py clean --all
	rm -rf dist build rpm-build
	rm -rf ${PKGNAME}.egg-info

dist:
	$(PYTHON) setup.py sdist --formats=gztar
	$(PYTHON) setup.py build

install:
	$(PYTHON) setup.py install -f -O1 --skip-build
