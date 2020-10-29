# XFLR5 XML Generator
Script to quickly generate xml files that XFLR5 can interpret as planes and analysis objects.
If you want to run many simulations where the plane or analysis change only in a few parameters, then you normally need to slowly create those objects through the XFLR5 interface.
With this script you can quickly generate hundreds of files and then import them into XFLR5.

## Usage:
Using this script is simple, but you will need to take a close look at the syntax of the input file if you truly want to take advantage of all its potential.

### Generate your model files from XML5
Go into XFLR5 and create a plane and analysis as you would normally. This program will change specific parameters of given XML files, so if you want a specific value for a parameter
that you don't want to change with this program, then set it in XFLR5 through the interface. For example, if I want all my plane models to use the same Y-Axe panel distribution, I
have to manually set that value in XFLR5. Once the plane and analysis are fully defined, export both objects as XML files.

A good idea is to manually do the first simulation in the set of simulations that you want to run. That way, you can check that the results are as expected and you have not forgotten
to set any parameter.

### Study your XML files
Once you have your XML files, you want to open them with a text editor and find the parameters that you want to change. The element names in XML are usually very descriptive, and
it will not be hard for you to identify the parameters of interest. For example, if I want to change the chord of your plane, then the XML element that controls that element is 
in the plane XML, under the path Plane/Sections/Section/Chord

### Write your input file
You have an example of a valid input file in https://github.com/juan-g-bonilla/xflr5-xml-generator/blob/master/usage_example/inputs.txt . We will use this example throughout
this section to illustrate different features.

The input file must be able to be parsed my numpy.loadtxt (https://numpy.org/doc/stable/reference/generated/numpy.loadtxt.html). Essentially, all rows must have the same number
of columns, and each row is separated by whitespace (that means that, for example, "NACA 2000" will be interpreted as two different columns, which may not be desired. A
solution is discussed in the following sections.)

#### The header
The header is the most important part of the input file. It's the first row of the file, and it defines what parameter is stored in each column.

Each column of the header is formated as "x:path", where "x" is either the letter "p" or "a" to specify if the element to change is in the XML of the plane or of the analysis respectively.
"path", on the other hand, must define a valid element or elements in the XML to be changed. The syntax is detailed in https://docs.python.org/2/library/xml.etree.elementtree.html#supported-xpath-syntax

One special header parameter is the "name". It will define the plane and analysis name, as well as the output file name for that specified row.

In the example, we can comment several interesting header paramenters:
* "Name": as we can see, the special header parameter "name" is case insensitive. We can use "NAME", "Name", "nAmE"...
* "p://Left_Side_FoilName": The initial "p" denotes that we want to modify the XML file of the plane. The "//Left_Side_FoilName" syntax means that we will search the entire XML
file until we find ALL elements called Left_Side_FoilName. This allows changing the Left_Side_FoilName parameter for many different sections in only one column.
* "p://Section[3]/Chord": Maybe we don't want to change all sections at the same time, as we did want with the Left_Side_FoilName. By specifying [int], we can select the specific
element to change. This header element will find the entire tree until it finds ONLY the third Section, and then change the chord of ONLY that section.
* "a:Polar/Reference_Area": A simpler approach. We select the analysis XML file by writing "a:", and then manually specify the path from the root: (root)->Polar->Reference_Area.
By doing so, we can ensure that only the Reference_Area element inside Polar is changed, and not any other Reference_Area element. It is good practice to manually write the path
instead of relying in "//" to search the tree for you, as the latter could return unexpected elements.

#### Data row
The simplest way to define a test case is to write in each column of a row the parameters that define a specific configuration that you want to simulate.
In the example file, we can see that row 2 (first row after header row) follows this approach. This row will make it so the program outputs a plane and an analysis xml named 
"Test_A", where the Left_Side_FoilName and Right_Side_FoilName of all sections is NACA 2030, the chord length of the 3rd section is 2.0 and the reference area for the analysis is 30.
Here you may have noticed a piece of special syntax: if we want to write a space within a parameter, we need to use the special notation "\_" ("NACA\_2030" interpreted as "NACA 2030").

This script can do much more than a simple row, however. We can use lists of parameters within a single row to define multiple configurations at the same time.
In the example file, we can see that in row 3, the 4th row has two parameters between (). The script will interpret this row as two different rows, one where "p://Section[3]/Chord"
is set to 0.4, and another where it is set to 0.2.

We can also define multiple lists of parameters in the same row. If we define for example two lists A and B, then the script will interpret traverse both lists in parallel
to define the equivalent rows. For example, if "p://Section[3]/Chord" is set to (0.4,0.2) and "a:Polar/Reference_Area" is set to (40,20), then that row will be interpreted
as two different rows, one with "p://Section[3]/Chord" = 0.4 and "a:Polar/Reference_Area" = 40, and the other with "p://Section[3]/Chord" = 0.2 and "a:Polar/Reference_Area" = 20.

Finally, we can define "perpendicular" lists. By placing an identifier before each list (example: "1()" or "2()"), we can make it so for each element in list 1, we will generate
a new row with each of the elements of list 2. This means that for a single row with perpendicular lists 1 and 1, we get a total of length(list1)*length(list2) rows. Lists that have
the same identifier are traversed parallely.
For example, in the last row of our input file we can see 4 lists and 2 different identifiers. This row represents a real problem we may encounter: we wish to test 3 different airfoils
and 3 different tip lengths. However, in order to change the airfoil in XFLR5 we need to change 2 parameters at the same time: Left_Side_FoilName and Right_Side_FoilName. Similarly,
when we change the tip length of the wing, it's surface area changes, and the reference area changes accordingly. This row will be interpreted as 9 rows, which can be more closely
studied in the file https://github.com/juan-g-bonilla/xflr5-xml-generator/blob/master/usage_example/input_equivalent.txt .

### Run the script
Run the script. You can do `python XFLR5XMLGenerator.py -h` to see help in the console.

### Input results into XFLR5
First, import all XML files corresponding to the planes. Then, import the analysis. They should get paired automatically. Importing the analysis files may take a bit.

## Final word
This project was developed in a couple of days by suggestion of a close collegue. I cannot
guarantee that it will function correctly for all use cases. I tried testing it as much as I could, but errors are bound to occur for test cases I did not cover. 
Feel free to contact me with any suggestion regarding this script or if you find any bugs.

## License
This project is published under the MIT License. For more information, see LICENSE file.
