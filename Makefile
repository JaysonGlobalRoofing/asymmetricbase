
all: clean build sync
	
	
clean:
	rm -rf build dist *.deb MANIFEST

build: clean
	python setup.py bdist_rpm
	sudo alien -dc dist/*.noarch.rpm

sync: build
	rsync -avh *.deb jayson:
	rsync -avh *.deb westpoint: