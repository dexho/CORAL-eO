# CORAL for eO

their stuff: [github](https://github.com/jmchandonia/CORAL), [informational slides](https://docs.google.com/presentation/d/1nkllV1vmHMk5uVh2eoZlJ4M-8HUEhDOB/edit?usp=sharing&ouid=102598671403657474606&rtpof=true&sd=true)

our: [CORAL-eO github](https://github.com/dexho/CORAL-eO)

point of contact for questions: John-Marc Chandonia, ```JMChandonia@lbl.gov```
## __purpose__

To ensure that data in echusOverlook is FAIR (findable, accessible, interoperable, reusable), which is a prerequisite to standardizing and democratizing space mission design.

CORAL is...

* a way of enforcing bounds on the creation of a spreadsheet through  what its column/row headers are, and what types of values it can hold
  * 'contextons' are units of context: it's a tuple of a __unit__ and an __object__
  * there are a restricted number of predefined units and objects (ontologies) to choose from
  * each entry in the spreadsheet must be associated with a contexton that provides context on what it is
* a way to track where data comes from and how it is modified, through a provenance graph
* an API to ArangoDB, a graph database
* created for ENIGMA

I got CORAL running and minimally functional over the summer, with the following progress:

* working backend installations of CORAL/ArangoDB in MacOS and Ubuntu
* able to define toy, _static_ brick data type of eO inventory and reference mission architecture -- see [brick_type_templates.json](https://github.com/dexho/CORAL-eO/blob/main/back_end/python/var/brick_type_templates.json)
* able to manipulate ontologies -- see [typedef.json](https://github.com/dexho/CORAL-eO/blob/main/back_end/python/var/typedef.json)
* able to upload, download, and use eO data from ArangoDB through CORAL and CORAL's API -- see [jupyter notebooks](https://github.com/dexho/CORAL-eO/blob/main/back_end/python)

## __current TODOs:__
* ## installing CORAL [issue #207](https://github.com/cubes-space/echusOverlook/issues/207)

* installation is not that well documented on their github -- I had to make several changes and it was a pain
* if it doesn't work on windows, you can use an old lab macbook (running Ubuntu) that I already set CORAL up on

* ## game plan for data provenance [issue #203](https://github.com/cubes-space/echusOverlook/issues/203)
  * The current use of CORAL creates static bricks to represent immutable data like sequencing reads. These static data types serve as a skeleton for the data provenance graph -- spinning off of static bricks are dynamically created data types, such as when a scientist makes a custom brick to represent a certain experiment they did
  * figure out static and dynamic data types
  * the current flow of object creation in eO looks something like this:

```
CONFIG --> ITEMS --------> MODEL (tm & initial)
              |             |
              |             |------> FULL INVENTORY  <---- SINGLE ITEM INV
              |             |------> METRICS <----- CONSTANTS
              |--SIMITEMS-->|------> SIMULATION
```


* ## defining ontologies [issue #204](https://github.com/cubes-space/echusOverlook/issues/204)
  * I add ontology ideas to the github issue description every time I think of one
* ## create bricks to represent the following spreadsheet/matrix-like data types in eO [issue #202](https://github.com/cubes-space/echusOverlook/issues/202)
  * likely static
    1. config -- [example](https://github.com/cubes-space/echusOverlook/blob/8ad0ffd00bfed20e3842c75b774cb3b714373ed3/tests/configs/rma.json)
    2. inventory 
        * single items - includes most excel sheets in ```eo/inv/subsystems``` -- [example](https://github.com/cubes-space/echusOverlook/blob/master/eo/inv/subsystems/AAA.xlsx)
        * complete inventories -- [1](https://github.com/dexho/CORAL-eO/blob/main/example/eO/data/chois/4cm_5400d.csv), [2](https://github.com/dexho/CORAL-eO/blob/main/example/eO/data/chois/Inventory_Master.xlsx)
        * inventory + composition data -- not critical
    3. mission segments and associated constants -- [example](https://github.com/dexho/CORAL-eO/blob/main/example/eO/data/chois/constants.xlsx)
  * likely dynamic

    4. transition matrix of max size NxNxS
        * **note that the ALSSAT data is represented using ```dict```, while the HabNet data is represented using ```defaultdict```
        * values are all floats -- [ALSSAT transition matrix](https://github.com/dexho/CORAL-eO/blob/main/example/eO/data/chois/alssat_tm.json)
        * values are either floats or tuples: ```(bound method reference, [list of strings])``` -- [HabNet transition matrix](https://github.com/dexho/CORAL-eO/blob/main/example/eO/data/chois/habnet_tm.json)
    5. NxS initial vector
        * values are all floats -- [ALSSAT initial](https://github.com/dexho/CORAL-eO/blob/main/example/eO/data/chois/alssat_initial.json), [HabNet initial](https://github.com/dexho/CORAL-eO/blob/main/example/eO/data/chois/habnet_initial.json)
    6. Item paramteres and usage (still thinking about this)
    7. SimItem parameters and usage (still thinking about this)


## __after ^ the above__

* Item/SimItem comparator, compatibility finder
* use CORAL to define and/or apply different mission metrics
* eO website/public leaderboard/gamification
## __questions to think about__

* What is the best way of leveraging CORAL to improve eO?
* How do we use CORAL to make eO easier to use?
* What is the best _amount_ of CORAL to use given the intended audience of eO?
  * Previous space tools are heavily based in Excel and MATLAB (if not pencil and paper)
  * Biologists/bioengineers and space scientists don't necessarily care about data standards or working in the cloud -- in fact, they are more likely to be put off if required to use them
  * Keep in mind that CORAL was developed to handle wet lab data, especially sequencing data. Meanwhile, eO primarily needs CORAL to strengthen its framework for defining and keeping track of objects that represent mission components.
* To what extent is ArangoDB necessary? Most users of the eO library will working in their local environment. Can they use a minimal part of CORAL to validate data creation, and only interface with ArangoDB to upload their designs to the public server?
* How to set up the public server?
* When someone contributes a new object, how do they specify or constrain its intended use cases?
* When someone writes a new metric, how do they specify what data must be available for the calculation to be carried out?
