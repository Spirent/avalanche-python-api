###############################################################################
#
#                           Avalanche Python API
#                         by Spirent Communications
#
#   Date: June 6, 2016
# Author: Matthew Jefferson - matt.jefferson@spirent.com
#
# Description: This is a Python wrapper for the Avalanche Tcl API. This software
#              translates the Python commands into the corresponding Tcl commands.
#              It also returns the response as a Python data structure, if 
#              possible.
#
###############################################################################
#
# Modification History
# Version  Modified
# 1.0.0    6/6/2016 by Matthew Jefferson
#           -Initial release.
#
# 1.1.0    10/28/2016 by Matthew Jefferson
#           -Added the methods reserveAll and releaseAll.
#           -Fixed a small issue with Python2 support.
#
# 1.1.1    11/11/2016 by Matthew Jefferson
#           -Fixed an issue with av.config. Most values are now encased in 
#            curly brackets (just like the GUI export). This fixes an issue
#            with some rare parameters.
#           -Fixed an issue with av.perform and the "export" command.
#
# 1.1.2    11/30/2016 by Matthew Jefferson
#           -Changed the init slightly so that the apipath and libpath are placed
#            at the head of the Tcl auto_path. This will impact the usefulness
#            of the TCLLIBPATH environment variable.
#
# 1.1.3    01/10/2017 by Matthew Jefferson
#           -Uploaded the library to PyPI.
#
# 1.1.4    01/10/2017 by Matthew Jefferson
#           -Messed up 1.1.3. Uploading the updated code.
#
# 1.1.5    01/10/2017 by Matthew Jefferson
#           -Fixed a small issue with integers.
#
###############################################################################

###############################################################################
# Copyright (c) 2016 SPIRENT COMMUNICATIONS OF CALABASAS, INC.
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
#  3. Neither the name SPIRENT, SPIRENT COMMUNICATIONS, SMARTBITS, Spirent 
#     TestCenter, Avalanche, nor the names of its contributors may be used to 
#     endorse or promote products derived from this software without specific 
#     prior written permission.
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

from __future__ import print_function

    
import sys

import getpass          # Used to retrieve the username.
import ast              # Used to convert strings to dict.
import os

from shutil import copyfile     # Used for copying files.

# The following are required for logging.
import logging
import datetime
import inspect
#from inspect import getargvalues, stack

if sys.hexversion >= 0x03000000:
   from tkinter import *
else:
   from Tkinter import *

class AVA:
    ###############################################################################
    ####
    ####    Public Methods
    ####
    ###############################################################################
    def login(self, userName="", password="", mode="", workspace="", tempworkspace=False):   
        """
        Description:
            Starts a new Avalanche Automation session or connects to an already existent session.
            Uses the default workspace, named Default, if "workspace=<workspaceName> 
            option - value pair has not been defined. Use the "workspace=<workspaceName>" 
            option - value pair to log in to an existing custom workspace, or to create a new 
            custom workspace, and log in to it.         
        """
        self.LogCommand()

        tclcode = "av::login"

        if userName != "" or password != "" or mode != "":
            if userName == "":
                userName = getpass.getuser()

            tclcode += " " + userName

        if password != "" or mode != "":
            if password == "":
                password = "default"

            # The password is currently ignored.
            tclcode += " " + password

        if mode != "":
            tclcode += " " + mode

        if tempworkspace:
            tclcode += " -temp-workspace"
        else:            
            if workspace != "":
                tclcode += " -workspace " + workspace
        
        result = self.Exec(tclcode)

        logging.info("ABL Log Location: " + self.tcl.eval("av::get system1 -ablLogLocation"))
        logging.info("Username: " + self.tcl.eval("av::get system1 -user"))
        logging.info("Workspace: " + self.tcl.eval("av::get system1 -workspace"))
        logging.info("Project Path: " + self.tcl.eval("av::get system1.metainfo -defaultDirectoryPath"))

        logging.debug(" - Python result  - " + str(result))
        return result

    #==============================================================================
    def logout(self):
        """
        Description:
            Closes the session, stops any running test, saves any non-saved data 
            on the disk, and stops the Avalanche Automation (java) process by 
            default, when either no argument is provided or when the shutdown 
            argument is provided (see examples). The only difference between the 
            shutdown and no-shutdown arguments is stopping or not stopping the 
            Avalanche Automation (java) process. The av.logout command with the 
            no-shutdown argument will leave the Avalanche Automation (java) 
            process running after the user logs out.
            If the temporary workspace is used (see av.login command description),
            the av.logout command deletes all the tests and test results that were
            created during the session.
        """
        self.LogCommand()
        result = self.Exec("av::logout")
        logging.debug(" - Python result  - " + str(result))
        return result

    #==============================================================================
    def config(self, objecthandle, **kwargs):
        """ 
        Description
            Updates the attribute of an object with a new value, if it meets the validation rules.

        Syntax
            av.config objectHandle attrName=value [, [attrName=value] ...]
            av.config objectHandle DANPath=value [, [DANPath=value] ...]
            av.config DDNPath attrName=value [, [attrName=value] ...]
            av.config DDNPath DANPath=value [, [DANPath=value] ...]            

        Comments
            The av::config command modifies the value of one or more object attributes, if it meets 
            the validation rules. Note: If you attempt to modify an attribute for a read-only object,
            or a specified value does not meet the validation rules, the av::config command raises 
            an exception.
            -When you modify object attributes, use attrName/value pairs. 
             For example: av::config project1 -name Project1
            -You can use Direct Descendant Notation (DDN) to identify the object and Descendant 
             Attribute Notation (DAN) to identify the attribute. 
             For example:
                A DAN path is a dotted path name beginning with a sequence of one or more object types, 
                and ending with an attribute name. Avalanche Automation combines the handle (or the 
                DDNPath) with the DANPath to resolve the attribute reference. The path must identify 
                a valid sequence of objects in the Avalanche Automation data model hierarchy.
                  av::config $project.test -name Test1
                  av::config $project -userprofile.name SSLv3                    
             In both DDN and DAN paths, an object type name may have an index suffix (an integer in 
             parentheses) to reference one of multiple children of the same type.
             For more information about these notations, see Referencing Objects: Object Paths. 

        Return Value
            None. Errors are raised as exceptions, encoded as string values that describe the error condition.

        Example            
            av.config("userprofile1", dnsRetries=10)
            av.config("userprofile1", cifsng.cifsngDataRandomization=true)
            av.config(project + ".test.userprofile", sipng.firstRTPPort=1026)
        """
        self.LogCommand()
        tclcode = 'av::config ' + objecthandle + ' '

        for key in kwargs:
            #tclcode = tclcode + ' ' + '-' + key + ' "' + str(kwargs[key]) + '"'
            reg = re.compile("\[")
            if reg.match(str(kwargs[key])):
                # This is a Tcl command (eg: [NULL]).
                tclcode = tclcode + ' ' + '-' + key + " " + str(kwargs[key])
            else:
                tclcode = tclcode + ' ' + '-' + key + ' {' + str(kwargs[key]) + '}'

        result = self.Exec(tclcode)
        logging.debug(" - Python result  - " + str(result))                    
        return result

    #==============================================================================
    def get(self, objecthandle, *args):
        """
        Description:
            Returns the value(s) of one or more object attributes, or a set of 
            object handles.
            Returns a single value if a single attribute is specified, otherwise,
            a dictionary is returned.

        Syntax:
            av.get handle [attributeName]
            av.get handle [DANPath]
            av.get DDNPath [attributeName]
            av.get DDNPath [DANPath]
            av.get handle | DDNPath [relationName]   

        Comments
            The av.get command returns the value of one or more object attributes, or, 
            in the case of relation references, one or more object handles.
                -The handle identifies the object from which data will be retrieved. 
                 If you do not specify any attributes, Avalanche Automation returns the 
                 values for all attributes and all relations defined for the object.
                -attributeName identifies an attribute for the specified object.
                -The DANPath (Descendant Attribute Notation path) is a dotted path name 
                 beginning with a sequence of one or more relation names, and ending with 
                 an attribute name. A relation name may have an index suffix (an integer 
                 in parenthesis) to reference one of multiple children of the same type. 
                 Avalanche Automation combines the handle (or the DDNPath) with the DANPath 
                 to resolve the attribute reference. The path must identify a valid 
                 sequence of objects in the test hierarchy. For example:
                      av.get(project, "test(1).name")
                -Avalanche Automation combines the object and attribute specifications to 
                 retrieve the value of the attribute for the first Test object child of the 
                 project.
                -The DDNPath (Direct Descendant Notation path) is a dotted path name sequence. 
                 The sequence begins with an object handle, followed by one or more relation 
                 names. The path must identify a valid sequence of objects in the data model 
                 hierarchy. Avalanche Automation returns data for the object identified by 
                 the last name in the sequence. For example:
                      av.get("project1.test", "name")
                 In this case, Avalanche Automation returns the value of the name attribute 
                 for the first Test child of the specified Project object.
                -If there is more than one instance of a particular object type, as children
                 of the specified object, use an index notation. (In the example above, the 
                 index value 1 is implied.) Avalanche Automation assigns index values in the 
                 order of object creation. For example:
                      av.get(project + ".test(2)")
            Avalanche Automation returns the attributes and all relations for the second
            Test object child of the specified Project object.
            When you use a relation reference with the get function, it provides access 
            to one or more objects connected to the object identified by a handle (or DDNPath). 
            Specify a name for the relation reference, using relationName. 
            For example:
                av.get(project, "Tests")
            This function call returns the handle(s) for the Test child object(s) of the 
            Project object.

        Return Value
            When you retrieve one or more attributes, av.get returns the single attribute 
            value or a dictionary. If you do not specify any attributes, the get function 
            can return either a single value or a dictionary.
            Errors are raised as exceptions, encoded as string values that describe the 
            error condition.

        Example
            av.get(project, "path")
            av.get(test, "netrworkprofile.tcpoptions.tcptimeout")
            av.get(project + "userprofile(2)", "nfs.dataRandomization")
        """
        self.LogCommand()
        tclcode = "av::get " + objecthandle

        for key in args:
            tclcode += " -" + key

        result = self.Exec(tclcode)

        # Determine if we need to return a dictionary or just the result of the command.
        if len(args) == 0:
            result = self.List2Dict(result)

        logging.debug(" - Python result  - " + str(result))
        return result

    #==============================================================================
    def perform(self, command, objecthandle, **kwargs):
        """        
        Description
            Executes a custom command or subcommand for the specified object.

        Syntax
            av.perform(<sub-command>, <handle>, [[<argument>], [...])
        Comments
            The av.perform command executes a sub-command. See the Avalanche Automation 
            Object Reference document (Avalanche_Auto_Obj_Ref.pdf) for a complete list 
            of sub-commands.

        Return Value
            The return value depends on the sub-command type, and is absent in most cases.
            Errors are raised as exceptions, encoded as string values that describe the 
            error condition.

        Example       
            av.perform("save", "system1")
            av.perform("export", "system1", projectsTestsHandles="test1")
        """
        self.LogCommand()

        tclcode = "av::perform " + command + " " + objecthandle

        if command == "SetInterfaceAttributes":
            # Unfortunately, engineering has a sick sense of humor.
            # This command IGNORES the argument names, and instead makes the arguments position dependent.
            # One word...What.The.F%$#.
            # av::perform SetInterfaceAttributes $tests_handle.topology.interface(1) -port 10.140.99.40/1/1 -physIf 0 -interfaceDisplayString 0,0 -interfaceLocationString 0,0

            port           = kwargs["port"] 
            physIf         = kwargs["physIf"]
            display        = kwargs["interfaceDisplayString"]
            locationstring = kwargs["interfaceLocationString"]

            tclcode += " -engineering " + port + " -please " + str(physIf) + " -fix " + display + " -this " + locationstring

        elif command == "Export":
            # For this command, the arguments MUST be in a specific order (don't ask me why).
            test    = kwargs["projectstestshandles"] 

            tclcode += " -projectstestshandles " + test

            if "options" in kwargs:
                tclcode += ' -options "' + kwargs["options"] + '"'

            if "newpath" in kwargs:
                newpath = kwargs["newpath"]
                tclcode += ' -newpath "' + kwargs["newpath"] + '"'            

        else:
            for key in kwargs:
                tclcode = tclcode + " " + "-" + key + ' "' + str(kwargs[key]) + '"'


        result = self.Exec(tclcode)
        logging.debug(" - Python result  - " + str(result))
        return result

    #==============================================================================
    def apply(self, testHandle, trial=0, continueIfAlreadyRunning=0, removeOldTest=0, rerun=0):
        """
        Description
            Starts a specified test on the devices.

        Syntax
            av.apply(<testHandle>, [trial], [continueIfAlreadyRunning], [removeOldTest], [rerun])
        
        Comments
            The apply command saves the configuration, performs validation, uploads 
            test configuration to devices, and runs (or reruns) the test. This call
            is asynchronous, so the client will get control right after the call. 
            The standard async_method_completed event will be sent after the test is
            started; the specific test state events will also be sent. For more 
            information, please refer to Running the Test.
        
        Return Value
            The request id. Errors are raised as exceptions, encoded as string values
            that describe the error condition.
        
        Example       
            av.apply(testHandle)
            av.apply(testHandle, 1)
        """         
        self.LogCommand()
        tclcode = "av::apply " + testHandle + " " + str(trial) + " " + str(continueIfAlreadyRunning) + " " + str(removeOldTest) + " " + str(rerun)

        result = self.Exec(tclcode)
        logging.debug(" - Python result  - " + str(result))
        return result

    #==============================================================================
    def connect(self, ipAddress, type="", executesynchronous=""):
        """
        Description
            Connects to the specified device.
        
        Syntax
            av.connect(<ipAddress>, [<type>="STC|Appliance"], [<executesynchronous>=false|true])
        
        Comments
            After this command call is completed, the device will be added to the device 
            list under the PhysicalChassisManager object. If Avalanche Automation is already 
            connected to this device, then it gets the latest state from the device and returns 
            the existent handle. The av::connect command runs in synchronous mode by default. 
            The mode can be changed by using the -executesyschronous Boolean option.
            If a -type is not specified, the Appliance platform will be assumed and tried. If 
            Avalanche TclAPI fails to connect, then the Spirent TestCenter chassis is assumed 
            to be the hardware platform, and the connection will be retried.
        
        Return Value
            The request id, if run in asynchronous mode; the chassis/appliance handle, if run 
            in synchronous mode (default). Otherwise, errors will be displayed on the screen.
        
        Example        
            av.connect("10.72.55.80")
        """
        self.LogCommand()
        tclcode = "av::connect " + ipAddress

        if type != "":
            tclcode += " -type " + type

        if executesynchronous != "":
            tclcode += " -executesynchronous " + executesynchronous

        requestid = self.Exec(tclcode)
        logging.debug(" - Python result  - " + str(requestid))
        return requestid

    #==============================================================================
    def create(self, objecttype, under, **kwargs):
        """
        Description
            Creates a new object of the specified type, under the specified parent.

        Syntax
            av.create(<objecttype>, [attr=<value>] ...])
        
        Comments
            The av.create command creates one or more Avalanche Automation objects under the 
            specified parent object. When you call the create function, you specify the type(s) 
            of one or more objects to be created. You can specify:
                -An object type name (such as the Project object or the Test object). For example: 
                 av.create("project", under="system1", name="Project1")
                -When you create an object, you must specify the handle of the parent object 
                 under which the new object is to be created.
                -When you create an object, you can also set the object attributes at the same 
                 time. To set attributes, specify one or more attribute name/value pairs.
                -If you specify attribute name/value pairs, together with an object type path, 
                 Avalanche Automation applies the attribute values to the object associated 
                 with the last name specified in the object type path. In the following example, 
                 Avalanche Automation creates a Project object. When Avalanche Automation creates 
                 the Project object, it sets the name attribute to Project1 and the path attribute 
                 to C:\Project\Project1.
                    av.create("project", under="system1", name="Project1", path="C:/Projects/Project1")
                -You can specify a Descendant Attribute Notation (DAN) path as part of the attribute
                 reference. Avalanche Automation uses the specified object type to create the primary
                 object, and the DAN path to create any additional objects. For information about path 
                 name specification, see Object, Attribute, and Relation References.
        
        Return Value
            The av.create command returns a unique string value that is the object handle 
            for the object specified in the function call. (The av.create function returns only 
            the handle for the primaryobject that is created. To obtain the handles for any 
            descendent objects that are created, use the get function to retrieve the child objects.)
        
        Example        
            project = av.create("project", under="system1", name="Project1")
            test = av.create("tests", under=project, name="Test1", testType="deviceComplex")
            sp = av.create("ServerProfiles", under=project, name="ServerProfile", applicationProtocol="HTTP", http.keepAlive="on")        
        """
        self.LogCommand()
        tclcode = "av::create " + objecttype + " -under " + under

        for key in kwargs:
            tclcode = tclcode + " " + "-" + key + " " + str(kwargs[key])

        objecthandle = self.Exec(tclcode)
        logging.debug(" - Python result  - " + str(objecthandle))
        return objecthandle        

    #==============================================================================
    def delete(self, handle):
        """
        Description
            Deletes a node from the data model.

       Syntax
            av.delete(<handle>)
            av.delete(<DDNPath>)

        Comments
            Deletes the object identified by the objectHandle or DDNPath from the 
            data model. Avalanche Automation also deletes all descendants of the 
            specified object (if any).
        
        Return Value 
            None. 
            Errors are raised as exceptions, encoded as string values that 
            describe the error condition.
            
        Example            
            av.delete(projectHandle)
            av.delete(projectHandle + ".userp")
        """
        self.LogCommand()
        tclcode = "av::delete " + handle

        result = self.Exec(tclcode)
        logging.debug(" - Python result  - " + str(result))
        return result

    #==============================================================================
    def disconnect(self, ipAddress):
        """
        Description
            Disconnects from the specified device and removes it from the device 
            list under the PhysicalDevicesManager object.

        Syntax
            av.disconnect(<ipAddress>)
    
        Comments
            Does nothing, if Avalanche Automation was not connected to specified device.
        
        Return Value
            None. Errors are raised as exceptions, encoded as string values that 
            describe the error condition.
    
        Example
            av.disconnect("10.50.20.77")
        """
        self.LogCommand()
        tclcode = "av::disconnect " + ipAddress
        result = self.Exec(tclcode)
        logging.debug(" - Python result  - " + str(result))
        return result

    #==============================================================================
    def getEvents(self):
        """
        Description
            Gets the events that were generated by Avalanche Automation for this session, 
            from the latest av.getEvents call.
    
        Syntax
            av.getEvents
        
        Comments
            None.
  
        Return Value
            A list of generated event dictionaries. Refer to Events Handling for event object details.
            Errors are raised as exceptions, encoded as string values that describe the error condition.
      
        Example
            av.getEvents        
        """
        self.LogCommand()
        tclcode = "av::getEvents"

        tclresult = self.Exec(tclcode)

        # The goal is to create a Python list of dictionaries, where element of the list
        # is a Avalanche Event dictionary with the keys "message", "additional" and "name".
        # The "additional" key is also a dictionary.
        eventlist = []

        # First step is to break the Tcl list into a Python list (using Tcl).
        tclcode =  "set pythonlist {};"
        tclcode += "foreach event [list " + tclresult + "] {"
        tclcode += "    regsub -all {\\n} $event {} event;"
        tclcode += "    append pythonlist \\\"$event\\\" , "
        tclcode += "};"        
        tclcode += "return $pythonlist"
        tclresult = self.tcl.eval(tclcode)
        # This step is what converts the Tcl string to a list.
        listofstrings = ast.literal_eval(tclresult)

        # Now convert each list element to a dictionary.
        for event in listofstrings:   
            # Construct a Python dictionary using Tcl.
            # This is done because it is MUCH easier for Tcl to deal with Tcl lists.
            tclcode =  "set pythondict \{;"
            tclcode += "foreach element [list " + event + "] {"
            tclcode += "    append pythondict \"\\\"[lindex $element 0]\\\": \\\"[lindex $element 1]\\\", \""
            tclcode += "}; append pythondict \}; return $pythondict"

            tclresult = self.tcl.eval(tclcode)
            eventdict = ast.literal_eval(tclresult)

            # The "addtional" field may contain an additional list of information.
            # This is also converted into a dictionary.
            if eventdict["additional"] != "":
                tclcode  = "set pythondict \{;"
                tclcode += "foreach element [list " + eventdict["additional"] + "] {"
                tclcode += "    append pythondict \"\\\"[lindex $element 0]\\\": \\\"[lindex $element 1]\\\", \""
                tclcode += "}; append pythondict \}; return $pythondict"

                tclresult = self.tcl.eval(tclcode)
                eventdict["additional"] = ast.literal_eval(tclresult)

            eventlist.append(eventdict)

        logging.debug(" - Python result  - " + str(eventlist))
        return eventlist

    #==============================================================================
    def getSessions(self):
        """
        Description
            Retrieves the list of registered sessions on Avalanche Automation.

        Syntax
            av.getSessions
            
        Comments
            You can use this function without being logged in to an Avalanche Automation session.
    
        Return Value
            A list of registered sessions.
        
        Example
            av.getSessions        
        """
        self.LogCommand()
        tclcode = "av::getSessions"

        tclresult = self.Exec(tclcode)     
        logging.debug(" - Python result  - " + str(tclresult))
        return tclresult

    #==============================================================================
    def release(self, portAddress):
        """
        Description
            Releases the specified port.

        Syntax
            av.release(<portAddress>)
    
        Comments
            You can only release ports that you have reserved. For information about 
            port reservations, and the syntax for identifying ports, see the description 
            of the reserve function.
        
        Return Value
            None. Errors are raised as exceptions, encoded as string values that 
            describe the error condition.
            
        Example
            av.release("10.50.70.82/1/1")
        """       
        self.LogCommand()     
        tclcode = "av::release " + portAddress

        result = self.Exec(tclcode)         
        logging.debug(" - Python result  - " + str(result))
        return result

    #==============================================================================
    def reserve(self, portAddress):
        """
        Description
            Reserves the specified port.
        
        Syntax
            av.reserve(<portAddress>)

        Comments
            Reserves the specified port for the username that was specified/determined
            upon the av.login command. You must be connected to the chassis (or appliance)
            before you can reserve ports. The port can only be reserved if it is available 
            (that is, if not disabled or reserved by another user). To force reserve a 
            port, use the av.perform("reservePort") command.

        Return Value
            Handle to the PhysicalPort object.
            Errors are raised as exceptions, encoded as string values that describe 
            the error condition.
            
        Example
            av.reserve("10.50.70.82/2/1")
        """
        self.LogCommand()
        tclcode = "av::reserve " + portAddress

        porthandle = self.Exec(tclcode)         
        logging.debug(" - Python result  - " + str(porthandle))
        return porthandle

    #==============================================================================
    def reserveAll(self, test, force=False):
        # Reserve all of the interfaces defined in the test.
        # Do this by determining the existing interfaces, and then reserving them.
        # The user only need set the "port" attribute for each interface object
        # before calling this method.
        #
        # This method replaces the following native calls:
        #   perform("SetInterfaceAttributes")
        #   connect(<chassisip>)
        #   perform("ReservePort") or reserve()
        
        
        # We need to find the information for the "SetInterfaceAttributes" command.
        # It is found in the physical port information when you connect to the hardware/virtual.
        
        for config in self.get(test, "configuration").split():
            for topology in self.get(config, "topology").split():
                for interface in self.get(topology, "interface").split():
                    location = self.get(interface, "port")

                    # We need to connect to the chassis to pull the physical port information.
                    # We could do this more efficiently (only connect once per unquie chassis).                
                    chassisip = self.get(interface, "adminIPAddress")
                    self.connect(chassisip)

                    # Locate the physical port referenced by the "location".
                    for chassis in self.get("system1.physicalchassismanager", "physicalchassis").split():
                         for module in self.get(chassis, "physicaltestmodules").split():
                            for port in self.get(module, "ports").split():
                                if self.get(port, "location") == location:
                                    # We found the port. Now map and reserve it.
                                    physif = self.get(port, "physIf")
                                    ids    = self.get(port, "locationDisplayString")
                                    ils    = self.get(port, "locationString")

                                    self.perform("SetInterfaceAttributes", interface, port=location, physIf=physif, interfaceDisplayString=ids, interfaceLocationString=ils)

                                    if force:
                                        self.perform("ReservePort", "system1", portaddress=location, force="force")
                                    else:
                                        self.perform("ReservePort", "system1", portaddress=location)
        return

    #==============================================================================
    def releaseAll(self):
        # Release all ports that are currently reserved by this process.

        for chassis in self.get("system1.physicalchassismanager", "physicalchassis").split():
             for module in self.get(chassis, "physicaltestmodules").split():
                for port in self.get(module, "ports").split():
                    if self.get(port, "reservationState") == "Reserved by User":

                        self.release(self.get(port, "location"))
        return        

    #==============================================================================
    def setABLLogAutoCleanup(self, bEnabled):
        """
        Description
            Automatically removes the current test's log files at the end of the test run.
        
        Syntax
            av.setABLLogAutoCleanup(<bEnabled>)

        Comments
            Automatically removes the current test's log files at the end of the test run.

        Return Value
            None.

        Example
            av.setABLLogAutoCleanup(1)
        """
        self.LogCommand()
        tclcode = "av::setABLLogAutoCleanup " + str(bEnabled)

        result = self.Exec(tclcode)        
        logging.debug(" - Python result  - " + str(result))
        return result

    #==============================================================================
    def downloadABLlogs(self, path=""):
        """
        Description
            Don't know...it's not a documented command.
        
        Syntax
            av.downloadABLlogs(<path>)

        Comments
            I'm assuming this downloads the ABL logs to the specified path.

        Return Value
            None.

        Example
            av.downloadABLlogs()
        """
        self.LogCommand()
        if path == "":
            path = os.path.abspath(os.getcwd())

        tclcode = "av::downloadABLlogs " + path

        result = self.Exec(tclcode)        
        logging.debug(" - Python result  - " + str(result))
        return result

    #==============================================================================
    def subscribe(self, side, viewAttributesList):
        """
        Description
            Subscribes to view the list of runtime statistics that users specify.
            
        Syntax
            av.subscribe(<side>, <viewAttributesList>)
            
        Comments
            Subscribes to view runtime statistics for those that user specifies as 
            viewAttributesList. The attribute names should be one of the supported 
            statistics names, for example, http,successfulConns or http,attemptedConns. 
            Wildcards are also supported, such as http*. Please refer to Appendix A. 
            List of Runtime Statistics for full list of runtime statistics.
        
        Return Value
            Returns the handle to the ResultDataSet object, which consists of the 
            ResultDataObject with statistics values. By default, the returned 
            ResultDataSet will only contain the latest actual values. In order to 
            obtain the values from a specific point in time during the test run, user
            must add the 'all' keyword to the list of viewAttributesList. See Runtime 
            statistics for more information.

        Example            
            av.subscribe("client", ["http,successfulConns", "http,attemptedConns"])
            av.subscribe("server", "http*")
        """      
        self.LogCommand()
        tclcode = "av::subscribe " + side + " [list " + " ".join(viewAttributesList) + "]"

        resultdataset = self.Exec(tclcode)         
        logging.debug(" - Python result  - " + str(resultdataset))
        return resultdataset

    #==============================================================================
    def unsubscribe(self, handle):
        """
        Description
            Removes a subscription for the specified ResultDataSet.
            
        Syntax
            av.unsubscribe(<handle>)
            
        Comments
            The av.unsubscribe command removes a subscription for the specified handle 
            of the ResultDataSet object that was returned by the subscribe function.
            
        Return Value
            None. Errors are raised as exceptions, encoded as string values that 
            describe the error condition.
            
       Example
            av.unsubscribe(rdsHandle)
        """
        self.LogCommand()
        tclcode = "av::unsubscribe " + handle

        result = self.Exec(tclcode)         
        logging.debug(" - Python result  - " + str(result))
        return result
    
    #==============================================================================
    def waitUntilCommandIsDone(self, requestId=""):
        """
        Description
            Waits until the command specified by the request id is complete.
            
        Syntax
            av.waitUntilCommandIsDone(<requestId>)
            
        Comments
            This function waits until the command, specified by request id, is out 
            of the PENDING state and completes its job. This is useful for asynchronous 
            commands. If the requestId is not specified, then it waits until any 
            command is completed.
            
        Return Value
            Result of an asynchronous command.
            Errors are raised as exceptions, encoded as string values that describe the error condition.
        
        Example
            av.waitUntilCommandIsDone(av.connect("10.50.70.82", executesynchronous=False))

            CAUTION: "av.waitUntilCommandIsDone" will time out if the command it waits for does
            not complete in a certain time.        
        """
        self.LogCommand()
        tclcode = "av::waitUntilCommandIsDone"


        # NOTE: Not yet tested!


        if requestId != "":
             tclcode += " " + requestId

        tclresult = self.Exec(tclcode)         
        logging.debug(" - Python result  - " + str(tclresult))
        return tclresult

    #==============================================================================
    def handleOf(self, parentHandle, relationName, objectName):
        """
        Description
            Retrieves the handle of an object by its type name, parent handle, and 
            name of the object.
    
        Syntax
            av.handleOf(<parentHandle>, <relationName>, <objectName>)
    
        Comments
            Searches children that are identified by the relation name of the parent 
            object, identified by a handle, and retrieves the handle of the object 
            named objectName. The object that is searched should have a name attribute.

        Return Value
            Handle of the object.
            Errors are raised as exceptions, encoded as string values that describe the 
            error condition.

        Example           
            av.handleOf("project1", "serverprofiles", "IPv6")
            av.handleOf("system1", "projects", "Project1")
        """
        self.LogCommand()
        tclcode = "av::handleOf " + parentHandle + " " + relationName + " " + objectName
        objecthandle = self.Exec(tclcode)
        logging.debug(" - Python result  - " + str(objecthandle))
        return objecthandle

    #==============================================================================
    def nodeExists(self, handle):
        """
        Description
            Checks whether the object specified by the handle exists in the data model.
        
        Syntax
            av.nodeExists(<handle>)
                
       Comments
            Checks whether the object specified by the handle exists in the data model 
            (i.e. the get function will return information about the object).

        Return Value
            1, if the object exists in the data model, otherwise 0.
        
        Example        
            av.nodeExists("project1")
            av.nodeExists(testHandle)
        """
        self.LogCommand()
        tclcode = "av::nodeExists " + handle
        tclresult = self.Exec(tclcode)
        result = ast.literal_eval(tclresult)
        logging.debug(" - Python result  - " + str(result))
        return result

    #==============================================================================
    def createProject(self, **kwargs):
        """
        Description
            Creates a new project.

        Syntax
            av::createProject(project=<name>)

        Comments
            Creates a new Project object in the system, with a specified name.

        Return Value
            Handle of the newly created object.
            Errors are raised as exceptions, encoded as string values that describe the error condition.

        Example
            av.createProject(project="Project1")
        """
        self.LogCommand()
        tclcode = "av::createProject"

        for key in kwargs:
            tclcode = tclcode + " " + "-" + key + " " + str(kwargs[key])

        objecthandle = self.Exec(tclcode)
        logging.debug(" - Python result  - " + str(objecthandle))
        return objecthandle

    #==============================================================================
    def createTest(self, **kwargs):
        """
        Description
            Creates a new Test object under a specified Project object.
        
        Syntax
            av.createTest(project=<projectHandle>, test=<testName>, type=<testType>
            av.createTest(project=<projectName>, test=<testName>, type=<testType>
        
        Return Value
            Handle of the newly created Test object.
            Errors are raised as exceptions, encoded as string values that describe the error condition.            
        
        Comments
            Creates a new test, under the specified project, with the specified name of a specified type.

        Example
           av.createTest(project="project1", test="Test1", type="deviceComplex")
        """
        self.LogCommand()
        tclcode = "av::createTest"

        for key in kwargs:
            tclcode = tclcode + " " + "-" + key + " " + str(kwargs[key])

        objecthandle = self.Exec(tclcode)
        logging.debug(" - Python result  - " + str(objecthandle))
        return objecthandle

    
    #==============================================================================
    def getOrCreateNode(self, parenthandle, relationname, arguments):
        """
        Description
            Gets handle of node under specified parent with specified name and 
            relation from parent. If the node does not exist, this function creates it.

        Syntax
            av.getOrCreateNode(<parentHandle>, <relationName>, args)
        
        Return Value
            The getOrCreateNode command returns a handle which is under parent with 
            specified name and relation from parent.

        Example
            httpbody_handle=av.getOrCreateNode(projectHandle, "httpbodies", "Default")
            tests_handle=av.getOrCreateNode(testHandle, "configuration", "Test_0001")
        """
        self.LogCommand()
        tclcode = "getOrCreateNode " + parenthandle + " " + relationname + " " + arguments

        objecthandle = self.Exec(tclcode)
        logging.debug(" - Python result  - " + str(objecthandle))
        return objecthandle

    #==============================================================================
    def normalizePath(self, path):
        self.LogCommand()
        result = os.path.abspath(path)
        logging.debug(" - Python result  - " + str(result))
        return result

    #==============================================================================
    def waitEvent(self, command):   
        self.LogCommand() 
        result = self.Exec("av::waitEvent " + command)
        logging.debug(" - Python result  - " + str(result))
        return result

    #==============================================================================
    def DebugLogFile(self, status):
        """
        Description
            Turns some logging on or off.

        Syntax
            av.DebugLogFile("on")
        
        Return Value
            None.
        """        
        self.LogCommand()
        result = self.Exec("av::DebugLogFile " + status)
        logging.debug(" - Python result  - " + str(result))
        return result

    #==============================================================================
    def StopStatusMsg(self, status):
        self.LogCommand()
        result = self.Exec("av::StopStatusMsg " + status)
        logging.debug(" - Python result  - " + str(result))
        return result

    #==============================================================================
    def AnalyzeABLEvents(self, event):       
        self.LogCommand() 
        result = self.Exec("av::AnalyzeABLEvents " + event)
        logging.debug(" - Python result  - " + str(result))
        return result

    ###############################################################################
    ####
    ####    Private Methods
    ####
    ###############################################################################

    def Exec(self, command):
        logging.debug(" - Tcl command - " + command)
        
        try:
            result = self.tcl.eval(command)

        except Exception as errmsg:
            logging.error(errmsg)            
            raise
        
        logging.debug(" - Tcl result  - " + result)
        return result

    #==============================================================================
    def List2Dict(self, result):
        # Converts a Tcl list (which is a string) into a Python dictionary.       

        # Use Tcl to convert the list into a Python-friendly dict string.
        tclcode =  "proc isnumeric value {                           \n\
                        if {![catch {expr {abs($value)}}]} {         \n\
                            return 1                                 \n\
                        }                                            \n\
                        set value [string trimleft $value 0]         \n\
                        if {![catch {expr {abs($value)}}]} {         \n\
                            return 1                                 \n\
                        }                                            \n\
                        return 0                                     \n\
                    }                                                \n\
                    proc tclList2Dict { args } {                     \n\
                        set result $args                             \n\
                        set output {}                                \n\
                        foreach {key value} $result {                \n\
                            regsub {^-} $key {} key                  \n\
                            if { [isnumeric $value] } {              \n\
                                append output \"'$key': $value, \"   \n\
                            } else {                                 \n\
                                regsub -all {'} $value {\\'} value   \n\
                                regsub -all {\"} $value {\\\"} value \n\
                                append output \"'$key': '$value', \" \n\
                            }                                        \n\
                        }                                            \n\
                                                                     \n\
                        regsub {, $} $output {} output               \n\
                        set output [list $output]                    \n\
                        return $output                               \n\
                    }"

        # This eval instantiates the Tcl procedures.
        self.tcl.eval(tclcode)
        # This eval executes the Tcl procedure and returns the result.
        tclresult = self.tcl.eval("tclList2Dict " + result)

        # This command converts the Tcl string into a dict object.
        return ast.literal_eval(tclresult)

    #==============================================================================
    def convertEventString(self, tclstring):
        # The goal is to create a Python list of dictionaries, where element of the list
        # is a Avalanche Event dictionary with the keys "message", "additional" and "name".
        # The "additional" key is also a dictionary.
        eventlist = []

        # First step is to break the Tcl list into a Python list (using Tcl).
        tclcode = "set pythonlist {} \n \
                   foreach event [list " + tclstring + "] {\n \
                       append pythonlist \\\"$event\\\" , \n \
                   } \n\
                   return $pythonlist"
        tclresult = self.tcl.eval(tclcode)
        # This step is what converts the Tcl string to a list.
        listofstrings = ast.literal_eval(tclresult)

        # Now convert each list element to a dictionary.
        for event in listofstrings:   
            # Construct a Python dictionary using Tcl.
            # This is done because it is MUCH easier for Tcl to deal with Tcl lists.
            tclcode =  "set pythondict \{;"
            tclcode += "foreach element [list " + event + "] {"
            tclcode += "    append pythondict \"\\\"[lindex $element 0]\\\": \\\"[lindex $element 1]\\\", \""
            tclcode += "}; append pythondict \}; return $pythondict"

            tclresult = self.tcl.eval(tclcode)
            eventdict = ast.literal_eval(tclresult)

            # The "addtional" field may contain an additional list of information.
            # This is also converted into a dictionary.
            if eventdict["additional"] != "":
                tclcode  = "set pythondict \{;"
                tclcode += "foreach element [list " + eventdict["additional"] + "] {"
                tclcode += "    append pythondict \"\\\"[lindex $element 0]\\\": \\\"[lindex $element 1]\\\", \""
                tclcode += "}; append pythondict \}; return $pythondict"

                tclresult = self.tcl.eval(tclcode)
                eventdict["additional"] = ast.literal_eval(tclresult)

            eventlist.append(eventdict)

        return eventlist  

    #==============================================================================
    def LogCommand(self):
        """
        Log the calling function to the log, including its arguments.
        """        
        # Retrieve the args for the command.
        posname, kwname, args = inspect.getargvalues(inspect.stack()[1][0])[-3:]
        posargs = args.pop(posname, [])
        args.update(args.pop(kwname, []))

        functionname = inspect.currentframe().f_back.f_code.co_name       

        # Output the command in a format that looks like normal Python syntax.
        logmsg = " - Python command - " + functionname
        arguments = ""
        for key in args:            
            if key != "self":                
                value = args[key]
                if value == "":
                    value = '""'

                arguments += key + "=\"" + str(value) + "\", "

        if arguments != "":
            # Remove the final comma and space (", ").
            arguments = arguments[:-2]

        logmsg += "(" + arguments + ")"

        logging.debug(logmsg)
        return                

    #==============================================================================
    def __init__(self, apipath=None, logpath=None, loglevel="DEBUG"):
        """
        Load the Avalanche API and initialize the Python environment.

        'apipath' optionally specifies the location of the Avalanche API installation.
        'logpath' optionally specifies the location where the logs are to be stored.

        Returns None.
        """

        # Construct the log path.            
        if logpath:
            self.logpath = logpath
        else:
            defaultlogpath = "~/Spirent/Avalanche/Logs/"

            now = datetime.datetime.now()
            defaultlogpath += now.strftime("%Y-%m-%d-%H-%M-%S")
            defaultlogpath += "_PID"
            defaultlogpath += str(os.getpid())
            defaultlogpath = os.path.expanduser(defaultlogpath)
            
            # The environment variable overwrites the default path.    
            self.logpath = os.getenv("AVA_LOG_OUTPUT_DIRECTORY", defaultlogpath)        

        self.logpath = os.path.abspath(self.logpath)
        self.logfile = os.path.join(self.logpath, "avalanche_python.log")        

        if not os.path.exists(self.logpath):
            os.makedirs(self.logpath)

        # NOTE: Consider limiting the number of log directories that are created.
        #       It would mean deleting older directories.

        #16/05/18 11:03:53.717 INFO  3078268608 - user.scripting       - stc::get automationoptions -suppressTclErrors
        #16/05/18 11:03:53.717 INFO  3078268608 - user.scripting       - return  false
        #2016-05-19 14:05:56,382 UserID   =mjefferson
        #2016-05-19 14:05:56,382 Log Level=INFO

        if loglevel == "CRITICAL":
            loglevel = logging.CRITICAL
        elif loglevel == "ERROR":
            loglevel = logging.ERROR
        elif loglevel == "WARNING":
            loglevel = logging.WARNING
        elif loglevel == "INFO":            
            loglevel = logging.INFO
        else:
            # DEBUG is the default log level.
            loglevel = logging.DEBUG        
            
        logging.basicConfig(filename=self.logfile, filemode="w", level=loglevel, format="%(asctime)s %(levelname)s %(message)s")
        #logging.Formatter(fmt='%(asctime)s.%(msecs)03d',datefmt='%Y/%m/%d %H:%M:%S')
        # Add timestamps to each log message.
        #logging.basicConfig()
        # The logger is now ready.        

        logging.info("Spirent Avalanche Python API is starting up...")
        logging.info("OS Type      = " + os.name)
        logging.info("API Path     = " + apipath)
        logging.info("UserID       = " + getpass.getuser())
        logging.info("Log Level    = " + logging.getLevelName(loglevel))     
        logging.info("Current Path = " + os.path.abspath(os.getcwd()))   
        logging.info("Log Path     = " + self.logpath)

        # Instantiate the Tcl interpreter.
        self.tcl = Tcl()

        #if logpath != None:
        #    self.tclinterp.tk.call('eval', 'set ::env(STC_LOG_OUTPUT_DIRECTORY) [pwd]')

        # There are a number of Tcl packages required by Avalanche API.
        #   TclX
        #   Tcllib
        #   Tbcload
        #   msgcat
        #   ...there may be others        
        # Most are NOT included with the Avalanche API, so I have included them with
        # this wrapper in the ./lib subdirectory.

        if apipath:     
            # Add the path to the API so that Tcl can find it.
            libpath = apipath + "/lib"

            # Add brackets just in case the path has spaces.
            apipath = "{" + apipath + "}"
            libpath = "{" + libpath + "}"

            # Use this code if you want the TCLLIBPATH environment variable to be able 
            # to override the auto_path used by a script.            
            #self.Exec('lappend ::auto_path ' + apipath)
            #self.Exec('lappend ::auto_path ' + libpath)

            # This code makes sure that the Python wrapper always uses the exact path
            # specified by av.init(apipath).
            self.Exec('set ::auto_path "' + libpath + ' $::auto_path"')
            self.Exec('set ::auto_path "' + apipath + ' $::auto_path"')
            


        # Add the lib directory that is included with this module.
        generallibpath = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')        
        generallibpath = generallibpath + "/lib"

        if os.name == "nt":
            oslibpath = generallibpath + "/windows"
        elif os.name == "posix":
            oslibpath = generallibpath + "/linux"
        else:
            print("Unsupported OS:" + os.name)

        self.Exec('lappend ::auto_path [file normalize ' + generallibpath + ']')
        self.Exec('lappend ::auto_path [file normalize ' + oslibpath + ']')

        logging.info("Tcl Version  = " + self.tcl.eval("info patchlevel"))
        logging.info("Tcl ::auto_path = " + self.tcl.eval('set ::auto_path'))
        logging.info("Loading the Avalanche API in the Tcl interpreter...")
        self.Exec("package require av")

        # I hate these status messages.
        self.StopStatusMsg("on")

        return


###############################################################################
####
####    Main
####
###############################################################################
