#
# Copyright 2005-2012 the Boeing Company.
# See the LICENSE file included in this distribution.
#

#
# Widgets are defined in this array.
# widget array: name, {config, init, periodic, move}
#
array set widgets {
	"Throughput" 
	{ widget_thru_config widget_thru_init widget_thru_periodic widget_thru_move } 
	"Adjacency"
	{ widget_adjacency_config widget_adjacency_init widget_adjacency_periodic widget_adjacency_move }
}
# TODO:   fix CPU Widget; it is disabled because Linux network namespaces and
#         FreeBSD jails do not have a CPU usage reporting mechanism right now
#	"CPU" 
#	{ widget_cpu_config widget_cpu_init widget_cpu_periodic widget_cpu_move }

# Common Observer Widget definitions
set widgets_obs_quagga {
    5 
    {{OSPFv2 neighbors} {vtysh -c {show ip ospf neighbor}}}

    6
    {{OSPFv3 neighbors} {vtysh -c {show ipv6 ospf6 neighbor}}}

    12
    {{OSPFv3 MDR level} {vtysh -c {show ipv6 ospf6 mdrlevel}}}

    13
    {{PIM neighbors} {vtysh -c {show ip pim neighbor}}}
}

# Observer Widget definitions for FreeBSD
array set widgets_obs_bsd $widgets_obs_quagga
array set widgets_obs_bsd {
	1
	{ "processes" "ps ax" }
	2
	{ "ifconfig" "ifconfig" }
	3
	{ "IPv4 routes" "netstat -f inet -rn" }
	4
	{ "IPv6 routes" "netstat -f inet6 -rn" }
	7
	{ "IPv4 listening sockets" "sockstat -4l" }
	8
	{ "IPv6 listening sockets" "sockstat -6l" }
	9
	{ "IPv4 MFC entries" "ifmcstat -f inet" }
	10
	{ "IPv6 MFC entries" "ifmcstat -f inet6" }
	11
	{ "firewall rules" "ipfw -a list" }
	12
	{ "IPsec policies" "setkey -DP" }
}

# Observer Widget definitions for Linux
array set widgets_obs_linux $widgets_obs_quagga
array set widgets_obs_linux {
	1
	{ "processes" "ps -e" }
	2
	{ "ifconfig" "/sbin/ifconfig" }
	3
	{ "IPv4 routes" "/sbin/ip -4 ro" }
	4
	{ "IPv6 routes" "/sbin/ip -6 ro" }
	7
	{ "Listening sockets" "netstat -tuwnl" }
	8
	{ "IPv4 MFC entries" "/sbin/ip -4 mroute show" }
	9
	{ "IPv6 MFC entries" "/sbin/ip -6 mroute show" }
	10
	{ "firewall rules" "/sbin/iptables -L" }
	11
	{ "IPSec policies" "setkey -DP" }
}

set widget_loop_ID -1

#
# Set default Observer Widget array, used when widgets.conf is unvailable.
#
proc init_default_widgets_obs {} {
    global systype widgets widgets_obs widget_obs last_widgetObserveNode
    global widgets_obs_bsd widgets_obs_linux

    setSystype
    array unset widgets_obs
    if { [lindex $systype 0] == "Linux" } {
	set arrayname widgets_obs_linux
	# this works, but we will instead reset all indices:
	#array set widgets_obs [array get widgets_obs_linux]
    } else {
	set arrayname widgets_obs_bsd
    }

    # this resets the array indices to be 1, 2, 3, etc.
    set i 1
    foreach {idx value} [array get $arrayname] {
	set name [lindex $value 0]
	set cmd  [lindex $value 1]
	array set widgets_obs [list $i [list $name $cmd]]
	incr i
    }
}

#
# Dynamically loads the widget menu from the widget array
#
proc init_widget_menu {} {
    global widgets last_widgetObserveNode

    menu .menubar.widgets -tearoff 1
    menu .menubar.widgets.obs -tearoff 1

    .menubar.widgets add cascade -label "Observer Widgets" \
	-menu .menubar.widgets.obs

    # standard widgets
    foreach w [array names widgets] {
	global enable_$w
        set enable_$w 0
	# note that a more modular way to break out submenus would be nice here 
	if { $w == "Adjacency" } {
	    widget_adjacency_init_submenu .menubar.widgets
	    continue
	}
	#
	.menubar.widgets add checkbutton -label "$w" -variable enable_$w \
		-command "[lindex $widgets($w) 1] menu"
    }

    # observer widgets
    init_widget_obs_menu

    # configure each widget
    .menubar.widgets add separator
    foreach w [array names widgets] {
	.menubar.widgets add command -label "Configure $w..." \
		-command [lindex $widgets($w) 0]
    }

}

proc init_widget_obs_menu {} {
    global widgets_obs widget_obs last_widgetObserveNode

    # clear the existing menu
    .menubar.widgets.obs delete 0 end

    # observer widgets
    set widget_obs 0
    set last_widgetObserveNode [clock clicks -milliseconds]
    .menubar.widgets.obs add radiobutton -label "None" -variable widget_obs \
	-value 0 -command "obsBtn default"
    set obs [array names widgets_obs]
    foreach w [lsort -integer  $obs] {
	set capt [lindex $widgets_obs($w) 0]
	.menubar.widgets.obs add radiobutton -label "$capt" \
		 -variable widget_obs -value $w -command "obsBtn gray"
    }
    .menubar.widgets.obs add command -label "Edit..." \
		-command configObsWidgets

}

#
# Calls the periodic proc for each enabled widget
#
# this loop fires periodically, started from exec.tcl/setOperMode(exec)
proc widget_loop { } {
    global oper_mode widget_loop_ID
    set c .c
    set now [clock clicks -milliseconds]
    set refresh_ms 1000

    # terminates this event loop
    if { $oper_mode != "exec" } {
	# cleanup here
	widgets_stop
	return
    }

    # call periodic function for each widget
    global widgets
    foreach w [array names widgets] {
	global enable_$w
        if { [set enable_$w] } {
	    if {$widget_loop_ID == -1} { ;# first time: call initialize func
		[lindex $widgets($w) 1] start
	    }
	    [lindex $widgets($w) 2] $now
	}
    }
    update ;# let the GUI process things

    # account for time elapsed doing periodic functions
    set now2 [clock clicks -milliseconds]
    set refresh_ms [expr {$refresh_ms - ($now2-$now)}]
    if { $refresh_ms <= 0 } {
#	puts "warning: widget periodic functions are unable to keep up ($refresh_ms ms lost)"
    	set refresh_ms 100
    }
    set widget_loop_ID [after $refresh_ms { widget_loop }]
}


#
# De-initialize widgets
#
proc widgets_stop { } {
    # call periodic function for each widget
    global widgets widget_loop_ID

    after cancel $widget_loop_ID ;# prevent the widget loop from executing
    set widget_loop_ID -1

    foreach w [array names widgets] {
	global enable_$w
        if { [set enable_$w] } {
	    [lindex $widgets($w) 1] "stop"
	}
    }
}


#
# Calls the node movement handler each enabled widget
#
# called from editor.tcl, button1-motion
proc widgets_move_node { c node done } {
    global oper_mode

    if { $oper_mode != "exec" } {
	return
    }

    # call node move function for each widget
    global widgets
    foreach w [array names widgets] {
	global enable_$w
        if { [set enable_$w] } {
	    [lindex $widgets($w) 3] $c $node $done
	}
    }
}

# popup the widget menu from a button
proc popupObserverWidgets {} {
    global activetool
    set activetool select
    set x [expr [winfo rootx .left.observe] + 10]
    set y [expr [winfo rooty .left.observe] + 10]
    .menubar.widgets.obs post $x $y
}

# change the color of the observer widget toolbar button
proc obsBtn { color } {
    # default color is efebe7, but theme dependent?
    if { $color == "default" } {
    	set color [.left.select cget -bg]
	floatingInfo .c "" ""
    }
    catch { .left.observe configure -bg $color }
}

# dummy functions for widgets that don't define
proc widget_config_none {} {
    return
}
proc widget_init_none {command} {
    return
}
proc widget_periodic_none {now} {
    return
}
proc widget_move_none {c node done} {
    return
}

# observer widget support
proc widgetObserveNode {c node} {
    global oper_mode eid widget_obs widgets_obs

    # not running, no observer selected
    if { $oper_mode != "exec" } { return }
    if { ![info exists widgets_obs($widget_obs)] } { return }
    global last_widgetObserveNode
    if { [winfo pointerxy .] == $last_widgetObserveNode} {
	return; # cursor has not really moved -- avoid callback loop
    }
    # delete popup
    if { $node == "" } {
	floatingInfo $c "" ""
	return
    }
    # observe layer3 NETWORK nodes only
    if { [[typemodel $node].layer] == "LINK" && \
	 [getNodeModel $node] != "remote" } {
	return
    }
    set last_widgetObserveNode [winfo pointerxy .]
    set obsinfo $widgets_obs($widget_obs)

    set sock [lindex [getEmulPlugin $node] 2]
    set exec_num [newExecCallbackRequest observer]
    set cmd [lindex $obsinfo 1]
    set cmd [string map { \{ ' \} ' } $cmd] ;# replace brackets with quotes
    sendExecMessage $sock $node $cmd $exec_num 0x30
}

# popup a dialog box for editing the Observer Widget list
# results are stored in widgets.conf file and widget_obs array
proc configObsWidgets {} {
    global widgets_obs last_obswidget_selected LIBDIR

    set wi .obsWidgetsConfig
    catch {destroy $wi}
    toplevel $wi

    wm transient $wi .
    wm resizable $wi 0 0
    wm title $wi "Observer Widgets"

    set last_obswidget_selected -1

    # turn on/off remote execution
    frame $wi.t -borderwidth 4
    set img [image create photo -file "$LIBDIR/icons/tiny/observe.gif"]
    radiobutton $wi.t.img -indicatoron 0 -activebackground gray \
			-selectcolor [.left cget -bg] -image $img
    label $wi.t.help -wraplength 350 -text "Observer Widgets are commands run on a node upon mouse-over with their result displayed in a popup box. Their associated commands should exit quickly in order to avoid display delay."
    pack $wi.t.img $wi.t.help -side left
    pack $wi.t -fill x -side top

    # controls for editing entries
    labelframe $wi.c -text "Widget settings"
    frame $wi.c.c -borderwidth 4
    label $wi.c.c.namelab -text "Name     "
    entry $wi.c.c.name -bg white -width 30
    bind $wi.c.c.name <KeyPress> "$wi.c.c3.add configure -state normal"
    pack $wi.c.c.namelab $wi.c.c.name -side left
    pack $wi.c.c -fill x -side top

    frame $wi.c.c2 -borderwidth 4
    label $wi.c.c2.cmdlab -text "Command"
    entry $wi.c.c2.cmd -bg white -width 40
    pack $wi.c.c2.cmdlab $wi.c.c2.cmd -side left
    pack $wi.c.c2 -fill x -side top

    frame $wi.c.c3 -borderwidth 4
    button $wi.c.c3.add -text "new" \
	-command "configObsWidgetsHelper $wi 1"
    button $wi.c.c3.mod -text "modify" \
	-command "configObsWidgetsHelper $wi 2" 
    button $wi.c.c3.del -text "delete" \
	-command "configObsWidgetsHelper $wi 3" 
    pack $wi.c.c3.del $wi.c.c3.mod $wi.c.c3.add -side right
    pack $wi.c.c3 -fill x -side top

    pack $wi.c -fill x -side top

    # list of widgets
    frame $wi.s -borderwidth 4
    listbox $wi.s.servers -selectmode single -width 50 \
	-yscrollcommand "$wi.s.servers_scroll set" -exportselection 0
    scrollbar $wi.s.servers_scroll -command "$wi.s.servers yview" 
    pack $wi.s.servers $wi.s.servers_scroll -fill y -side left
    pack $wi.s -fill x -side top
    bind $wi.s.servers <<ListboxSelect>> "selectObsWidgetConf $wi"

    # up/down buttons
    frame $wi.buttons2
    foreach b {up down} {
        set img$b [image create photo -file $LIBDIR/icons/tiny/arrow.${b}.gif]
	if { $b=="up" } { set cmd 4 } else { set cmd 5 }
	button $wi.buttons2.$b -image [set img${b}] \
		-command "configObsWidgetsHelper $wi $cmd"
    }
    pack $wi.buttons2.up $wi.buttons2.down -side left -expand 1
    pack $wi.buttons2 -side top -fill x -pady 2

    # populate the list
    foreach w [lsort -integer [array names widgets_obs]] {
	set name [lindex $widgets_obs($w) 0]
	$wi.s.servers insert end $name
    }

    # apply/cancel buttons
    frame $wi.b -borderwidth 4
    button $wi.b.apply -text "Apply" -command \
	"writeWidgetsConf; destroy $wi; init_widget_obs_menu"
    button $wi.b.reset -text "Reset All" -command "resetObsWidgets"
    button $wi.b.cancel -text "Cancel" -command "loadWidgetsConf;  destroy $wi"
    pack $wi.b.cancel $wi.b.reset $wi.b.apply -side right
    pack $wi.b -side bottom
    focus $wi.b.apply

    after 100 {	catch { set wi .obsWidgetsConfig; grab $wi; \
	    		$wi.s.servers selection set 0; \
			selectObsWidgetConf $wi } }
}

#
# Load the widgets.conf file into the widgets_obs array.
#
proc loadWidgetsConf { } {
    global CONFDIR widgets_obs
    set confname "$CONFDIR/widgets.conf"
    if { [catch { set f [open "$confname" r] } ] } {
	init_default_widgets_obs
	if { [catch { set f [open "$confname" w+] } ] } {
	    puts "***Warning: could not create a default $confname file."
	    return
	}
        foreach w [lsort -integer [array names widgets_obs]] {
	    set name [lindex $widgets_obs($w) 0]
	    set cmd [lindex $widgets_obs($w) 1]
	    puts $f "$w {{$name} {$cmd}}"
	}
	close $f
    	if { [catch { set f [open "$confname" r] } ] } {
	    return
	}
    }

    array unset widgets_obs

    while { [ gets $f line ] >= 0 } {
	if { [string range $line 0 0] == "#" } { continue } ;# skip comments
	array set widgets_obs $line
    }
    close $f
}

#
# Write the widgets.conf file from the widgets_obs array.
#
proc writeWidgetsConf { } {
    global CONFDIR widgets_obs
    set confname "$CONFDIR/widgets.conf"
    if { [catch { set f [open "$confname" w] } ] } {
	puts "***Warning: could not write widgets file: $confname"
	return
    }

    set header "# widgets.conf: CORE Observer Widgets customization file."
    puts $f $header
    foreach w [lsort -integer [array names widgets_obs]] {
	puts $f "$w { $widgets_obs($w) }"
    }
    close $f
}

# handle the move up/down buttons for the canvas selection window
proc manageCanvasUpDown { w dir } {
    global widgets_obs last_obswidget_selected
    # get the currently selected item
    set i [$w.s.servers get $last_obswidget_selected]
    if {$i < 0} { return }
    set i [lindex $i 0]
    set item [$w.cl get $i]

    if {$dir == "down" } {
        set max [expr {[llength $canvas_list] - 1}]
    	if {$i >= $max } { return }
	set newi [expr {$i + 1}]
    } else {
    	if {$i <= 0} { return }
	set newi [expr {$i - 1}]
    }

    # change the position
    $w.cl delete $i
    $w.cl insert $newi $item
    $w.cl selection set $newi
    $w.cl see $newi

    # update hidden list of canvas numbers
    set new_canvas_list [$w.list cget -text]
    set item [lindex $new_canvas_list $i]
    set new_canvas_list [lreplace $new_canvas_list $i $i]
    set new_canvas_list [linsert $new_canvas_list $newi $item]
    $w.list configure -text $new_canvas_list
}

# add/modify/remove server in list
proc configObsWidgetsHelper { wi action } {
    global widgets_obs last_obswidget_selected
    set index end
    set arrindex [expr {[array size widgets_obs] + 1}] ;#  index for new items

    # delete from list, array
    if { $action > 1 } { ;# delete/modify
	if { $last_obswidget_selected < 0 } { return }
	if { $action > 3 } { ;# move up/down
	    if { $action == 4 && $last_obswidget_selected == 0 } { return }
	    if { $action == 5 && $last_obswidget_selected > \
		 [expr {[array size widgets_obs] - 2}] } { return }
	}
	set server [$wi.s.servers get $last_obswidget_selected]
	$wi.s.servers delete $last_obswidget_selected
	# listbox index 0 item is array item 1
	set index $last_obswidget_selected
	set arrindex [expr { $last_obswidget_selected + 1 }]
	array unset widgets_obs $arrindex
	set oldarrindex $arrindex
	if { $action == 3 } { ;# delete
	    $wi.c.c3.add configure -state normal
	    return
	} elseif { $action == 4 } { ;# move up
	    incr index -1
	    incr arrindex -1
	} elseif { $action == 5 } { ;# move down
	    incr index
	    incr arrindex
	}
    }

    # new widget item
    set newwidget [$wi.c.c.name get]
    $wi.s.servers insert $index $newwidget
    # update the array
    set cmd [$wi.c.c2.cmd get]
    if { $action > 3 } {
	# move widgets_obs(arrindex) to widgets_obs(oldarrindex)
	set tmp $widgets_obs($arrindex)
	array set widgets_obs [list $oldarrindex $tmp]
    }
    array set widgets_obs [list $arrindex [list $newwidget $cmd]]
    # update the list
    $wi.s.servers selection set $index
    set last_obswidget_selected $index
    $wi.c.c3.add configure -state disabled
}

# connects the widgets listbox with entry elements
proc selectObsWidgetConf { wi } {
    global widgets_obs last_obswidget_selected
    set selected [$wi.s.servers curselection]

    # clear entries
    $wi.c.c.name delete 0 end 
    $wi.c.c2.cmd delete 0 end

    set w [$wi.s.servers get $selected]
    set si -1
    foreach i [array names widgets_obs] {
	if { [lindex $widgets_obs($i) 0] == $w } { set si $i; break }
    }
    if { $si < 0 } { return }
    $wi.c.c3.add configure -state disabled
    set last_obswidget_selected $selected

    # insert entries from array
    $wi.c.c.name insert 0 [lindex $widgets_obs($si) 0]
    $wi.c.c2.cmd insert 0 [lindex $widgets_obs($si) 1]
}

proc resetObsWidgets {} {
    set m "Reset to the default list of Observer Widgets?"
    set m "$m\nYou will lose any custom widgets."
    set choice [tk_messageBox -type yesno -default no -icon warning -message $m]
    if { $choice == "no" } { return }

    init_default_widgets_obs
    init_widget_obs_menu
    configObsWidgets
}

proc exec_observer_callback { node execnum cmd result status } {
    set c .c
    if { $result == "" } { return }
    floatingInfo $c $node $result
}


################################################################################
#####                                                                      #####
#####                         Throughput Widget                            #####
#####                                                                      #####
################################################################################

array set thruConfig { show 1 avg 1 thresh 250.0 width 10 color #FF0000 }

# netgraph names of pipe nodes
array set throughput_cache { }

#
# Throughput widget config dialog
#
proc widget_thru_config {} {
    set wi .thru_config
    catch {destroy $wi}
    toplevel $wi

    wm transient $wi .
    wm resizable $wi 0 0
    wm title $wi "Throughput config"
    global thruConfig

    # Show throughput
    frame $wi.tlab -borderwidth 4
    checkbutton $wi.tlab.show_thru \
	-text "Show throughput label on every link" -variable thruConfig(show)
    checkbutton $wi.tlab.avg \
	-text "Use exponentially weighted moving average" \
	-variable thruConfig(avg)
    pack $wi.tlab.show_thru $wi.tlab.avg -side top -anchor w -padx 4 
    pack $wi.tlab -side top

    frame $wi.msg -borderwidth 4
    global systype
    if { [lindex $systype 0] == "FreeBSD" } {
	set lab1txt "Note: links with no impairments (bw, delay,\netc) "
	set lab1txt "${lab1txt}will display 0.0 throughput"
    } else {
	set lab1txt ""
    }
    label $wi.msg.lab1 -text $lab1txt
    pack $wi.msg.lab1 -side top -padx 4 -pady 4
    pack $wi.msg -side top

    labelframe $wi.hi -padx 4 -pady 4 -text "Link highlighting"
    
    # Threshold (set to zero to disable)
    label $wi.hi.lab1 -text \
    	"Highlight link if throuhgput exceeds this "
    pack $wi.hi.lab1 -side top -anchor w
    frame $wi.hi.t
    label $wi.hi.t.lab1 -text "threshold (0 for disabled):"
    entry $wi.hi.t.thresh -bg white -width 8 -textvariable thruConfig(thresh)
    label $wi.hi.t.lab2 -text "kbps"
    pack $wi.hi.t.lab2 $wi.hi.t.thresh $wi.hi.t.lab1 -side right -padx 4 -pady 4
    pack $wi.hi.lab1 $wi.hi.t -side top
    scale $wi.hi.threshscale -from 0.0 -to 1000.0 -orient horizontal \
    	-showvalue false -sliderrelief raised -variable thruConfig(thresh)
    pack $wi.hi.threshscale -side top -fill x
   
    frame $wi.hi.w
    label $wi.hi.w.lab3 -text "Highlight link width:"
    spinbox $wi.hi.w.width -bg white -width 8 -textvariable thruConfig(width) \
    	-from 0 -to 40
    pack $wi.hi.w.width $wi.hi.w.lab3 -side right -padx 4 -pady 4
    pack $wi.hi.w -side top

    frame $wi.hi.co -borderwidth 4
    label $wi.hi.co.lab1 -text "Highlight color:"
    set color $thruConfig(color)
    label $wi.hi.co.color -fg black -bg $color -text $color
    button $wi.hi.co.colbtn -text "Color..." -command \
	"popupColor bg $wi.hi.co.color true"
    pack $wi.hi.co.colbtn $wi.hi.co.color $wi.hi.co.lab1 \
    	-side right -padx 4 -pady 4
    pack $wi.hi.co -side top
    
    pack $wi.hi -side top

    # OK button at bottom
    frame $wi.butt -borderwidth 6
    button $wi.butt.apply -text "OK" -command "widget_thru_config_apply $wi"
    pack $wi.butt.apply -side right
    pack $wi.butt -side bottom
    bind $wi <Key-Escape> "destroy $wi"
    bind $wi <Key-Return> "destroy $wi"
    after 100 {
	catch { grab .thru_config }
    }
}

proc widget_thru_config_apply { wi } {
    # this is needed because label textvariable won't update
    global thruConfig
    set thruConfig(color) [$wi.hi.co.color cget -bg]
    destroy $wi
}

#
# Throughput widget de/initialization
#
proc widget_thru_init {command} {
    global showLinkLabels enable_Throughput g_execRequests
    global link_thru_stats link_thru_avg_stats link_thru_last_time

    array set g_execRequests { thru "" }
    array set link_thru_stats {}
    array set link_thru_avg_stats {}
    set link_thru_last_time [clock clicks -milliseconds]
    # Initialize
    if { $enable_Throughput } {
	set showLinkLabels 1
	foreach object [.c find withtag linklabel] {
	    .c itemconfigure $object -state normal
	}
	if { $command != "stop" } {
	    widget_thru_init_cache
	}
    }

    # De-initialize
    if { !$enable_Throughput || $command == "stop" } {
	global link_list
        foreach link $link_list {
	    set lnode1 [lindex [linkPeers $link] 0]
	    set lnode2 [lindex [linkPeers $link] 1]
	    updateLinkLabel $link
	    set width [getLinkWidth $link]
	    .c itemconfigure "link && $link" -width $width

	    if { [nodeType $lnode1] == "wlan" } {
		.c delete -withtag "$lnode2 && rangecircles"
	    }
	}
    }
}

# build an array of netgraph IDs of pipe nodes, using node/interface
# names as the key
proc widget_thru_init_cache { } {
    global throughput_cache systype
    if { [lindex $systype 0] == "Linux" } { return }

    array unset throughput_cache *
    set ngctlout [nexec localnode sudo ngctl l]
    foreach ngctlline [split $ngctlout "\n"] {
	set ngtype [lindex $ngctlline 3]
	if { $ngtype != "pipe" } { continue }
	set ngname [lindex $ngctlline 1]
	if { $ngname == "<unnamed>" } { continue }
	set ngpipeout [split [nexec localnode sudo ngctl show $ngname:] "\n"]
	set if1 [ngctl_output_to_ifname [lindex $ngpipeout 3]]
	set if2 [ngctl_output_to_ifname [lindex $ngpipeout 4]]
	array set throughput_cache [list $if1 $ngname]
	array set throughput_cache [list $if2 $ngname]
    }
}

# helper to convert a line from 'ngctl show' output into an interface name
proc ngctl_output_to_ifname { line } {
    set ngname [lindex $line 1]
    # chop off "_148" portion of "n2_0_148"
    set i [string last "_" $ngname]
    if { $i < 0 } { return $ngname }
    incr i -1
    set name [string range $ngname 0 $i]
    return $name
}

#
# Throughput widget periodic procedure
#
proc widget_thru_periodic { now } {
    global systype eid link_list 
    global link_thru_stats link_thru_avg_stats link_thru_last_time thruConfig
    global throughput_cache

    set alpha 0.4

    # get the number of seconds elapsed since we were last here
    set dt [expr { ($now - $link_thru_last_time)/1000.0 }]
    set link_thru_last_time $now
    if { $dt <= 0.0 } { return }
    
    # keep wireless stats in an array
    array set wireless_stats {}

    # TODO: use CORE API so we don't need to read the local filesystem to
    #       retrieve the interface statistics; also a publish/subscribe model
    #       may be better than this periodic polling
    if { [lindex $systype 0] == "Linux" } {
	# read /proc/net/dev
	if { [catch {set f [open "/proc/net/dev" r]} e] } {
	    puts "error opening /proc/net/dev: $e"
	    return
	}
	set stats [read $f]
	close $f
	set stats [split $stats "\n"]
    }

    foreach link $link_list {
	set lnode1 [lindex [linkPeers $link] 0]
	set lnode2 [lindex [linkPeers $link] 1]
	set if1n [string range [ifcByPeer $lnode1 $lnode2] 3 end]
	set if2n [string range [ifcByPeer $lnode2 $lnode1] 3 end]
	set key "${lnode1}_${if1n}-${lnode2}_${if2n}"

	# get stats from /proc/dev/net that we already read
	if { [lindex $systype 0] == "Linux" } {
	    set ifname [getstats_link_ifname $link]
	    set bytes [getstats_bytes_proc $stats $ifname]

	# read stats per link from Netgraph pipes
	} else {
	    set cache_key "${lnode1}_${if1n}"
	    if { ![info exists throughput_cache($cache_key)] } {
		puts "throughput: skipping link $link ($cache_key)"; continue;
	    }
	    set ngname $throughput_cache($cache_key)
	    set stats [nexec $lnode1 sudo ngctl msg $ngname: getstats]
	    set bytes [getstats_bytes_netgraph $stats]
	}

	# init new stats bucket
	if { ![info exists link_thru_stats($key)] } {
	    set link_thru_stats($key) $bytes
	    continue
	}
	set bytes2 $link_thru_stats($key)
	set link_thru_stats($key) $bytes

	# convert to kilobits per second
	set div [expr { (1000.0 / 8.0) * $dt }]
	set kbps_down [expr { ([lindex $bytes 0]-[lindex $bytes2 0]) / $div }]
	set kbps_up [expr { ([lindex $bytes 1]-[lindex $bytes2 1]) / $div }]
	set kbps [expr {$kbps_down + $kbps_up}]
	
	if { $thruConfig(avg) } {
	    if { ![info exists link_thru_avg_stats($key)] } {
		set link_thru_avg_stats($key) $kbps
	    } else {
		set s2 $link_thru_avg_stats($key)
		set s [expr {($alpha*$kbps) + (1.0-$alpha)*$s2}]
		set link_thru_avg_stats($key) $s
		set kbps $s
	    }
	}
	set kbps_str [format "%.3f" $kbps] 

	# wireless link - keep total of wireless throughput for this node
	#   (supports membership to multiple wlans)
	if { [nodeType $lnode1] == "wlan" } {
	    if {![info exists wireless_stats($lnode2)]} {
	        set wireless_stats($lnode2) 0
	    }
	    set wireless_stats($lnode2) [expr {$kbps+$wireless_stats($lnode2)}]
	# normal wired links
	} else {
	    if { $thruConfig(thresh) > 0.0 && \
	         $kbps_str > $thruConfig(thresh) } {
	        set width $thruConfig(width)
		set color $thruConfig(color)
	    } else {
	    	set width [getLinkWidth $link]
		set color [getLinkColor $link]
	    }
	    if { $thruConfig(show) } {
		.c itemconfigure "linklabel && $link" -text "$kbps_str kbps"
	    }
	    .c itemconfigure "link && $link" -width $width -fill $color
	}
    }; # end foreach link

    # after summing all wireless link bandwidths, go back and perform
    # highlighting and label updating
    foreach node [array names wireless_stats] {
	set kbps_str [format "%.3f" $wireless_stats($node)]
    
	# erase any existing circles (otherwise we get duplicates)
	.c delete -withtag "$node && rangecircles"
	# wireless circle if exceeding threshold
	if { $thruConfig(thresh) > 0.0 && $kbps_str > $thruConfig(thresh) } {
	    	global zoom
		#set radius [expr {$zoom * [getNodeRange $lnode1]/2}]
		set radius [expr {$zoom * 45.0}]
	    	set coords [getNodeCoords $node]
		set x [expr {[lindex $coords 0] * $zoom}]
		set y [expr {[lindex $coords 1] * $zoom}]
		set x1 [expr $x - $radius]
		set y1 [expr $y - $radius]
		set x2 [expr $x + $radius]
		set y2 [expr $y + $radius]
		set newcircle [.c create oval $x1 $y1 $x2 $y2 \
			-width 4 -outline $thruConfig(color) -dash {10 4} \
			-tags "$node circle rangecircles"]
	}
	# wireless kbps label
	if { $thruConfig(show) } {
	    global zoom
	    set coords [getNodeCoords $node]
	    set x [expr {([lindex $coords 0] + 55) * $zoom}]
	    set y [expr {([lindex $coords 1] + 10) * $zoom}]
	    set newtext [.c create text $x $y -justify center -fill black \
			    -text "$kbps_str kbps" -tags "$node rangecircles"]
	}
    }; # end foreach wireless node

}

# helper to convert ng_pipe stats into upstream/downstream bytes
proc getstats_bytes_netgraph { raw_input } {
    # Rec'd response "getstats" (1) from "e0_n0-n1:":
    # Args:   { downstream={ FwdOctets=416 FwdFrames=6 } 
    #           upstream={ FwdOctets=416 FwdFrames=6 } }
    set tmp [split $raw_input ":"]
    if { [llength $tmp] != 4 } {
    	return [list 0 0]
    }
    
    set statline [lindex [lindex $tmp 3] 0]
    set down [lindex $statline 1]
    set up [lindex $statline 5]
    # downstream FwdOctets
    set down_bytes [lindex [split $down "="] 1]
    # upstream FwdOctets
    set up_bytes [lindex [split $up "="] 1]

    if { $down_bytes == "" } { set down_bytes 0 }
    if { $up_bytes == "" } { set up_bytes 0 }

    return [list $down_bytes $up_bytes]
}

proc getstats_link_ifname { link } {
    set lnode1 [lindex [linkPeers $link] 0]
    set lnode2 [lindex [linkPeers $link] 1]

    # choose the interface name
    set node_num -1
    if { [[typemodel $lnode1].layer] == "NETWORK" } {
	set node_num [string range $lnode1 1 end]
	set ifname [ifcByPeer $lnode1 $lnode2]
    } elseif { [[typemodel $lnode2].layer] == "NETWORK" } {
	set node_num [string range $lnode2 1 end]
	set ifname [ifcByPeer $lnode2 $lnode1]
    }
    if { $node_num < 0 } { return "" }

    set emulp [getEmulPlugin n$node_num]
    if { [lindex $emulp 1] == "cored.py" } {
	# TODO: need to determine session number used by cored.py
	#       instead this uses a '*' character for a regexp match against
	#       the interfaces in /proc/net/dev
	set ifname "n$node_num\\.$ifname\\.*"
    } else {
        incr node_num 1000
        set ifnum [string range $ifname 3 end]
        set ifname veth$node_num.$ifnum
    }
    return $ifname
}

# helper to convert /proc/net/dev stats into upstream/downstream bytes
proc getstats_bytes_proc { raw_input ifname } {
    set ifname_len [string length $ifname]

    foreach statline $raw_input {
	# when ifname ends with '*' treat it as a regular expression
	if { [string index $ifname end] == "*" } {
	    set statifname [lindex [split $statline ":"] 0]
	    if { [regexp $ifname $statifname] } {
		break
	    }
	# match the ifname exactly
	} elseif { [string range $statline 0 $ifname_len] == "$ifname:" } { 
	    break 
	}
	set statline ""
    }

    # statline looks like: "veth1004.1:134998400  101150    0   ..."
    # store the numbers into stats
    set statline [split $statline ":"]
    set stats [lindex $statline 1]

    set down_bytes [lindex $stats 0]
    set up_bytes [lindex $stats 8] 
    
    if { $down_bytes == "" } { set down_bytes 0 }
    if { $up_bytes == "" } { set up_bytes 0 }

    return [list $down_bytes $up_bytes]
}

# Node movement for throughput widget
proc widget_thru_move { c node done } {
    $c delete -withtag "$node && rangecircles"
}

################################################################################
#####                                                                      #####
#####                              CPU Widget                              #####
#####                                                                      #####
################################################################################

array set cpuConfig { show 1 loc lr thresh 75.0 radius 30 color #FFFF00 }

#
# CPU widget config dialog
#
proc widget_cpu_config {} {
    set wi .cpu_config
    catch {destroy $wi}
    toplevel $wi

    wm transient $wi .
    wm resizable $wi 0 0
    wm title $wi "CPU config"
    global cpuConfig

    # Show CPU
    labelframe $wi.disp -text "CPU Display Options"
    frame $wi.disp.tlab -borderwidth 4
    checkbutton $wi.disp.tlab.show_cpu \
	-text "Show CPU usage label on every node" -variable cpuConfig(show)
    pack $wi.disp.tlab.show_cpu -side right -padx 4 -pady 4
    pack $wi.disp.tlab -side top
    frame $wi.disp.loc -borderwidth 4
    label $wi.disp.loc.lab -text "Location of CPU label:"
    radiobutton $wi.disp.loc.a -text "upper-left" -variable cpuConfig(loc) \
    	-value ul
    radiobutton $wi.disp.loc.b -text "upper-right" -variable cpuConfig(loc) \
    	-value ur
    radiobutton $wi.disp.loc.c -text "lower-left" -variable cpuConfig(loc) \
    	-value ll
    radiobutton $wi.disp.loc.d -text "lower-right" -variable cpuConfig(loc) \
    	-value lr
    pack $wi.disp.loc.lab -side top
    pack $wi.disp.loc.a $wi.disp.loc.b -side left -anchor n
    pack $wi.disp.loc.c $wi.disp.loc.d -side left -anchor s
    pack $wi.disp.loc -side top

    pack $wi.disp -side top -fill x


    labelframe $wi.hi -padx 4 -pady 4 -text "Node highlighting"
    
    # Threshold (set to zero to disable)
    label $wi.hi.lab1 -text "Highlight node if CPU usage exceeds this "
    pack $wi.hi.lab1 -side top -anchor w
    frame $wi.hi.t
    label $wi.hi.t.lab1 -text "threshold (0 for disabled):"
    entry $wi.hi.t.thresh -bg white -width 8 -textvariable cpuConfig(thresh)
    label $wi.hi.t.lab2 -text "% CPU"
    pack $wi.hi.t.lab2 $wi.hi.t.thresh $wi.hi.t.lab1 -side right -padx 4 -pady 4
    pack $wi.hi.lab1 $wi.hi.t -side top
  
    # Highlight color/width
    frame $wi.hi.w
    label $wi.hi.w.lab3 -text "radius:"
    spinbox $wi.hi.w.width -bg white -width 8 -textvariable cpuConfig(radius) \
    	-from 1 -to 150 -increment 5
    pack $wi.hi.w.width $wi.hi.w.lab3 -side right -padx 4 -pady 4

    label $wi.hi.w.lab1 -text "Highlight color:"
    set color $cpuConfig(color)
    label $wi.hi.w.color -fg black -bg $color -text $color
    button $wi.hi.w.colbtn -text "Color..." -command \
	"popupColor bg $wi.hi.w.color true"
    pack $wi.hi.w.colbtn $wi.hi.w.color $wi.hi.w.lab1 \
    	-side right -padx 4 -pady 4
    pack $wi.hi.w -side top
    
    pack $wi.hi -side top -fill x

    # OK button at bottom
    frame $wi.butt -borderwidth 6
    button $wi.butt.apply -text "OK" -command "widget_cpu_config_apply $wi"
    pack $wi.butt.apply -side right
    pack $wi.butt -side bottom
    bind $wi <Key-Escape> "destroy $wi"
    bind $wi <Key-Return> "destroy $wi"
    after 100 {
	catch { grab .cpu_config }
    }
}

proc widget_cpu_config_apply { wi } {
    # this is needed because label textvariable won't update
    global cpuConfig
    set cpuConfig(color) [$wi.hi.w.color cget -bg]
    destroy $wi
}

#
# CPU widget de/initialization
#
proc widget_cpu_init {command} {
    global enable_CPU systype g_execRequests

    array set g_execRequests { cpu "" }

    # Initialize
    if { $enable_CPU } {
    }

    # De-initialize
    if { !$enable_CPU || $command == "stop" } {
	.c delete -withtag "cpulabel || cpuhi"
    }
}

#
# CPU widget periodic procedure
#
proc widget_cpu_periodic { now } {
    global systype

    set emulp [getEmulPlugin "*"]
    if { [lindex $emulp 1] == "cored.py" } {
	puts "warning: the CPU widget is not functional for this platform yet"
	return
    }
    if { [lindex $systype 0] == "Linux" } {
	widget_cpu_periodic_openvz $now
    } else {
	widget_cpu_periodic_vimage $now
    }
}

proc widget_cpu_periodic_vimage { now } {
    global eid node_list cpuConfig zoom

    # TODO: collect from all exec hosts
    set vimageout [nexec localnode vimage -l]
    array set cpustats [getstats_cpu_vimage $vimageout]

    foreach node $node_list {
	# this skips all nodes that are not vimages
    	if { ![info exists cpustats($eid\_$node)] } { continue }

	set newtext [format "%.2f %%" $cpustats($eid\_$node)]
	set coords [getCPUcoords $node]
	set x [lindex $coords 0] 
	set y [lindex $coords 1] 
	set basex [lindex $coords 2] 
	set basey [lindex $coords 3] 

	set existing [.c find withtag "cpulabel && $node"]
	if { [llength $existing] == 0 } { ;# create new label
	    set cpulabel [.c create text $x $y -text $newtext \
	    			-tags "cpulabel && $node"]
	} else { ;# use existing label
	    set cpulabel [lindex $existing 0]
	    .c itemconfigure $cpulabel -text $newtext
	}
	.c raise $cpulabel
	# perform highlighting 
	set existing [.c find withtag "cpuhi && $node"]
	if { $cpustats($eid\_$node) >= $cpuConfig(thresh) } {
	    if { [llength $existing] == 0 } {
	    	set color $cpuConfig(color)
	    	set rad $cpuConfig(radius)
	    	set cpuhi [.c create oval [expr {$basex - $rad}] \
			[expr {$basey - $rad}] [expr {$basex + $rad}] \
			[expr {$basey + $rad}] -fill $color -outline $color \
			-tag "cpuhi $node" ]
		.c raise $cpulabel
		#.c raise "link && $node"
		.c raise "node && $node"
	    }
	    
	} elseif { [llength $existing] > 0 } {
	    .c delete $existing
	}
	.c raise floatinfo;# fix observer widget raise order
    }

}

proc widget_cpu_periodic_openvz { now } {
    global eid node_list cpuConfig zoom

    array set cpustats [getstats_cpu_vestat]

    foreach node $node_list {
	# this skips all nodes that are not vimages
	set node_num [expr { 1000 +  [string range $node 1 end] }]
    	if { ![info exists cpustats($node_num)] } { continue }

	set newtext [format "%.2f %%" $cpustats($node_num)]
	set coords [getCPUcoords $node]
	set x [lindex $coords 0] 
	set y [lindex $coords 1] 
	set basex [lindex $coords 2] 
	set basey [lindex $coords 3] 

	set existing [.c find withtag "cpulabel && $node"]
	if { [llength $existing] == 0 } { ;# create new label
	    set cpulabel [.c create text $x $y -text $newtext \
	    			-tags "cpulabel && $node"]
	} else { ;# use existing label
	    set cpulabel [lindex $existing 0]
	    .c itemconfigure $cpulabel -text $newtext
	}
	.c raise $cpulabel
	# perform highlighting 
	set existing [.c find withtag "cpuhi && $node"]
	if { $cpustats($node_num) >= $cpuConfig(thresh) } {
	    if { [llength $existing] == 0 } {
	    	set color $cpuConfig(color)
	    	set rad $cpuConfig(radius)
	    	set cpuhi [.c create oval [expr {$basex - $rad}] \
			[expr {$basey - $rad}] [expr {$basex + $rad}] \
			[expr {$basey + $rad}] -fill $color -outline $color \
			-tag "cpuhi $node" ]
		.c raise $cpulabel
		.c raise "node && $node"
	    }
	    
	} elseif { [llength $existing] > 0 } {
	    .c delete $existing
	}
	.c raise floatinfo;# fix observer widget raise order
    }

}

# helper to return x,y of CPU label based on config
proc getCPUcoords { node } {
    global cpuConfig zoom

    set coords [getNodeCoords $node]
    set basex [lindex $coords 0]
    set basey [lindex $coords 1]
    switch -exact $cpuConfig(loc) {
    ul { set xoff -25; set yoff -25 }
    ur { set xoff 25; set yoff -25 }
    ll { set xoff -25; set yoff 25 }
    lr { set xoff 25; set yoff 25 }
    }
    set x [expr { ([lindex $coords 0] + $xoff) * $zoom }]
    set y [expr { ([lindex $coords 1] + $yoff) * $zoom }]
    return [list $x $y $basex $basey]
}

# helper to convert `vimage -l` output to node_name/cpu list
proc getstats_cpu_vimage { raw_input} {
    set tmp [split $raw_input "\n"]
    set numlines [llength $tmp]
    if { $numlines <= 4 } {
    	return [list 0 0]
    }
  
    # add node_name/cpu to a list
    set ret {}
    set i 0
    set node_name ""
    while { $numlines > 0 } {
	set line [lindex $tmp $i]
	incr i
        if { $node_name == "" } {
	    if { [string range $line 0 3] != "    " } {
		set node_name [lindex [split $line \"] 1]
		lappend ret $node_name
	    }
	} elseif { [string range $line 0 6] == "    CPU" } {
	    set cpu [lindex [split $line :] 1]
	    set cpu [string trim $cpu " %"]
	    lappend ret $cpu
	    set node_name ""
	}
	incr numlines -1
    }

    return $ret
}

# helper to convert /proc/vz/vestat output to node_name/cpu list
proc getstats_cpu_vestat { } {
    global cpu_vestat_history; # remember previous jiffies
    set Hertz 100.0; # from <asm/param.h>, varies per architecture

    # read /proc/vz/vestat    
    if { [catch {set f [open "/proc/vz/vestat" r]} e] } {
	puts "error opening /proc/vz/vestat: $e"
	return
    }
    set vestat [read $f]
    close $f
    set lines [split $vestat "\n"]
    if { [llength $lines] <= 2 } {
    	return [list 0 0]
    }

    # read /proc/uptime
    if { [catch {set f [open "/proc/uptime" r]} e] } {
	puts "error opening /proc/uptime: $e"
	return
    }
    set uptime [read $f]
    close $f
    set uptime_now [lindex $uptime 1]
    if { ![info exists cpu_vestat_history(uptime)] } {
	set uptime_old $uptime_now
    } else {
	set uptime_old $cpu_vestat_history(uptime)
    }
    array set cpu_vestat_history [list uptime $uptime_now]
    set elapsed [expr {$uptime_now - $uptime_old}]
    if { $elapsed == 0.0 } { set elapsed 1.0 }; # don't divide by zero
   
  
    # add node_name/cpu to a list
    set ret {}
    for { set i 0 } { $i < [llength $lines] } { incr i } {
	set line [lindex $lines $i]
	set node_num [lindex $line 0]
	# skip text lines
	if { $node_num == "" } { continue }
	if { ![string is integer $node_num] } { continue }

	set user [lindex $line 1]
	set nice [lindex $line 2]
	set system [lindex $line 3]

	set jiffies_now [expr {$user+$nice+$system}]
	if { ![info exists cpu_vestat_history($node_num)] } {
	    set jiffies_old $jiffies_now
	} else {
	    set jiffies_old $cpu_vestat_history($node_num)
	}
	array set cpu_vestat_history [list $node_num $jiffies_now]
	# s = j / hz
	set cpu [expr { ($jiffies_now - $jiffies_old)  / ($Hertz * $elapsed) }]
	#puts "num=$node_num  user=$user nice=$nice sys=$system cpu=$cpu"
	lappend ret $node_num
	lappend ret $cpu
    }

    return $ret
}

# Node movement for CPU widget
proc widget_cpu_move { c node done } {
    $c delete -withtag "cpulabel && $node"
    $c delete -withtag "cpuhi && $node"
}

################################################################################
#####                                                                      #####
#####                           Adjaceny Widget                            #####
#####                                                                      #####
################################################################################

array set adjacency_config { proto "ipv6 ospf6" offset 1 colors \
			      { Down black Init yellow Twoway green \
				ExChan red Loadin orange Full blue \
				default gray } }
array set adjacency_cache { }

#
# Adjacency widget config dialog
#
proc widget_adjacency_config {} {
    set wi .adj_config
    catch {destroy $wi}
    toplevel $wi

    wm transient $wi .
    wm resizable $wi 0 0
    wm title $wi "Adjacency config"
    global adjacency_config

    labelframe $wi.po -text "Protocol options"
    frame $wi.po.p -borderwidth 4
    label $wi.po.p.help -text "Show adjacencies for:"
    radiobutton $wi.po.p.pr -text "OSPFv2" -variable adjacency_config(proto) \
	-value "ip ospf" -command ".c delete -withtags adjline"
    radiobutton $wi.po.p.pr2 -text "OSPFv3" -variable adjacency_config(proto) \
    	-value "ipv6 ospf6" -command ".c delete -withtags adjline"
    pack $wi.po.p.help -side top
    pack $wi.po.p.pr $wi.po.p.pr2 -side left -padx 4 -pady 4
    pack $wi.po.p $wi.po -side top -fill x

    labelframe $wi.do -text "Display options"
    frame $wi.do.d
    checkbutton $wi.do.d.offset -text "slightly offset adjaency lines" \
	-variable adjacency_config(offset) \
	-command ".c delete -withtags adjline"
    pack $wi.do.d.offset -side left
    pack $wi.do.d -side top -fill x

    # configurable state colors
    frame $wi.do.c
    array set colors $adjacency_config(colors)
    foreach adj [lsort -dictionary [array names colors]] {
	frame $wi.do.c.c$adj
	label $wi.do.c.c$adj.lab -text "$adj"
	set color $colors($adj)
	label $wi.do.c.c$adj.col -fg black -bg $color -text $color
	pack $wi.do.c.c$adj.lab $wi.do.c.c$adj.col -side left -fill x
	pack $wi.do.c.c$adj -side top -anchor w
	bind $wi.do.c.c$adj.col \
		<Button-1> "popupColor bg $wi.do.c.c$adj.col true"
    }
    pack $wi.do.c -side top
    pack $wi.do -side top -fill x

    # OK button at bottom
    frame $wi.butt -borderwidth 6
    button $wi.butt.apply -text "OK" \
	 -command "widget_adjacency_config_apply $wi"
    pack $wi.butt.apply -side right
    pack $wi.butt -side bottom
    bind $wi <Key-Escape> "destroy $wi"
    bind $wi <Key-Return> "destroy $wi"
    after 100 {
	catch { grab .cpu_config }
    }

}

proc widget_adjacency_config_apply { wi } {
    global adjacency_config
    set changed 0
    array set colors $adjacency_config(colors)
    foreach adj [array names colors] {
	set color $colors($adj)
	set newcolor [$wi.do.c.c$adj.col cget -text]
	if { $color != $newcolor } {
	    array set colors [list $adj $newcolor]
	    set changed 1
	}
    }

    if { $changed } {
	set adjacency_config(colors) [array get colors]
	.c delete -withtags "adjline"
    }
    destroy $wi
}

proc get_router_id {node} {
    global oper_mode

    # search custom-config
    if { [getCustomEnabled $node] == true } {
	set rid_string [regexp -inline \
			    {router-id [0-9]+\.[0-9]+\.[0-9]+\.[0-9]+} \
			    [getCustomConfig $node]]
	if {[string range $rid_string 1 9] == "router-id" } {
	    return [string range $rid_string 11 end-1]
	}
    }

    # search network config
    # search OSPFv3 config for router ID
    foreach line [netconfFetchSection $node "router ospf6"] {
	if {[string range $line 0 9] == " router-id"} {
	    return [string range $line 11 end]
	}
    }
    # search OSPFv2 config for router ID
    foreach line [netconfFetchSection $node "router ospf"] {
	if {[string range $line 0 9] == " router-id"} {
	    return [string range $line 11 end]
	}
    }

    if { $oper_mode != "exec" }  { return }

    # use exec message here for retrieving router ID
    set sock [lindex [getEmulPlugin $node] 2]
    set exec_num [newExecCallbackRequest adjacencyrouterid]
    set cmd "vtysh -c 'show ipv6 ospf6'"
    sendExecMessage $sock $node $cmd $exec_num 0x30
    set exec_num [newExecCallbackRequest adjacencyrouterid]
    set cmd "vtysh -c 'show ip ospf'"
    sendExecMessage $sock $node $cmd $exec_num 0x30
    return ""
}

#
# Adjacency widget de/initialization
#
proc widget_adjacency_init {command} {
    global enable_Adjacency enable_Adjacency_v2 enable_Adjacency_v3
    global node_list adjacency_cache adjacency_config adjacency_lock
    global g_execRequests
    set c .c

    set adjacency_lock 0
    array set g_execRequests [list adjacency ""]

    # Menu item selected on/off
    if { $command == "menu2" || $command == "menu3" } {
	# set global enable flag for v2/v3 adjacency display
	set enable_Adjacency \
	    [expr {$enable_Adjacency_v2 | $enable_Adjacency_v3}]
	# toggle other OSPFv2/v3 menu items off
	if { $command == "menu2" && $enable_Adjacency_v2 } {
	    set enable_Adjacency_v3 0
	    set adjacency_config(proto) "ip ospf"
	} elseif { $command == "menu3" && $enable_Adjacency_v3 } {
	    set enable_Adjacency_v2 0
	    set adjacency_config(proto) "ipv6 ospf6"
	}
    }

    # Initialize
    if { $enable_Adjacency && $command != "stop" } {
	array unset adjacency_cache *
	foreach node $node_list { ;# save router-id node pairs for later lookup
	    if { [nodeType $node] != "router" } { continue }
	    if {[lsearch {router mdr} [getNodeModel $node]] < 0} {
		continue
	    }
	    set rtrid [get_router_id $node]
	    if {$rtrid != ""} {
		array set adjacency_cache [list $rtrid $node]
	    }
	} ;# end foreach node
    }

    # De-initialize
    if { !$enable_Adjacency || $command == "stop" } {
	set enable_Adjacency 0
	set enable_Adjacency_v2 0
	set enable_Adjacency_v3 0
	$c delete -withtags "adjline"
	after 200 { .c delete -withtags "adjline" }
    }
}

#
# Adjacency widget periodic procedure
#
proc widget_adjacency_periodic { now } {
    global node_list adjacency_config adjacency_cache adjacency_lock
    global enable_Adjacency
    set changed 0

    set proto $adjacency_config(proto)

    foreach node $node_list {
	if { [nodeType $node] != "router" } { continue }
	if {[lsearch {router mdr} [getNodeModel $node]] < 0} {
	    continue
	}

	if { $adjacency_lock == $node } { continue }
	# when using cored.py, send Execute Message and draw line using
	# widget_adjacency_callback after the response has been received
	set sock [lindex [getEmulPlugin $node] 2]
	set exec_num [newExecCallbackRequest adjacency]
	set cmd "vtysh -c 'show $proto neighbor'"
	sendExecMessage $sock $node $cmd $exec_num 0x30
    }
}

# Execute Message callback
proc exec_adjacency_callback { node execnum cmd result status } {
    global eid node_list adjacency_config adjacency_cache adjacency_lock
    global enable_Adjacency
    global g_api_exec_num
    set changed 0
    set c .c

    set proto $adjacency_config(proto)
    array set colors $adjacency_config(colors)
    if { $adjacency_config(offset) } { set o 5 } else { set o 0 }

    $c addtag adjdelete withtag "adjline && $node" ;# flag del all adjlines 
    set adjs [getadj_from_neighbors $result $proto]
    foreach adj $adjs {
	    set peer [lindex $adj 0]
	    set line [$c find withtag "adjline && $node && $peer"]

	    if { ![info exists adjacency_cache($peer)] } {
		puts "adjacency: node $node skipping $peer"; continue;
	    }

	    # change color of the line based on adjacency state
	    set adjstate [lindex $adj 1]
	    if { ![info exists colors($adjstate)] } {
		set color $colors(default)
	    } else {
		set color $colors($adjstate)
	    }

	    if { $line == "" } {;	# draw a half line if none
	        set coords [getNodeCoords $node]
		set node2 $adjacency_cache($peer)
		if { $adjacency_lock == $node2 } { continue }
		set coords2 [getNodeCoords $node2]
		set x [lindex $coords 0]; set y [lindex $coords 1]
		set x2 [lindex $coords2 0]; set y2 [lindex $coords2 1]
		# these tags are later used in widget_adjacency_move()
		set a [$c create line $x $y [expr {$o + $x + (($x2 - $x)/2) }] \
				     [expr {$o + $y + (($y2 - $y)/2) }] \
			 -fill $color -width 3 \
			 -tags "adjline $node $peer"]
		$c lower $a "node && $node"
	    } else {; 			# update existing half line
		$c itemconfigure $line -fill $color ;# update the color
		$c dtag $line "adjdelete" ;# don't delete this adjline
		$c lower $line "node && $node"
	    }
    }
    $c delete -withtags "adjdelete && $node" ;# delete stale adjlines
}

# Execute Message callback for getting the router ID
proc exec_adjacencyrouterid_callback { node execnum cmd result status } {
    global adjacency_cache

    # match both OSPFv2 and OSPFv3 responses
    set rid [regexp -inline {Router-ID[:]? [0-9]+\.[0-9]+\.[0-9]+\.[0-9]+} \
    		$result]
    if {$rid != ""} {
	set rtrid [eval lindex $rid 1]
	array set adjacency_cache [list $rtrid $node]
    }
}

# helper to convert neighbor list into adjacencies list
proc getadj_from_neighbors { raw_input proto } {
    set ret { }
#Neighbor ID     Pri    DeadTime  State/IfState         Duration I/F[State]
#10.0.0.2          1    00:00:06   Init/PointToPoint    00:00:00 eth0[PointToP
#10.0.0.2          1    00:00:06 Twoway/PointToPoint    00:00:00 eth0[PointToP
#10.0.0.2          1    00:00:06   Full/PointToPoint    00:00:38 eth0[PointToP
#10.0.7.2          1 Full/Backup       37.240s 10.0.0.2        eth0:10.0.0.1
    foreach line [split $raw_input "\n"] {
	set rtrid [string trim [string range $line 0 14]]
	if { $rtrid == "Neighbor ID" } { continue }
	set parts [split $rtrid .]
	if {[llength $parts] != 4} { continue }; # not in A.B.C.D format!

	if { $proto == "ipv6 ospf6" } { ;# string offsets depend on protocol
	    set state [string trim [string range $line 32 37 ]]
	} else { ;# ipv4
	    set state [string trim [string range $line 19 23 ]]
	    # convert some OSPFv2 states to OSPFv3 to simplify coloring
	    switch -exact -- "$state" {
	    "Dele" { set state "Down" }
	    "Atte" { set state "Init" }
	    "2-Wa" { set state "Twoway" }
	    "ExSt" { set state "ExChan" }
	    "Exch" { set state "ExChan" }
	    "Load" { set state "Loadin" }
	    }
	}
	lappend ret [list $rtrid $state]
    }
    return $ret
}

# Node movement for adjacency widget
proc widget_adjacency_move { c node done } {
    global adjacency_lock adjacency_config adjacency_cache
    set c .c

    if { $adjacency_config(offset) } { set o 5 } else { set o 0 }

    set adjacency_lock $node

    foreach line [$c find withtag "adjline && $node"] {
	set n1 [lindex [$c gettags $line] 1]
	set peer [lindex [$c gettags $line] 2]
	if { ![info exists adjacency_cache($peer)] } { continue }
	set n2 $adjacency_cache($peer)  ;# convert peer router ID to node
	set coords [getNodeCoords $n1]
	set coords2 [getNodeCoords $n2]
	set x [lindex $coords 0]; set y [lindex $coords 1]
	set x2 [lindex $coords2 0]; set y2 [lindex $coords2 1]
	$c coords $line $x $y [expr {$o + $x + (($x2 - $x)/2) }] \
			     [expr {$o + $y + (($y2 - $y)/2) }]
	$c lower $line "node && $n1"
	# move any half line coming from peer to this moved node
	foreach peerline [$c find withtag "adjline && $n2"] {
	    set peer2 [lindex [$c gettags $peerline] 2]
	    if { ![info exists adjacency_cache($peer2)] } { continue }
	    if { $adjacency_cache($peer2) == $node } {
		$c coords $peerline $x2 $y2 \
			[expr {$o + $x2 + (($x - $x2)/2) }] \
			[expr {$o + $y2 + (($y - $y2)/2) }]
		$c lower $peerline "node && $n2"
		break
	    }

	} ;# end foreach peerline
    } ;# end foreach line

    if { $done } { set adjacency_lock 0 }
}

#
# Build Adjacency Widget menu items
#
proc widget_adjacency_init_submenu { m } {
    global widgets
    menu $m.adj -tearoff 1
    $m add cascade -label "Adjacency" -menu $m.adj
    set w "Adjacency"

    foreach v [list 2 3] {
	global enable_${w}_v${v}
	set enable_${w}_v${v} 0
	$m.adj add checkbutton -label "OSPFv$v" -variable enable_${w}_v${v} \
		-command "[lindex $widgets($w) 1] menu$v"
    }
}

# load the widgets.conf file when this file is loaded
loadWidgetsConf
