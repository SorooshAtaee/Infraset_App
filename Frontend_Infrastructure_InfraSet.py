from ghpythonlib.componentbase import executingcomponent as component
import rhinoscriptsyntax as rs
import Rhino.Geometry as rg
import System
from Grasshopper.Kernel import GH_RuntimeMessageLevel as RML


class InfrasetAssembly(component):
    def RunScript(self, Name, assembly_data_list1, assembly_data_list2, assembly_data_list3, assembly_data_list4, assembly_data_list5,
                  assembly_data_list6, assembly_data_list7, assembly_data_list8, assembly_data_list9, assembly_data_list10,
                   null3, energy_reduction_factor, water_reduction_factor, ghg_reduction_factor):

        # Default values for optional inputs
        energy_reduction_factor = energy_reduction_factor or 0
        water_reduction_factor = water_reduction_factor or 0
        ghg_reduction_factor = ghg_reduction_factor or 0

        # Initialize cumulative variables
        embodied_energy_coefficient = 0
        embodied_water_coefficient = 0
        embodied_GHG_coefficient = 0
        operational_energy_coefficient = 0
        operational_ghg_coefficient = 0
        operational_water_coefficient = 0
        mass = 0
        concrete_and_plaster_products = 0
        plastics = 0
        metals = 0
        miscellaneous = 0
        sand_stone_ceramics = 0
        timber = 0
        glass = 0
        insulation = 0
        maintenance_embodied_ghg=0
        maintenance_embodied_water=0
        maintenance_embodied_energy=0
                # Embodied Water by Material Categories
        Insulation_Initial_Embodied_water = 0.0
        Timber_Initial_Embodied_water = 0.0
        Glass_Initial_Embodied_water = 0.0
        Sand_stone_ceramics_Initial_Embodied_water = 0.0
        Miscellaneous_Initial_Embodied_water = 0.0
        Metals_Initial_Embodied_water = 0.0
        Plastics_Initial_Embodied_water = 0.0
        Concrete_plaster_products_Initial_Embodied_water = 0.0
        # Embodied Energy by Material Categories
        Insulation_Initial_Embodied_energy = 0.0
        Timber_Initial_Embodied_energy = 0.0
        Glass_Initial_Embodied_energy = 0.0
        Sand_stone_ceramics_Initial_Embodied_energy = 0.0
        Miscellaneous_Initial_Embodied_energy = 0.0
        Metals_Initial_Embodied_energy = 0.0
        Plastics_Initial_Embodied_energy = 0.0
        Concrete_plaster_products_Initial_Embodied_energy = 0.0
        # Embodied GHG by Material Categories
        Insulation_Initial_Embodied_GHG = 0.0
        Timber_Initial_Embodied_GHG = 0.0
        Glass_Initial_Embodied_GHG = 0.0
        Sand_stone_ceramics_Initial_Embodied_GHG = 0.0
        Miscellaneous_Initial_Embodied_GHG = 0.0
        Metals_Initial_Embodied_GHG = 0.0
        Plastics_Initial_Embodied_GHG = 0.0
        Concrete_plaster_products_Initial_Embodied_GHG = 0.0
        # Maintenance Embodied Metrics
        Insulation_Maintenance_Embodied_water = 0.0
        Timber_Maintenance_Embodied_water = 0.0
        Glass_Maintenance_Embodied_water = 0.0
        Sand_stone_ceramics_Maintenance_Embodied_water = 0.0
        Miscellaneous_Maintenance_Embodied_water = 0.0
        Metals_Maintenance_Embodied_water = 0.0
        Plastics_Maintenance_Embodied_water = 0.0
        Concrete_plaster_products_Maintenance_Embodied_water = 0.0
        Insulation_Maintenance_Embodied_energy = 0.0
        Timber_Maintenance_Embodied_energy = 0.0
        Glass_Maintenance_Embodied_energy = 0.0
        Sand_stone_ceramics_Maintenance_Embodied_energy = 0.0
        Miscellaneous_Maintenance_Embodied_energy = 0.0
        Metals_Maintenance_Embodied_energy = 0.0
        Plastics_Maintenance_Embodied_energy = 0.0
        Concrete_plaster_products_Maintenance_Embodied_energy = 0.0
        Insulation_Maintenance_Embodied_GHG = 0.0
        Timber_Maintenance_Embodied_GHG = 0.0
        Glass_Maintenance_Embodied_GHG = 0.0
        Sand_stone_ceramics_Maintenance_Embodied_GHG = 0.0
        Miscellaneous_Maintenance_Embodied_GHG = 0.0
        Metals_Maintenance_Embodied_GHG = 0.0
        Plastics_Maintenance_Embodied_GHG = 0.0
        Concrete_plaster_products_Maintenance_Embodied_GHG = 0.0

        # Combine all assembly data lists into one list
        all_assembly_data_lists = [
            assembly_data_list1, assembly_data_list2, assembly_data_list3, assembly_data_list4, assembly_data_list5,
            assembly_data_list6, assembly_data_list7, assembly_data_list8, assembly_data_list9, assembly_data_list10
        ]

        # Filter out None values
        all_assembly_data_lists = [data for data in all_assembly_data_lists if data is not None]

        # Process each assembly data list to aggregate the values
        for assembly_data_list in all_assembly_data_lists:
            for key, value in assembly_data_list:
                if key == 'embodied_energy_coefficient':
                    embodied_energy_coefficient += value
                elif key == 'embodied_water_coefficient':
                    embodied_water_coefficient += value
                elif key == 'embodied_GHG_coefficient':
                    embodied_GHG_coefficient += value
                elif key == 'operational_energy_coefficient':
                    operational_energy_coefficient += value
                elif key == 'operational_ghg_coefficient':
                    operational_ghg_coefficient += value
                elif key == 'operational_water_coefficient':
                    operational_water_coefficient += value
                elif key == 'maintenance_embodied_water':
                    maintenance_embodied_water += value
                elif key == 'maintenance_embodied_ghg':
                    maintenance_embodied_ghg += value
                elif key == 'maintenance_embodied_energy':
                    maintenance_embodied_energy += value
                elif key == 'mass':
                    mass += value
                elif key == 'Concrete and plaster products':
                    concrete_and_plaster_products += value
                elif key == 'Plastics':
                    plastics += value
                elif key == 'Metals':
                    metals += value
                elif key == 'Miscellaneous':
                    miscellaneous += value
                elif key == 'Sand, stone and ceramics':
                    sand_stone_ceramics += value
                elif key == 'Timber':
                    timber += value
                elif key == 'Glass':
                    glass += value
                elif key == 'Insulation':
                    insulation += value
                                # Embodied Water by Material Categories
                elif key == 'Insulation_Initial_Embodied_water':
                    Insulation_Initial_Embodied_water += value
                elif key == 'Timber_Initial_Embodied_water':
                    Timber_Initial_Embodied_water += value
                elif key == 'Glass_Initial_Embodied_water':
                    Glass_Initial_Embodied_water += value
                elif key == 'Sand_stone_ceramics_Initial_Embodied_water':
                    Sand_stone_ceramics_Initial_Embodied_water += value
                elif key == 'Miscellaneous_Initial_Embodied_water':
                    Miscellaneous_Initial_Embodied_water += value
                elif key == 'Metals_Initial_Embodied_water':
                    Metals_Initial_Embodied_water += value
                elif key == 'Plastics_Initial_Embodied_water':
                    Plastics_Initial_Embodied_water += value
                elif key == 'Concrete_plaster_products_Initial_Embodied_water':
                    Concrete_plaster_products_Initial_Embodied_water += value
                # Embodied Energy by Material Categories
                elif key == 'Insulation_Initial_Embodied_energy':
                    Insulation_Initial_Embodied_energy += value
                elif key == 'Timber_Initial_Embodied_energy':
                    Timber_Initial_Embodied_energy += value
                elif key == 'Glass_Initial_Embodied_energy':
                    Glass_Initial_Embodied_energy += value
                elif key == 'Sand_stone_ceramics_Initial_Embodied_energy':
                    Sand_stone_ceramics_Initial_Embodied_energy += value
                elif key == 'Miscellaneous_Initial_Embodied_energy':
                    Miscellaneous_Initial_Embodied_energy += value
                elif key == 'Metals_Initial_Embodied_energy':
                    Metals_Initial_Embodied_energy += value
                elif key == 'Plastics_Initial_Embodied_energy':
                    Plastics_Initial_Embodied_energy += value
                elif key == 'Concrete_plaster_products_Initial_Embodied_energy':
                    Concrete_plaster_products_Initial_Embodied_energy += value
                # Embodied GHG by Material Categories
                elif key == 'Insulation_Initial_Embodied_GHG':
                    Insulation_Initial_Embodied_GHG += value
                elif key == 'Timber_Initial_Embodied_GHG':
                    Timber_Initial_Embodied_GHG += value
                elif key == 'Glass_Initial_Embodied_GHG':
                    Glass_Initial_Embodied_GHG += value
                elif key == 'Sand_stone_ceramics_Initial_Embodied_GHG':
                    Sand_stone_ceramics_Initial_Embodied_GHG += value
                elif key == 'Miscellaneous_Initial_Embodied_GHG':
                    Miscellaneous_Initial_Embodied_GHG += value
                elif key == 'Metals_Initial_Embodied_GHG':
                    Metals_Initial_Embodied_GHG += value
                elif key == 'Plastics_Initial_Embodied_GHG':
                    Plastics_Initial_Embodied_GHG += value
                elif key == 'Concrete_plaster_products_Initial_Embodied_GHG':
                    Concrete_plaster_products_Initial_Embodied_GHG += value
                # Maintenance Embodied Water by Material Categories
                elif key == 'Insulation_Maintenance_Embodied_water':
                    Insulation_Maintenance_Embodied_water += value
                elif key == 'Timber_Maintenance_Embodied_water':
                    Timber_Maintenance_Embodied_water += value
                elif key == 'Glass_Maintenance_Embodied_water':
                    Glass_Maintenance_Embodied_water += value
                elif key == 'Sand_stone_ceramics_Maintenance_Embodied_water':
                    Sand_stone_ceramics_Maintenance_Embodied_water += value
                elif key == 'Miscellaneous_Maintenance_Embodied_water':
                    Miscellaneous_Maintenance_Embodied_water += value
                elif key == 'Metals_Maintenance_Embodied_water':
                    Metals_Maintenance_Embodied_water += value
                elif key == 'Plastics_Maintenance_Embodied_water':
                    Plastics_Maintenance_Embodied_water += value
                elif key == 'Concrete_plaster_products_Maintenance_Embodied_water':
                    Concrete_plaster_products_Maintenance_Embodied_water += value

                # Maintenance Embodied Energy by Material Categories
                elif key == 'Insulation_Maintenance_Embodied_energy':
                    Insulation_Maintenance_Embodied_energy += value
                elif key == 'Timber_Maintenance_Embodied_energy':
                    Timber_Maintenance_Embodied_energy += value
                elif key == 'Glass_Maintenance_Embodied_energy':
                    Glass_Maintenance_Embodied_energy += value
                elif key == 'Sand_stone_ceramics_Maintenance_Embodied_energy':
                    Sand_stone_ceramics_Maintenance_Embodied_energy += value
                elif key == 'Miscellaneous_Maintenance_Embodied_energy':
                    Miscellaneous_Maintenance_Embodied_energy += value
                elif key == 'Metals_Maintenance_Embodied_energy':
                    Metals_Maintenance_Embodied_energy += value
                elif key == 'Plastics_Maintenance_Embodied_energy':
                    Plastics_Maintenance_Embodied_energy += value
                elif key == 'Concrete_plaster_products_Maintenance_Embodied_energy':
                    Concrete_plaster_products_Maintenance_Embodied_energy += value

                # Maintenance Embodied GHG by Material Categories
                elif key == 'Insulation_Maintenance_Embodied_GHG':
                    Insulation_Maintenance_Embodied_GHG += value
                elif key == 'Timber_Maintenance_Embodied_GHG':
                    Timber_Maintenance_Embodied_GHG += value
                elif key == 'Glass_Maintenance_Embodied_GHG':
                    Glass_Maintenance_Embodied_GHG += value
                elif key == 'Sand_stone_ceramics_Maintenance_Embodied_GHG':
                    Sand_stone_ceramics_Maintenance_Embodied_GHG += value
                elif key == 'Miscellaneous_Maintenance_Embodied_GHG':
                    Miscellaneous_Maintenance_Embodied_GHG += value
                elif key == 'Metals_Maintenance_Embodied_GHG':
                    Metals_Maintenance_Embodied_GHG += value
                elif key == 'Plastics_Maintenance_Embodied_GHG':
                    Plastics_Maintenance_Embodied_GHG += value
                elif key == 'Concrete_plaster_products_Maintenance_Embodied_GHG':
                    Concrete_plaster_products_Maintenance_Embodied_GHG += value

        # Apply wastage coefficient and reduction factors to the aggregated values
        def apply_factors(value, reduction_factor):
            return value * (1 - reduction_factor / 100)
        embodied_energy_coefficient = apply_factors(embodied_energy_coefficient, energy_reduction_factor)
        embodied_water_coefficient = apply_factors(embodied_water_coefficient, water_reduction_factor)
        embodied_GHG_coefficient = apply_factors(embodied_GHG_coefficient, ghg_reduction_factor)


        # Generate a final assembly data list
        final_assembly_data_list = [
            ('Name', Name),
            ('embodied_energy_coefficient', embodied_energy_coefficient),
            ('embodied_water_coefficient', embodied_water_coefficient),
            ('embodied_GHG_coefficient', embodied_GHG_coefficient),
            ('operational_energy_coefficient', operational_energy_coefficient),
            ('operational_ghg_coefficient', operational_ghg_coefficient),
            ('operational_water_coefficient', operational_water_coefficient),
            ('maintenance_embodied_energy', maintenance_embodied_energy),
            ('maintenance_embodied_ghg', maintenance_embodied_ghg),
            ('maintenance_embodied_water', maintenance_embodied_water),
            ('mass', mass),
            ('concrete_and_plaster_products', concrete_and_plaster_products),
            ('plastics', plastics),
            ('metals', metals),
            ('miscellaneous', miscellaneous),
            ('sand_stone_ceramics', sand_stone_ceramics),
            ('timber', timber),
            ('glass', glass),
            ('insulation', insulation),
            # Embodied Water by Material Categories
    ('Insulation_Initial_Embodied_water', Insulation_Initial_Embodied_water),
    ('Timber_Initial_Embodied_water', Timber_Initial_Embodied_water),
    ('Glass_Initial_Embodied_water', Glass_Initial_Embodied_water),
    ('Sand_stone_ceramics_Initial_Embodied_water', Sand_stone_ceramics_Initial_Embodied_water),
    ('Miscellaneous_Initial_Embodied_water', Miscellaneous_Initial_Embodied_water),
    ('Metals_Initial_Embodied_water', Metals_Initial_Embodied_water),
    ('Plastics_Initial_Embodied_water', Plastics_Initial_Embodied_water),
    ('Concrete_plaster_products_Initial_Embodied_water', Concrete_plaster_products_Initial_Embodied_water),

    # Embodied Energy by Material Categories
    ('Insulation_Initial_Embodied_energy', Insulation_Initial_Embodied_energy),
    ('Timber_Initial_Embodied_energy', Timber_Initial_Embodied_energy),
    ('Glass_Initial_Embodied_energy', Glass_Initial_Embodied_energy),
    ('Sand_stone_ceramics_Initial_Embodied_energy', Sand_stone_ceramics_Initial_Embodied_energy),
    ('Miscellaneous_Initial_Embodied_energy', Miscellaneous_Initial_Embodied_energy),
    ('Metals_Initial_Embodied_energy', Metals_Initial_Embodied_energy),
    ('Plastics_Initial_Embodied_energy', Plastics_Initial_Embodied_energy),
    ('Concrete_plaster_products_Initial_Embodied_energy', Concrete_plaster_products_Initial_Embodied_energy),

    # Embodied GHG by Material Categories
    ('Insulation_Initial_Embodied_GHG', Insulation_Initial_Embodied_GHG),
    ('Timber_Initial_Embodied_GHG', Timber_Initial_Embodied_GHG),
    ('Glass_Initial_Embodied_GHG', Glass_Initial_Embodied_GHG),
    ('Sand_stone_ceramics_Initial_Embodied_GHG', Sand_stone_ceramics_Initial_Embodied_GHG),
    ('Miscellaneous_Initial_Embodied_GHG', Miscellaneous_Initial_Embodied_GHG),
    ('Metals_Initial_Embodied_GHG', Metals_Initial_Embodied_GHG),
    ('Plastics_Initial_Embodied_GHG', Plastics_Initial_Embodied_GHG),
    ('Concrete_plaster_products_Initial_Embodied_GHG', Concrete_plaster_products_Initial_Embodied_GHG),

    # Maintenance Embodied Water by Material Categories
    ('Insulation_Maintenance_Embodied_water', Insulation_Maintenance_Embodied_water),
    ('Timber_Maintenance_Embodied_water', Timber_Maintenance_Embodied_water),
    ('Glass_Maintenance_Embodied_water', Glass_Maintenance_Embodied_water),
    ('Sand_stone_ceramics_Maintenance_Embodied_water', Sand_stone_ceramics_Maintenance_Embodied_water),
    ('Miscellaneous_Maintenance_Embodied_water', Miscellaneous_Maintenance_Embodied_water),
    ('Metals_Maintenance_Embodied_water', Metals_Maintenance_Embodied_water),
    ('Plastics_Maintenance_Embodied_water', Plastics_Maintenance_Embodied_water),
    ('Concrete_plaster_products_Maintenance_Embodied_water', Concrete_plaster_products_Maintenance_Embodied_water),

    # Maintenance Embodied Energy by Material Categories
    ('Insulation_Maintenance_Embodied_energy', Insulation_Maintenance_Embodied_energy),
    ('Timber_Maintenance_Embodied_energy', Timber_Maintenance_Embodied_energy),
    ('Glass_Maintenance_Embodied_energy', Glass_Maintenance_Embodied_energy),
    ('Sand_stone_ceramics_Maintenance_Embodied_energy', Sand_stone_ceramics_Maintenance_Embodied_energy),
    ('Miscellaneous_Maintenance_Embodied_energy', Miscellaneous_Maintenance_Embodied_energy),
    ('Metals_Maintenance_Embodied_energy', Metals_Maintenance_Embodied_energy),
    ('Plastics_Maintenance_Embodied_energy', Plastics_Maintenance_Embodied_energy),
    ('Concrete_plaster_products_Maintenance_Embodied_energy', Concrete_plaster_products_Maintenance_Embodied_energy),

    # Maintenance Embodied GHG by Material Categories
    ('Insulation_Maintenance_Embodied_GHG', Insulation_Maintenance_Embodied_GHG),
    ('Timber_Maintenance_Embodied_GHG', Timber_Maintenance_Embodied_GHG),
    ('Glass_Maintenance_Embodied_GHG', Glass_Maintenance_Embodied_GHG),
    ('Sand_stone_ceramics_Maintenance_Embodied_GHG', Sand_stone_ceramics_Maintenance_Embodied_GHG),
    ('Miscellaneous_Maintenance_Embodied_GHG', Miscellaneous_Maintenance_Embodied_GHG),
    ('Metals_Maintenance_Embodied_GHG', Metals_Maintenance_Embodied_GHG),
    ('Plastics_Maintenance_Embodied_GHG', Plastics_Maintenance_Embodied_GHG),
    ('Concrete_plaster_products_Maintenance_Embodied_GHG', Concrete_plaster_products_Maintenance_Embodied_GHG),
        ]

        # Return the final values
        return (
            final_assembly_data_list,
    embodied_energy_coefficient, 
    embodied_water_coefficient, 
    embodied_GHG_coefficient,
    operational_energy_coefficient, 
    operational_ghg_coefficient, 
    operational_water_coefficient,
    maintenance_embodied_energy, 
    maintenance_embodied_ghg, 
    maintenance_embodied_water,
    mass, 
    concrete_and_plaster_products, 
    plastics, 
    metals, 
    miscellaneous, 
    sand_stone_ceramics, 
    timber, 
    glass, 
    insulation,
    
    # Embodied Water by Material Categories
    Insulation_Initial_Embodied_water,
    Timber_Initial_Embodied_water,
    Glass_Initial_Embodied_water,
    Sand_stone_ceramics_Initial_Embodied_water,
    Miscellaneous_Initial_Embodied_water,
    Metals_Initial_Embodied_water,
    Plastics_Initial_Embodied_water,
    Concrete_plaster_products_Initial_Embodied_water,

    # Embodied Energy by Material Categories
    Insulation_Initial_Embodied_energy,
    Timber_Initial_Embodied_energy,
    Glass_Initial_Embodied_energy,
    Sand_stone_ceramics_Initial_Embodied_energy,
    Miscellaneous_Initial_Embodied_energy,
    Metals_Initial_Embodied_energy,
    Plastics_Initial_Embodied_energy,
    Concrete_plaster_products_Initial_Embodied_energy,

    # Embodied GHG by Material Categories
    Insulation_Initial_Embodied_GHG,
    Timber_Initial_Embodied_GHG,
    Glass_Initial_Embodied_GHG,
    Sand_stone_ceramics_Initial_Embodied_GHG,
    Miscellaneous_Initial_Embodied_GHG,
    Metals_Initial_Embodied_GHG,
    Plastics_Initial_Embodied_GHG,
    Concrete_plaster_products_Initial_Embodied_GHG,

    # Maintenance Embodied Water by Material Categories
    Insulation_Maintenance_Embodied_water,
    Timber_Maintenance_Embodied_water,
    Glass_Maintenance_Embodied_water,
    Sand_stone_ceramics_Maintenance_Embodied_water,
    Miscellaneous_Maintenance_Embodied_water,
    Metals_Maintenance_Embodied_water,
    Plastics_Maintenance_Embodied_water,
    Concrete_plaster_products_Maintenance_Embodied_water,

    # Maintenance Embodied Energy by Material Categories
    Insulation_Maintenance_Embodied_energy,
    Timber_Maintenance_Embodied_energy,
    Glass_Maintenance_Embodied_energy,
    Sand_stone_ceramics_Maintenance_Embodied_energy,
    Miscellaneous_Maintenance_Embodied_energy,
    Metals_Maintenance_Embodied_energy,
    Plastics_Maintenance_Embodied_energy,
    Concrete_plaster_products_Maintenance_Embodied_energy,

    # Maintenance Embodied GHG by Material Categories
    Insulation_Maintenance_Embodied_GHG,
    Timber_Maintenance_Embodied_GHG,
    Glass_Maintenance_Embodied_GHG,
    Sand_stone_ceramics_Maintenance_Embodied_GHG,
    Miscellaneous_Maintenance_Embodied_GHG,
    Metals_Maintenance_Embodied_GHG,
    Plastics_Maintenance_Embodied_GHG,
    Concrete_plaster_products_Maintenance_Embodied_GHG
        )