# nautilus-new-file

Adds a "New Text Document" item to the right-click context menu in GNOME
Files (Nautilus), similar to Windows Explorer's "New > Text Document".

Right-clicking on empty space in a folder shows the menu item. Clicking it
opens a small dialog pre-filled with a default file name (`New Text
Document.txt`, `New Text Document (1).txt`, ...); the base name is
pre-selected so you can just start typing to override it. Confirming creates
the file in the current folder and opens it in your default text editor
(GNOME Text Editor by default), switching focus to it.

## Requirements

- GNOME Files (Nautilus) 4.x, GTK4-based
- [`nautilus-python`](https://gitlab.gnome.org/GNOME/nautilus-python)

On Fedora:

```sh
sudo dnf install nautilus-python
```

On Debian/Ubuntu:

```sh
sudo apt install python3-nautilus
```

## Install

```sh
mkdir -p ~/.local/share/nautilus-python/extensions/
cp new_text_file.py ~/.local/share/nautilus-python/extensions/
nautilus -q
```

Nautilus will pick up the extension the next time it starts.

## Uninstall

```sh
rm ~/.local/share/nautilus-python/extensions/new_text_file.py
nautilus -q
```

## Notes

- The "New Text Document" item only appears when right-clicking empty space
  in a folder (matching Windows' behavior), not when right-clicking a file.
- Focus handoff to the editor relies on Wayland's `xdg-activation`
  protocol via GTK's `Gdk.AppLaunchContext`; it's requested while the
  dialog's window is still alive, since the token handshake needs a live
  surface to attach to.

---

*This project, including this README, was developed with the assistance of
[Claude Code](https://claude.com/claude-code).*
