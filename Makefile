VERSION=1.0.1
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
	sudo cp -rf res *.py /opt/mind-flash
	sudo ln -sf /opt/mind-flash/mf_gui.py /usr/bin/msh-gui
	sudo ln -sf /opt/mind-flash/mf_entity.py /usr/bin/msh

# sudo apt remove mind-flash -y && make build-dist && sudo dpkg -i dist/mind-flash.deb
build-dist:clean-dist
	@if [ "$(PLATFORM)" = "win32" ]; then \
		rm -rf build dist; \
		pyinstaller mf_gui.py -wy; \
		cp -r third-party/win32/* ./dist/; \
		cp -r res ./dist/mf_gui; \
		cd dist; zip -r msh-tray-$(VERSION)-win32.zip ./*; cd ..; \
	elif [ "$(PLATFORM)" = "linux" ]; then \
		mkdir -p build/opt/mind-flash; mkdir dist; \
		cp -r third-party/linux/mind-flash-deb/* ./build/; \
		cp -r res *.py ./build/opt/mind-flash; \
		dpkg-deb --build build dist/mind-flash_$(VERSION)_all.deb; \
	else \
		echo "Not supporting platform: $(PLATFORM)."; \
	fi

clean-dist:
	@rm -rf build dist

clean:clean-dist
	@rm -f *.spec