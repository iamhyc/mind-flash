# Mind Flash

It's a flash over your mind. <img src="./res/icons/pulse_heart.png" width="24">



![preview-01](./previews/preview-04.png)



## Install

The latest out-of-the-box packages are available on [release page](https://github.com/iamhyc/mind-flash/releases/latest).

**Manual build:**

1. Have `python3` and `python3-pip` (latest version) installed;

2. Download this repository, and execute `make` in the repository folder;
   
    > It will automatically download the requirements, and install itself in system (need root privilege).
    
3. Run `msh-userfix` in your terminal (support gnome or dde desktop), and then try <kbd>Super</kbd> + <kbd>N</kbd> to start the journey.
   
    > This script will fix default shortcut binding for current user, and functions for Fcitx input method.
    > If nothing happened, try manually add the custom key binding to `/usr/bin/msh-gui` for your used desktop.
    
4. (Optional) Build platform-dependent distribution package by run `make build-dist`, and the package will be generated in `./dist` folder.

## Usage

**Basic Usage:**

| Default Shortcuts |                 Function                 |
| :-------------: | :--------------------------------------: |
| <kbd>Super</kbd> + <kbd>N</kbd> | Launch |
|    <kbd>Escape</kbd> OR <kbd>Ctrl</kbd>+<kbd>W</kbd>    | Close |
| Double <kbd>click</kbd> | Show/Hide History |
| <kbd>Ctrl</kbd> + <kbd>Return</kbd> OR <kbd>Enter</kbd> | Next Line |
|    <kbd>Return</kbd>    |          Save & Exit    |
**Todo List Usage**: please refer to tooltip by hovering over the `TODO LIST` title.

**Other Features:**

- support `**bold_text**` and `*italic_tex*` style;

- support `<a href="">...</a>` hyperlink;

- support screenshot (pixmap) pasting;

  > right-click on thumbnail to copy, left-click for pop-up preview (scroll for zooming).

- support file drag-and-drop saving;

  > right-click on thumbnail to copy, left-click to open containing folder.

- support export history records into Markdown style on your Desktop.

## License
This project is licensed under [GPLv3](LICENSE).
