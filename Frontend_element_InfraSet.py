from ghpythonlib.componentbase import executingcomponent as component
from Infraset238 import MaterialDatabase, ElementDatabase
from Grasshopper.Kernel import GH_RuntimeMessageLevel as RML
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path
from Grasshopper.Kernel import GH_Document
from Grasshopper.Kernel.Special import GH_ValueList, GH_ValueListItem
import System
from System.Drawing import PointF

class InfrasetElement(component):
    def RunScript(self, connect_button, element_category, No, element_data_list, null1, wastage_coefficient, material_service_life, null2, energy_reduction_factor, water_reduction_factor, ghg_reduction_factor):
        # Initialize outputs
        output_tree = DataTree[object]()
        embodied_energy_coefficient = 0.0
        embodied_water_coefficient = 0.0
        embodied_GHG_coefficient = 0.0
        operational_energy_coefficient = 0.0
        operational_ghg_coefficient = 0.0
        operational_water_coefficient = 0.0
        maintenance_embodied_energy = 0.0
        maintenance_embodied_ghg = 0.0
        maintenance_embodied_water = 0.0
        maintenance_mass = 0.0
        mass = 0.0
        concrete_and_plaster_products_mass = 0.0
        plastics_mass = 0.0
        metals_mass = 0.0
        miscellaneous_mass = 0.0
        sand_stone_ceramics_mass = 0.0
        timber_mass = 0.0
        glass_mass = 0.0
        insulation_mass = 0.0
        
        # Category breakdown variables (Initial)
        Concrete_plaster_products_Initial_Embodied_GHG = 0.0
        Plastics_Initial_Embodied_GHG = 0.0
        Metals_Initial_Embodied_GHG = 0.0
        Miscellaneous_Initial_Embodied_GHG = 0.0
        Sand_stone_ceramics_Initial_Embodied_GHG = 0.0
        Timber_Initial_Embodied_GHG = 0.0
        Insulation_Initial_Embodied_GHG = 0.0
        Glass_Initial_Embodied_GHG = 0.0
        
        # Category breakdown variables (Maintenance)
        Concrete_plaster_products_Maintenance_Embodied_GHG = 0.0
        Plastics_Maintenance_Embodied_GHG = 0.0
        Metals_Maintenance_Embodied_GHG = 0.0
        Miscellaneous_Maintenance_Embodied_GHG = 0.0
        Sand_stone_ceramics_Maintenance_Embodied_GHG = 0.0
        Timber_Maintenance_Embodied_GHG = 0.0
        Insulation_Maintenance_Embodied_GHG = 0.0
        Glass_Maintenance_Embodied_GHG = 0.0
        
        # Energy category variables (Initial)
        Concrete_plaster_products_Initial_Embodied_energy = 0.0
        Plastics_Initial_Embodied_energy = 0.0
        Metals_Initial_Embodied_energy = 0.0
        Miscellaneous_Initial_Embodied_energy = 0.0
        Sand_stone_ceramics_Initial_Embodied_energy = 0.0
        Timber_Initial_Embodied_energy = 0.0
        Insulation_Initial_Embodied_energy = 0.0
        Glass_Initial_Embodied_energy = 0.0
        
        # Energy category variables (Maintenance)
        Concrete_plaster_products_Maintenance_Embodied_energy = 0.0
        Plastics_Maintenance_Embodied_energy = 0.0
        Metals_Maintenance_Embodied_energy = 0.0
        Miscellaneous_Maintenance_Embodied_energy = 0.0
        Sand_stone_ceramics_Maintenance_Embodied_energy = 0.0
        Timber_Maintenance_Embodied_energy = 0.0
        Insulation_Maintenance_Embodied_energy = 0.0
        Glass_Maintenance_Embodied_energy = 0.0
        
        # Water category variables (Initial)
        Concrete_plaster_products_Initial_Embodied_water = 0.0
        Plastics_Initial_Embodied_water = 0.0
        Metals_Initial_Embodied_water = 0.0
        Miscellaneous_Initial_Embodied_water = 0.0
        Sand_stone_ceramics_Initial_Embodied_water = 0.0
        Timber_Initial_Embodied_water = 0.0
        Insulation_Initial_Embodied_water = 0.0
        Glass_Initial_Embodied_water = 0.0
        
        # Water category variables (Maintenance)
        Concrete_plaster_products_Maintenance_Embodied_water = 0.0
        Plastics_Maintenance_Embodied_water = 0.0
        Metals_Maintenance_Embodied_water = 0.0
        Miscellaneous_Maintenance_Embodied_water = 0.0
        Sand_stone_ceramics_Maintenance_Embodied_water = 0.0
        Timber_Maintenance_Embodied_water = 0.0
        Insulation_Maintenance_Embodied_water = 0.0
        Glass_Maintenance_Embodied_water = 0.0

        # Initialize databases
        material_db = MaterialDatabase()
        element_db = ElementDatabase(material_db.material_db)
        
        try:
            element_db.populate_elements()
        except:
            self.AddRuntimeMessage(RML.Warning, "Failed to populate element database")
            return

        # Create value list when button is pressed
        if connect_button and self.Params.Input[1].SourceCount == 0:
            try:
                element_categories = [cat for cat in element_db.element_db.keys()]
                vl = GH_ValueList()
                vl.CreateAttributes()
                for cat in element_categories:
                    item = GH_ValueListItem(cat, '"%s"' % cat)
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
                self.AddRuntimeMessage(RML.Error, "Value list creation failed: {0}".format(str(e)))

        # Main calculations
        element_data = {}
        if element_category and element_db.element_db:
            element_data = element_db.element_db.get(str(element_category), {})
            if element_data:
                No = No or 1
                wastage = (wastage_coefficient or 0) / 100.0
                analysis_period = material_service_life or 60  # This is the analysis period in years
                energy_red = (energy_reduction_factor or 0) / 100.0
                water_red = (water_reduction_factor or 0) / 100.0
                ghg_red = (ghg_reduction_factor or 0) / 100.0

                try:
                    # ═══════════════════════════════════════════════════════════════
                    # HEADLINE INITIAL CALCULATIONS (NO TIME SCALING - happens once)
                    # ═══════════════════════════════════════════════════════════════
                    embodied_energy = element_data.get("Initial_Embodied_Energy_(MJ)", 0)
                    embodied_water = element_data.get("Initial_Embodied_Water_(L)", 0)
                    embodied_GHG = element_data.get("Initial_Embodied_GHG_(kgCO2e)", 0)
                    
                    embodied_energy_coefficient = embodied_energy * (1 + wastage) * No * (1 - energy_red)
                    embodied_water_coefficient = embodied_water * (1 + wastage) * No * (1 - water_red)
                    embodied_GHG_coefficient = embodied_GHG * (1 + wastage) * No * (1 - ghg_red)

                    # Mass calculations (NO time scaling)
                    mass = element_data.get("Total_Mass_(kg)", 0) * (1 + wastage) * No * 0.001
                    concrete_and_plaster_products_mass = element_data.get("Concrete and plaster products_Mass_(kg)", 0) * (1 + wastage) * No * 0.001
                    plastics_mass = element_data.get("Plastics_Mass_(kg)", 0) * (1 + wastage) * No * 0.001
                    metals_mass = element_data.get("Metals_Mass_(kg)", 0) * (1 + wastage) * No * 0.001
                    miscellaneous_mass = element_data.get("Miscellaneous_Mass_(kg)", 0) * (1 + wastage) * No * 0.001
                    sand_stone_ceramics_mass = element_data.get("Sand, stone and ceramics_Mass_(kg)", 0) * (1 + wastage) * No * 0.001
                    timber_mass = element_data.get("Timber_Mass_(kg)", 0) * (1 + wastage) * No * 0.001
                    glass_mass = element_data.get("Glass_Mass_(kg)", 0) * (1 + wastage) * No * 0.001
                    insulation_mass = element_data.get("Insulation_Mass_(kg)", 0) * (1 + wastage) * No * 0.001

                    # ═══════════════════════════════════════════════════════════════
                    # HEADLINE MAINTENANCE CALCULATIONS (SCALE BY ANALYSIS PERIOD)
                    # ═══════════════════════════════════════════════════════════════
                    maintenance_embodied_energy = element_data.get("Maintenance_Embodied_Energy_(MJ)", 0) * No * (analysis_period / 60)
                    maintenance_embodied_ghg = element_data.get("Maintenance_Embodied_GHG_(kgCO2e)", 0) * No * (analysis_period / 60)
                    maintenance_embodied_water = element_data.get("Maintenance_Embodied_Water_(L)", 0) * No * (analysis_period / 60)
                    maintenance_mass = element_data.get("Maintenance_Mass_(kg)", 0) * No * 0.001 * (analysis_period / 60)
                    
                    # ═══════════════════════════════════════════════════════════════
                    # CATEGORY BREAKDOWNS - INITIAL (NO TIME SCALING!)
                    # These happen once at construction, so just multiply by No
                    # ═══════════════════════════════════════════════════════════════
                    
                    # Initial GHG by category
                    Concrete_plaster_products_Initial_Embodied_GHG = element_data.get("Concrete and plaster products_Initial_Embodied_GHG_(kgCO2e)", 0) * No
                    Plastics_Initial_Embodied_GHG = element_data.get("Plastics_Initial_Embodied_GHG_(kgCO2e)", 0) * No
                    Metals_Initial_Embodied_GHG = element_data.get("Metals_Initial_Embodied_GHG_(kgCO2e)", 0) * No
                    Miscellaneous_Initial_Embodied_GHG = element_data.get("Miscellaneous_Initial_Embodied_GHG_(kgCO2e)", 0) * No
                    Sand_stone_ceramics_Initial_Embodied_GHG = element_data.get("Sand, stone and ceramics_Initial_Embodied_GHG_(kgCO2e)", 0) * No
                    Glass_Initial_Embodied_GHG = element_data.get("Glass_Initial_Embodied_GHG_(kgCO2e)", 0) * No
                    Timber_Initial_Embodied_GHG = element_data.get("Timber_Initial_Embodied_GHG_(kgCO2e)", 0) * No
                    Insulation_Initial_Embodied_GHG = element_data.get("Insulation_Initial_Embodied_GHG_(kgCO2e)", 0) * No
                    
                    # Initial Energy by category
                    Concrete_plaster_products_Initial_Embodied_energy = element_data.get("Concrete and plaster products_Initial_Embodied_energy_(MJ)", 0) * No
                    Plastics_Initial_Embodied_energy = element_data.get("Plastics_Initial_Embodied_energy_(MJ)", 0) * No
                    Metals_Initial_Embodied_energy = element_data.get("Metals_Initial_Embodied_energy_(MJ)", 0) * No
                    Miscellaneous_Initial_Embodied_energy = element_data.get("Miscellaneous_Initial_Embodied_energy_(MJ)", 0) * No
                    Sand_stone_ceramics_Initial_Embodied_energy = element_data.get("Sand, stone and ceramics_Initial_Embodied_energy_(MJ)", 0) * No
                    Glass_Initial_Embodied_energy = element_data.get("Glass_Initial_Embodied_energy_(MJ)", 0) * No
                    Timber_Initial_Embodied_energy = element_data.get("Timber_Initial_Embodied_energy_(MJ)", 0) * No
                    Insulation_Initial_Embodied_energy = element_data.get("Insulation_Initial_Embodied_energy_(MJ)", 0) * No
                    
                    # Initial Water by category
                    Concrete_plaster_products_Initial_Embodied_water = element_data.get("Concrete and plaster products_Initial_embodied_water_(L)", 0) * No
                    Plastics_Initial_Embodied_water = element_data.get("Plastics_Initial_Embodied_water_(L)", 0) * No
                    Metals_Initial_Embodied_water = element_data.get("Metals_Initial_Embodied_water_(L)", 0) * No
                    Miscellaneous_Initial_Embodied_water = element_data.get("Miscellaneous_Initial_Embodied_water_(L)", 0) * No
                    Sand_stone_ceramics_Initial_Embodied_water = element_data.get("Sand, stone and ceramics_Initial_Embodied_water_(L)", 0) * No
                    Glass_Initial_Embodied_water = element_data.get("Glass_Initial_Embodied_water_(L)", 0) * No
                    Timber_Initial_Embodied_water = element_data.get("Timber_Initial_Embodied_water_(L)", 0) * No
                    Insulation_Initial_Embodied_water = element_data.get("Insulation_Initial_Embodied_water_(L)", 0) * No

                    # ═══════════════════════════════════════════════════════════════
                    # CATEGORY BREAKDOWNS - MAINTENANCE (SCALE BY ANALYSIS PERIOD!)
                    # These recur over the analysis period
                    # ═══════════════════════════════════════════════════════════════
                    
                    # Maintenance GHG by category
                    Concrete_plaster_products_Maintenance_Embodied_GHG = element_data.get("Concrete and plaster products_Maintenance_Embodied_GHG_(kgCO2e)", 0) * No * (analysis_period / 60)
                    Plastics_Maintenance_Embodied_GHG = element_data.get("Plastics_Maintenance_Embodied_GHG_(kgCO2e)", 0) * No * (analysis_period / 60)
                    Metals_Maintenance_Embodied_GHG = element_data.get("Metals_Maintenance_Embodied_GHG_(kgCO2e)", 0) * No * (analysis_period / 60)
                    Miscellaneous_Maintenance_Embodied_GHG = element_data.get("Miscellaneous_Maintenance_Embodied_GHG_(kgCO2e)", 0) * No * (analysis_period / 60)
                    Sand_stone_ceramics_Maintenance_Embodied_GHG = element_data.get("Sand, stone and ceramics_Maintenance_Embodied_GHG_(kgCO2e)", 0) * No * (analysis_period / 60)
                    Glass_Maintenance_Embodied_GHG = element_data.get("Glass_Maintenance_Embodied_GHG_(kgCO2e)", 0) * No * (analysis_period / 60)
                    Timber_Maintenance_Embodied_GHG = element_data.get("Timber_Maintenance_Embodied_GHG_(kgCO2e)", 0) * No * (analysis_period / 60)
                    Insulation_Maintenance_Embodied_GHG = element_data.get("Insulation_Maintenance_Embodied_GHG_(kgCO2e)", 0) * No * (analysis_period / 60)
                    
                    # Maintenance Energy by category
                    Concrete_plaster_products_Maintenance_Embodied_energy = element_data.get("Concrete and plaster products_Maintenance_Embodied_energy_(MJ)", 0) * No * (analysis_period / 60)
                    Plastics_Maintenance_Embodied_energy = element_data.get("Plastics_Maintenance_Embodied_energy_(MJ)", 0) * No * (analysis_period / 60)
                    Metals_Maintenance_Embodied_energy = element_data.get("Metals_Maintenance_Embodied_energy_(MJ)", 0) * No * (analysis_period / 60)
                    Miscellaneous_Maintenance_Embodied_energy = element_data.get("Miscellaneous_Maintenance_Embodied_energy_(MJ)", 0) * No * (analysis_period / 60)
                    Sand_stone_ceramics_Maintenance_Embodied_energy = element_data.get("Sand, stone and ceramics_Maintenance_Embodied_energy_(MJ)", 0) * No * (analysis_period / 60)
                    Glass_Maintenance_Embodied_energy = element_data.get("Glass_Maintenance_Embodied_energy_(MJ)", 0) * No * (analysis_period / 60)
                    Timber_Maintenance_Embodied_energy = element_data.get("Timber_Maintenance_Embodied_energy_(MJ)", 0) * No * (analysis_period / 60)
                    Insulation_Maintenance_Embodied_energy = element_data.get("Insulation_Maintenance_Embodied_energy_(MJ)", 0) * No * (analysis_period / 60)
                    
                    # Maintenance Water by category
                    Concrete_plaster_products_Maintenance_Embodied_water = element_data.get("Concrete and plaster products_Maintenance_Embodied_Water_(L)", 0) * No * (analysis_period / 60)
                    Plastics_Maintenance_Embodied_water = element_data.get("Plastics_Maintenance_Embodied_Water_(L)", 0) * No * (analysis_period / 60)
                    Metals_Maintenance_Embodied_water = element_data.get("Metals_Maintenance_Embodied_Water_(L)", 0) * No * (analysis_period / 60)
                    Miscellaneous_Maintenance_Embodied_water = element_data.get("Miscellaneous_Maintenance_Embodied_Water_(L)", 0) * No * (analysis_period / 60)
                    Sand_stone_ceramics_Maintenance_Embodied_water = element_data.get("Sand, stone and ceramics_Maintenance_Embodied_Water_(L)", 0) * No * (analysis_period / 60)
                    Glass_Maintenance_Embodied_water = element_data.get("Glass_Maintenance_Embodied_Water_(L)", 0) * No * (analysis_period / 60)
                    Timber_Maintenance_Embodied_water = element_data.get("Timber_Maintenance_Embodied_Water_(L)", 0) * No * (analysis_period / 60)
                    Insulation_Maintenance_Embodied_water = element_data.get("Insulation_Maintenance_Embodied_Water_(L)", 0) * No * (analysis_period / 60)

                except KeyError as e:
                    self.AddRuntimeMessage(RML.Warning, "Missing data key: {0}".format(str(e)))

        # Process input DataTree correctly
        if element_data_list:
            for i in range(element_data_list.BranchCount):
                branch = element_data_list.Branch(i)
                for item in branch:
                    if isinstance(item, tuple) and len(item) == 2:
                        key, value = item
                        if key == 'embodied_energy_coefficient':
                            embodied_energy_coefficient += value
                        elif key == 'embodied_water_coefficient':
                            embodied_water_coefficient += value
                        elif key == 'embodied_GHG_coefficient':
                            embodied_GHG_coefficient += value
                        elif key == 'mass':
                            mass += value
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
                        elif key == 'operational_energy_coefficient':
                            operational_energy_coefficient += value
                        elif key == 'operational_ghg_coefficient':
                            operational_ghg_coefficient += value
                        elif key == 'operational_water_coefficient':
                            operational_water_coefficient += value
                        elif key == 'maintenance_embodied_energy':
                            maintenance_embodied_energy += value
                        elif key == 'maintenance_embodied_ghg':
                            maintenance_embodied_ghg += value
                        elif key == 'maintenance_embodied_water':
                            maintenance_embodied_water += value
                        elif key == 'maintenance_mass':
                            maintenance_mass += value
                        # Maintenance water categories
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
                        # Initial water categories
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
                        # Maintenance energy categories
                        elif key == 'Concrete_plaster_products_Maintenance_Embodied_energy':
                            Concrete_plaster_products_Maintenance_Embodied_energy += value
                        elif key == 'Plastics_Maintenance_Embodied_energy':
                            Plastics_Maintenance_Embodied_energy += value
                        elif key == 'Metals_Maintenance_Embodied_energy':
                            Metals_Maintenance_Embodied_energy += value
                        elif key == 'Miscellaneous_Maintenance_Embodied_energy':
                            Miscellaneous_Maintenance_Embodied_energy += value
                        elif key == 'Sand_stone_ceramics_Maintenance_Embodied_energy':
                            Sand_stone_ceramics_Maintenance_Embodied_energy += value
                        elif key == 'Glass_Maintenance_Embodied_energy':
                            Glass_Maintenance_Embodied_energy += value
                        elif key == 'Timber_Maintenance_Embodied_energy':
                            Timber_Maintenance_Embodied_energy += value
                        elif key == 'Insulation_Maintenance_Embodied_energy':
                            Insulation_Maintenance_Embodied_energy += value
                        # Initial energy categories
                        elif key == 'Concrete_plaster_products_Initial_Embodied_energy':
                            Concrete_plaster_products_Initial_Embodied_energy += value
                        elif key == 'Plastics_Initial_Embodied_energy':
                            Plastics_Initial_Embodied_energy += value
                        elif key == 'Metals_Initial_Embodied_energy':
                            Metals_Initial_Embodied_energy += value
                        elif key == 'Miscellaneous_Initial_Embodied_energy':
                            Miscellaneous_Initial_Embodied_energy += value
                        elif key == 'Sand_stone_ceramics_Initial_Embodied_energy':
                            Sand_stone_ceramics_Initial_Embodied_energy += value
                        elif key == 'Glass_Initial_Embodied_energy':
                            Glass_Initial_Embodied_energy += value
                        elif key == 'Timber_Initial_Embodied_energy':
                            Timber_Initial_Embodied_energy += value
                        elif key == 'Insulation_Initial_Embodied_energy':
                            Insulation_Initial_Embodied_energy += value
                        # Maintenance GHG categories
                        elif key == 'Concrete_plaster_products_Maintenance_Embodied_GHG':
                            Concrete_plaster_products_Maintenance_Embodied_GHG += value
                        elif key == 'Plastics_Maintenance_Embodied_GHG':
                            Plastics_Maintenance_Embodied_GHG += value
                        elif key == 'Metals_Maintenance_Embodied_GHG':
                            Metals_Maintenance_Embodied_GHG += value
                        elif key == 'Miscellaneous_Maintenance_Embodied_GHG':
                            Miscellaneous_Maintenance_Embodied_GHG += value
                        elif key == 'Sand_stone_ceramics_Maintenance_Embodied_GHG':
                            Sand_stone_ceramics_Maintenance_Embodied_GHG += value
                        elif key == 'Glass_Maintenance_Embodied_GHG':
                            Glass_Maintenance_Embodied_GHG += value
                        elif key == 'Timber_Maintenance_Embodied_GHG':
                            Timber_Maintenance_Embodied_GHG += value
                        elif key == 'Insulation_Maintenance_Embodied_GHG':
                            Insulation_Maintenance_Embodied_GHG += value
                        # Initial GHG categories
                        elif key == 'Concrete_plaster_products_Initial_Embodied_GHG':
                            Concrete_plaster_products_Initial_Embodied_GHG += value
                        elif key == 'Plastics_Initial_Embodied_GHG':
                            Plastics_Initial_Embodied_GHG += value
                        elif key == 'Metals_Initial_Embodied_GHG':
                            Metals_Initial_Embodied_GHG += value
                        elif key == 'Miscellaneous_Initial_Embodied_GHG':
                            Miscellaneous_Initial_Embodied_GHG += value
                        elif key == 'Sand_stone_ceramics_Initial_Embodied_GHG':
                            Sand_stone_ceramics_Initial_Embodied_GHG += value
                        elif key == 'Glass_Initial_Embodied_GHG':
                            Glass_Initial_Embodied_GHG += value
                        elif key == 'Timber_Initial_Embodied_GHG':
                            Timber_Initial_Embodied_GHG += value
                        elif key == 'Insulation_Initial_Embodied_GHG':
                            Insulation_Initial_Embodied_GHG += value

        # Build output DataTree
        path = GH_Path(0)
        output_tree.AddRange([
            ('element_category', element_category),
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
            # Maintenance water categories
            ('Insulation_Maintenance_Embodied_water', Insulation_Maintenance_Embodied_water),
            ('Timber_Maintenance_Embodied_water', Timber_Maintenance_Embodied_water),
            ('Glass_Maintenance_Embodied_water', Glass_Maintenance_Embodied_water),
            ('Sand_stone_ceramics_Maintenance_Embodied_water', Sand_stone_ceramics_Maintenance_Embodied_water),
            ('Miscellaneous_Maintenance_Embodied_water', Miscellaneous_Maintenance_Embodied_water),
            ('Metals_Maintenance_Embodied_water', Metals_Maintenance_Embodied_water),
            ('Plastics_Maintenance_Embodied_water', Plastics_Maintenance_Embodied_water),
            ('Concrete_plaster_products_Maintenance_Embodied_water', Concrete_plaster_products_Maintenance_Embodied_water),
            # Initial water categories
            ('Insulation_Initial_Embodied_water', Insulation_Initial_Embodied_water),
            ('Timber_Initial_Embodied_water', Timber_Initial_Embodied_water),
            ('Glass_Initial_Embodied_water', Glass_Initial_Embodied_water),
            ('Sand_stone_ceramics_Initial_Embodied_water', Sand_stone_ceramics_Initial_Embodied_water),
            ('Miscellaneous_Initial_Embodied_water', Miscellaneous_Initial_Embodied_water),
            ('Metals_Initial_Embodied_water', Metals_Initial_Embodied_water),
            ('Plastics_Initial_Embodied_water', Plastics_Initial_Embodied_water),
            ('Concrete_plaster_products_Initial_Embodied_water', Concrete_plaster_products_Initial_Embodied_water),
            # Maintenance energy categories
            ('Concrete_plaster_products_Maintenance_Embodied_energy', Concrete_plaster_products_Maintenance_Embodied_energy),
            ('Plastics_Maintenance_Embodied_energy', Plastics_Maintenance_Embodied_energy),
            ('Metals_Maintenance_Embodied_energy', Metals_Maintenance_Embodied_energy),
            ('Miscellaneous_Maintenance_Embodied_energy', Miscellaneous_Maintenance_Embodied_energy),
            ('Sand_stone_ceramics_Maintenance_Embodied_energy', Sand_stone_ceramics_Maintenance_Embodied_energy),
            ('Glass_Maintenance_Embodied_energy', Glass_Maintenance_Embodied_energy),
            ('Timber_Maintenance_Embodied_energy', Timber_Maintenance_Embodied_energy),
            ('Insulation_Maintenance_Embodied_energy', Insulation_Maintenance_Embodied_energy),
            # Initial energy categories
            ('Concrete_plaster_products_Initial_Embodied_energy', Concrete_plaster_products_Initial_Embodied_energy),
            ('Plastics_Initial_Embodied_energy', Plastics_Initial_Embodied_energy),
            ('Metals_Initial_Embodied_energy', Metals_Initial_Embodied_energy),
            ('Miscellaneous_Initial_Embodied_energy', Miscellaneous_Initial_Embodied_energy),
            ('Sand_stone_ceramics_Initial_Embodied_energy', Sand_stone_ceramics_Initial_Embodied_energy),
            ('Glass_Initial_Embodied_energy', Glass_Initial_Embodied_energy),
            ('Timber_Initial_Embodied_energy', Timber_Initial_Embodied_energy),
            ('Insulation_Initial_Embodied_energy', Insulation_Initial_Embodied_energy),
            # Maintenance GHG categories
            ('Concrete_plaster_products_Maintenance_Embodied_GHG', Concrete_plaster_products_Maintenance_Embodied_GHG),
            ('Plastics_Maintenance_Embodied_GHG', Plastics_Maintenance_Embodied_GHG),
            ('Metals_Maintenance_Embodied_GHG', Metals_Maintenance_Embodied_GHG),
            ('Miscellaneous_Maintenance_Embodied_GHG', Miscellaneous_Maintenance_Embodied_GHG),
            ('Sand_stone_ceramics_Maintenance_Embodied_GHG', Sand_stone_ceramics_Maintenance_Embodied_GHG),
            ('Glass_Maintenance_Embodied_GHG', Glass_Maintenance_Embodied_GHG),
            ('Timber_Maintenance_Embodied_GHG', Timber_Maintenance_Embodied_GHG),
            ('Insulation_Maintenance_Embodied_GHG', Insulation_Maintenance_Embodied_GHG),
            # Initial GHG categories
            ('Concrete_plaster_products_Initial_Embodied_GHG', Concrete_plaster_products_Initial_Embodied_GHG),
            ('Plastics_Initial_Embodied_GHG', Plastics_Initial_Embodied_GHG),
            ('Metals_Initial_Embodied_GHG', Metals_Initial_Embodied_GHG),
            ('Miscellaneous_Initial_Embodied_GHG', Miscellaneous_Initial_Embodied_GHG),
            ('Sand_stone_ceramics_Initial_Embodied_GHG', Sand_stone_ceramics_Initial_Embodied_GHG),
            ('Glass_Initial_Embodied_GHG', Glass_Initial_Embodied_GHG),
            ('Timber_Initial_Embodied_GHG', Timber_Initial_Embodied_GHG),
            ('Insulation_Initial_Embodied_GHG', Insulation_Initial_Embodied_GHG),
        ], path)

        return (
            output_tree,
            material_service_life,
            null1,
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
            insulation_mass
        )
