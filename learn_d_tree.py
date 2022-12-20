import sys
import imp
import risktools
import time
import os
import random
import json
import math

###### learn_d_tree.py
#      This file will learn a decision tree from a given datafile.
#      It is designed to work with data generated by the generate_dt_data.py script, 
#      but could be modified to work with other data
######

class DNode():
    """This is the class for a decision tree node"""
    
    def __init__(self, parent, data, data_focus):
        """Initialize a decision tree node."""
        self.parent = parent
        self.depth = 1
        # Used features records all the features that have already been used to split the data before this node. So we can ignore them when splitting this node
        self.used_features = []
        if parent is not None:
            self.depth = parent.depth + 1
            self.used_features = parent.used_features[:]
            
        self.positive_child = None
        self.negative_child = None
        
        # data is a list of all the data examples at the root node.  We don't copy them, but instead keep a list of which entries each node should focus on
        self.data = data
        # data_focus is a list of the data entries (their indices) that constitute this node's data
        self.data_focus = data_focus 
        if data_focus is not None and len(data_focus) > 0:
            self.compute_pos_prob()
        self.split_feature = None
    
    def compute_pos_prob(self):
        """Compute the fraction of this node's data that have a positive label (1) """
        positives = 0
        for f in self.data_focus:
            d = self.data[f]
            if d.label == 1:
                positives += 1
        self.positive_probability = float(positives) / float(len(self.data_focus))
        self.entropy = self.compute_entropy(self.positive_probability)
    
    def compute_entropy(self,p):
        """Compute the entropy for a given probability p"""
        ### ASSIGNMENT - BEGIN TASK 1 ###
        
        #RETURN THE ENTROPY FOR THIS 0 <= p <= 1
        return 0
        ### ASSIGNMENT - END TASK 1 ###
    
    def save_node(self, savefile):
        """Save out this node's information, including for its children"""
        if self.split_feature is None:
            savefile.write(json.dumps(self.positive_probability) + '\n')
        else:
            savefile.write(json.dumps(self.positive_probability) + '|' + json.dumps(self.split_feature) + '\n')
            self.positive_child.save_node(savefile)
            self.negative_child.save_node(savefile)
    
    def load_node(self, loadfile):
        """Load this node from the file, including for its children"""
        loadline = loadfile.readline()
        splitline = loadline.split('|')
        if len(splitline) == 1:
            self.positive_probability = json.loads(splitline[0])
        else:
            self.positive_probability = json.loads(splitline[0])    
            self.split_feature = json.loads(splitline[1])
            self.positive_child = DNode(self,None,None)
            self.positive_child.load_node(loadfile)
            self.negative_child = DNode(self,None,None)
            self.negative_child.load_node(loadfile)
    
    def print_node(self):
        """Display this node's information to the screen"""
        for d in range(self.depth):
            print('-',) 
        if self.split_feature is not None:
            if self.data:   
                print(self.data[0].feature_names[self.split_feature], '<', self.split_feature, '> (', self.positive_probability, ' , ', 1 - self.positive_probability, ' ) , ', len(self.data_focus), ' examples   reached here')
            else:
                print('<', self.split_feature, '> (', self.positive_probability, ' , ', 1 - self.positive_probability, ' )')
            self.positive_child.print_node()
            self.negative_child.print_node()
        else:
            if self.data:
                print('(', self.positive_probability, ' , ', 1 - self.positive_probability, ' ) , ', len(self.data_focus), ' examples reached here')
            else:
                print('(', self.positive_probability, ' , ', 1 - self.positive_probability, ' )')
    
    def determine_info_gain(self, feature_index):
        """Determine the information gain for the given feature"""
        ### ASSIGNMENT - BEGIN TASK 2 ###

        #Feature index is the index of the feature that we are evaluating
        #self.data has all the data, but this node only cares about those
        #data entries listed in self.data_focus (this is an array of the indices of data instances we care about)
        #each data entry is a DData object, see below for its details
        
        #RETURN THE INFORMATION GAIN IF WE WERE TO SPLIT ON THIS FEATURE
        
        return 0
            
        ### ASSIGNMENT - END TASK 2 ###
        
    
    def classify(self, instance):
        """Return the probability that this instance is positive, given its features.  If this node has children, pass to the correct child, otherwise, return probability of positive from this node"""
        if self.split_feature == None:
            return self.positive_probability
        else:
            if instance[self.split_feature] == 1:
                return self.positive_child.classify(instance)
            else:
                return self.negative_child.classify(instance)
         
    def determine_split(self, depth_limit):
        """Determine which feature that this node should split on.  If all examples that reach here have the same label, don't split.  If depth limit has been reached, don't split."""
        #Just return if tree is deep enough or if all examples are labelled correctly
        if self.depth == depth_limit or self.positive_probability == 1 or self.positive_probability == 0:
            return
          
        best_feature = None
        best_feature_information_gain = 0
            
        for i in range(len(self.data[0].features)):
            if i not in self.used_features:
                
                current_gain = self.determine_info_gain(i)
                
                if best_feature is None or current_gain > best_feature_information_gain:
                    best_feature = i
                    best_feature_information_gain = current_gain
            
        #Split on best_feature
        self.split_feature = best_feature
    
        positive_focus = []
        negative_focus = []
        
        self.used_features.append(best_feature)
        
        for f in self.data_focus:
            d = self.data[f]
            if d.features[best_feature] == 1:
                positive_focus.append(f)
            else:
                negative_focus.append(f)
            
        
        self.positive_child = DNode(self,self.data,positive_focus)
        
        self.negative_child = DNode(self,self.data,negative_focus)
    
        self.positive_child.determine_split(depth_limit)
        self.negative_child.determine_split(depth_limit)
    
class DTree():
    """A Decision Tree class"""
    def __init__(self, data):
        data_focus = None
        if data is not None:
            data_focus = range(len(data))
        self.root = DNode(None,data,data_focus)
    
    def learn_tree(self, depth_limit):
        self.root.determine_split(depth_limit)
    
    def get_prob_of_win(self, instance):
        return self.root.classify(instance)
    
    def print_tree(self):
        self.root.print_node()
    
    def save_tree(self, savename):
        savefile = open(savename, 'w')
        self.root.save_node(savefile)
        savefile.close()
        
    def load_tree(self, loadname):
        loadfile = open(loadname, 'r')
        self.root.load_node(loadfile)
        loadfile.close()
    
def loadDTree(loadfilename):
    """This will load and return a DTree object from the given filename"""
    tree = DTree(None)
    tree.load_tree(loadfilename)
    return tree
    
class DData():
    """The data structure used to store the data for learning the decision tree"""
    def __init__(self, features, label, feature_names):
        self.features = features
        self.label = label
        self.feature_names = feature_names

def print_usage():
    print('USAGE: python learn_d_tree.py data_filename depth')
       
def read_data(datafile):
    """This will load the data from the given datafile"""
    #First read feature_names
    newline = datafile.readline()
    feature_names = json.loads(newline)
    
    dataover = False
    
    dataset = []
    
    while not dataover:
        newline = datafile.readline()
        splitline = newline.split('|')
        if not newline:
            dataover = True
        else:
            features = json.loads(splitline[0])
            label = json.loads(splitline[1])

            datum = DData(features, label, feature_names)
            dataset.append(datum)
    return dataset
    
if __name__ == "__main__":
    #Get ais from command line arguments
    if len(sys.argv) != 3:
        print_usage()
    
    #get data file name
    datafilename = sys.argv[1]
    
    #get depth of tree to learn
    depth = int(sys.argv[2])
    
    #Open the datafile
    datafile = open(datafilename, 'r')    
    
    #Read/Load the data from the file
    data = read_data(datafile)
    
    #Close the datafile
    datafile.close()
    
    #Create the Decision Tree object
    tree = DTree(data)
    
    #Learn the decision tree to the given depth
    tree.learn_tree(depth)
    
    #Print out the learned tree to the screen
    tree.print_tree()
    
    print('Learned tree. Saving to file')
    
    #Create the filename to save the tree to
    savefilename = 'decision_trees\\' + datafilename[9:-4] + '_' + str(depth) + '.dtree'
    
    #Save the tree to that file
    tree.save_tree(savefilename)
    print('Saved file to ', savefilename)

    #Check the saved tree by reloading and printing.  We can check to make sure it matches.
    print('Loading tree.')
    tree2 = loadDTree(savefilename)
    tree2.print_tree()
    
    