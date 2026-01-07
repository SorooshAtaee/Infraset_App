from ghpythonlib.componentbase import executingcomponent as component
from Backend_InfraSet import MaterialDatabase, AssemblyDatabase, ElementDatabase
import rhinoscriptsyntax as rs
import Rhino.Geometry as rg
import System
from Grasshopper.Kernel import GH_RuntimeMessageLevel as RML
from Grasshopper.Kernel.Special import GH_ValueList, GH_ValueListItem
from Grasshopper.Kernel import GH_Document
from System.Drawing import PointF

class InfrasetAssembly(component):
    def RunScript(
        self,
        connect_button,
        assembly_category,
        No,
        element_data_list,
        null1,
        length1,
        width,
        height,
        area_input,
        null2,
        wastage_coefficient,
        material_service_life,
        null3,
        energy_reduction_factor,
        water_reduction_factor,
        ghg_reduction_factor,
        traffic_factor,
        PKT_million_60_years_input,
    ):
        # Value list creation logic
        if connect_button and self.Params.Input[1].SourceCount == 0:
            try:
                material_db = MaterialDatabase()
                assembly_db = AssemblyDatabase(material_db.material_db)
                assembly_db.populate_assemblies()
                
                vl = GH_ValueList()
                vl.CreateAttributes()
                
                for cat in assembly_db.assembly_db.keys():
                    item = GH_ValueListItem(str(cat), "\"{0}\"".format(str(cat)))  # Legacy formatting
                    vl.ListItems.Add(item)
                
                vl.Attributes.Pivot = PointF(
                    self.Params.Input[1].Attributes.Pivot.X - 250,
                    self.Params.Input[1].Attributes.Pivot.Y
                )
                
                ghdoc = self.OnPingDocument()
                ghdoc.AddObject(vl, False)
                self.Params.Input[1].AddSource(vl)
                self.Params.OnParametersChanged()
                ghdoc.ScheduleSolution(5, GH_Document.GH_ScheduleDelegate(self.ExpireSolution))
                
            except Exception as e:
                self.AddRuntimeMessage(RML.Error, "Value list failed: {0}".format(str(e)))  # Legacy formatting

        # Original calculations (unchanged)
        element_data_list = element_data_list or []
        wastage_coefficient = wastage_coefficient or 0
        energy_reduction_factor = energy_reduction_factor or 0
        water_reduction_factor = water_reduction_factor or 0
        ghg_reduction_factor = ghg_reduction_factor or 0
        traffic_factor = traffic_factor or 1
        No = No or 1
        material_service_life = material_service_life or 60
        length1 = length1 or 1
        width = width or 1
        height = height or 1
        # Initialize material-specific accumulators
        concrete_and_plaster_products_mass = 0.0
        plastics_mass = 0.0
        glass_mass = 0.0
        insulation_mass = 0.0
        metals_mass = 0.0
        miscellaneous_mass = 0.0
        sand_stone_ceramics_mass = 0.0
        timber_mass = 0.0
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



        center = surface = length2 = distance = box_height = assembly_db_result = None
        material_db = MaterialDatabase()
        assembly_db = AssemblyDatabase(material_db.material_db)
        element_db = ElementDatabase(material_db.material_db)
        assembly_db.populate_assemblies()

        assembly_data = assembly_db.assembly_db.get(assembly_category)
        if not assembly_data:
            self.AddRuntimeMessage(RML.Warning, "No data found for: {0}".format(assembly_category))
            return None

        PKT_million_60_years = (
            PKT_million_60_years_input
            if PKT_million_60_years_input is not None
            else assembly_data.get("PKT_million_60_years", 1)
        )

        if area_input is not None:
            area = area_input
        else:
            area = int(length1 * width)

        volume = area * height 

        energy_reduction_factor = min(max(energy_reduction_factor, 0), 100)
        water_reduction_factor = min(max(water_reduction_factor, 0), 100)
        ghg_reduction_factor = min(max(ghg_reduction_factor, 0), 100)
        wastage_coefficient = min(max(wastage_coefficient, 0), 100)

        embodied_energy_coefficient = embodied_water_coefficient = embodied_GHG_coefficient = 0
        maintenance_embodied_energy = maintenance_embodied_ghg = maintenance_embodied_water = maintenance_mass = 0
        pavement_mass = aluminum_mass = gravel_mass = asphalt_mass = wood_mass = upvc_mass = polycarbonate_mass = recycled_aggregate_mass = cement_mass = sand_mass = 0

        if assembly_data:
            embodied_energy_coefficient = assembly_data.get('Initial_Embodied_Energy_(MJ)', 0)
            embodied_water_coefficient = assembly_data.get('Initial_Embodied_Water_(L)', 0)
            embodied_GHG_coefficient = assembly_data.get('Initial_Embodied_GHG_(kgCO2e)', 0)

            embodied_energy_coefficient *= (1 + wastage_coefficient / 100) if embodied_energy_coefficient != 0 else 0
            embodied_water_coefficient *= (1 + wastage_coefficient / 100) if embodied_water_coefficient != 0 else 0
            embodied_GHG_coefficient *= (1 + wastage_coefficient / 100) if embodied_GHG_coefficient != 0 else 0

            embodied_energy_coefficient *= (1 - energy_reduction_factor / 100) if embodied_energy_coefficient != 0 else 0
            embodied_water_coefficient *= (1 - water_reduction_factor / 100) if embodied_water_coefficient != 0 else 0
            embodied_GHG_coefficient *= (1 - ghg_reduction_factor / 100) if embodied_GHG_coefficient != 0 else 0

            mass = assembly_data.get('Total_Mass_(kg)', 0) 
            concrete_and_plaster_products_mass = assembly_data.get('Concrete and plaster products_Mass_(kg)', 0) 
            plastics_mass = assembly_data.get('Plastics_Mass_(kg)', 0) 
            metals_mass = assembly_data.get('Metals_Mass_(kg)', 0) 
            miscellaneous_mass = assembly_data.get('Miscellaneous_Mass_(kg)', 0) 
            sand_stone_ceramics_mass = assembly_data.get('Sand, stone and ceramics_Mass_(kg)', 0) 
            timber_mass = assembly_data.get('Timber_Mass_(kg)', 0) 
            glass_mass = assembly_data.get('Glass_Mass_(kg)', 0) 
            insulation_mass = assembly_data.get('Insulation_Mass_(kg)', 0) 

            maintenance_embodied_energy = assembly_data.get('Maintenance_Embodied_Energy_(MJ)', 0) 
            maintenance_embodied_ghg = assembly_data.get('Maintenance_Embodied_GHG_(kgCO2e)', 0) 
            maintenance_embodied_water = assembly_data.get('Maintenance_Embodied_Water_(L)', 0) 
            maintenance_mass = assembly_data.get('Maintenance_Mass_(kg)', 0) 

            operational_energy_coefficient = assembly_data.get('Operational_Energy_(MJ/No)', 0) * (1 - energy_reduction_factor / 100)
            operational_ghg_coefficient = assembly_data.get('Operational_GHG_(kgCO2e/No)', 0) * (1 - ghg_reduction_factor / 100)
            operational_water_coefficient = assembly_data.get('Operational_Water_(L/No)', 0) * (1 - water_reduction_factor / 100)
            
                                # Embodied calculations GHG for material categories
            Concrete_plaster_products_Initial_Embodied_GHG = assembly_data.get("Concrete and plaster products_Initial_Embodied_GHG_(kgCO2e)", 0) * No * (material_service_life / 60)* volume
            Plastics_Initial_Embodied_GHG = assembly_data.get("Plastics_Initial_Embodied_GHG_(kgCO2e)", 0) * No * (material_service_life / 60)* volume
            Metals_Initial_Embodied_GHG = assembly_data.get("Metals_Initial_Embodied_GHG_(kgCO2e)", 0) * No * (material_service_life / 60)* volume
            Miscellaneous_Initial_Embodied_GHG = assembly_data.get("Miscellaneous_Initial_Embodied_GHG_(kgCO2e)", 0) * No * (material_service_life / 60)* volume
            Sand_stone_ceramics_Initial_Embodied_GHG = assembly_data.get("Sand, stone and ceramics_Initial_Embodied_GHG_(kgCO2e)", 0) * No * (material_service_life / 60)* volume
            Glass_Initial_Embodied_GHG = assembly_data.get("Glass_Initial_Embodied_GHG_(kgCO2e)", 0) * No * (material_service_life / 60)* volume
            Timber_Initial_Embodied_GHG = assembly_data.get("Timber_Initial_Embodied_GHG_(kgCO2e)", 0) * No * (material_service_life / 60)* volume
            Insulation_Initial_Embodied_GHG = assembly_data.get("Insulation_Initial_Embodied_GHG_(kgCO2e)", 0) * No * (material_service_life / 60)* volume
                    
                    # Maintenance Embodied GHG calculations for material categories
            Concrete_plaster_products_Maintenance_Embodied_GHG = assembly_data.get("Concrete and plaster products_Maintenance_Embodied_GHG_(kgCO2e)", 0) * No * (material_service_life / 60)* volume
            Plastics_Maintenance_Embodied_GHG = assembly_data.get("Plastics_Maintenance_Embodied_GHG_(kgCO2e)", 0) * No * (material_service_life / 60)* volume
            Metals_Maintenance_Embodied_GHG = assembly_data.get("Metals_Maintenance_Embodied_GHG_(kgCO2e)", 0) * No * (material_service_life / 60)* volume
            Miscellaneous_Maintenance_Embodied_GHG = assembly_data.get("Miscellaneous_Maintenance_Embodied_GHG_(kgCO2e)", 0) * No * (material_service_life / 60)* volume
            Sand_stone_ceramics_Maintenance_Embodied_GHG = assembly_data.get("Sand, stone and ceramics_Maintenance_Embodied_GHG_(kgCO2e)", 0) * No * (material_service_life / 60)* volume
            Glass_Maintenance_Embodied_GHG = assembly_data.get("Glass_Maintenance_Embodied_GHG_(kgCO2e)", 0) * No * (material_service_life / 60)* volume
            Timber_Maintenance_Embodied_GHG = assembly_data.get("Timber_Maintenance_Embodied_GHG_(kgCO2e)", 0) * No * (material_service_life / 60)* volume
            Insulation_Maintenance_Embodied_GHG = assembly_data.get("Insulation_Maintenance_Embodied_GHG_(kgCO2e)", 0) * No * (material_service_life / 60)* volume
                    
                    # Embodied calculations Energy for material categories
            Concrete_plaster_products_Initial_Embodied_energy = assembly_data.get("Concrete and plaster products_Initial_Embodied_energy_(MJ)", 0) * No * (material_service_life / 60)* volume
            Plastics_Initial_Embodied_energy = assembly_data.get("Plastics_Initial_Embodied_energy_(MJ)", 0) * No * (material_service_life / 60)* volume
            Metals_Initial_Embodied_energy = assembly_data.get("Metals_Initial_Embodied_energy_(MJ)", 0) * No * (material_service_life / 60)* volume
            Miscellaneous_Initial_Embodied_energy = assembly_data.get("Miscellaneous_Initial_Embodied_energy_(MJ)", 0) * No * (material_service_life / 60)* volume
            Sand_stone_ceramics_Initial_Embodied_energy = assembly_data.get("Sand, stone and ceramics_Initial_Embodied_energy_(MJ)", 0) * No * (material_service_life / 60)* volume
            Glass_Initial_Embodied_energy = assembly_data.get("Glass_Initial_Embodied_energy_(MJ)", 0) * No * (material_service_life / 60)* volume
            Timber_Initial_Embodied_energy = assembly_data.get("Timber_Initial_Embodied_energy_(MJ)", 0) * No * (material_service_life / 60)* volume
            Insulation_Initial_Embodied_energy = assembly_data.get("Insulation_Initial_Embodied_energy_(MJ)", 0) * No * (material_service_life / 60)* volume
                    
                    # Maintenance Embodied Energy calculations for material categories
            Concrete_plaster_products_Maintenance_Embodied_energy = assembly_data.get("Concrete and plaster products_Maintenance_Embodied_energy_(MJ)", 0) * No * (material_service_life / 60)* volume
            Plastics_Maintenance_Embodied_energy = assembly_data.get("Plastics_Maintenance_Embodied_energy_(MJ)", 0) * No * (material_service_life / 60)* volume
            Metals_Maintenance_Embodied_energy = assembly_data.get("Metals_Maintenance_Embodied_energy_(MJ)", 0) * No * (material_service_life / 60)* volume
            Miscellaneous_Maintenance_Embodied_energy = assembly_data.get("Miscellaneous_Maintenance_Embodied_energy_(MJ)", 0) * No * (material_service_life / 60)* volume
            Sand_stone_ceramics_Maintenance_Embodied_energy = assembly_data.get("Sand, stone and ceramics_Maintenance_Embodied_energy_(MJ)", 0) * No * (material_service_life / 60)* volume
            Glass_Maintenance_Embodied_energy = assembly_data.get("Glass_Maintenance_Embodied_energy_(MJ)", 0) * No * (material_service_life / 60)* volume
            Timber_Maintenance_Embodied_energy = assembly_data.get("Timber_Maintenance_Embodied_energy_(MJ)", 0) * No * (material_service_life / 60)* volume
            Insulation_Maintenance_Embodied_energy = assembly_data.get("Insulation_Maintenance_Embodied_energy_(MJ)", 0) * No * (material_service_life / 60)* volume
                    
                    # Embodied calculations water for material categories
            Concrete_plaster_products_Initial_Embodied_water = assembly_data.get("Concrete and plaster products_Initial_embodied_water_(L)", 0) * No * (material_service_life / 60)* volume
            Plastics_Initial_Embodied_water = assembly_data.get("Plastics_Initial_Embodied_water_(L)", 0) * No * (material_service_life / 60)* volume
            Metals_Initial_Embodied_water = assembly_data.get("Metals_Initial_Embodied_water_(L)", 0) * No * (material_service_life / 60)* volume
            Miscellaneous_Initial_Embodied_water = assembly_data.get("Miscellaneous_Initial_Embodied_water_(L)", 0) * No * (material_service_life / 60)* volume
            Sand_stone_ceramics_Initial_Embodied_water = assembly_data.get("Sand, stone and ceramics_Initial_Embodied_water_(L)", 0) * No * (material_service_life / 60)* volume
            Glass_Initial_Embodied_water = assembly_data.get("Glass_Initial_Embodied_water_(L)", 0) * No * (material_service_life / 60)* volume
            Timber_Initial_Embodied_water = assembly_data.get("Timber_Initial_Embodied_water_(L)", 0) * No * (material_service_life / 60)* volume
            Insulation_Initial_Embodied_water = assembly_data.get("Insulation_Initial_Embodied_water_(L)", 0) * No * (material_service_life / 60)* volume
                    
                    # Maintenance Embodied water calculations for material categories
            Concrete_plaster_products_Maintenance_Embodied_water = assembly_data.get("Concrete and plaster products_Maintenance_Embodied_Water_(L)", 0) * No * (material_service_life / 60)* volume
            Plastics_Maintenance_Embodied_water = assembly_data.get("Plastics_Maintenance_Embodied_Water_(L)", 0) * No * (material_service_life / 60)* volume
            Metals_Maintenance_Embodied_water = assembly_data.get("Metals_Maintenance_Embodied_Water_(L)", 0) * No * (material_service_life / 60)* volume
            Miscellaneous_Maintenance_Embodied_water = assembly_data.get("Miscellaneous_Maintenance_Embodied_Water_(L)", 0) * No * (material_service_life / 60)* volume
            Sand_stone_ceramics_Maintenance_Embodied_water = assembly_data.get("Sand, stone and ceramics_Maintenance_Embodied_Water_(L)", 0) * No * (material_service_life / 60)* volume
            Glass_Maintenance_Embodied_water = assembly_data.get("Glass_Maintenance_Embodied_Water_(L)", 0) * No * (material_service_life / 60)* volume
            Timber_Maintenance_Embodied_water = assembly_data.get("Timber_Maintenance_Embodied_Water_(L)", 0) * No * (material_service_life / 60)* volume
            Insulation_Maintenance_Embodied_water = assembly_data.get("Insulation_Maintenance_Embodied_Water_(L)", 0) * No * (material_service_life / 60)* volume

            operational_energy_coefficient *= (material_service_life / 60)
            operational_ghg_coefficient *= (material_service_life / 60)
            operational_water_coefficient *= (material_service_life / 60)

            embodied_energy_coefficient *= No * volume * (1 + wastage_coefficient / 100)
            embodied_water_coefficient *= No * volume * (1 + wastage_coefficient / 100)
            embodied_GHG_coefficient *= No * volume * (1 + wastage_coefficient / 100)
            mass *= No * volume * (1 + wastage_coefficient / 100)
            concrete_and_plaster_products_mass *= No * volume * (1 + wastage_coefficient / 100)
            plastics_mass *= No * volume * (1 + wastage_coefficient / 100)
            metals_mass *= No * volume * (1 + wastage_coefficient / 100)
            miscellaneous_mass *= No * volume * (1 + wastage_coefficient / 100)
            sand_stone_ceramics_mass *= No * volume * (1 + wastage_coefficient / 100)
            timber_mass *= No * volume * (1 + wastage_coefficient / 100)
            glass_mass *= No * volume * (1 + wastage_coefficient / 100)
            insulation_mass *= No * volume * (1 + wastage_coefficient / 100)
            operational_energy_coefficient *= No * volume
            operational_ghg_coefficient *= No * volume
            operational_water_coefficient *= No * volume 

            maintenance_embodied_energy *= No * volume * traffic_factor * (1 + wastage_coefficient / 100) * (1 - energy_reduction_factor / 100)*(material_service_life / 60)
            maintenance_embodied_ghg *= No * volume * traffic_factor * (1 + wastage_coefficient / 100) * (1 - ghg_reduction_factor / 100)*(material_service_life / 60)
            maintenance_embodied_water *= No * volume * traffic_factor * (1 + wastage_coefficient / 100) * (1 - water_reduction_factor / 100) *(material_service_life / 60)
            maintenance_mass *= No * volume * traffic_factor * (1 + wastage_coefficient / 100) * (material_service_life / 60)
            
            

        if element_data_list:
            for key, value in element_data_list:
                if key == 'maintenance_embodied_energy':
                    maintenance_embodied_energy += value
                elif key == 'maintenance_embodied_ghg':
                    maintenance_embodied_ghg += value
                elif key == 'maintenance_embodied_water':
                    maintenance_embodied_water += value
                elif key == 'maintenance_mass':
                    maintenance_mass += value
                elif key == 'pavement_mass':
                    pavement_mass += value
                elif key == 'aluminum_mass':
                    aluminum_mass += value
                elif key == 'gravel_mass':
                    gravel_mass += value
                elif key == 'asphalt_mass':
                    asphalt_mass += value
                elif key == 'wood_mass':
                    wood_mass += value
                elif key == 'upvc_mass':
                    upvc_mass += value
                elif key == 'polycarbonate_mass':
                    polycarbonate_mass += value
                elif key == 'recycled_aggregate_mass':
                    recycled_aggregate_mass += value
                elif key == 'cement_mass':
                    cement_mass += value
                elif key == 'sand_mass':
                    sand_mass += value
                elif key == 'operational_energy_coefficient':
                    operational_energy_coefficient += value
                elif key == 'operational_ghg_coefficient':
                    operational_ghg_coefficient += value
                elif key == 'operational_water_coefficient':
                    operational_water_coefficient += value
                elif key == 'embodied_energy_coefficient':
                    embodied_energy_coefficient += value
                elif key == 'embodied_water_coefficient':
                    embodied_water_coefficient += value
                elif key == 'embodied_GHG_coefficient':
                    embodied_GHG_coefficient += value
                elif key == 'mass':
                    mass += value
                elif key == 'maintenance_embodied_energy':
                    maintenance_embodied_energy += value
                elif key == 'maintenance_embodied_ghg':
                    maintenance_embodied_ghg += value
                elif key == 'maintenance_embodied_water':
                    maintenance_embodied_water += value
                elif key == 'maintenance_mass':
                    maintenance_mass += value
                # Material-Specific Mass
                elif key == 'Concrete and plaster products':
                    concrete_and_plaster_products_mass += value
                elif key == 'Plastics':
                    plastics_mass += value
                elif key == 'Glass':
                    glass_mass += value
                elif key == 'Insulation':
                    insulation_mass += value
                elif key == 'Metals':
                    metals_mass += value
                elif key == 'Miscellaneous':
                    miscellaneous_mass += value
                elif key == 'Sand, stone and ceramics':
                    sand_stone_ceramics_mass += value
                elif key == 'Timber':
                    timber_mass += value
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

        embodied_energy_coefficient /= PKT_million_60_years
        embodied_water_coefficient /= PKT_million_60_years
        embodied_GHG_coefficient /= PKT_million_60_years
        mass /= PKT_million_60_years
        concrete_and_plaster_products_mass /= PKT_million_60_years
        plastics_mass /= PKT_million_60_years
        metals_mass /= PKT_million_60_years
        miscellaneous_mass /= PKT_million_60_years
        sand_stone_ceramics_mass /= PKT_million_60_years
        timber_mass /= PKT_million_60_years
        glass_mass /= PKT_million_60_years
        insulation_mass /= PKT_million_60_years
        operational_energy_coefficient /= PKT_million_60_years
        operational_ghg_coefficient /= PKT_million_60_years
        operational_water_coefficient /= PKT_million_60_years
        maintenance_embodied_energy /= PKT_million_60_years
        maintenance_embodied_ghg /= PKT_million_60_years
        maintenance_embodied_water /= PKT_million_60_years
        maintenance_mass /= PKT_million_60_years

        assembly_data_list = [
            ('assembly_category', assembly_category),
            ('material_service_life', material_service_life),
            ('embodied_energy_coefficient', embodied_energy_coefficient),
            ('embodied_water_coefficient', embodied_water_coefficient),
            ('embodied_GHG_coefficient', embodied_GHG_coefficient),
            ('operational_energy_coefficient', operational_energy_coefficient),
            ('operational_ghg_coefficient', operational_ghg_coefficient),
            ('operational_water_coefficient', operational_water_coefficient),
            ('maintenance_embodied_energy', maintenance_embodied_energy),
            ('maintenance_embodied_ghg', maintenance_embodied_ghg),
            ('maintenance_embodied_water', maintenance_embodied_water),
            ('maintenance_mass', maintenance_mass),
            ('mass', mass),
            ('Concrete and plaster products', concrete_and_plaster_products_mass),
            ('Plastics', plastics_mass),
            ('Glass', glass_mass),
            ('Insulation', insulation_mass),
            ('Metals', metals_mass),
            ('Miscellaneous', miscellaneous_mass),
            ('Sand, stone and ceramics', sand_stone_ceramics_mass),
            ('Timber', timber_mass),
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

        return (
            PKT_million_60_years,
            area,
            null1,
            assembly_data_list,
            embodied_energy_coefficient,
            embodied_water_coefficient,
            embodied_GHG_coefficient,
            operational_energy_coefficient,
            operational_ghg_coefficient,
            operational_water_coefficient,
            maintenance_embodied_energy,
            maintenance_embodied_ghg,
            maintenance_embodied_water,
            maintenance_mass,
            null2,
            mass,
            concrete_and_plaster_products_mass,
            plastics_mass,
            metals_mass,
            miscellaneous_mass,
            sand_stone_ceramics_mass,
            timber_mass,
            glass_mass,
            insulation_mass,
        )
