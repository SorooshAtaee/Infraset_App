from ghpythonlib.componentbase import executingcomponent as component
import rhinoscriptsyntax as rs
import Rhino.Geometry as rg
import System
from Grasshopper.Kernel import GH_RuntimeMessageLevel as RML

class InfrasetAssembly(component):
    def RunScript(self, Name, assembly_data_list1, assembly_data_list2, assembly_data_list3, assembly_data_list4, assembly_data_list5,
                  assembly_data_list6, assembly_data_list7, assembly_data_list8, assembly_data_list9, assembly_data_list10,
                  null3, energy_reduction_factor, water_reduction_factor, ghg_reduction_factor):

        # --- 1. HELPER FUNCTION TO FLATTEN DATA TREES & LISTS WITH KEY NORMALIZATION ---
        def extract_kv_lists(data):
            if data is None:
                return []
            
            # KEY NORMALIZATION MAP: Maps output key names (lowercase/underscores) back to expected key names (capitalized/spaces)
            # This fixes the bug where chaining InfrasetAssembly components causes mass categories to not sum
            key_map = {
                'concrete_and_plaster_products': 'Concrete and plaster products',
                'plastics': 'Plastics',
                'metals': 'Metals',
                'miscellaneous': 'Miscellaneous',
                'sand_stone_ceramics': 'Sand, stone and ceramics',
                'timber': 'Timber',
                'glass': 'Glass',
                'insulation': 'Insulation',
            }
            
            result = []
            def is_kv_tuple(item):
                return isinstance(item, tuple) and len(item) == 2 and isinstance(item[0], str)
            
            def process_item(item):
                if is_kv_tuple(item):
                    key, value = item
                    # Normalize the key if it's in the map
                    normalized_key = key_map.get(key, key)
                    result.append((normalized_key, value))
                elif isinstance(item, list):
                    for sub_item in item:
                        process_item(sub_item)
            
            # If it's a Grasshopper DataTree
            if hasattr(data, 'Branches'):
                for branch in data.Branches:
                    for item in branch:
                        process_item(item)
                return result
                
            # If it's a standard Python list
            if isinstance(data, list):
                for item in data:
                    process_item(item)
                return result
                
            return []

        # --- 2. INITIALIZE DICTIONARY FOR ALL EXPECTED KEYS ---
        expected_keys = [
            'embodied_energy_coefficient', 'embodied_water_coefficient', 'embodied_GHG_coefficient',
            'operational_energy_coefficient', 'operational_ghg_coefficient', 'operational_water_coefficient',
            'maintenance_embodied_water', 'maintenance_embodied_ghg', 'maintenance_embodied_energy',
            'mass', 'Concrete and plaster products', 'Plastics', 'Metals', 'Miscellaneous', 
            'Sand, stone and ceramics', 'Timber', 'Glass', 'Insulation',
            'Insulation_Initial_Embodied_water', 'Timber_Initial_Embodied_water', 'Glass_Initial_Embodied_water',
            'Sand_stone_ceramics_Initial_Embodied_water', 'Miscellaneous_Initial_Embodied_water', 
            'Metals_Initial_Embodied_water', 'Plastics_Initial_Embodied_water', 'Concrete_plaster_products_Initial_Embodied_water',
            'Insulation_Initial_Embodied_energy', 'Timber_Initial_Embodied_energy', 'Glass_Initial_Embodied_energy',
            'Sand_stone_ceramics_Initial_Embodied_energy', 'Miscellaneous_Initial_Embodied_energy', 
            'Metals_Initial_Embodied_energy', 'Plastics_Initial_Embodied_energy', 'Concrete_plaster_products_Initial_Embodied_energy',
            'Insulation_Initial_Embodied_GHG', 'Timber_Initial_Embodied_GHG', 'Glass_Initial_Embodied_GHG',
            'Sand_stone_ceramics_Initial_Embodied_GHG', 'Miscellaneous_Initial_Embodied_GHG', 
            'Metals_Initial_Embodied_GHG', 'Plastics_Initial_Embodied_GHG', 'Concrete_plaster_products_Initial_Embodied_GHG',
            'Insulation_Maintenance_Embodied_water', 'Timber_Maintenance_Embodied_water', 'Glass_Maintenance_Embodied_water',
            'Sand_stone_ceramics_Maintenance_Embodied_water', 'Miscellaneous_Maintenance_Embodied_water', 
            'Metals_Maintenance_Embodied_water', 'Plastics_Maintenance_Embodied_water', 'Concrete_plaster_products_Maintenance_Embodied_water',
            'Insulation_Maintenance_Embodied_energy', 'Timber_Maintenance_Embodied_energy', 'Glass_Maintenance_Embodied_energy',
            'Sand_stone_ceramics_Maintenance_Embodied_energy', 'Miscellaneous_Maintenance_Embodied_energy', 
            'Metals_Maintenance_Embodied_energy', 'Plastics_Maintenance_Embodied_energy', 'Concrete_plaster_products_Maintenance_Embodied_energy',
            'Insulation_Maintenance_Embodied_GHG', 'Timber_Maintenance_Embodied_GHG', 'Glass_Maintenance_Embodied_GHG',
            'Sand_stone_ceramics_Maintenance_Embodied_GHG', 'Miscellaneous_Maintenance_Embodied_GHG', 
            'Metals_Maintenance_Embodied_GHG', 'Plastics_Maintenance_Embodied_GHG', 'Concrete_plaster_products_Maintenance_Embodied_GHG'
        ]
        
        totals = {key: 0.0 for key in expected_keys}

        # --- 3. AGGREGATE DATA FROM ALL INPUTS ---
        all_inputs = [
            assembly_data_list1, assembly_data_list2, assembly_data_list3, assembly_data_list4, assembly_data_list5,
            assembly_data_list6, assembly_data_list7, assembly_data_list8, assembly_data_list9, assembly_data_list10
        ]

        for data_list in all_inputs:
            kv_pairs = extract_kv_lists(data_list)
            for key, value in kv_pairs:
                if key in totals:
                    totals[key] += value

        # --- 4. APPLY REDUCTION FACTORS ---
        def apply_factors(value, reduction_factor):
            factor = reduction_factor if reduction_factor is not None else 0
            return value * (1 - factor / 100.0)
            
        totals['embodied_energy_coefficient'] = apply_factors(totals['embodied_energy_coefficient'], energy_reduction_factor)
        totals['embodied_water_coefficient'] = apply_factors(totals['embodied_water_coefficient'], water_reduction_factor)
        totals['embodied_GHG_coefficient'] = apply_factors(totals['embodied_GHG_coefficient'], ghg_reduction_factor)

        # --- 5. GENERATE FINAL ASSEMBLY DATA LIST ---
        final_assembly_data_list = [
            ('Name', Name),
            ('embodied_energy_coefficient', totals['embodied_energy_coefficient']),
            ('embodied_water_coefficient', totals['embodied_water_coefficient']),
            ('embodied_GHG_coefficient', totals['embodied_GHG_coefficient']),
            ('operational_energy_coefficient', totals['operational_energy_coefficient']),
            ('operational_ghg_coefficient', totals['operational_ghg_coefficient']),
            ('operational_water_coefficient', totals['operational_water_coefficient']),
            ('maintenance_embodied_energy', totals['maintenance_embodied_energy']),
            ('maintenance_embodied_ghg', totals['maintenance_embodied_ghg']),
            ('maintenance_embodied_water', totals['maintenance_embodied_water']),
            ('mass', totals['mass']),
            ('concrete_and_plaster_products', totals['Concrete and plaster products']),
            ('plastics', totals['Plastics']),
            ('metals', totals['Metals']),
            ('miscellaneous', totals['Miscellaneous']),
            ('sand_stone_ceramics', totals['Sand, stone and ceramics']),
            ('timber', totals['Timber']),
            ('glass', totals['Glass']),
            ('insulation', totals['Insulation'])
        ]
        
        # Add the detailed category breakdowns to the list
        for key in expected_keys:
            if key not in ['mass', 'Concrete and plaster products', 'Plastics', 'Metals', 'Miscellaneous', 
                           'Sand, stone and ceramics', 'Timber', 'Glass', 'Insulation', 
                           'embodied_energy_coefficient', 'embodied_water_coefficient', 'embodied_GHG_coefficient', 
                           'operational_energy_coefficient', 'operational_ghg_coefficient', 'operational_water_coefficient', 
                           'maintenance_embodied_energy', 'maintenance_embodied_ghg', 'maintenance_embodied_water']:
                final_assembly_data_list.append((key, totals[key]))

        # --- 6. PREPARE INDIVIDUAL OUTPUTS (Matching your exact original order) ---
        return_keys = [
            'embodied_energy_coefficient', 'embodied_water_coefficient', 'embodied_GHG_coefficient',
            'operational_energy_coefficient', 'operational_ghg_coefficient', 'operational_water_coefficient',
            'maintenance_embodied_energy', 'maintenance_embodied_ghg', 'maintenance_embodied_water',
            'mass', 'Concrete and plaster products', 'Plastics', 'Metals', 'Miscellaneous', 
            'Sand, stone and ceramics', 'Timber', 'Glass', 'Insulation',
            'Insulation_Initial_Embodied_water', 'Timber_Initial_Embodied_water', 'Glass_Initial_Embodied_water',
            'Sand_stone_ceramics_Initial_Embodied_water', 'Miscellaneous_Initial_Embodied_water', 
            'Metals_Initial_Embodied_water', 'Plastics_Initial_Embodied_water', 'Concrete_plaster_products_Initial_Embodied_water',
            'Insulation_Initial_Embodied_energy', 'Timber_Initial_Embodied_energy', 'Glass_Initial_Embodied_energy',
            'Sand_stone_ceramics_Initial_Embodied_energy', 'Miscellaneous_Initial_Embodied_energy', 
            'Metals_Initial_Embodied_energy', 'Plastics_Initial_Embodied_energy', 'Concrete_plaster_products_Initial_Embodied_energy',
            'Insulation_Initial_Embodied_GHG', 'Timber_Initial_Embodied_GHG', 'Glass_Initial_Embodied_GHG',
            'Sand_stone_ceramics_Initial_Embodied_GHG', 'Miscellaneous_Initial_Embodied_GHG', 
            'Metals_Initial_Embodied_GHG', 'Plastics_Initial_Embodied_GHG', 'Concrete_plaster_products_Initial_Embodied_GHG',
            'Insulation_Maintenance_Embodied_water', 'Timber_Maintenance_Embodied_water', 'Glass_Maintenance_Embodied_water',
            'Sand_stone_ceramics_Maintenance_Embodied_water', 'Miscellaneous_Maintenance_Embodied_water', 
            'Metals_Maintenance_Embodied_water', 'Plastics_Maintenance_Embodied_water', 'Concrete_plaster_products_Maintenance_Embodied_water',
            'Insulation_Maintenance_Embodied_energy', 'Timber_Maintenance_Embodied_energy', 'Glass_Maintenance_Embodied_energy',
            'Sand_stone_ceramics_Maintenance_Embodied_energy', 'Miscellaneous_Maintenance_Embodied_energy', 
            'Metals_Maintenance_Embodied_energy', 'Plastics_Maintenance_Embodied_energy', 'Concrete_plaster_products_Maintenance_Embodied_energy',
            'Insulation_Maintenance_Embodied_GHG', 'Timber_Maintenance_Embodied_GHG', 'Glass_Maintenance_Embodied_GHG',
            'Sand_stone_ceramics_Maintenance_Embodied_GHG', 'Miscellaneous_Maintenance_Embodied_GHG', 
            'Metals_Maintenance_Embodied_GHG', 'Plastics_Maintenance_Embodied_GHG', 'Concrete_plaster_products_Maintenance_Embodied_GHG'
        ]

        # Return the final list and all individual variables
        return (final_assembly_data_list,) + tuple(totals[k] for k in return_keys)
