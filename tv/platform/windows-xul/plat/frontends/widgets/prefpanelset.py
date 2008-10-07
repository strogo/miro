# Miro - an RSS based video player application
# Copyright (C) 2005-2008 Participatory Culture Foundation
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA
#
# In addition, as a special exception, the copyright holders give
# permission to link the code of portions of this program with the OpenSSL
# library.
#
# You must obey the GNU General Public License in all respects for all of
# the code used other than OpenSSL. If you modify file(s) with this
# exception, you may extend this exception to your version of the file(s),
# but you are not obligated to do so. If you do not wish to do so, delete
# this exception statement from your version. If you delete this exception
# statement from all source files in the program, then also delete it here.

from miro.dialogs import BUTTON_CLOSE
from miro.frontends.widgets import imagepool
from miro.plat.frontends.widgets import widgetset

def get_platform_specific(name):
    pass

class PreferencesWindow(widgetset.Dialog):
    def __init__(self, title):
        widgetset.Dialog.__init__(self, title)
        self.tab_container = widgetset.TabContainer()

    def append_panel(self, name, panel, title, image_name):
        image = imagepool.get(resources.path(image_name))
        self.tab_container.append_tab(panel, title, image)
    
    def finish_panels(self):
        self.set_extra_widget(self.tab_container)
        self.add_button(BUTTON_CLOSE.text)
        
    def select_panel(self, panel, all_panels):
        index = 0
        if panel is not None:
            for i, bits in enumerate(all_panels):
                if bits[0] == panel:
                    index = i
                    break
        self.tab_container.select_tab(index)

    def show(self):
        self.run()
