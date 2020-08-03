# Mind Flash

It's a flash over your mind. <img src="./res/icons/pulse_heart.png" width="24">



![preview-01](./previews/preview-03.png)



## Install

The latest *multi-platform* packages are available on [release page](https://github.com/iamhyc/mind-flash/releases/latest).

> For Linux user, please run `msh-userfix` after installation for *fcitx* and *custom keybindings* fix.

**Manual build:**

1. Have `python3` and `python3-pip` (latest version) installed;

2. Download this repository, and execute `make` in the repository folder;
   
    > It will automatically download the requirements, and install itself in system (need root privilege).
    
3. Use `msh-gui` to display GUI, and `msh` for CLI.
   
    > The default shortcut binding for gnome/dde is: <kbd>Super</kbd> + <kbd>N</kbd>.
    
4. (Optional) Build platform-dependent distribution package by run `make build-dist`, and the package will be generated in `./dist` folder.

## Usage

**Basic usage:**

| Default Shortcuts |                 Function                 |
| :-------------: | :--------------------------------------: |
| <kbd>Super</kbd> + <kbd>N</kbd> | Quick Launch |
|    <kbd>Ctrl</kbd> + <kbd>Return</kbd> OR <kbd>Enter</kbd>    | Next Line |
|    <kbd>Return</kbd>    |            Save&Exit    |
|                 |                                          |
|  Double <kbd>click</kbd> OR <kbd>Alt</kbd>+<kbd>H</kbd>  |     Popup History |
|  <kbd>Alt</kbd> + <kbd>v</kbd>  | History - Week |
| <kbd>Alt</kbd> + <kbd>vv</kbd> | History - Month |
| <kbd>Alt</kbd> + <kbd>vvv</kbd> | History - Year |
| <kbd>Alt</kbd> + <kbd>k</kbd> | Last piece of History |
| <kbd>Alt</kbd> + <kbd>j</kbd> | Next piece of History |
* `*italic_text*`, `**bold_text**` render support when input
* <kbd>Ctrl</kbd> + <kbd>V</kbd> support pasting plaintext or image

**Todolist usage**:

* <kbd>Alt</kbd> + <kbd>Q</kbd> to add current text to todolist
* **Right Click** on item to toggle completion status
* **Double Click** on item to remove the item

## License
This project is licensed under [GPLv3](LICENSE).
