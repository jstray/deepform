# Python program to sort a list of 
# tuples by the second Item using sorted()  
  
# Function to sort the list by second item of tuple 
# def Sort_Tuple(tup):  
tup = [('rishav', 10), ('akash', 5), ('ram', 20), ('gaurav', 15)]  
    # reverse = None (Sorts in Ascending order)  
    # key is set to sort using second element of  
    # sublist lambda has been used  
print(sorted(tup, key = lambda x: x[1], reverse = True))   
  
# Driver Code  
#tup = [('rishav', 10), ('akash', 5), ('ram', 20), ('gaurav', 15)]  
  
# printing the sorted list of tuples 
#print(Sort_Tuple(tup))  