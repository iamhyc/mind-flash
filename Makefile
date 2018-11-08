
all:depends install

depends:
	sudo apt install qt5-qmake qtbase5-dev-tools libqt5core5a libqt5widgets5 python3-pip \
	&& sudo pip3 install termcolor

install:
	mkdir -p ~/.mf
	chmod +x ./mf_entity.py ./mf_gui.py
	sudo mkdir -p /opt/mind-flash
	sudo cp -rf ./* /opt/mind-flash
	sudo ln -sf /opt/mind-flash/mf_gui.py /usr/bin/msh-gui
	sudo ln -sf /opt/mind-flash/mf_entity.py /usr/bin/msh