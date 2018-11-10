# Mind Flash

It's a flash over your mind. <img src="./icons/pulse_heart.png" width="24">

### Preview

![preview-01](./previews/preview-01.gif)

### Install

1. Download this repository
2. Prepare `python3` and `python3-pip` on your Linux system
3. Execute `make` in the folder
4. Use `msh-gui` for GUI version, and `msh` for text-based version
5. (Optional) bind shortcuts for `msh-gui` for quick launch

### Usage

|    Function     |                 Shortcut                 |
| :-------------: | :--------------------------------------: |
|  Quick Launch   | <kbd>Ctrl</kbd> + <kbd>Alt</kbd> + <kbd>m</kbd> |
|    Next Line    | <kbd>Ctrl</kbd> + <kbd>Return</kbd> OR <kbd>Enter</kbd> |
|    Save&Exit    |            <kbd>Return</kbd>             |
|                 |                                          |
|  Popup History  |         Double <kbd>click</kbd>          |
|  History - Week  | <kbd>Alt</kbd> + <kbd>v</kbd> |
| History - Month  | <kbd>Alt</kbd> + <kbd>vv</kbd> |
| History - Year | <kbd>Alt</kbd> + <kbd>vvv</kbd> |
|  Last History   | <kbd>Alt</kbd> + <kbd>k</kbd> |
|  Next History   | <kbd>Alt</kbd> + <kbd>j</kbd> |

> for now, you should bind the `quick launch` shortcut by yourself

### TODO

- [x] Add GUI, Shortcuts Binding
- [x] Single Instance (now with socket)
- [x] Add Index Function, and Day Splitter
- [x] Implement Complex Key Binding
- [x] Implement Fetch Function
- [x] ~~Add rsync function, with Private Key~~ 
  (for now, sync `~/.mf` with your cloud service)
- [ ] Fix Fetch Function Replement
- [ ] Auto update function
- [ ] Clipboard Images Support
- [ ] Add Chinese Characters Support
  (point of first beta release)
- [ ] Listview for History
- [ ] Listview for Todolist
  (point of first formal release)
