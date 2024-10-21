#!/bin/bash

# Array of common garden plant names to search for
plants=(
    "Solanum lycopersicum"   # Tomato
    "Ocimum basilicum"       # Basil
    "Allium schoenoprasum"   # Chives
    "Thymus vulgaris"        # Thyme
    "Petroselinum crispum"   # Parsley
    "Mentha spicata"         # Mint (Spearmint)
    "Rosmarinus officinalis" # Rosemary
    "Origanum vulgare"       # Oregano
    "Coriandrum sativum"     # Cilantro
    "Anethum graveolens"     # Dill
    "Spinacia oleracea"      # Spinach
    "Lactuca sativa"         # Lettuce
    "Capsicum annuum"        # Pepper (Bell/Chili)
    "Cucumis sativus"        # Cucumber
    "Daucus carota"          # Carrot
    "Cucurbita pepo"         # Zucchini
    "Fragaria × ananassa"    # Strawberry
)

output_file="plants.txt"

> "$output_file"

# Loop through each plant and run the API query
for plant in "${plants[@]}"
do
    echo "Searching for: $plant"
    
    # Run the Python script and pass the plant as an argument
    python3 api.py scientific_name "$plant" >> "$output_file"
    
    echo "--------------------------------------"
done
