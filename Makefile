
all:dependency install

dependency:
	sudo pip3 install termcolor

install:
	mkdir -p ~/.mf
	touch ~/.mf/mf_history
	sudo cp -f ./main.py /usr/bin/msh