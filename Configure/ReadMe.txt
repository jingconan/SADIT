/* Copyright (C) 
* 2011 - Jing Conan Wang, hbhzwj@gmail.com
* This program is free software; you can redistribute it and/or
* modify it under the terms of the GNU General Public License
* as published by the Free Software Foundation; either version 2
* of the License, or (at your option) any later version.
* 
* This program is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
* GNU General Public License for more details.
* 
* You should have received a copy of the GNU General Public License
* along with this program; if not, write to the Free Software
* Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
* 
*/
/**
* @file ReadMe.txt
* @brief ReadMe File for Automatic Config File Generator For fs simualtor
* @author Jing Conan Wang, hbhzwj@gmail.com
* @version 0.0
* @date 2011-10-24
*/

To Run the Program Just Need to type
>> python GenDotConf.py
in the command window
the output.dot in current directory will be the configuration file that
automatically generated.

You may need to install pydot before run this program. there is one copy in
tools folder. 
just go to pydot folder and type
>> python setup.py install

If you want to change the parameter, just revise the main() in GenDotConf.py
graphSize --> the size of the graph
link_attr --> the attributes for the link in the graph. 

The node ip will be automatically selected from validip.txt


