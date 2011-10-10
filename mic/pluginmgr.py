#!/usr/bin/python -tt
#
# Copyright (c) 2011 Intel, Inc.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; version 2 of the License
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
# for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc., 59
# Temple Place - Suite 330, Boston, MA 02111-1307, USA.

import os, sys
from mic import msger
from mic import pluginbase

DEFAULT_PLUGIN_LOCATION = "/usr/lib/mic/plugins"

PLUGIN_TYPES = ["imager", "backend"] # TODO  "hook"

class PluginMgr(object):
    plugin_dirs = {}

    # make the manager class as singleton
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(PluginMgr, cls).__new__(cls, *args, **kwargs)

        return cls._instance

    def __init__(self, plugin_dirs=[]):

        # default plugin directory
        for pt in PLUGIN_TYPES:
            self._add_plugindir(os.path.join(DEFAULT_PLUGIN_LOCATION, pt))

        for dir in plugin_dirs:
            self._add_plugindir(dir)

        # load all the plugins
        self._load_all()

    def _add_plugindir(self, dir):
        dir = os.path.abspath(os.path.expanduser(dir))

        if not os.path.isdir(dir):
            msger.warning("Plugin dir is not a directory or does not exist: %s" % dir)
            return

        if dir not in self.plugin_dirs:
            self.plugin_dirs[dir] = False
            # the value True/False means "loaded"

    def _load_all(self):
        for (pdir, loaded) in self.plugin_dirs.iteritems():
            if loaded: continue

            sys.path.insert(0, pdir)
            for mod in [x[:-3] for x in os.listdir(pdir) if x.endswith(".py")]:
                if mod and mod != '__init__':
                    if mod in sys.modules:
                        msger.debug("Module %s already exists, skip" % mod)
                    else:
                        try:
                            pymod = __import__(mod)
                            self.plugin_dirs[pdir] = True
                            msger.debug("Plugin module %s:%s imported" % (mod, pymod.__file__))
                        except ImportError, e:
                            msger.warning('%s, skip plugin %s/%s' %(str(e), os.path.basename(pdir), mod))

            del(sys.path[0])

    def get_plugins(self, ptype):
        """ the return value is dict of name:class pairs """
        return pluginbase.get_plugins(ptype)
