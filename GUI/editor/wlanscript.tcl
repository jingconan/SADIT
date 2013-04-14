#
# Copyright 2005-2012 the Boeing Company.
# See the LICENSE file included in this distribution.
#

#
# run a scengen mobility script
proc wlanRunMobilityScript { wlan } {
    set scriptfile [lindex [netconfFetchSection $wlan scriptfile] 0]

    if { $scriptfile == "" } {
    	return
    }
    loadMobilityScript $wlan $scriptfile
}

#
# initialize global script array
proc initMobilityScriptVars { wlan } {
    global script_$wlan
    # array of initial coordinates for each node
    set script_${wlan}(coords,ID) ""
    # array of calculated speeds for each node
    set script_${wlan}(speeds,ID) ""
    # array of destination coordinates for each node
    set script_${wlan}(dcoords,ID) ""
    # list of destinations
    set script_${wlan}(dests) ""
    # index of current destination to process
    set script_${wlan}(dest_index) 0
    # clock time of when the script started
    set script_${wlan}(start_time) 0
    # the end time of the script
    set script_${wlan}(max_time) 0
    # clock time since last round was run in milliseconds
    set script_${wlan}(last_time) 0
    # resolution for timer firing in milliseconds
    set script_${wlan}(res) 50
    # clock time of last range calculation
    set script_${wlan}(last_calc) 0
    # simulated time -- tied to timescale widget
    set script_${wlan}(time) 0
    # tied to loop checkbox
    set script_${wlan}(loop) 1
    # tied to play/pause/stop buttons
    set script_${wlan}(state) init
}

#
# load mobility script file into a multi-dimensional global array
proc loadMobilityScript { wlan scriptfile } {
    global zoom
    if { $scriptfile == "" } {
    	return
    }
    set scriptfile [absPathname $scriptfile]
    if { [catch {set f [open "$scriptfile" r]}] } {
    	puts "***Warning: could not open script file '$scriptfile'"
	return
    }
    set c .c
    global script_$wlan
    initMobilityScriptVars $wlan
    set max_time 0


    # these regex matches from emul (c)2001 HRL/Boeing
    set reg_setdest {^\$ns_ at ([0-9]+\.[0-9]+) \"\$node_\(([0-9]+)\) setdest ([0-9]+\.[0-9]+) ([0-9]+\.[0-9]+) ([0-9]+\.[0-9]+)\"}
    set reg_set {^\$node_\(([0-9]+)\) set ([XYZ])_ ([0-9]+\.[0-9]+)}
    set reg_hdr1 {^# nodes: ([0-9]+), max time: ([0-9]+\.[0-9]+), *}
    # XXX TODO: read the range and bandwidth from the script header

    # read lines from mobility script file
    while { [ gets $f line ] >= 0 } {
        # header line indicates max script time
	if { [regexp $reg_hdr1 $line junk junk max_time] } {
	    set max_time [expr $max_time * 1000]
        # the setdest lines indicate node speed/destination
    	} elseif { [regexp $reg_setdest $line junk time index x y speed] } {
	    # destinations are recorded in a node_dests array
	    set node [mapScriptIndexToNode $index]
	    set time [expr $time * 1000]
	    lappend script_${wlan}(dests) "$time $node $x $y $speed"
	    if {$time > $max_time} { set max_time $time }
        # the set X/Y/Z lines indicate node's starting coordinates
	} elseif { [regexp $reg_set $line junk index coord pos] } {
	    # initial positions are recorded in a node_coords array
	    set node [mapScriptIndexToNode $index]
	    if { $coord == "X" } {
	    	set x $pos
	    } elseif { $coord == "Y" } {
	    	set y $pos
	    	set script_${wlan}(coords,$node) "$x $y"
		# once we have X and Y, move the node
		moveNodeAbs $c $node [expr {$x * $zoom}] [expr {$y * $zoom}]
	    }
	}
    }
    close $f
    foreach wl [findWlanNodes ""] { updateAllRanges $wl 0 }
    set script_${wlan}(max_time) $max_time
}

#
# event loop that moves nodes arounds
proc wlanRunMobilityRound { c wlan now } {
    # milliseconds for each node calculation
    global script_$wlan
    set max_time [set script_${wlan}(max_time)]
    # time since script start
    set time [expr $now - [set script_${wlan}(start_time)]]
    # time since last round
    set dt [expr $now - [set script_${wlan}(last_time)]]

    set script_${wlan}(last_time) $now
    set script_${wlan}(time) $time 

    #puts "XXX wlanRunMobilityRound($wlan) time=$time dt=$dt"
    
    # control looping
    if {$time > $max_time} {
        if { [set script_${wlan}(loop)] } {
	    set time 0
            set script_${wlan}(time) $time 
	    set script_${wlan}(start_time) $now
	    set script_${wlan}(dest_index) 0
	    set script_${wlan}(last_calc) $time
	    moveNodesInitial $c $wlan
    	    foreach wl [findWlanNodes ""] { updateAllRanges $wl 0 }
	} else {
	    set script_${wlan}(state) stop
	}
    # normal round
    } else {
    	# apply node speed
        moveNodes $c $wlan [expr $dt * .001]
	# calculate range every so often
        if { [expr $time - [set script_${wlan}(last_calc)]] > 1000 } {
	    set script_${wlan}(last_calc) $time
	    # update range for every wlan since node movement may affect
            # node range for any wireless network
	    foreach wl [findWlanNodes ""] {
		updateAllRanges $wl 0
		# update all last_calc times?
		# probably not, since further node movement may require another
	    }
	}
    }

    # starting at the last processed destination entry, loop through all
    # of the dests that occur at this time
    for { set i [set script_${wlan}(dest_index)] } \
    	{ $i < [llength [set script_${wlan}(dests)]] } \
	{ incr i } {
	set dest [lindex [set script_${wlan}(dests)] $i]
	
	# time for the next destination has not arrived yet
	if { [lindex $dest 0] > [expr $time] } {
	    break
	}
	#puts "$i at $time dest=$dest"
	updateNodeSpeed $c $wlan $dest
	# set the index to the next destination, so this destination
	# is only processed once.
	set script_${wlan}(dest_index) [expr $i + 1]
    }
}

# returns a node based on the given index, which has been read
# from a mobility script file
proc mapScriptIndexToNode { index } {
	return n$index
}

#
# calculate node coordinate speeds given a new destination
proc updateNodeSpeed { c wlan dest } {
    global script_${wlan} zoom
    set dest_items [split $dest " "]
    set node [lindex $dest_items 1]
    # get initial X,Y coordiantes
    set img [$c find withtag "node && $node"]
    set coords [$c coords $img]
    if { $coords == "" } {
    	# ignore destination for nodes that don't exist on the canvas
    	return
    }
    set initx [expr {[lindex $coords 0] / $zoom} ]
    set inity [expr {[lindex $coords 1] / $zoom} ]
    # get destination X,Y coordinates
    set destx [lindex $dest_items 2]
    set desty [lindex $dest_items 3]
    set script_${wlan}(dcoords,$node) [list $destx $desty]
    # get speed
    set speed [lindex $dest_items 4]

    # update the speeds array
    # calculations derived from emul (c)2001 HRL/Boeing
    if { [expr $destx - $initx] == 0 } {
    	# avoid divide-by-zero
	if { [expr $desty < $inity] } {
	 	set speed_y -$speed
	} else {
	 	set speed_y $speed
	}
    	set script_${wlan}(speeds,$node) [list 0 $speed_y]
	return
    }
    set alpha [ expr atan(($desty - $inity) / ($destx - $initx)) ]
    if { $destx < $initx } {
    	# correct negative angles
    	set alpha [ expr $alpha + 2*acos(0) ]
    }
    set speed_y [ expr $speed * sin($alpha) ]
    set speed_x [ expr $speed * cos($alpha) ]
    set script_${wlan}(speeds,$node) [list $speed_x $speed_y]
}

#
# check if a node has reached its destination
# and stop it
proc checkNodeDest { c wlan node dx_ref dy_ref } {
    global script_${wlan} zoom
    upvar dx $dx_ref
    upvar dy $dy_ref

    if { ![info exists script_${wlan}(dcoords,$node)] } {
    	return
    }
    set dcoords [set script_${wlan}(dcoords,$node)]

    # get current X,Y coordiantes
    set img [$c find withtag "node && $node"]
    set coords [$c coords $img]
    if { $coords == "" } {
    	# ignore destination for nodes that don't exist on the canvas
    	return
    }
    set x1 [expr { [lindex $coords 0] / $zoom} ]
    set y1 [expr { [lindex $coords 1] / $zoom} ]
    set x2 [lindex $dcoords 0]
    set y2 [lindex $dcoords 1]

    set distx [expr $x2 - $x1]
    set disty [expr $y2 - $y1]

    #puts "$node $x1 $y1 to $x2 $y2 ($distx $disty)"
    if { [expr abs($distx)] <= [expr abs($dx)] && \
    	 [expr abs($disty)] <= [expr abs($dy)] } {
    	#puts "$node has reached its destination of $x2 $y2 "
    	set script_${wlan}(speeds,$node) [list 0 0]
	unset script_${wlan}(speeds,$node)
	set dx $distx
	set dy $disty
    }

}

#
# move all nodes that have a speed
proc moveNodes { c wlan dt } {
    global node_list zoom
    global script_${wlan}

    foreach node $node_list {
	if { ![info exists script_${wlan}(speeds,$node)] } {
		continue
        }
	set speed [set script_${wlan}(speeds,$node)]
	set speed_x [lindex $speed 0]
	set speed_y [lindex $speed 1]
	set dx [expr $speed_x * $dt]
	set dy [expr $speed_y * $dt]
	checkNodeDest $c $wlan $node dx dy
	moveNodeIncr $c $node [expr {$dx * $zoom}] [expr {$dy * $zoom}]
    }
}

#
# move all nodes to their starting location
# called upon script looping
proc moveNodesInitial { c wlan } {
    global node_list zoom
    global script_${wlan}

    foreach node $node_list {
	if { ![info exists script_${wlan}(coords,$node)] } {
		continue
        }
	if { [info exists script_${wlan}(speeds,$node)] } {
		unset script_${wlan}(speeds,$node)
        }
	set coords [set script_${wlan}(coords,$node)]
	set x [lindex $coords 0]
	set y [lindex $coords 1]
	moveNodeAbs $c $node [expr {$x * $zoom}] [expr {$y * $zoom}]
    }
}

#
# show a script dialog box
proc showScriptPopup { wlan } {
    global script_$wlan
    global LIBDIR

    set w .scriptpopup$wlan
    catch {destroy $w}
    toplevel $w

    wm transient $w .
    wm title $w "[getNodeName $wlan] mobility script"
    wm geometry $w 320x80

    #
    # scale frame
    #frame $w.fsc -borderwidth 4
    frame $w.fsc -borderwidth 0
    scale $w.fsc.timescale -from 0 -to [set script_${wlan}(max_time)] \
    	-orient horizontal -showvalue true -sliderrelief sunken \
	-variable script_${wlan}(time) -length 684
    # -state disabled
    pack $w.fsc.timescale -side left -padx 4 -pady 4
    pack $w.fsc -side top -anchor w
    
    #
    # control frame
    #
    frame $w.fctl -borderwidth 0
    # play/pause buttons
    foreach b {play pause stop} {
        set img$b [image create photo \
    		 -file $LIBDIR/icons/tiny/script_$b.gif]
    	radiobutton $w.fctl.$b -indicatoron 0 -image [set img${b}] \
	    	-variable script_${wlan}(state) -value $b \
		-selectcolor [$w cget -bg]
    }
    $w.fctl.play configure -command "unpauseMobilityScript $wlan"
    $w.fctl.stop configure -command "resetMobilityScript $wlan"
    # loop checkbox
    checkbutton $w.fctl.loop -text "loop" -variable script_${wlan}(loop)
    # resolution text entry
    label $w.fctl.resl -text "resolution:"
    entry $w.fctl.res -width 4 -textvariable script_${wlan}(res) \
    			-validate focusout -vcmd {checkIntRange %P 15 5000}
    label $w.fctl.resl2 -text "ms"
    pack $w.fctl.play $w.fctl.pause $w.fctl.stop -side left -padx 4 -pady 4
    pack $w.fctl.loop -side left -padx 4 -pady 4
    pack $w.fctl.resl $w.fctl.res $w.fctl.resl2 -side left -padx 4 -pady 4
    pack $w.fctl -side bottom -anchor w

    #$w.fctl.res insert 0 [set script_${wlan}(res)]
    
}

#
# when play button is pressed (after pause),
# the script is unpaused by changing the start time
proc unpauseMobilityScript { wlan } {
    global script_$wlan
    set now [clock clicks -milliseconds]
    set old_start [set script_${wlan}(start_time)]
    set old_last [set script_${wlan}(last_time)]
    if { $old_start == 0 } {
	set old_start $now
	set old_last $now
    }
    set time_shift [expr $now - $old_last]
    set script_${wlan}(start_time) [expr $old_start + $time_shift]
    set script_${wlan}(last_time) [expr $now - [set script_${wlan}(res)]]
#   puts "Resuming script after $time_shift seconds."
    # run a script when mobility starts, such as /tmp/mobility-n3-start.sh
    set script_name "/tmp/mobility-${wlan}-start.sh"
    if { [file exists $script_name] } {
	if { [catch {exec /bin/sh $script_name &} err] } {
	    puts "WLAN $wlan script $script_name error: $err"
	} else {
	    puts "WLAN $wlan script launched with PID $err"
	}
    }
}

#
# when stop button is pressed, reset variables
# and the timeline, move nodes to initial positions
proc resetMobilityScript { wlan } {
    global script_$wlan
    # index of current destination to process
    set script_${wlan}(dest_index) 0
    # clock time of when the script started
    set script_${wlan}(start_time) 0
    # clock time of last range calculation
    set script_${wlan}(last_calc) 0
    # simulated time -- tied to timescale widget
    set script_${wlan}(time) 0
    # reset node positions
    moveNodesInitial .c $wlan
    foreach wl [findWlanNodes ""] { updateAllRanges $wl 1 }
}

#
# this loop fires periodically, started from exec.tcl/setOperMode(exec)
proc mobility_script_loop {} {
    global oper_mode
    set c .c
    set now [clock clicks -milliseconds]
    set refresh_ms 5000

    set wlanlist [findWlanNodes ""]

    # terminates this event loop
    if { $oper_mode != "exec" } {
	# close any script windows, cleanup
	foreach wlan $wlanlist {
	    global script_$wlan
	    if { [info exists script_$wlan] } {
		set script_${wlan}(state) stop
	        catch {destroy .scriptpopup$wlan}
	    }
	}
        return
    }

    foreach wlan $wlanlist {
        # skip wlan nodes that do not have a mobility script
	global script_$wlan
    	if { ![info exists script_$wlan] } {
	    continue
	}
	if { [set script_${wlan}(state)] == "pause" ||
	     [set script_${wlan}(state)] == "stop" } {
	    continue
	}
	if { [set script_${wlan}(state)] == "init" } {
	    if { ![info exists .scriptpopup$wlan] } { 
	        showScriptPopup $wlan
	    }
	    set script_${wlan}(start_time) $now
	    set script_${wlan}(last_time) $now
	    set script_${wlan}(state) stop
	    continue
	}
	if { [set script_${wlan}(start_time)] == 0 } {
	    set script_${wlan}(start_time) $now
	    set script_${wlan}(last_time) $now
	    # showScriptPopup $wlan
	}
        wlanRunMobilityRound $c $wlan $now
	if { [set script_${wlan}(res)] < $refresh_ms } { 
		set refresh_ms [set script_${wlan}(res)] 
	}
    }
    
    after $refresh_ms { mobility_script_loop }
}
