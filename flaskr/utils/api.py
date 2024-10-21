import os
import requests
import json
from typing import Union, Dict, List

import sys # for testing 

# Get the API key from the environment
API_KEY = os.getenv('PLANT_API_KEY')

# set the base URL
URL = 'https://trefle.io/api/v1/species'

def clean_response(data: Dict[str, any]) -> Dict[str, any]:
    ''' Clean the response data from the API
    
    params:
    - data: dict'''
    plant_data = {
                'id': data['id'],
                'common_name' : data['common_name'],
                'image' : data['image_url'],
                'scientific_name': data['scientific_name']
            }
    
    return plant_data
  
def filter_species(q_type: str, q: str) -> Union[Dict[str, any], Exception]:
    """
    Filter by plant species by a specific filter key and value.

    This function queries the Trefle API using the given key (`q_type`) 
    and value (`q`) and returns the cleaned data of the first result 
    or an exception if the request fails.

    Parameters:
    ----------
    q_type : str
        The key to filter the species search (e.g., 'common_name').
    q : str
        The value corresponding to the filter key (e.g., 'tomato').

    Returns:
    -------
    Union[Dict[str, Any], Exception]
        The cleaned plant data as a dictionary or an exception if an error occurs.
    """

    #build_url = f'{URL}'

    params = {
        'token': API_KEY,
        f'filter[{q_type}]': q
    }

    # Make the request  
    try: 
        response = requests.get(URL, params=params)
        
        if response.status_code == 200:
            plant = response.json()
            data = plant['data']
            
            #print(json.dumps(data, indent=4))
            data = data[0]
            plant_data = clean_response(data)
            #print(plant_data)
            return plant_data
        else:
            return response.status_code 
    # return exception if not found
    except requests.exceptions.RequestException as e:
        return e

def get_species_by_id(id: int) -> Union[Dict[str, any], Exception]:
    params = {
        'token': API_KEY
    }

    # Make the request  
    try: 
        response = requests.get(f'{URL}/{id}', params=params)
        
        if response.status_code == 200:
            plant = response.json()
            data = plant['data']
            
            #print(json.dumps(data, indent=4))
            #data = data[0]
            plant_data = clean_response(data)
            #print(plant_data)
            return plant_data
        else:
            return response.status_code 
    # return exception if not found
    except requests.exceptions.RequestException as e:
        return e
    
def get_default_species() -> Union[List[Dict], Exception]:
    
    ids = (269338, #tomato
           64847, # basil
           204043, # chives
           87441, #garden thyme
           200080, # garden parsley
           61646, # spearmint
           78383, # rosemary
           143463, # garden dill
           115385, # spinach
           28023, # garden lettuce
           167936, # Cucumber
           171170, # carrot
           264892 #garden strawberry 
           )
    
    params = {
        'token': API_KEY
    }

    return_val = []

    # Make the request  
    try: 
        for id in ids:
            response = requests.get(f'{URL}/{id}', params=params)
        
            if response.status_code == 200:
                plant = response.json()
                data = plant['data']
                
                #print(json.dumps(data, indent=4))
                #data = data[0]
                plant_data = clean_response(data)
                #print(plant_data)
                return_val.append(plant_data)
                print(return_val)
            else:
                return response.status_code 
        return return_val
    # return exception if not found
    except requests.exceptions.RequestException as e:
        return e

if __name__ == '__main__':
    #search_all(sys.argv[1])
    #get_recommended()
    #print(filter_species(sys.argv[1], sys.argv[2]))
    print(get_default_species())