#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   InstructionsView.py por:
#   Flavio Danesse <fdanesse@gmail.com>
#   Uruguay

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, Pango, GdkPixbuf

import os
from glob import glob

from Globales import COLORES
from JAMediaImagenes.ImagePlayer import ImagePlayer


class HelpSlideShow(Gtk.EventBox):

    def __init__(self):

        Gtk.EventBox.__init__(self)

        self.modify_bg(Gtk.StateFlags.NORMAL, COLORES["toolbar"])

        self.slides = []
        self.index_select = 0
        self.imagenplayer = False
        self.control = False

        self.drawing = Gtk.DrawingArea()
        eventcontainer = Gtk.EventBox()
        eventcontainer.modify_bg(Gtk.StateFlags.NORMAL, COLORES["toolbar"])
        self.label = Gtk.Label("Text")
        self.label.set_property("justify", Gtk.Justification.CENTER)
        self.drawing.modify_bg(Gtk.StateFlags.NORMAL, COLORES["toolbar"])
        self.label.modify_bg(Gtk.StateFlags.NORMAL, COLORES["toolbar"])
        self.label.modify_fg(Gtk.StateFlags.NORMAL, COLORES["window"])
        eventcontainer.add(self.label)

        hbox = Gtk.HBox()
        self.left = Gtk.Button()
        self.left.set_can_focus(False)
        self.left.set_relief(Gtk.ReliefStyle.NONE)
        imagen = Gtk.Image()
        imagen.set_from_file("Imagenes/flecha_izquierda.png")
        self.left.set_border_width(0)
        self.left.add(imagen)
        self.left.connect("clicked", self.go_left)
        hbox.pack_start(self.left, True, True, 0)

        hbox.add(eventcontainer)

        self.right = Gtk.Button()
        self.right.set_relief(Gtk.ReliefStyle.NONE)
        self.right.set_can_focus(False)
        imagen = Gtk.Image()
        imagen.set_from_file("Imagenes/flecha_derecha.png")
        self.right.set_border_width(0)
        self.right.add(imagen)
        self.right.connect("clicked", self.go_right)
        hbox.pack_end(self.right, True, True, 0)

        tabla = Gtk.Table(rows=8, columns=1, homogeneous=True)
        tabla.attach(self.drawing, 0, 1, 0, 7, ypadding=5)
        tabla.attach(hbox, 0, 1, 7, 8)

        align = Gtk.Alignment(xalign=0.5, yalign=0.5, xscale=0.7, yscale=0.95)
        align.add(tabla)

        self.add(align)

    def go_right(self, widget):
        self.__run_secuencia()
        self.left.show()
        self.right.show()

    def go_left(self, widget):
        self.__run_secuencia(offset=-1)
        self.left.show()
        self.right.show()

    def __run_secuencia(self, widget=None, offset=1):
        self.stop()
        self.index_select += offset
        self.path = self.slides[self.index_select % len(self.slides)]
        self.imagenplayer = ImagePlayer(self.drawing, self.path)
        self.label.set_text("Slide %i of %i" % (
            self.index_select % len(self.slides) + 1, len(self.slides)))

        return True

    def toggle(self):
        if self.control:
            GObject.source_remove(self.control)
            self.control = False
            self.modify_bg(Gtk.StateFlags.NORMAL, COLORES['rojo'])
            self.left.show()
            self.right.show()
        else:
            self.modify_bg(Gtk.StateFlags.NORMAL, COLORES['window'])
            self.play()
            self.left.hide()
            self.right.hide()

    def reset(self):
        self.modify_bg(Gtk.StateFlags.NORMAL, COLORES['window'])
        self.play()

    def stop(self):
        if self.imagenplayer:
            self.imagenplayer.stop()
            del(self.imagenplayer)
            self.imagenplayer = False

    def play(self):
        if not self.control:
            self.control = GObject.timeout_add(10000, self.__run_secuencia)

    def load(self):
        self.stop()
        self.slides = sorted(glob("Imagenes/slides/slide*.png"))
        self.index_select = -1
        self.__run_secuencia()
        return False


class InstructionsView(Gtk.EventBox):

    __gsignals__ = {
        "credits": (GObject.SIGNAL_RUN_FIRST,
                    GObject.TYPE_NONE, ()),
        "start": (GObject.SIGNAL_RUN_FIRST,
                  GObject.TYPE_NONE, ())}

    def __init__(self):

        Gtk.EventBox.__init__(self)

        self.modify_bg(Gtk.StateFlags.NORMAL, COLORES["contenido"])
        self.set_border_width(4)

        self.helpslideshow = HelpSlideShow()

        self.add(self.helpslideshow)
        self.show_all()

    def __decolor(self, widget, event, filestub):
        widget.get_image().set_from_file("Imagenes/%s_disabled.png" % filestub)

    def __color(self, widget, event, filestub):
        widget.get_image().set_from_file("Imagenes/%s.png" % filestub)

    def __credits(self, widget):
        self.emit("credits")

    def __start(self, widget):
        self.fix_scale()
        self.emit("start")

    def stop(self):
        self.helpslideshow.stop()
        self.hide()

    def fix_scale(self):
        pixbuf = GdkPixbuf.Pixbuf.new_from_file("Imagenes/welcome_slide.png")
        screen = self.get_window().get_screen()
        desired_height = screen.get_height() - 180
        desired_width = pixbuf.get_height() / desired_height * pixbuf.get_width()
        pixbuf = pixbuf.scale_simple(desired_width, desired_height, 2)
        self.image.set_from_pixbuf(pixbuf)

    def run(self):
        self.helpslideshow.load()
        self.show()
