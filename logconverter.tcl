###############################################################################
#
#                               Log Converter
#                         by Spirent Communications
#
#   Date: November 17, 2014
# Author: Matthew Jefferson - matt.jefferson@spirent.com
#
# Description: Converts the specified HLTAPI log file into a Tcl script.
#
###############################################################################
#
# Modification History
# Version  Modified
# 1.0.0    11/17/2014 by Matthew Jefferson
#           -Began work on package.
#
###############################################################################

set __package_version__ 1.0.0

###############################################################################
# Copyright (c) 2014 SPIRENT COMMUNICATIONS OF CALABASAS, INC.
# All Rights Reserved
#
#                SPIRENT COMMUNICATIONS OF CALABASAS, INC.
#                            LICENSE AGREEMENT
#
#  By accessing or executing this software, you agree to be bound by the terms
#  of this agreement.
#
# Redistribution and use of this software in source and binary forms, with or
# without modification, are permitted provided that the following conditions
# are met:
#  1. Redistribution of source code must retain the above copyright notice,
#     this list of conditions and the following disclaimer.
#  2. Redistribution's in binary form must reproduce the above copyright notice.
#     This list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
#  3. Neither the name SPIRENT, SPIRENT COMMUNICATIONS, SMARTBITS, SPIRENT
#     TESTCENTER, AVALANCHE NEXT, LANDSLIDE, nor the names of its contributors
#     may be used to endorse or promote products derived from this software
#     without specific prior written permission.
#
# This software is provided by the copyright holders and contributors [as is]
# and any express or implied warranties, including, but not limited to, the
# implied warranties of merchantability and fitness for a particular purpose
# are disclaimed. In no event shall the Spirent Communications of Calabasas,
# Inc. Or its contributors be liable for any direct, indirect, incidental,
# special, exemplary, or consequential damages (including, but not limited to,
# procurement of substitute goods or services; loss of use, data, or profits;
# or business interruption) however caused and on any theory of liability,
# whether in contract, strict liability, or tort (including negligence or
# otherwise) arising in any way out of the use of this software, even if
# advised of the possibility of such damage.
#
###############################################################################


###############################################################################
####
####    Public Procedures
####
###############################################################################

proc convertLog { inputfilename {outputfilename ""} } {

    if { [file exists $inputfilename] } {
        set fh [open $inputfilename r]
        set filetext [read $fh]
        close $fh
    } else {
        error "The file '$inputfilename' does not exist."
    }

    set tclcode ""
    foreach line [regexp -inline -line -all -- {Tcl command - .*} $filetext] {
        regsub {Tcl command -} $line {} line

        # # Make sure "::sth::" is prefixed to each command.
        # set cmd  [lindex $line 0]
        # if { ! [regexp {::sth::} $cmd] } {
        #     set cmd "::sth::$cmd"
        # }


        # set args [lindex $line 1]   ;# This will strip off the brackets from the arguments.

        append tclcode $line \n
    }

    if { $outputfilename eq "" } {
        # Just modifiy the inputfilename for the outputfilename.
        set outputfilename [file rootname $inputfilename]
        append outputfilename "_converted.tcl"
    }

    puts "Writting output to '$outputfilename'..."
    set fh [open $outputfilename w+]
    puts $fh $tclcode
    close $fh

    return
}


###############################################################################
####
####    Main
####
###############################################################################

set inputfilename {../testing/issue/avalanche_python.log}

convertLog $inputfilename "../testing/issue/converted.tcl"