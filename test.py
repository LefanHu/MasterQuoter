# Python program to update 
# JSON 
import json 
  
  
# function to add to JSON 
def write_json(data, filename='quotes.json'): 
    with open(filename,'w') as f: 
        json.dump(data, f, indent=4) 
      
      
with open('quotes.json') as json_file: 
    data = json.load(json_file)
    temp = data['quotes'] 
  
    # python object to be appended 
    y = {"userid": "<@!some other user",
         "message": "some other message"
    }
  
    # appending data to emp_details  
    temp.append(y) 
      
write_json(data)