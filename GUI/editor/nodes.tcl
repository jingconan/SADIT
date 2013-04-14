#
# Copyright 2010-2012 the Boeing Company.
# See the LICENSE file included in this distribution.
#
# author:	Jeff Ahrenholz <jeffrey.m.ahrenholz@boeing.com>
#
# Support for managing CORE plugins from the GUI.
#

global execMode
if { $execMode == "interactive" } {
    package require Ttk
}

# these are the default node types when nodes.conf does not exist
#      index {name normal-icon tiny-icon services type metadata}
array set g_node_types_default {
    1 {router router.gif router.gif {zebra OSPFv2 OSPFv3 vtysh IPForward} \
       netns {built-in type for routing}}
    2 {host host.gif host.gif {DefaultRoute SSH} \
       netns {built-in type for servers}}
    3 {PC pc.gif pc.gif {DefaultRoute} \
       netns {built-in type for end hosts}}
    4 {mdr mdr.gif mdr.gif {zebra OSPFv3MDR vtysh IPForward} \
       netns {built-in type for wireless routers}}
    5 {prouter router_green.gif router_green.gif \
           {zebra OSPFv2 OSPFv3 vtysh IPForward} \
       physical {built-in type for physical nodes}}
}

# magic number of fields that are configurable for a service
set NUM_SERVICE_FIELDS 7
# possible machine types for nodes
set MACHINE_TYPES "netns physical"

# array populated from nodes.conf file
array set g_node_types { }

#
# Load the nodes.conf file into the g_nodes array
#
proc loadNodesConf { } {
    global CONFDIR g_node_types g_node_types_default MACHINE_TYPES
    set confname "$CONFDIR/nodes.conf"
    if { [catch { set f [open $confname r] } ] } {
        puts "Creating a default $confname"
        unset g_node_types
        array set g_node_types [array get g_node_types_default]
        writeNodesConf
        return
    }

    array unset g_nodes

    while { [ gets $f line ] >= 0 } {
        if { [string range $line 0 0] == "#" } { continue } ;# skip comments

        # fix-up 5-element list to include node type
        if { [llength $line] == 2 } {
            set idx [lindex $line 0]; set data [lindex $line 1]
            if { [llength $data] == 5 } {
                set data [linsert $data 4 [lindex $MACHINE_TYPES 0]]
                set line [list $idx $data]
            }
        }

        # load into array of nodes
        if { [catch {array set g_node_types $line} e] } {
            puts "Error reading $confname line '$node': $e"
        }
    }
    close $f
}

#
# Write the nodes.conf file from the g_nodes array.
#
proc writeNodesConf { } {
    global CONFDIR g_node_types
    set confname "$CONFDIR/nodes.conf"
    if { [catch { set f [open "$confname" w] } ] } {
        puts "***Warning: could not write nodes file: $confname"
        return
    }

    set header "# nodes.conf: CORE node templates customization file."
    set header "$header\n# format: index {name normal-icon tiny-icon services"
                                          set header "$header type metadata}"
    puts $f $header
    foreach i [lsort -integer [array names g_node_types]] {
        puts $f "$i { $g_node_types($i) }"
    }
    close $f
}

# return a list of names of node types
proc getNodeTypeNames {} {
    global g_node_types
    set names ""
    foreach i [lsort -integer [array names g_node_types]] {
        set node_type_data $g_node_types($i)
        set name [lindex $node_type_data 0]
        lappend names $name
    }
    # puts $names
    return $names
}

proc getNodeRoleName {} {
    return "none client server botmaster"
}

# return the image path name for the specified node type
# size should equal "tiny" or "normal"
proc getNodeTypeImage { type size } {
    global g_node_types LIBDIR
    foreach i [lsort -integer [array names g_node_types]] {
        set node_type_data $g_node_types($i)
        if { [lindex $node_type_data 0] == $type } {
            if { $size == "tiny" } {
                set imgf [lindex $node_type_data 2]
            } else {
                set imgf [lindex $node_type_data 1]
            }
            # if the image has no path, assume it can be
            # found in $LIBDIR/icons/tiny
            if { [string first "/" $imgf] < 0 } {
                set imgf "$LIBDIR/icons/$size/$imgf"
            }
            return $imgf
        }
    }
    return ""
}

# return the index in the global array for the given node type
proc getNodeTypeIndex { type } {
    global g_node_types
    foreach i [lsort -integer [array names g_node_types]] {
        set node_type_data $g_node_types($i)
        if { [lindex $node_type_data 0] == $type } {
            return $i
        }
    }
    return -1
}

# return the default services for this node type
proc getNodeTypeServices { type } {
    global g_node_types
    foreach i [lsort -integer [array names g_node_types]] {
        set node_type_data $g_node_types($i)
        if { [lindex $node_type_data 0] == $type } {
            return [lindex $node_type_data 3]
        }
    }
    return ""
}

# return the machine type (e.g. netns, physical, xen) of the currently selected
# node type from the toolbar
proc getNodeTypeMachineType { type } {
    global MACHINE_TYPES g_node_types
    set default_machine_type [lindex $MACHINE_TYPES 0]
    set i [getNodeTypeIndex $type]
    if { $i < 0 } { return $default_machine_type }; # failsafe
    return [lindex $g_node_types($i) 4]
}

proc getNodeTypeProfile { type } {
    global g_node_types
    foreach i [lsort -integer [array names g_node_types]] {
        set node_type_data $g_node_types($i)
        if { [lindex $node_type_data 0] == $type } {
            if {[llength $node_type_data] >= 7 } {
                return [lindex $node_type_data 6]
            }
            break ;# profile may be empty
        }
    }
    return ""
}

# return the machine type (e.g. netns, physical, xen) of the currently selected
# node type from the toolbar
proc getNodeTypeMachineType { type } {
    global MACHINE_TYPES g_node_types
    set default_machine_type [lindex $MACHINE_TYPES 0]
    set i [getNodeTypeIndex $type]
    if { $i < 0 } { return $default_machine_type }; # failsafe
    return [lindex $g_node_types($i) 4]
}

#
# Popup a services configuration dialog box. Similar to popupCapabilityConfig
# but customized for configuring node services. This dialog has two uses:
# (1) selecting the default services for a node type (when session > -1), and
# (2) selecting/customizing services for a certain node
#
proc popupServicesConfig { channel node types values captions possible_values groups session } {
    global plugin_img_edit
    global g_service_ctls
    global g_sent_nodelink_definitions
    set wi .popupServicesConfig
    catch {destroy $wi}
    toplevel $wi
    wm transient $wi . 

    # instead of using vals, the activated services are stored in this list
    set activated ""
    if { $session > -1 } {
        global g_node_type_services_hint
        if { ![info exists g_node_type_services_hint] } {
            set g_node_type_services_hint "router"
        }
        set title "Default services"
        set toptitle "Default services for node type $g_node_type_services_hint"
        set activated [getNodeTypeServices $g_node_type_services_hint]
    } else {
        set title "Node [getNodeName $node] ($node) services"
        set toptitle $title
        set activated [getNodeServices $node true]
    }
    wm title $wi $title

    label $wi.top -text $toptitle 
    pack $wi.top -side top -padx 4 -pady 4

    frame $wi.vals -relief raised -borderwidth 1

    set g_sent_nodelink_definitions 0 ;# only send node/link defs once
    set g_service_ctls {} ;# list of checkboxes

    set n 0
    set gn 0
    set lastgn -1
    foreach type $types {
    # group values into frames based on groups TLV
        set groupinfo [popupCapabilityConfigGroup $groups [expr {$n + 1}]]
        set gn [lindex $groupinfo 0]
        set groupcaption [lindex $groupinfo 1]
        if { $lastgn != $gn } {
            labelframe $wi.vals.$gn -text $groupcaption \
                -borderwidth 1 -padx 4 -pady 4
        }
        frame $wi.vals.$gn.item$n
        if {$type != 11} { ;# boolean value
                           puts "warning: skipping service config [lindex $captions $n]"
                           incr n
                           continue
        }
        set servicename [lindex $captions $n]
        global $wi.vals.$gn.item$n.entval
        checkbutton $wi.vals.$gn.item$n.ent -width 12 -wraplength 90 \
            -variable $wi.vals.$gn.item$n.entval -text $servicename \
            -offrelief flat -indicatoron false -overrelief raised
        lappend g_service_ctls $wi.vals.$gn.item$n.ent

        if { [lsearch -exact $activated [lindex $captions $n]] == -1 } {
            set value 0 ;# not in the activated list
        } else {
            set value 1
        }
        set $wi.vals.$gn.item$n.entval $value
        if { $session < 0 } {
            set needcustom false
            if { $n < [llength $possible_values] } {
                if { [lindex $possible_values $n] == 1 } { set needcustom true }
            }
            set btn $wi.vals.$gn.item$n.custom
            button $btn -image $plugin_img_edit \
                -command "customizeService $wi $node $servicename $btn"
            setCustomButtonColor $btn $node $servicename $needcustom
            pack $wi.vals.$gn.item$n.custom -side right -padx 4 -pady 4
        }
        pack $wi.vals.$gn.item$n.ent -side right -padx 4 -pady 4
        pack $wi.vals.$gn.item$n -side top -anchor e
        if { $lastgn != $gn } {
            pack $wi.vals.$gn -side left -anchor n -fill both
            set lastgn $gn
        }
        incr n
    }; # end foreach
    pack $wi.vals.$gn -side left -anchor n -fill both
    pack $wi.vals -side top -padx 4 -pady 4

    # Apply / Cancel buttons
    set apply_cmd "popupServicesConfigApply $wi $channel $node $session"
    set cancel_cmd "destroy $wi"
    frame $wi.btn
    button $wi.btn.apply -text "Apply" -command $apply_cmd
    button $wi.btn.def -text "Defaults" -command \
        "popupServicesConfigDefaults $wi $node {$types} {$captions} {$groups}"
    button $wi.btn.cancel -text "Cancel" -command $cancel_cmd
    set buttons [list $wi.btn.apply $wi.btn.cancel]
    if { $session < 0 } {
        set buttons [linsert $buttons 1 $wi.btn.def]
    }
    foreach b $buttons { pack $b -side left -padx 4 -pady 4 }
    pack $wi.btn -side bottom
    bind $wi <Key-Return> $apply_cmd
    bind $wi <Key-Escape> $cancel_cmd

    #after 100 {
    #	grab .popupServicesConfig
    #}
}

#
# Save the selection of activated services with the node or in the g_node_types
# array when configuring node type defaults.
#
proc popupServicesConfigApply { wi channel node session } {
    set vals [getSelectedServices]

    # save default services for a node type into the g_node_types array
    if { $session > -1 } {
        global g_node_types g_node_type_services_hint
        set type $g_node_type_services_hint
        set idx [getNodeTypeIndex $type]
        if { $idx < 0 } { 
            puts "warning: skipping unknown node type $type"
        } else {
            set typedata $g_node_types($idx)
            set typedata [lreplace $typedata 3 3 $vals]
            array set g_node_types [list $idx $typedata]
        }
        # save the services configured for a specific node
    } else {
        setNodeServices $node $vals
    }

    destroy $wi
}

# load the default set of services for this node type
proc popupServicesConfigDefaults { wi node types captions groups } {
    set type [getNodeModel $node]
    set defaults [getNodeTypeServices $type]
    for { set n 0 } { $n < [llength $types] } { incr n } {
        set groupinfo [popupCapabilityConfigGroup $groups [expr {$n + 1}]]
        set gn [lindex $groupinfo 0]

        set val 0
        set valname [lindex $captions $n]
        if { [lsearch $defaults $valname] != -1 } { set val 1 }
        global $wi.vals.$gn.item$n.entval
        set $wi.vals.$gn.item$n.entval $val
    }
}

#
# Popup a service customization dialog for a given service on a node
# The customize/edit button next to a service has been pressed
#
proc customizeService { wi node service btn } {
    global g_sent_nodelink_definitions
    global plugin_img_add plugin_img_del plugin_img_folder
    global plugin_img_open plugin_img_save
    set selected [getSelectedServices]
    # if service is not enabled, enable it here
    if { [lsearch -exact $selected $service] == -1 } {
        set i [string last ".custom" $btn]
        set entval [string replace $btn $i end ".entval"]
        global $entval
        set $entval 1
        lappend selected $service
    }

    # inform the CORE services about all nodes and links, so it can build
    # custom configurations for services
    if { $g_sent_nodelink_definitions == 0 } {
        set g_sent_nodelink_definitions 1
        set sock [lindex [getEmulPlugin $node] 2]
        sendNodeLinkDefinitions $sock
    }

    set w .popupServicesCustomize
    catch {destroy $w}
    toplevel $w
    wm transient $w . 
    wm title $w "$service on node [getNodeName $node] ($node)"

    ttk::frame $w.top
    ttk::label $w.top.lab -text "$service service"

    ttk::frame $w.top.meta
    ttk::label $w.top.meta.lab -text "Meta-data"
    ttk::entry $w.top.meta.ent -width 40
    pack $w.top.lab -side top
    pack $w.top.meta.lab -side left -padx 4 -pady 4
    pack $w.top.meta.ent -fill x -side left -padx 4 -pady 4
    pack $w.top.meta -side top
    pack $w.top -side top -padx 4 -pady 4

    ttk::notebook $w.note
    pack $w.note -fill both -expand true -padx 4 -pady 4
    ttk::notebook::enableTraversal $w.note

    set enableapplycmd "$w.btn.apply configure -state normal"

    ### Files ###
    ttk::frame $w.note.files
    set fileshelp "Config files and scripts that are generated for this"
    set fileshelp "$fileshelp service."
    ttk::label $w.note.files.help -text $fileshelp
    pack $w.note.files.help -side top -anchor w -padx 4 -pady 4
    $w.note add $w.note.files -text "Files" -underline 0

    ttk::frame $w.note.files.name
    ttk::label $w.note.files.name.lab -text "File name:"
    set combo $w.note.files.name.combo
    ttk::combobox $combo -width 30
    set helpercmd "customizeServiceFileHelper $w"
    ttk::button $w.note.files.name.add -image $plugin_img_add \
        -command "listboxAddDelHelper add $combo $combo true; $helpercmd false"
    ttk::button $w.note.files.name.del -image $plugin_img_del \
        -command "listboxAddDelHelper del $combo $combo true; $helpercmd true"
    foreach c [list open save] {
        ttk::button $w.note.files.name.$c -image [set plugin_img_$c] -command \
            "genericOpenSaveButtonPress $c $w.note.files.txt $w.note.files.name.combo"
    }
    pack $w.note.files.name.lab -side left
    pack $w.note.files.name.combo -side left -fill x -expand true
    foreach c [list add del open save] {
        pack $w.note.files.name.$c -side left
    }
    pack $w.note.files.name -side top -anchor w -padx 4 -pady 4 -fill x

    text $w.note.files.txt -bg white -width 80 -height 10 \
        -yscrollcommand "$w.note.files.scroll set" -undo 1
    ttk::scrollbar $w.note.files.scroll -command "$w.note.files.txt yview"

    pack $w.note.files.txt -side left -fill both -expand true
    pack $w.note.files.scroll -side right -fill y
    bind $w.note.files.txt <KeyPress> $enableapplycmd

    global g_service_configs_tmp g_service_configs_last
    if { [info exists g_service_configs_tmp ] } {
        array unset g_service_configs_tmp
    }
    array set g_service_configs_tmp {}
    set g_service_configs_last ""
    bind $w.note.files.name.combo <<ComboboxSelected>> "$helpercmd true"
    bind $w.note.files.name.combo <KeyPress> $enableapplycmd

    ### Directories ###
    ttk::frame $w.note.dirs
    $w.note add $w.note.dirs -text "Directories" -underline 0
    set helptxt "Directories required by this service that are"
    set helptxt "$helptxt unique for each node."
    ttk::label $w.note.dirs.help -text $helptxt
    pack $w.note.dirs.help -side top -anchor w -padx 4 -pady 4

    ttk::treeview $w.note.dirs.tree -height 3 -selectmode browse
    $w.note.dirs.tree heading \#0 -text "Per-node directories"
    $w.note.dirs.tree insert {} end -id root -text "/" -open true \
        -image $plugin_img_folder
    ttk::button $w.note.dirs.add -image $plugin_img_add \
        -command "customizeServiceDirectoryHelper $w add; $enableapplycmd"
    ttk::button $w.note.dirs.del -image $plugin_img_del \
        -command "customizeServiceDirectoryHelper $w del; $enableapplycmd"

    pack $w.note.dirs.tree -side top -fill both -expand true -padx 4 -pady 4
    pack $w.note.dirs.del $w.note.dirs.add -side right

    ### Startup/shutdown ###
    ttk::frame $w.note.ss
    $w.note add $w.note.ss -text "Startup/shutdown" -underline 0

    global g_service_startup_index
    set g_service_startup_index 50
    ttk::frame $w.note.ss.si
    ttk::label $w.note.ss.si.idxlab -text "Startup index:"
    ttk::entry $w.note.ss.si.idxval -width 5 \
        -textvariable g_service_startup_index
    ttk::scale $w.note.ss.si.idx -from 0 -to 100 -orient horizontal \
        -variable g_service_startup_index \
        -command "$enableapplycmd; scaleresolution 1 g_service_startup_index"
    pack $w.note.ss.si.idxlab $w.note.ss.si.idxval -side left -padx 4 -pady 4
    pack $w.note.ss.si.idx -side left -expand true -fill x -padx 4 -pady 4
    pack $w.note.ss.si -side top -padx 4 -pady 4 -fill x

    set captions "Startup Shutdown Validate"
    foreach c "up down val" {
        set fr $w.note.ss
        set caption [lindex $captions 0]
        set captions [lreplace $captions 0 0]
        ttk::labelframe $fr.$c -text "$caption Commands"

        ttk::frame $fr.$c.edit
        ttk::entry $fr.$c.edit.cmd -width 40
        ttk::button $fr.$c.edit.add -image $plugin_img_add \
            -command "listboxAddDelHelper add $fr.$c.edit.cmd $fr.$c.cmds.list false; $enableapplycmd"
        ttk::button $fr.$c.edit.del -image $plugin_img_del \
            -command "listboxAddDelHelper del $fr.$c.edit.cmd $fr.$c.cmds.list false; $enableapplycmd"
        pack $fr.$c.edit.cmd -side left -fill x -expand true
        pack $fr.$c.edit.add $fr.$c.edit.del -side left

        ttk::frame $fr.$c.cmds
        listbox $fr.$c.cmds.list -height 5 -width 50 \
            -yscrollcommand "$fr.$c.cmds.scroll set" -exportselection 0
        bind $fr.$c.cmds.list <<ListboxSelect>> "listboxSelect $fr.$c.cmds.list $fr.$c.edit.cmd"
        ttk::scrollbar $fr.$c.cmds.scroll -command "$fr.$c.cmds.list yview"
        pack $fr.$c.cmds.list  -side left -fill both -expand true
        pack $fr.$c.cmds.scroll -side left -fill y
        pack $fr.$c.edit $fr.$c.cmds -side top -anchor w -fill x
        pack $fr.$c -side top -fill x -expand true
    }


    set closecmd "destroy $w; setCustomButtonColor $btn $node $service false"

    ttk::frame $w.btn
    ttk::button $w.btn.apply -text "Apply" -state disabled \
        -command "customizeServiceApply $w $node $service; $closecmd"
    ttk::button $w.btn.reset -text "Defaults" \
        -command "customizeServiceReset $w $node $service {$selected}; $w.btn.close configure -text Close"
    ttk::button $w.btn.close -text "Cancel" -command $closecmd
    pack $w.btn.apply $w.btn.reset $w.btn.close -side left
    pack $w.btn -side top -padx 4 -pady 4

    #after 100 grab $w
    # populate dialog values
    customizeServiceRefresh $service "$w $node {$selected}"
}

# helper for add/delete directories from treeview
proc customizeServiceDirectoryHelper { w cmd } {
    if { $cmd == "add" } {
        set dir [tk_chooseDirectory -mustexist false -initialdir "/" \
            -parent $w -title "Add a per-node directory"]
        if { $dir == "" } { return }
        set dir [string range $dir 1 end] ;# chop off leading slash
        treeviewInsert $w.note.dirs.tree root [split $dir "/"]
    } elseif { $cmd == "del" } {
        set s [$w.note.dirs.tree selection]
        if { $s == "root" } { return } ;# may not delete root
        $w.note.dirs.tree delete $s ;# delete the current selection
        set parents [lreplace [split $s /] end end]
        # delete all parents of the selected node if they do not have children
        while {[llength $parents] > 1} {
            set parent [join $parents "/"]
            if { [llength [$w.note.dirs.tree children $parent]] == 0 } {
                $w.note.dirs.tree delete $parent
            }
            set parents [lreplace $parents end end]
        }
    }
}

# helper for switching files based on combo box selection
proc customizeServiceFileHelper { w clear } {
    global g_service_configs_tmp g_service_configs_last
    # save old config to array
    set cfg [$w.note.files.txt get 0.0 end-1c]
    if { [info exists g_service_configs_last] && \
         $g_service_configs_last != "" } {
        array set g_service_configs_tmp [list $g_service_configs_last $cfg]
    }
    set cfgname [$w.note.files.name.combo get]
    set g_service_configs_last $cfgname

    # populate with new config
    if { $clear } { $w.note.files.txt delete 0.0 end }
    if { ![info exists g_service_configs_tmp($cfgname)] } {
        array set g_service_configs_tmp [list $cfgname ""]
    } else {
        set cfg $g_service_configs_tmp($cfgname)
        $w.note.files.txt insert 0.0 $cfg
    }
}

# Helper for add/delete button next to a list/combo box; from is the text entry
# from which the value is copied, and to is the list/combo box where the value
# is inserted upon add
proc listboxAddDelHelper { cmd from to combo } {
    set current [$from get] ;# current text from entry or combo
    if { $combo } {
        set values [$to cget -values]
        set i [lsearch -exact $values $current]
    }

    if { $cmd == "add" } {
        if { $combo } {
            if { $i != -1 } { return } ;# item already exists
            lappend values $current
            $to configure -values $values
        } else {
            $to insert end $current
        }
    } elseif { $cmd == "del" } {
        if { $combo } {
        # search combo box values for current text
            if { $i == -1 } { return } ;# item doesn't exist
            set values [lreplace $values $i $i]
            $to configure -values $values
        } else {
            set values [$to curselection]
            if { $values == "" } { return } ;# no current selection
            $to delete [lindex $values 0] ;# delete only first selected item
        }
        $from delete 0 end ;# clear text entry/combo on delete
    }
}

# helper to populate a text entry when a listbox selection has changed
proc listboxSelect { lb ent } {
    set i [$lb curselection]
    $ent delete 0 end
    if { $i == "" } { return }
    $ent insert 0 [$lb get $i]
}


#
# color the customize/edit button adjacent to each service checkbutton
#
proc setCustomButtonColor { btn node service needcustom } {
    set color lightgray ;# default button background color

    if { $needcustom } {
        set color yellow
    }
    if { [getCustomService $node $service] != "" } {
        set color green
    }
    $btn configure -bg $color
}

proc scaleresolution { res var val } {
    set factor [expr {1 / $res}]
    set val [expr {int($val * $factor) / $factor}]
    global $var
    set $var $val
    return $val
}

# return a list of services that have been selected (checkbox is checked)
proc getSelectedServices { } {
    global g_service_ctls
    set selected {}
    foreach c $g_service_ctls {
        global $c
        set service [$c cget -text]
        set var [$c cget -variable]
        global $var
        if { [set $var] == 1 } { lappend selected $service }
    }
    return $selected
}

# send a config request message with the opaque field set to query for all
# service parameters; the opaque field is "service:s5,s2,s3,s4", where service
# s5 is being configured
proc customizeServiceRefresh { var args } {
    set args [lindex $args 0]
    set w [lindex $args 0]
    set node [lindex $args 1]
    set services [lindex $args 2]

    # move service to the front of the list of services
    set i [lsearch $services $var]
    if { $i < 0 } {
        puts "error: service $var not found in '$services'"
        return
    } elseif { $i > 0 } {
        set services [lreplace $services $i $i]
        set services [linsert $services 0 $var]
    }

    set values [getCustomService $node $var]
    if { $values != "" } {
    # use a saved custom config for this service
        customizeServiceValues $node $values $services
        return
    } else {
    # request service parameters from daemon
        set svcstr [join $services ","]
        set sock [lindex [getEmulPlugin $node] 2]
        sendConfRequestMessage $sock $node services 0x1 -1 "service:$svcstr"
    }
    update
}

# this returns a list of values for the service s on node if a custom service
# configuration exists
proc getCustomService { node s } {
    set values [getCustomConfigByID $node "service:$s"]
    return $values
}

# this helper is invoked upon receiving the reply to the message sent from
# customizeServiceRefresh; it populates the dialog box fields
proc customizeServiceValues { node values services } {
    global NUM_SERVICE_FIELDS plugin_img_folder
    set w .popupServicesCustomize
    if { ![winfo exists $w] } {
    #puts "warning: services config helper window $w doesn't exist"
        return
    } elseif { [llength $values] != $NUM_SERVICE_FIELDS } {
        puts -nonewline "warning: services config helper mismatched values, "
        puts "discarding [lindex $services 0] config for $node"
        return
    }

    # populate meta-data
    set meta [lindex $values 6]
    $w.top.meta.ent delete 0 end
    $w.top.meta.ent insert end $meta

    # populate Files tab
    set files [tupleStringToList [lindex $values 1]]
    set chosenfile [lindex $files 0] ;# auto-display first file from list
    $w.note.files.name.combo configure -values $files
    $w.note.files.name.combo delete 0 end
    if { $chosenfile != "" } {
        $w.note.files.name.combo insert 0 $chosenfile
    }
    global g_service_configs_last
    set g_service_configs_last $chosenfile

    # file data
    set service [lindex $services 0]
    foreach f $files {
        set filedata [join [getCustomService $node "$service:$f"] "\n"]
        if { $filedata != "" } {
        # use file contents from existing config
            customizeServiceFile $node $f $filedata
        } elseif { $f !=  "" } {
        # request the file contents
            set svcstr [join $services ","]
            set sock [lindex [getEmulPlugin "*"] 2]
            set opaque "service:$svcstr:$f"
            sendConfRequestMessage $sock $node services 0x1 -1 $opaque
        }
    }

    # populate Directories tab
    set dirs [tupleStringToList [lindex $values 0]]
    $w.note.dirs.tree delete root
    $w.note.dirs.tree insert {} end -id root -text "/" -open true \
        -image $plugin_img_folder
    foreach dir $dirs {
        set dir [string range $dir 1 end] ;# chop off leading slash
        treeviewInsert $w.note.dirs.tree root [split $dir "/"]
    }

    # populate Startup/shutdown tab
    set idx [lindex $values 2]
    global g_service_startup_index
    set g_service_startup_index $idx

    set valuesidx 3
    foreach c "up down val" {
        set fr $w.note.ss
        $fr.$c.edit.cmd delete 0 end
        $fr.$c.cmds.list delete 0 end
        foreach cmd [tupleStringToList [lindex $values $valuesidx]] {
            if { $cmd != "" } { $fr.$c.cmds.list insert end $cmd }
        }
        incr valuesidx
    }

    $w.btn.apply configure -state disabled
}

# this helper is invoked upon receiving a File Message in reply to the Config
# Message sent from customizeServiceRefresh; it populates the config file entry
proc customizeServiceFile { node name data } {
    global g_service_configs_tmp g_service_configs_last
    set w .popupServicesCustomize
    if { ![winfo exists $w] } { return }

    # store file data in array
    array set g_service_configs_tmp [list $name $data]

    # display file if currently selected
    if { $g_service_configs_last == $name } {
        $w.note.files.txt delete 0.0 end
        $w.note.files.txt insert end $data
    }
}

# helper to recursively add a directory path to a treeview
proc treeviewInsert { tree parent items } {
    global plugin_img_folder
    # pop first item
    set item [lindex $items 0]
    set items [lreplace $items 0 0]
    if { ![$tree exists "$parent/$item"] } {
        $tree insert $parent end -id "$parent/$item" -text $item -open true \
            -image $plugin_img_folder
    }

    if { [llength $items] > 0 } {
        treeviewInsert $tree "$parent/$item" $items
    }
}

# return all children that are leaf nodes in a tree
proc treeviewLeaves { tree parent } {
    set leaves ""
    set children [$tree children $parent]
    if { [llength $children] == 0 } {
        return $parent
    }
    foreach child $children {
        set leaves [concat $leaves [treeviewLeaves $tree $child]]
    }
    return $leaves
}

# apply button pressed on customizeService dialog
proc customizeServiceApply { w node service } {
    global NUM_SERVICE_FIELDS

    catch { $w.btn.apply configure -state disabled }

    set values ""

    # Directories
    set dirs ""
    set dirstmp [treeviewLeaves $w.note.dirs.tree root]
    foreach dir $dirstmp {
        set dir [string replace $dir 0 3] ;# chop off "root" prefix
        if { $dir == "" } { continue }
        lappend dirs $dir
    }
    lappend values [listToTupleString $dirs]

    # Files
    set files [$w.note.files.name.combo cget -values]
    lappend values [listToTupleString $files]

    # Startup index
    global g_service_startup_index
    lappend values $g_service_startup_index

    # Startup/shutdown commands
    foreach c "up down val" {
        set cmds [$w.note.ss.$c.cmds.list get 0 end]
        lappend values [listToTupleString $cmds]
    }

    # meta
    lappend values [$w.top.meta.ent get]

    # save values without config file
    setCustomConfig $node "service:$service" $service $values 0
    global g_service_configs_tmp g_service_configs_last
    set cfg [$w.note.files.txt get 0.0 end-1c]
    array set g_service_configs_tmp [list $g_service_configs_last $cfg]
    foreach cfgname $files {
        if { ![info exists g_service_configs_tmp($cfgname)] } {
            puts "missing config for file '$cfgname'"
            continue
        }
        set cfg [split $g_service_configs_tmp($cfgname) "\n"]
        setCustomConfig $node "service:$service:$cfgname" $cfgname $cfg 0
    }

    array unset g_service_configs_tmp
    unset g_service_configs_last

    #  may want to apply here, if some config validation is implemented or
    #  runtime applying of service customization
    #  otherwise this is not necessary due to config being sent upon startup
    #  also more logic would be needed for using the reset button
    #set sock [lindex [getEmulPlugin $node] 2]
    #set types [string repeat "10 " [llength $values]]
    #sendConfReplyMessage $sock $node services $types $values "service:$service"
}

#
# reset button is pressed on customizeService dialog
#
proc customizeServiceReset { w node service services } {
    set cfgnames [$w.note.files.name.combo cget -values]
    setCustomConfig $node "service:$service" "" "" 1
    foreach cfgname [tupleStringToList $cfgnames] {
        setCustomConfig $node "service:$service:$cfgname" "" "" 1
    }

    customizeServiceRefresh $service [list $w $node $services]
}

#
# Popup a profile configuration dialog box, using popupCapabilityConfig
#
proc popupNodeProfileConfig { channel node model types values captions bitmap possible_values groups session opaque } {
    global g_node_types

    set opaque_items [split $opaque :]
    if { [llength $opaque_items] != 2 } { 
        puts "warning: received unexpected opaque data in conf message!"
        return
    }
    set nodetype [lindex $opaque_items 1]
    # check if we already have config for this profile, replacing values
    set existing_values [getNodeTypeProfile $nodetype]
    if { $existing_values != "" } {
        if { [llength $existing_values] == [llength $values] } {
            set values $existing_values
        } else { ;# this accommodates changes to models
                 puts "warning: discarding stale profile for $model from nodes.conf"
        }
    }

    popupCapabilityConfig $channel $node $model $types $values \
        $captions $bitmap $possible_values $groups
}

proc popupNodeProfileConfigApply { vals } {
    global g_node_types g_node_type_services_hint
    set type $g_node_type_services_hint
    set idx [getNodeTypeIndex $type]
    if { $idx < 0 } {
        puts "warning: skipping unknown node type $type"
    } else {
        set typedata $g_node_types($idx)
        if { [llength $typedata] < 7 } {
            set typedata [linsert $typedata 6 $vals] ;# no profile in list
        } else {
            set typedata [lreplace $typedata 6 6 $vals] ;# update the profile
        }
        array set g_node_types [list $idx $typedata]
    }
    # node type will be used in sendConfReplyMessage opaque data
    return "model:$type"
}

array set g_nodes_button_tooltips {
    add "add a new node type"
    save "apply changes to this node type"
    del "remove the selected node type"
    up "move the node type up in the list"
    down "move the selected node type down in the list"
}

# show the CORE Node Types configuration dialog
# this allows the user to define new node types having different names, icons,
# and default set of services
proc popupNodesConfig {} {
    global g_nodes_types g_nodes_button_tooltips MACHINE_TYPES g_machine_type

    global LIBDIR

    set wi .nodesConfig
    catch {destroy $wi}
    toplevel $wi

    wm transient $wi .
    wm resizable $wi 0 1
    wm title $wi "CORE Node Types"

    # list of nodes
    labelframe $wi.s -borderwidth 0 -text "Node Types"
    listbox $wi.s.nodes -selectmode single -height 5 -width 15 \
        -yscrollcommand "$wi.s.nodes_scroll set" -exportselection 0
    scrollbar $wi.s.nodes_scroll -command "$wi.s.nodes yview" 
    pack $wi.s.nodes $wi.s.nodes_scroll -fill y -side left
    pack $wi.s -padx 4 -pady 4 -fill both -side top -expand true

    # image button bar
    frame $wi.bbar
    set buttons "add save del"
    foreach b $buttons {
    # re-use images from the plugin dialog
        global plugin_img_$b
        button $wi.bbar.$b -image [set plugin_img_$b] \
            -command "nodesConfigHelper $wi $b"
        pack $wi.bbar.$b -side left
        balloon $wi.bbar.$b $g_nodes_button_tooltips($b)
    }
    pack $wi.bbar -padx 4 -pady 4 -fill x -side top

    # up/down buttons
    foreach b {up down} {
        set img$b [image create photo -file $LIBDIR/icons/tiny/arrow.${b}.gif]
        button $wi.bbar.$b -image [set img${b}] \
            -command "nodesConfigHelper $wi $b"
        pack $wi.bbar.$b -side left
        balloon $wi.bbar.$b $g_nodes_button_tooltips($b)
    }

    # node type edit area
    frame $wi.s.edit -borderwidth 4
    frame $wi.s.edit.0
    label $wi.s.edit.0.namelab -text "Name"
    entry $wi.s.edit.0.name -bg white -width 20 
    pack $wi.s.edit.0.namelab $wi.s.edit.0.name -side left

    frame $wi.s.edit.1
    label $wi.s.edit.1.iconlab -text "Icon"
    entry $wi.s.edit.1.icon -bg white -width 25
    button $wi.s.edit.1.filebtn -text "..." \
        -command "nodesConfigImgDialog $wi $wi.s.edit.1.icon normal"
    pack $wi.s.edit.1.iconlab $wi.s.edit.1.icon $wi.s.edit.1.filebtn -side left
    bind $wi.s.edit.1.icon <KeyPress> "nodesConfigImg $wi"

    canvas $wi.s.edit.0.c -width 60 -height 60
    # -bg white
    pack $wi.s.edit.0.c -side right -padx 10
    bind $wi.s.edit.0.c <Button> \
        "nodesConfigImgDialog $wi $wi.s.edit.1.icon normal"

    frame $wi.s.edit.2
    label $wi.s.edit.2.icontlab -text "Icon (small)"
    entry $wi.s.edit.2.icont -bg white -width 20
    button $wi.s.edit.2.filebtn -text "..." \
        -command "nodesConfigImgDialog $wi $wi.s.edit.2.icont tiny"
    pack $wi.s.edit.2.icontlab $wi.s.edit.2.icont $wi.s.edit.2.filebtn \
        -side left

    frame $wi.s.edit.5
    label $wi.s.edit.5.metalab -text "Meta-data  "
    entry $wi.s.edit.5.meta -bg white -width 25
    pack $wi.s.edit.5.metalab $wi.s.edit.5.meta -side left

    frame $wi.s.edit.3
    set machinetypemenu [tk_optionMenu $wi.s.edit.3.type g_machine_type \
        [lindex $MACHINE_TYPES 0]]
    foreach t [lrange $MACHINE_TYPES 1 end] {
        $machinetypemenu add radiobutton -label $t -value $t \
            -variable g_machine_type \
            -command "nodesConfigMachineHelper $wi"
    }
    button $wi.s.edit.3.services -text "Services..." \
        -command "nodesConfigServices $wi services"
    button $wi.s.edit.3.config -text "Profile..." \
        -command "nodesConfigServices $wi profile"
    pack $wi.s.edit.3.type $wi.s.edit.3.services $wi.s.edit.3.config -side left

    pack $wi.s.edit.0 $wi.s.edit.1 $wi.s.edit.2 $wi.s.edit.5 \
        -side top -anchor w
        #-padx 4 -pady 4
    pack $wi.s.edit.3 -side top -padx 4 -pady 4 -anchor w
    pack $wi.s.edit -fill both -side right

    # populate the list
    nodesConfigRefreshList $wi
    bind $wi.s.nodes <<ListboxSelect>> "nodesConfigSelect $wi \"\""
    $wi.s.nodes selection set 0
    nodesConfigSelect $wi ""


    # close button 
    frame $wi.b -borderwidth 0
    button $wi.b.close -text "Close" -command "nodesConfigClose $wi"
    pack $wi.b.close -side right
    pack $wi.b -side bottom
}

proc nodesConfigRefreshList { wi } {
    global g_node_types

    set selected_idx [$wi.s.nodes curselection]

    $wi.s.nodes delete 0 end
    # this resets the g_node_types array so the indices match the listbox
    set idx 0
    foreach i [lsort -integer [array names g_node_types]] {
        incr idx
        set node_type_data $g_node_types($i)
        set name [lindex $node_type_data 0]
        $wi.s.nodes insert end $name
        if { $i != $idx } {
            array unset g_node_types $i
            array set g_node_types [list $idx $node_type_data]
        }
    }

    if { $selected_idx != "" } {
        $wi.s.nodes selection set $selected_idx
        nodesConfigSelect $wi ""
    }
}

# change a node type selection or save it to an array when cmd="save"
# this updates the edit controls with text from the array, or vice-versa
proc nodesConfigSelect { wi cmd } {
    global g_node_types g_machine_type

    set selected_idx [$wi.s.nodes curselection]
    if { $selected_idx == "" } { return }

    set idx [expr {$selected_idx + 1}]
    if { ![info exists g_node_types($idx)] } { return }

    set node_type_data $g_node_types($idx)

    set i 0
    foreach item [list name icon icont meta] {
        if { $i == 3 } { incr i 2 } ;# skip services, type
        if { $cmd == "save" } { ;# save from controls
                                set str [$wi.s.edit.$i.$item get]
                                set node_type_data [lreplace $node_type_data $i $i $str]
        } else { ;# write to the controls
                 $wi.s.edit.$i.$item delete 0 end
                 $wi.s.edit.$i.$item insert 0 [lindex $node_type_data $i]
        }
        incr i
    }

    if { $cmd == "save" } {
        set node_type_data [lreplace $node_type_data 4 4 $g_machine_type]
        array set g_node_types [list $idx $node_type_data]
        nodesConfigRefreshList $wi
    } else {
        set g_machine_type [lindex $node_type_data 4]
        nodesConfigImg $wi
    }
    nodesConfigMachineHelper $wi
}

# invoked when machine type is selected to enable/disable the profile button
proc nodesConfigMachineHelper { wi } {
    global g_machine_type g_plugins
    set cfgname "emul=$g_machine_type"
    # search plugin capabilities for support for this type of machine
    foreach p [array names g_plugins] {
        set caps [lindex $g_plugins($p) 5]
        if { [lsearch $caps $cfgname] != -1 } {
            $wi.s.edit.3.config configure -state normal
            return
        }
    }
    $wi.s.edit.3.config configure -state disabled
}

# popup a file selection dialog for the icon filenames
proc nodesConfigImgDialog { wi ctl size } {
    global g_imageFileTypes LIBDIR
    set dir "$LIBDIR/icons/$size/"
    set f [tk_getOpenFile -initialdir $dir -filetypes $g_imageFileTypes ]
    if { [string first $dir $f] == 0 } {
    # chop off default path of $dir
        set f [string range $f [string length $dir] end]
    } 
    if { $f != "" } {
        $ctl delete 0 end
        $ctl insert 0 $f
        if { $size == "normal" } { nodesConfigImg $wi }
    }
}

# update the node icon preview
proc nodesConfigImg { wi } {
    global LIBDIR

    set imgf [$wi.s.edit.1.icon get]
    set dir "$LIBDIR/icons/normal/"
    # image has no path, assume it can be found in LIBDIR
    if { [string first "/" $imgf] < 0 } { set imgf "$dir/$imgf" }

    set c $wi.s.edit.0.c
    set cw [lindex [$c configure -width] 4]
    set ch [lindex [$c configure -height] 4]
    $wi.s.edit.0.c delete "preview"
    if { [catch { set img [image create photo -file $imgf] } e] } {
    # puts "f=$imgf err=$e"
        set pad 5
        set x1 $pad; set y2 $pad
        set x2 [expr {$cw - $pad}]; set y1 [expr {$ch - $pad}]
        $c create line $x1 $y1 $x2 $y2 -fill red -width 3 -tags "preview"
    } else {
        set x [expr {$cw / 2}]; set y [expr {$ch / 2}]
        $c create image $x $y -image $img -tags "preview"
    }

}

# helper for adding, deleting, and rearranging (up/down) node types
proc nodesConfigHelper { wi cmd } {
    global g_node_types

    set ctl $wi.s.nodes
    set idx [$ctl curselection]
    if { $idx != "" } {
        set type [$ctl get $idx]
        set arridx [getNodeTypeIndex $type]
    } elseif { $cmd != "add" } { ;# must have item selected
                                 return
    }
    set newsel ""

    switch -exact -- $cmd {
        add {
            set n 1
            set types [getNodeTypeNames]
            while { [lsearch $types "router$n"] != -1 } { incr n }
            set newname "router$n"
            set arridx [expr {[array size g_node_types] + 1}]
            set newdata $g_node_types(1) ;# copy first item
            set newdata [lreplace $newdata 0 0 $newname]
            set newdata [lreplace $newdata 5 5 ""] ;# zero the meta-data
            array set g_node_types [list $arridx $newdata]
            set newsel [expr {$arridx - 1}] 
        }
        save {
            nodesConfigSelect $wi save
        }
        del {
            array unset g_node_types $arridx
        }
        up -
        down {
            if {$cmd == "up" } { 
                if { $arridx < 2 } { return }
                set newidx [expr {$arridx - 1}] 
                set newsel [expr {$idx - 1}] 
            } else {
                if { $idx >= [expr {[$ctl size] - 1}]} { return }
                set newidx [expr {$arridx + 1}]
                set newsel [expr {$idx + 1}] 
            }
            set newentry [lindex [array get g_node_types $arridx] 1]
            set oldentry [lindex [array get g_node_types $newidx] 1]
            if {$oldentry != ""} {
                array set g_node_types [list $arridx $oldentry] 
            }
            array set g_node_types [list $newidx $newentry]
        }
    }

    nodesConfigRefreshList $wi
    if { $newsel != "" } { 
        $ctl selection clear 0 end
        $ctl selection set $newsel
    }
    nodesConfigSelect $wi ""
}

# helper for services button
proc nodesConfigServices { wi services_or_profile } {
    global g_node_type_services_hint g_current_session g_machine_type
    set idx [$wi.s.nodes curselection]
    if { $idx == "" } { return }

    set g_node_type_services_hint [$wi.s.nodes get $idx]
    # use the default emulation plugin - not associated with any node
    set sock [lindex [getEmulPlugin "*"] 2]
    # node number 0 is sent, but these services are not associated with a node
    if { $services_or_profile == "profile" } {
        set services_or_profile $g_machine_type ;# address the e.g. "xen" model
        set opaque "$g_machine_type:$g_node_type_services_hint"
    } else {
        set opaque ""
    }
    sendConfRequestMessage $sock -1 $services_or_profile 0x1 -1 $opaque 
}

# helper for when close button is pressed
proc nodesConfigClose { wi } {
    writeNodesConf
    drawToolbarSubmenu "routers" [getNodeTypeNames]
    destroy $wi
}

# check for old service configs in all nodes
proc upgradeConfigServices {} {
    global node_list
    foreach node $node_list {
        upgradeNodeConfigService $node
        upgradeCustomPostConfigCommands $node
    }
}

# provide backwards-compatibility with changes to services fields here
proc upgradeNodeConfigService { node } {
    global NUM_SERVICE_FIELDS
    set cfgs [getCustomConfig $node]
    foreach cfg $cfgs {
        set cid [lindex [lsearch -inline $cfg "custom-config-id service:*"] 1]
        # skip configs that are not a service definition ("service:name")
        if { [llength [split $cid :]] != 2 } { continue }

        set values [getConfig $cfg config]
        if { [llength $values] != [expr {$NUM_SERVICE_FIELDS-1}] } { continue }

        # update from 6 service fields to 7 when introducing validate commands
        set service [lindex [split $cid :] 1]
        #puts -nonewline "note: updating service $service on $node with empty "
        #puts "validation commands"
        set values [linsert $values end-1 {}]
        setCustomConfig $node "service:$service" $service $values 0
    }
}

proc upgradeCustomPostConfigCommands { node } {
    set cfg [getCustomPostConfigCommands $node]
    if { $cfg == "" } { return }
    set cfgname "custom-post-config-commands.sh"
    set values "{} {('$cfgname', )} 35 {('sh $cfgname', )} {} {} {}"
    setCustomConfig $node "service:UserDefined" "UserDefined" $values 0
    setCustomConfig $node "service:UserDefined:$cfgname" $cfgname $cfg 0
    set services [getNodeServices $node true]
    lappend services "UserDefined"
    setNodeServices $node $services
    puts "adding user-defined custom-post-config-commands.sh service for $node"

}

# Helper for open/save buttons
# cmd is open or save; ctldata is the text control having the file data;
# ctlinitfn is the control having the initial filename
proc genericOpenSaveButtonPress { cmd ctldata ctlinitfn } {
# get initial filename from ctlinitfn
    set fn [file tail [$ctlinitfn get]]

    if { $cmd == "save" } {
        set title "Save File Text"
        set fn [tk_getSaveFile -title $title -initialfile $fn -parent $ctldata]
        set mode "w"
        set action "writing"
    } else {
        set title "Load File Text"
        set fn [tk_getOpenFile -title $title -initialfile $fn -parent $ctldata]
        set mode "r"
        set action "loading"
    }

    # user presses cancel
    if { $fn == "" } { return }

    if { [catch { set f [open $fn $mode] } e] } {
        puts "Error $action file $fn: $e"
        return
    }
    if { $cmd == "save" } {
        puts $f [$ctldata get 0.0 end-1c]
    } else {
        $ctldata delete 0.0 end
        while { [gets $f line] >= 0 } {
            $ctldata insert end "$line\n"
        }
    }
    close $f
}

#
# built-in node types
#
proc rj45.layer {}      { return LINK }
proc lanswitch.layer {} { return LINK }
proc hub.layer {}       { return LINK }
proc tunnel.layer {}    { return LINK }
proc wlan.layer {}      { return LINK }
proc router.layer {}    { return NETWORK }
proc router.shellcmd { n } { return "vtysh" }

# load the nodes.conf file when this file is loaded
loadNodesConf
