import pandas as pd
import numpy as np
import json

## Ignore dumb warnings. We are adults. We take our chances
import warnings
warnings.filterwarnings('ignore')


'''
INVENTORY CLASS
    * Dictionary tree structure
    * Can initialize inventory with excel file that follows template structure
    * Can add or remove items and systems
'''

'''
INVENTORY CLASS
    * Dictionary tree structure
    * Can initialize inventory with excel file that follows template structure
    * Can add or remove items and systems
'''

# TODO: probably some hidden issues with root class variable

class Inventory:
    
    root = None
    json = {}

    def __init__(self, name, parent, values=None, count=1, children=None):
        '''
        A proper tree data structure

        :param Inventory parent: an inventory object which is the immediate parent of this one
        :param str name: name of this entry
        :param dict values: a dictionary of M/V/P/C/T values
        :param dict children: a dictinoary mapping names to Inventory objects
        '''
        self.name = name
        self.parent = parent
        if values == None:
            values = {'mass': 0, 'volume': 0, 'power': 0, 'cooling': 0, 'crewtime': 0}
        self.values = values
        self.children = {}
        self.count = count    

    def __repr__(self):
        return(json.dumps(self.json, indent=4))

    def fromFile(xlsx_file):    
        '''
        Create inventory json (dictionary) from location of excel file.

        :param str xlsx_file: spreadsheet containing inventory items and M/V/P/C, specifically formatted
        :return: dict inventory_json: the full inventory
        '''
        inv = Inventory('Inventory', None, {})
        Inventory.root = inv
        Inventory.addSystem(inv, xlsx_file)

        return inv

    def addSystem(self, xlsx_file):
        '''
        Appends contents of xlsx_file to existing Inventory object
        '''
        data, sep = Inventory.__cleanData(self, xlsx_file)
        for row in data.iterrows():
            vals = row[1]

            # check if there are values to be added
            vals_sum = sum(vals[sep:])

            # add item to inventory if so
            if vals_sum > 0:
                lineage = list(vals[:sep-1])
                name = vals[sep-1]
                parent = Inventory.getNode(lineage)
                count = int(vals['Initial Count'])
                values = {
                # 'count_inuse': 0,
                # 'count_broken': 0,
                # 'segment': [],
                'mass': float(vals['M (kg)']),
                'volume': float(vals['V (m^3)']),
                'power': float(vals['P (kW)']),
                'cooling': float(vals['C (kW)']),
                }
                try:
                    values['crewtime']= float(vals['T'])
                except:
                    values['crewtime'] = 0
                    
                child = Inventory(name, parent, values, count)
                parent.insert(child)
                self.buildJson(child)
        self.json = Inventory.json
        Inventory.json = {}

    def getNode(lineage):
        '''
        Returns the node at the end of the specified traversal
        **Creates objects for intermediate nodes if they do not already exist
        :return Inventory object
        '''
        pointer = Inventory.root
        for n in lineage:
            try:
                if n not in pointer.children.keys():
                    new_node = Inventory(n, pointer)
                    pointer.children[n] = new_node
            except: #assuming this is first item to be added
                new_node = Inventory(n, pointer)
                pointer.children = {}
                pointer.children[n] = new_node
            pointer = pointer.children[n]
        return pointer

    def insert(self, child):
        '''
        Append child object to list of children.
        Update values of all parents

        :param Inventory child: new Inventory object
        '''
        self.children[child.name] = child

        pointer = self
        while self.parent != None:
            self.updateValues(child, 1)
            self = self.parent
            
        return self

    def add(self, name, values, *args):
        '''
        Manually add an item to the inventory.
        Unlike the insert function, does not require an Inventory object to be passed in
        :param str name: name of the new item
        :parm dict values: values of the new item
        :param str args: the lineage of parents not containing the item to be added

        :return dict: the new json representation of inventory
        '''
        parent = Inventory.getNode(args)
        child = Inventory(name, parent, values)
        parent.insert(child)
        self.buildJson(child)
        return self.root.json

    def remove(self, lineage):
        '''
        Remove an item from the inventory
        :param list lineage: list of node names from root to node to be removed, from general to specific
        '''
        pointer = self
        end_node = lineage[-1]
        for n in lineage[:-1]:
            pointer.updateValues(end_node, -1)
            pointer = pointer.children[n]
        pointer.remove(lineage[-1])

    def updateValues(self, child, sign):
        '''
        Add or subtract the values of child from its parents
        :param Inventory child: contains values to be added or subtracted
        :param int sign: +1/-1
        '''
        dict_1 = self.values
        dict_2 = child.values
        count = child.count

        final_values = {x: dict_1[x] + dict_2[x] * count * sign for x in dict_1.keys()}
        
        self.values = final_values

    def buildJson(self, child):
        lineage = [child]        
        pointer = self.root.json

        while child.parent != self.root:
            lineage += [child.parent]
            child = child.parent

        # reverse list so parent highest in inventory first
        lineage.reverse()

        for node in lineage:
            if node.name not in pointer.keys():
                pointer[node.name] = node.values
            else:
                try:
                    pointer[node.name]['mass'] = node.values['mass']
                    pointer[node.name]['volume'] = node.values['volume']
                    pointer[node.name]['power'] = node.values['power']
                    pointer[node.name]['cooling'] = node.values['cooling']
                    pointer[node.name]['crewtime'] = node.values['crewtime']
                except:
                    # dummy
                    x = 1
            pointer = pointer[node.name]
        
        # remove new entires in object.values for some reason
        # idk how instance variables work anymore
        for a in lineage:
            a.values = {x: a.values[x] for x in a.values.keys() if type(a.values[x]) != dict}            

    def contains(self, lineage):
        '''
        Checks if Inventory contains this item.
        :param list lineage: list of node names from root to node in question
        :return first node not found or True
        '''

        pointer = self.inventory_json
        for n in lineage:
            try:
                pointer = pointer.children[n]
            except:
                return n.name
        return True
    
    def getRoot(self):
        return self.root
    
    def getJson(self):
        return self.json

    def getValues(self):
        return self.values

    def getSubparts(self):
        return self.children

    def getParent(self):
        return self.parent 

    def getCount(self):
        return self.count 

    def getName(self):
        return self.name

    def getSegment(name):
        '''
        Helper method for the mission class (ESM calculation)
        :param str name: the name of the mission segment, as it is in the original spreadsheet
        :return Inventory: the Inventory object for this mission segment
        '''
        return Inventory.root.children[name]


    def __cleanData(self, xlsx_file):
        '''
        Handles bad decisions people made with their spreadsheets
        :param str xlsx_file: location of .xlsx
        :return DataFrame data: cleaned dataframe
        '''

        data = pd.read_excel(xlsx_file, header=0, engine="openpyxl")
        data.replace(r'^\s*$', np.nan, regex=True, inplace=True) # convert spaces (' ') to NaN
        data.dropna(axis=0, how='all', inplace=True) # drops rows with all NaNs
        # data.dropna(axis=1, how='all', inplace=True) # drops cols with all NaNs

        # separator between item/subsystems and values
        sep = data.columns.get_loc('Initial Count')
        
        # for columns before sep (ie: system, sub1, and sub2), fill empty cell with nearest above values
        # abstracted beyond strict number and name of columns here
        data.iloc[:, 0:sep-1] = data.iloc[:, 0:sep-1].fillna(method='ffill')
        data.fillna(0, inplace=True) # convert NaNs to 0 for compute 

        return data, sep

    # def return_item(self, system, subsystem1, subsystem2, obj, is_broken=False):
    #     """
    #     return OBJ back to the inventory after being used in (SYSTEM, SUBSYSTEM).
    #     remove OBJ from objects_in_use, decrement count_inuse in inventory and increment count_broken if necessary
    #     """
    #     assert self.contains(system, subsystem1, subsystem2, obj), \
    #     "inventory does not hold {0} in system {1} subsystem1 {2} and subsystem2 {3}".format(obj, system, subsystem1, subsystem2)

    #     item = self.inventory_json[system][subsystem1][subsystem2][obj]
    #     item["count_inuse"] -= 1
    #     if is_broken:
    #         item["count_broken"] += 1

    # def is_available(self, system, subsystem1, subsystem2, obj):
    #     """
    #     return true if there is an item of OBJ available to be used in the inventory, false otherwise
    #     """
    #     assert self.contains(system, subsystem1, subsystem2, obj), \
    #     "inventory does not hold {0} in system {1} subsystem1 {2} and subsystem2 {3}".format(obj, system, subsystem1, subsystem2)
        
    #     item = self.inventory_json[system][subsystem1][subsystem2][obj]
    #     return item["count_total"] - item["count_broken"] - item["count_inuse"] > 0


## Ignore dumb warnings. We are adults. We take our chances
import warnings
warnings.filterwarnings('ignore', category=FutureWarning)


'''
SEGMENT CLASS
    * Node graph; nodes are locations and segments are edges
    * Inventory and constants are instance variables

MISSION CLASS
    * Pass in segments as init parameters
    * Calculate ESM
    * Calculate xESM
'''

''' 
mission = RMA(parameters = mission segment objects)
mission = RMA(pd, sf, tr1, tr2, tr3)

mission.locations = ['Earth', 'Earth_orbit', 'Mars', 'Mars_orbit']
mission.pd = Segment object, path =  'Earth' -> 'Earth_orbit' -> 'Mars_orbit' -> 'Mars', 210 days, autonomous
mission.sf = Segment object, path = 'Mars' node, 500 days, crewed
mission.tr1 = Segment object, path = 'Earth' -> 'Earth_orbit' -> 'Mars_orbit' -> 'Mars', 210 days, crewed
mission.tr2 = Segment object, path = 'Mars' -> 'Mars_orbit' -> 'Earth_orbit' -> 'Earth', 210 days, crewed
mission.tr3 = Segment object, path = 'Mars_orbit' node, 500 days, crewed/autonomous

pd = Mission(name='Predeployment', paths=[], length=int, type=autonomous/crewed)

mission.setInventory(file path)
    inventory = Inventory(file)
    iterate through mission segments and set inventory to pointer in larger inventory? or create separate inventories for each
    or just have the same name
'''

class Segment:

    def __init__(self, name, path, constants, type):
        '''
        Creates Segment object such as according to mission segments described in the xESM paper

        :param str name: the name of the mission segment (out of pd, sf, tr1, tr2, tr3)
        :param list path: a list of tuples each representing an edge in segment path
        :param dict constants: Leq, Veq, Peq, Ceq, Req, Number of days, Number of days food eaten
        :param str type: autonomous or crewed
        '''
        self.name = name
        self.path = path
        self.constants = constants

        #TODO: assert constant names

        self.type = type
        self.inventory = None

    def getSegment(self):

        return self.name, self.path, self.type

    # def setInventory(self, inventory_pointer):
    #     '''
    #     :param dict inventory: dictionary pointer passed in
    #     '''
    #     self.inventory = inventory_pointer

class Mission:

    def __init__(self, *args):    
        '''
        Creates Mission object from mission segments passed in

        '''
        self.segments = args
        self.graph = []
        for a in args:
            self.graph.append(a.path)

    def __repr__(self):
        repr = '==================================================\n'

        # ESM
        for segment in self.segments:
            repr += segment.name + ' ESM: ' + str(round(segment.ESM, 2)) + '\n'
        repr += "\nTOTAL ESM: " + str(round(self.ESM, 2)) + '\n'

        for segment in self.segments:
            bar = int(segment.ESM / 1500)
            for i in range(bar + 1):
                repr += u'\u2588'
            repr += ' ' + segment.type + '\n'
        repr += '\n'

        # xESM
        for segment in self.segments:
            repr += segment.name + ' xESM: ' + str(round(segment.xESM, 2)) + '\n'
        repr += "\nTOTAL xESM: " + str(round(self.xESM, 2)) + '\n'

        for segment in self.segments:
            bar = int(segment.xESM / 1500)
            for i in range(bar + 1):
                repr += u'\u2588'
            repr += ' ' + segment.type + '\n'
        repr += '\n'

        return repr

    def setInventory(self, path):

        #TODO: assert inventory system

        inventory = Inventory.fromFile(path)
        self.root_inventory = inventory
        for segment in self.segments:
            segment.inventory = Inventory.getSegment(segment.name)
            segment.summary = segment.inventory.getValues()

    def setInventoryFromObject(self, inventory):
        self.root_inventory = inventory
        for segment in self.segments:
            segment.inventory = Inventory.getSegment(segment.name)
            segment.summary = segment.inventory.getValues()

    def ESM(self):
        '''
        Calculates regular ESM
        '''
        self.ESM = 0
        for segment in self.segments:
            summary = segment.summary
            Leq = segment.constants['Leq']
            Veq = segment.constants['Veq']
            Peq = segment.constants['Peq']
            Ceq = segment.constants['Ceq']
            Teq = segment.constants['Teq']
            duration = segment.constants['Number of days']
            segment.ESM = (summary['mass'] + summary['volume'] * Veq + summary['power'] * Peq + summary['cooling'] * Ceq + summary['crewtime'] * duration * Teq) * Leq
            
            self.ESM += segment.ESM

        return self.ESM

    def xESM(self):
        '''
        Calculates extended ESM
        '''
        self.xESM = 0
        for segment in self.segments:
            summary = segment.summary
            Leq = segment.constants['Leq']
            Veq = segment.constants['Veq']
            Peq = segment.constants['Peq']
            Ceq = segment.constants['Ceq']
            Teq = segment.constants['Teq']
            duration = segment.constants['Number of days']

            if segment.type == 'pd':
                segment.xESM = (summary['mass'] + summary['volume'] * Veq) * Leq
            elif segment.type == 'sf' or segment.type == 'tr3':
                segment.xESM = (summary['volume'] * Veq + summary['power'] * Peq + summary['cooling'] * Ceq \
                    + summary['crewtime'] * duration * Teq) * Leq
            else:
                segment.xESM = (summary['mass'] + summary['volume'] * Veq + summary['power'] * Peq + summary['cooling'] * Ceq \
                    + summary['crewtime'] * duration * Teq) * Leq
            self.xESM += segment.xESM
        

        return self.xESM
