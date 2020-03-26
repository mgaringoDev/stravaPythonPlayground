import pickle

def mySavePickle(name,var):
	pickle_out = open(name,"wb")
	pickle.dump(var,pickle_out)
	pickle_out.close()

def myLoadPickle(name):
	pickle_in = open(name,"rb")
	var = pickle.load(pickle_in)
	return var
