
all:depends install

depends:
	pip3 install termcolor python-dateutil

install:
	mkdir -p ~/.mf
	chmod +x ./mf_entity.py ./mf_gui.py
	sudo mkdir -p /opt/mind-flash
	sudo cp -rf ./* /opt/mind-flash
	sudo ln -sf /opt/mind-flash/mf_gui.py /usr/bin/msh-gui
	sudo ln -sf /opt/mind-flash/mf_entity.py /usr/bin/msh