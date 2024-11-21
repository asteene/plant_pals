import requests # type: ignore
import json

api_url = "https://openfarm.cc/api/v1/crops" 
default_plants = [
    'tomato',
    'rosemary',
    'sunflower',
    'thyme',
    'rose',
    'mint',
    'hydrangea'
]

def get_default_plants():
    plant_data = []
    for plant in default_plants:
        plant_data.append(get_plant_data_from_api(plant))

    return plant_data

def get_species_by_id(id):
    """Fetches plant data from the API."""
    response = requests.get(f'{api_url}/{id}')
    
    if response.status_code == 200:
        return clean_plant_data(response.json())  # Return the full response as JSON
    else:
        print(f"Failed to fetch data: {response.status_code}")
        return None

def get_plant_data_from_api(param):
    """Fetches plant data from the API."""
    response = requests.get(f'{api_url}/{param}')
    
    if response.status_code == 200:
        return clean_plant_data(response.json())  # Return the full response as JSON
    else:
        print(f"Failed to fetch data: {response.status_code}")
        return None

def clean_plant_data(plant_data):
    """Cleans the plant data and returns a dictionary with only needed fields."""
    cleaned_data = {}
    if plant_data:
        cleaned_data['id'] = plant_data['data']['id']
        cleaned_data['common_name'] = plant_data['data']['attributes']['name']
        cleaned_data['description'] = plant_data['data']['attributes']['description']
        cleaned_data['maintenence'] = {}
        cleaned_data['maintenence']['sun_requirements'] = plant_data['data']['attributes']['sun_requirements']
        cleaned_data['maintenence']['sowing_method'] = plant_data['data']['attributes']['sowing_method']
        cleaned_data['image'] = plant_data['data']['attributes']['main_image_path']
    
    return cleaned_data if cleaned_data else None

# Example usage:
if __name__ == '__main__':
    
    raw_data = get_plant_data_from_api(api_url, 'rosemary')
    cleaned_data = clean_plant_data(raw_data)

    #print(json.dumps(raw_data, indent=4))

    if cleaned_data:
        print(json.dumps(cleaned_data, indent=4))
    else:
        print("No relevant plant data found.")