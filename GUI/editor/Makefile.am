# CORE
# (c)2010-2012 the Boeing Company.
# See the LICENSE file included in this distribution.
#
# author: Jeff Ahrenholz  <jeffrey.m.ahrenholz@boeing.com>
#
# Makefile for installing the CORE GUI. Since it is a Tcl/Tk script, we do not
# build anything here.
#

TCL_FILES	= annotations.tcl api.tcl canvas.tcl cfgparse.tcl \
		core.tcl debug.tcl editor.tcl exec.tcl \
		filemgmt.tcl gpgui.tcl \
		graph_partitioning.tcl help.tcl \
		initgui.tcl ipv4.tcl ipv6.tcl \
		linkcfg.tcl mobility.tcl nodecfg.tcl \
		nodes.tcl ns2imunes.tcl plugins.tcl \
		tooltips.tcl topogen.tcl traffic.tcl util.tcl \
		version.tcl widget.tcl wlan.tcl wlanscript.tcl \
		exceptions.tcl

TINY_ICONS	= icons/tiny/button.play.gif \
		icons/tiny/select.gif icons/tiny/marker.gif \
		icons/tiny/rj45.gif icons/tiny/text.gif \
		icons/tiny/edit-delete.gif icons/tiny/stop.gif \
		icons/tiny/blank.gif icons/tiny/mobility.gif \
		icons/tiny/script_play.gif icons/tiny/arrow.gif \
		icons/tiny/lanswitch.gif icons/tiny/script_pause.gif \
		icons/tiny/pc.gif icons/tiny/rectangle.gif \
		icons/tiny/observe.gif icons/tiny/document-new.gif \
		icons/tiny/document-save.gif \
		icons/tiny/view-refresh.gif icons/tiny/moboff.gif \
		icons/tiny/document-properties.gif icons/tiny/arrow.up.gif \
		icons/tiny/host.gif icons/tiny/hub.gif \
		icons/tiny/twonode.gif icons/tiny/router.gif \
		icons/tiny/eraser.gif \
		icons/tiny/stock_connect.gif icons/tiny/stock_disconnect.gif \
		icons/tiny/ping.gif icons/tiny/link.gif \
		icons/tiny/start.gif \
		icons/tiny/trace.gif icons/tiny/button.stop.gif \
		icons/tiny/arrow.down.gif icons/tiny/oval.gif \
		icons/tiny/wlan.gif icons/tiny/delete.gif \
		icons/tiny/run.gif icons/tiny/tunnel.gif \
		icons/tiny/script_stop.gif \
		icons/tiny/router_black.gif icons/tiny/router_green.gif \
		icons/tiny/router_red.gif icons/tiny/router_yellow.gif \
		icons/tiny/router_purple.gif \
		icons/tiny/ap.gif icons/tiny/mdr.gif \
		icons/tiny/folder.gif \
		icons/tiny/cel.gif \
		icons/tiny/fileopen.gif

NORM_ICONS	= icons/normal/gps-diagram.xbm \
		icons/normal/router_black.gif icons/normal/host.gif \
		icons/normal/hub.gif \
		icons/normal/router.gif \
		icons/normal/rj45.gif icons/normal/antenna.gif \
		icons/normal/text.gif \
		icons/normal/lanswitch.gif icons/normal/core-icon.png \
		icons/normal/core-icon.xbm icons/normal/oval.gif \
		icons/normal/wlan.gif icons/normal/pc.gif \
		icons/normal/tunnel.gif icons/normal/core-logo-275x75.gif \
		icons/normal/router_red.gif icons/normal/router_green.gif \
		icons/normal/simple.xbm \
		icons/normal/document-properties.gif \
		icons/normal/thumb-unknown.gif \
		icons/normal/router_purple.gif icons/normal/router_yellow.gif \
		icons/normal/ap.gif icons/normal/mdr.gif

CONFIG_FILES	= configs/sample1.imn configs/sample1.scen \
		configs/sample1-bg.gif configs/sample2-ssh.imn \
		configs/sample3-bgp.imn	configs/sample4-nrlsmf.imn \
		configs/sample4.scen configs/sample4-bg.jpg \
		configs/sample5-mgen.imn configs/sample6-emane-rfpipe.imn \
		configs/sample7-emane-ieee80211abg.imn

OTHER_FILES	= core-bsd-cleanup.sh

#
# CORE GUI script (/usr/local/bin/core)
#
dist_bin_SCRIPTS = core

#
# Tcl/Tk scripts (/usr/local/lib/core)
#
coredir			= $(CORE_LIB_DIR)
dist_core_DATA		= $(TCL_FILES) 
dist_core_SCRIPTS	= $(OTHER_FILES)

#
# Icon files (/usr/local/lib/core/icons/[tiny,normal])
#
coreiconnormaldir	= $(coredir)/icons/normal
dist_coreiconnormal_DATA = $(NORM_ICONS)
coreicontinydir		= $(coredir)/icons/tiny
dist_coreicontiny_DATA	= $(TINY_ICONS)

#
# Sample configs (/usr/local/share/core/examples/configs)
#
coreconfigsdir		= $(datadir)/core/examples/configs
dist_coreconfigs_DATA	= $(CONFIG_FILES) 


dist-hook:
	rm -rf $(distdir)/addons/.svn

# extra cruft to remove
DISTCLEANFILES	= Makefile.in

# files to include in source tarball not included elsewhere
EXTRA_DIST 	= addons
