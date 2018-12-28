# Mind Flash

It's a flash over your mind. <img src="./icons/pulse_heart.png" width="24">

### Preview

![preview-01](./previews/preview-01.gif)

### Install

1. Download this repository

2. Prepare `python3` and `python3-pip` on your Linux system

3. Execute `make` in the folder

4. for text-based version: `msh` in your terminal

   for GUI-based version: `msh-gui` in your terminal, or `Super + N`

### Usage

| Default Shortcuts |                 Function                 |
| :-------------: | :--------------------------------------: |
| <kbd>Super</kbd> + <kbd>N</kbd> | Quick Launch |
|    <kbd>Ctrl</kbd> + <kbd>Return</kbd> OR <kbd>Enter</kbd>    | Next Line |
|    <kbd>Return</kbd>    |            Save&Exit    |
|                 |                                          |
|  Double <kbd>click</kbd>  |     Popup History |
|  <kbd>Alt</kbd> + <kbd>v</kbd>  | History - Week |
| <kbd>Alt</kbd> + <kbd>vv</kbd> | History - Month |
| <kbd>Alt</kbd> + <kbd>vvv</kbd> | History - Year |
| <kbd>Alt</kbd> + <kbd>k</kbd> | Last History |
| <kbd>Alt</kbd> + <kbd>j</kbd> | Next History |

> You could customize the key bindings in the configuration file `~/.config/mf/config.json`

### TODO

- [x] Add GUI, Shortcuts Binding
- [x] Single Instance (now with socket)
- [x] Add Index Function, and Day Splitter
- [x] Implement Complex Key Binding
- [x] Implement Fetch Function
- [x] ~~Add rsync function, with Private Key~~ 
  (for now, sync `~/.mf` with your cloud service)
- [x] Fix Fetch Function Replement
- [x] Add Chinese Characters Support
- [x] Clipboard Images Support
  ~~(point of first beta release)~~
- [ ] Remember Window Position
- [ ] Support Configuration File (position, shortcut binding)
- [ ] Refactor InputBox (auto adjust height, pixmap preview)
- [ ] Refactor HistoryBox (Item Listview, Item Aggregation)
  (point of first formal release)
