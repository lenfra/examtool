# -*- coding: utf-8 -*-
# noinspection PyUnresolvedReferences
from gi.repository import Gtk


class MessageDialogWindow(Gtk.Window):
    def __init__(self):
        # noinspection PyCallByClass
        Gtk.Window.__init__(self, title="Message dialogue")

        self.box = Gtk.Box(spacing=6)
        self.add(self.box)

    def confirmation_dialogue(self, primary, secondary=None):
        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.QUESTION,
                                   Gtk.ButtonsType.YES_NO, "%s" % primary)
        if secondary is not None:
            dialog.format_secondary_text("%s" % secondary)
        response = dialog.run()
        if response == Gtk.ResponseType.YES:
            dialog.destroy()
            return True
        elif response == Gtk.ResponseType.NO:
            dialog.destroy()
            return False

        dialog.destroy()

    def information_dialogue(self, primary, secondary):
        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO,
                                   Gtk.ButtonsType.OK, "%s" % primary)
        dialog.format_secondary_text(
            "%s" % secondary)
        dialog.run()
        dialog.destroy()

    def confirmation_dialogue_all(self, primary, secondary):
        _label = Gtk.Label(secondary)
        _checkbox = Gtk.CheckButton("Remember for all")
        dialog = Gtk.Dialog(title=primary, parent=self, flags=0)
        dialog.add_button(Gtk.STOCK_YES, Gtk.ResponseType.YES)
        dialog.add_button(Gtk.STOCK_NO, Gtk.ResponseType.NO)
        _box = dialog.get_content_area()
        _box.set_spacing(5)
        _box.add(_label)
        _box.add(_checkbox)
        _label.show()
        _checkbox.show()
        _response = dialog.run()
        dialog.destroy()
        return _response, _checkbox.get_active()

    def open_dialogue(self, primary, secondary):
        _label = Gtk.Label(secondary)
        dialog = Gtk.Dialog(title=primary, parent=self, flags=0)
        dialog.add_button(Gtk.STOCK_CLOSE, Gtk.ResponseType.NO)
        dialog.add_button(Gtk.STOCK_OPEN, Gtk.ResponseType.YES)
        _box = dialog.get_content_area()
        _box.set_spacing(5)
        _box.add(_label)
        _label.show()
        _response = dialog.run()
        dialog.destroy()
        return _response
