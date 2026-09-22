import os
import subprocess

import gi
gi.require_version("Nautilus", "4.1")
gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
from gi.repository import GObject, Gdk, Gio, Gtk, Nautilus


class NewTextFileExtension(GObject.GObject, Nautilus.MenuProvider):
    """Adds a 'New Text Document' item to Nautilus's background context menu."""

    def _folder_path(self, file_info):
        return Gio.File.new_for_uri(file_info.get_uri()).get_path()

    def _unique_name(self, folder, base_name, ext):
        candidate = f"{base_name}{ext}"
        if not os.path.exists(os.path.join(folder, candidate)):
            return candidate
        n = 1
        while True:
            candidate = f"{base_name} ({n}){ext}"
            if not os.path.exists(os.path.join(folder, candidate)):
                return candidate
            n += 1

    def _create_and_open(self, folder, name, launch_context):
        name = name.strip()
        if not name:
            return
        path = os.path.join(folder, name)
        if os.path.exists(path):
            base, ext = os.path.splitext(name)
            path = os.path.join(folder, self._unique_name(folder, base, ext))
        open(path, "x").close()

        gfile = Gio.File.new_for_path(path)
        app = Gio.AppInfo.get_default_for_type("text/plain", False)
        if app is not None:
            app.launch([gfile], launch_context)
        else:
            subprocess.Popen(["gnome-text-editor", path])

    def _prompt_for_name(self, folder):
        default_name = self._unique_name(folder, "New Text Document", ".txt")
        base, _ext = os.path.splitext(default_name)

        window = Gtk.Window(title="New Text Document")
        window.set_default_size(360, -1)
        window.set_resizable(False)
        window.set_modal(True)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_top(16)
        box.set_margin_bottom(16)
        box.set_margin_start(16)
        box.set_margin_end(16)
        window.set_child(box)

        entry = Gtk.Entry()
        entry.set_text(default_name)
        entry.set_activates_default(True)
        box.append(entry)

        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        button_box.set_halign(Gtk.Align.END)
        box.append(button_box)

        cancel_button = Gtk.Button(label="Cancel")
        create_button = Gtk.Button(label="Create")
        create_button.add_css_class("suggested-action")
        window.set_default_widget(create_button)
        button_box.append(cancel_button)
        button_box.append(create_button)

        def do_create(*_args):
            # The Wayland activation-token handshake needs our window's
            # surface to still be alive, so launch before destroying it.
            launch_context = window.get_display().get_app_launch_context()
            self._create_and_open(folder, entry.get_text(), launch_context)
            window.destroy()

        def do_cancel(*_args):
            window.destroy()

        create_button.connect("clicked", do_create)
        cancel_button.connect("clicked", do_cancel)
        entry.connect("activate", do_create)

        key_controller = Gtk.EventControllerKey()

        def on_key(_controller, keyval, _keycode, _state):
            if keyval == 65307:  # Escape
                do_cancel()
                return True
            return False

        key_controller.connect("key-pressed", on_key)
        window.add_controller(key_controller)

        window.present()
        entry.select_region(0, len(base))
        entry.grab_focus()

    def get_background_items(self, current_folder):
        item = Nautilus.MenuItem(
            name="NewTextFileExtension::new_text_file",
            label="New Text Document",
            tip="Create a new text file here and open it",
        )
        folder = self._folder_path(current_folder)
        item.connect("activate", lambda _menu: self._prompt_for_name(folder))
        return [item]
