
PLATFORM=$(shell python3 -c 'import sys; print(sys.platform)')
PYTHON_MINOR=$(shell python3 -c 'import sys; print(sys.version_info.minor)')

all:depends install

depends:
	pip3 install PyQt5 python-dateutil --user

install:
	mkdir -p ~/.mf
	chmod +x ./mf_entity.py ./mf_gui.py
	cp -f /usr/lib/x86_64-linux-gnu/qt5/plugins/platforminputcontexts/libfcitxplatforminputcontextplugin.so \
	~/.local/lib/python3.$(PYTHON_MINOR)/site-packages/PyQt5/Qt/plugins/platforminputcontexts/
	chmod +x ~/.local/lib/python3.$(PYTHON_MINOR)/site-packages/PyQt5/Qt/plugins/platforminputcontexts/libfcitxplatforminputcontextplugin.so
	sudo mkdir -p /opt/mind-flash
	sudo cp -rf ./* /opt/mind-flash
	sudo ln -sf /opt/mind-flash/mf_gui.py /usr/bin/msh-gui
	sudo ln -sf /opt/mind-flash/mf_entity.py /usr/bin/msh

build-dist:
	@if [ "$(PLATFORM)" = "win32" ]; then \
		rm -rf build dist; \
		pyinstaller mf_gui.py -wy; \
		cp -r third-party/* ./dist/; \
		cd dist; zip -r msh-tray.zip ./*; cd ..; \
	elif [ "$(PLATFORM)" = "linux" ]; then \
		echo "Not done for linux platform..."; \
	else \
		echo "Not supporting platform: $(PLATFORM)."; \
	fi

clean-dist:
	rm -rf build dist