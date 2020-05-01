import pickle

def mySavePickle(name,var):
	"""
	Save a variable to a pickle file
	
	Args:
	    name (dict): Dictionary to be saved into a pickle file
	    var (str): String name of the pickle file
	"""
	pickle_out = open(name,"wb")
	pickle.dump(var,pickle_out)
	pickle_out.close()

def myLoadPickle(name):
	"""
	Load a variable from a pickle file
	
	Args:
	    name (str): the name or path of the pickle file
	
	Returns:
	    TYPE: The pickled dictionary
	"""
	pickle_in = open(name,"rb")
	var = pickle.load(pickle_in)
	return var
