
# -*- coding: UTF-8 -*-
import copy
import os.path
from collections import OrderedDict
from math import sqrt, floor, ceil, log10, isnan
import rhinoscriptsyntax as rs
from Grasshopper import DataTree
from Rhino import Display
from Rhino import Geometry
from System import Drawing
from System import Guid
from System.Drawing import Color

# Material data table (embedded directly in code)
MATERIAL_DATA = [
    {
        "Material": "Steel",
        "Categories": "Metals",
        "Unit": "m³",
        "Embodied_GHG_Coefficient": 11358,
        "Embodied_Energy_Coefficient": 184172,
        "Embodied_Water_Coefficient": 203542,
        "Life_Span": 100,
        "Density": 7740
    },
    {
        "Material": "Concrete",
        "Categories": "Concrete and plaster products",
        "Unit": "m³",
        "Embodied_GHG_Coefficient": 336,
        "Embodied_Energy_Coefficient": 3640,
        "Embodied_Water_Coefficient": 5180,
        "Life_Span": 100,
        "Density": 1400
    },
    {
        "Material": "Cement",
        "Categories": "Concrete and plaster products",
        "Unit": "m³",
        "Embodied_GHG_Coefficient": 1950,
        "Embodied_Energy_Coefficient": 16520,
        "Embodied_Water_Coefficient": 10920,
        "Life_Span": 100,
        "Density": 1500
    },
    {
        "Material": "Wood",
        "Categories": "Timber",
        "Unit": "m³",
        "Embodied_GHG_Coefficient": 944,
        "Embodied_Energy_Coefficient": 13632,
        "Embodied_Water_Coefficient": 19110,
        "Life_Span": 80,
        "Density": 430
    },
    {
        "Material": "Painting",
        "Categories": "Miscellaneous",
        "Unit": "m³",
        "Embodied_GHG_Coefficient": 8500,
        "Embodied_Energy_Coefficient": 133200,
        "Embodied_Water_Coefficient": 247000,
        "Life_Span": 1,
        "Density": 1250
    },
    {
        "Material": "Polycarbonate",
        "Categories": "Plastics",
        "Unit": "m³",
        "Embodied_GHG_Coefficient": 16800,
        "Embodied_Energy_Coefficient": 228000,
        "Embodied_Water_Coefficient": 318000,
        "Life_Span": 25,
        "Density": 1200
    },
    {
        "Material": "uPVC",
        "Categories": "Plastics",
        "Unit": "m³",
        "Embodied_GHG_Coefficient": 5838,
        "Embodied_Energy_Coefficient": 106097,
        "Embodied_Water_Coefficient": 779390,
        "Life_Span": 35,
        "Density": 1390
    },
    {
        "Material": "Gravel",
        "Categories": "Sand, stone and ceramics",
        "Unit": "m³",
        "Embodied_GHG_Coefficient": 66.24,
        "Embodied_Energy_Coefficient": 897.6,
        "Embodied_Water_Coefficient": 3496,
        "Life_Span": 30,
        "Density": 1840
    },
    {
        "Material": "Sand",
        "Categories": "Sand, stone and ceramics",
        "Unit": "m³",
        "Embodied_GHG_Coefficient": 36,
        "Embodied_Energy_Coefficient": 510,
        "Embodied_Water_Coefficient": 2700,
        "Life_Span": 30,
        "Density": 1500
    },
    {
        "Material": "Asphalt",
        "Categories": "Miscellaneous",
        "Unit": "m³",
        "Embodied_GHG_Coefficient": 530,
        "Embodied_Energy_Coefficient": 1125.8,
        "Embodied_Water_Coefficient": 7672,
        "Life_Span": 100,
        "Density": 2649
    },
    {
        "Material": "Aluminium",
        "Categories": "Metals",
        "Unit": "m³",
        "Embodied_GHG_Coefficient": 79677,
        "Embodied_Energy_Coefficient": 1039096,
        "Embodied_Water_Coefficient": 661408,
        "Life_Span": 50,
        "Density": 2712
    },
    {
        "Material": "Recycled aggregate",
        "Categories": "Sand, stone and ceramics",
        "Unit": "m³",
        "Embodied_GHG_Coefficient": 10.56,
        "Embodied_Energy_Coefficient": 145.2,
        "Embodied_Water_Coefficient": 132,
        "Life_Span": 100,
        "Density": 1320
    },
    {
        "Material": "Hot_rolled_structural_steel",
        "Categories": "Metals",
        "Unit": "m³",
        "Embodied_GHG_Coefficient": 22790,
        "Embodied_Energy_Coefficient": 304640,
        "Embodied_Water_Coefficient": 291490,
        "Life_Span": 100,
        "Density": 7850
    },
    {
        "Material": "Concrete_25_MPA",
        "Categories": "Concrete and plaster products",
        "Unit": "m³",
        "Embodied_GHG_Coefficient": 361,
        "Embodied_Energy_Coefficient": 2581,
        "Embodied_Water_Coefficient": 4200,
        "Life_Span": 100,
        "Density": 2409
    },
    {
        "Material": "uPVC pipe - 114.3 mm outer dia., 4.85 mm thick",
        "Categories": "Plastics",
        "Unit": "m³",
        "Embodied_GHG_Coefficient": 5808.4,
        "Embodied_Energy_Coefficient": 106047.9,
        "Embodied_Water_Coefficient": 779041.9,
        "Life_Span": 25,
        "Density": 1400
    },
    {
        "Material": "uPVC pipe - 225.3 mm outer dia., 11.1 mm thick",
        "Categories": "Plastics",
        "Unit": "m³",
        "Embodied_GHG_Coefficient": 5760.0,
        "Embodied_Energy_Coefficient": 105600.0,
        "Embodied_Water_Coefficient": 776800.0,
        "Life_Span": 25,
        "Density": 1400
    },
    {
        "Material": "Double_glazing_flat_glass_20mm",
        "Categories": "Glass",
        "Unit": "m³",
        "Embodied_GHG_Coefficient": 5050,
        "Embodied_Energy_Coefficient": 66800,
        "Embodied_Water_Coefficient": 77900,
        "Life_Span": 25,
        "Density": 2600
    },
    {
        "Material": "RockWool_insulation",
        "Categories": "Insulation",
        "Unit": "m³",
        "Embodied_GHG_Coefficient": 266,
        "Embodied_Energy_Coefficient": 3997,
        "Embodied_Water_Coefficient": 4354,
        "Life_Span": 25,
        "Density": 70
    },
     # ───────────────────────────────────────
    # 🏗️ BELL-TO-MORELAND & PRESTON SPECIFIC MATERIALS
    # ───────────────────────────────────────
     # PRECAST CONCRETE (55 MPa, no SCM)
    {
        "Material": "Concrete_55_MPA__0pct_SCM",
        "Categories": "Concrete and plaster products",
        "Unit": "m³",
        "Embodied_GHG_Coefficient": 470,          # # 500 kg cement × 0.94 kgCO₂e/kg
        "Embodied_Energy_Coefficient": 4500,
        "Embodied_Water_Coefficient": 5180,
        "Life_Span": 100,
        "Density": 2400
    },
     # INSITU CONCRETE (50 MPa, 25% SCM – e.g., ZVR5418, VS502VR45)
    {
        "Material": "Concrete_50_MPA_25pct_SCM",
        "Categories": "Concrete and plaster products",
        "Unit": "m³",
        "Embodied_GHG_Coefficient": 336,   # 25% reduction due to fly ash/slag
        "Embodied_Energy_Coefficient": 3220,
        "Embodied_Water_Coefficient": 3970,
        "Life_Span": 100,
        "Density": 2409
    },
     # INSITU CONCRETE (40 MPa, 25% SCM – e.g., VS402VR45)
    {
        "Material": "Concrete_40_MPA_25pct_SCM",
        "Categories": "Concrete and plaster products",
        "Unit": "m³",
        "Embodied_GHG_Coefficient": 336 * 0.75,
        "Embodied_Energy_Coefficient": 3640 * 0.75,
        "Embodied_Water_Coefficient": 5180 * 0.75,
        "Life_Span": 100,
        "Density": 2400
    },

    # INSITU CONCRETE (25 MPa, 25–40% SCM – roadworks)
    {
        "Material": "Concrete_25_MPA_30pct_SCM",
        "Categories": "Concrete and plaster products",
        "Unit": "m³",
        "Embodied_GHG_Coefficient": 336 * 0.70,   # 30% SCM assumed
        "Embodied_Energy_Coefficient": 3640 * 0.70,
        "Embodied_Water_Coefficient": 5180 * 0.70,
        "Life_Span": 100,
        "Density": 2350
    },

    # REINFORCED CONCRETE PIPE (RCP)
    {
        "Material": "Reinforced_Concrete_Pipe_RCP",
        "Categories": "Concrete and plaster products",
        "Unit": "m³",
        "Embodied_GHG_Coefficient": 336,
        "Embodied_Energy_Coefficient": 3640,
        "Embodied_Water_Coefficient": 5180,
        "Life_Span": 100,
        "Density": 2400
    },

    # HDPE / PE PIPES (from Preston CSR)
    {
        "Material": "PE_Pipe_HDPE",
        "Categories": "Plastics",
        "Unit": "m³",
        "Embodied_GHG_Coefficient": 1800,         # ICE v3.0: ~1.8 kgCO2e/kg → ~1800 kg/m³
        "Embodied_Energy_Coefficient": 75000,
        "Embodied_Water_Coefficient": 220000,
        "Life_Span": 50,
        "Density": 950
    },

    # PVC PIPES (small diameter, e.g., 100–150mm)
    {
        "Material": "PVC_Pipe",
        "Categories": "Plastics",
        "Unit": "m³",
        "Embodied_GHG_Coefficient": 2200,         # Ecoinvent avg.
        "Embodied_Energy_Coefficient": 85000,
        "Embodied_Water_Coefficient": 250000,
        "Life_Span": 40,
        "Density": 1400
    },

    # STRUCTURAL STEEL SECTIONS (UC, WC, etc.)
    {
        "Material": "Steel_UC_WC_Sections",
        "Categories": "Metals",
        "Unit": "m³",
        "Embodied_GHG_Coefficient": 113578,
        "Embodied_Energy_Coefficient": 1841720,
        "Embodied_Water_Coefficient": 2035420,
        "Life_Span": 100,
        "Density": 7850
    },

    # STEEL REINFORCEMENT (Rebar)
    {
        "Material": "Steel_Reinforcing_Bar",
        "Categories": "Metals",
        "Unit": "m³",
        "Embodied_GHG_Coefficient": 11382,
        "Embodied_Energy_Coefficient": 184172,
        "Embodied_Water_Coefficient": 203542,
        "Life_Span": 100,
        "Density": 7850
    },

    # CRUSHED ROCK (Class 2/3/4)
    {
        "Material": "Crushed_Rock",
        "Categories": "Sand, stone and ceramics",
        "Unit": "m³",
        "Embodied_GHG_Coefficient": 66.24,
        "Embodied_Energy_Coefficient": 897.6,
        "Embodied_Water_Coefficient": 3496,
        "Life_Span": 100,
        "Density": 2450  # From B2M: 2.45 t/m³
    },

    # GENERAL FILL / EARTHWORKS
    {
        "Material": "General_Fill",
        "Categories": "Sand, stone and ceramics",
        "Unit": "m³",
        "Embodied_GHG_Coefficient": 15,           # Low impact, excavated/reused
        "Embodied_Energy_Coefficient": 200,
        "Embodied_Water_Coefficient": 500,
        "Life_Span": 100,
        "Density": 1800
    },

    # STABILISED SAND (for CSR)
    {
        "Material": "Stabilised_Sand",
        "Categories": "Sand, stone and ceramics",
        "Unit": "m³",
        "Embodied_GHG_Coefficient": 36 + (1950 * 0.1),  # Sand + 10% cement
        "Embodied_Energy_Coefficient": 510 + (16520 * 0.1),
        "Embodied_Water_Coefficient": 2700 + (10920 * 0.1),
        "Life_Span": 50,
        "Density": 1900
    },

    # uPVC pipes (already defined, but kept for clarity)
    {
        "Material": "uPVC pipe - 114.3 mm outer dia., 4.85 mm thick",
        "Categories": "Plastics",
        "Unit": "m³",
        "Embodied_GHG_Coefficient": 5808.4,
        "Embodied_Energy_Coefficient": 106047.9,
        "Embodied_Water_Coefficient": 779041.9,
        "Life_Span": 25,
        "Density": 1400
    },
    {
        "Material": "uPVC pipe - 225.3 mm outer dia., 11.1 mm thick",
        "Categories": "Plastics",
        "Unit": "m³",
        "Embodied_GHG_Coefficient": 5760.0,
        "Embodied_Energy_Coefficient": 105600.0,
        "Embodied_Water_Coefficient": 776800.0,
        "Life_Span": 25,
        "Density": 1400
    },

    # GLASS (for completeness)
    {
        "Material": "Double_glazing_flat_glass_20mm",
        "Categories": "Glass",
        "Unit": "m³",
        "Embodied_GHG_Coefficient": 5050,
        "Embodied_Energy_Coefficient": 66800,
        "Embodied_Water_Coefficient": 77900,
        "Life_Span": 25,
        "Density": 2600
    },

    # INSULATION
    {
        "Material": "RockWool_insulation",
        "Categories": "Insulation",
        "Unit": "m³",
        "Embodied_GHG_Coefficient": 266,
        "Embodied_Energy_Coefficient": 3997,
        "Embodied_Water_Coefficient": 4354,
        "Life_Span": 25,
        "Density": 70
         },
              # ───────────────────────────────────────
    # 🏗️ Belgian Standard Railway Track (Infrabel)
    # ───────────────────────────────────────
     # Rail_Ballast_0_80
     {
    "Material": "Rail_Ballast_0_80",
    "Categories": "Sand, stone and ceramics",
    "Unit": "m³",
    "Embodied_GHG_Coefficient": 66.24,      # Same as crushed rock
    "Embodied_Energy_Coefficient": 897.6,
    "Embodied_Water_Coefficient": 3496,
    "Life_Span": 30,
    "Density": 1800  # kg/m³ → 1.8 t/m³
},
{
    "Material": "Rail_Subballast_0_32",
    "Categories": "Sand, stone and ceramics",
    "Unit": "m³",
    "Embodied_GHG_Coefficient": 66.24,
    "Embodied_Energy_Coefficient": 897.6,
    "Embodied_Water_Coefficient": 3496,
    "Life_Span": 30,
    "Density": 1700
},
{
    "Material": "Rail_Bedding_Asphalt",
    "Categories": "Miscellaneous",
    "Unit": "m³",
    "Embodied_GHG_Coefficient": 530,        # Same as standard asphalt
    "Embodied_Energy_Coefficient": 1125.8,
    "Embodied_Water_Coefficient": 7672,
    "Life_Span": 20,  # Shorter lifespan for rail bedding
    "Density": 2350
},
    # ----------------------------------------------------
    # NEW ANCILLARIES MATERIALS
    # ----------------------------------------------------
    {
        "Material": "Aluminum",
        "Categories": "Metals",
        "Unit": "m³",
        "Embodied_GHG_Coefficient": 8000,
        "Embodied_Energy_Coefficient": 150000,
        "Embodied_Water_Coefficient": 50000,
        "Life_Span": 60,
        "Density": 2700 # Approx density for structural aluminum
    },
    {
        "Material": "Mild_Steel",
        "Categories": "Metals",
        "Unit": "m³",
        "Embodied_GHG_Coefficient": 17000,
        "Embodied_Energy_Coefficient": 280000,
        "Embodied_Water_Coefficient": 310000,
        "Life_Span": 100,
        "Density": 7850 # Same as Hot Rolled Steel
    },
    {
        "Material": "General_Polymer", # Used as a proxy for FRP Plate
        "Categories": "Plastics",
        "Unit": "m³",
        "Embodied_GHG_Coefficient": 10000,
        "Embodied_Energy_Coefficient": 160000,
        "Embodied_Water_Coefficient": 15000,
        "Life_Span": 50,
        "Density": 1800 # Proxy density for a dense polymer composite
    },
        # ----------------------------------------------------
    # NEW CONCRETE MIX: 50 MPa with 20% SCM (Humes)
    # ----------------------------------------------------
    {
        "Material": "Concrete_50_MPA_20pct_SCM", # Adjusted from 25% SCM to 20% SCM
        "Categories": "Concrete and plaster products",
        "Unit": "m³",
        "Embodied_GHG_Coefficient": 320, # Slightly higher than 25% SCM, lower than 0% SCM
        "Embodied_Energy_Coefficient": 3600,
        "Embodied_Water_Coefficient": 4600,
        "Life_Span": 100,
        "Density": 2500
    },
            # ----------------------------------------------------
    # Fly ash
    # ----------------------------------------------------
     {
        "Material": "Fly ash",
        "Categories": "Concrete and plaster products",
        "Unit": "m³",
        "Embodied_GHG_Coefficient": 100,  # kgCO2e/m³ (Proxy, as SCMs have lower embodied impact)
        "Embodied_Energy_Coefficient": 1000,  # MJ/m³
        "Embodied_Water_Coefficient": 500,  # L/m³
        "Life_Span": 100,
        "Density": 2200  # kg/m³
    }
]


class MaterialDatabase(object):
    def __init__(self):
        self.material_db = {}
        self.populate_material_db()

    def populate_material_db(self):
        for mat in MATERIAL_DATA:
            material_name = mat["Material"]
            self.material_db[material_name] = {
                "Embodied_GHG_Coefficient_(kgCO2e/FU)": mat["Embodied_GHG_Coefficient"],
                "Embodied_Energy_Coefficient_(MJ/FU)": mat["Embodied_Energy_Coefficient"],
                "Embodied_Water_Coefficient_(L/FU)": mat["Embodied_Water_Coefficient"],
                "Life_Span_(Years)": mat["Life_Span"],
                "Density_(kg/m³)": mat["Density"]
            }

    def print_material_db(self):
        print("Material Database (DB):")
        for material, properties in self.material_db.items():
            print(str(material) + ": " + str(properties))




class ElementDatabase(object):
    def __init__(self, material_db):
        self.material_db = material_db
        self.element_db = {}
        self.painting_factor = 60
        self.populate_elements()
        
    def calculate_embodied_metrics(self, material_name, thickness_m):
        # Calculate the volume in m³ (assuming 1 m² area for simplicity)
        volume_m3 = thickness_m * 1
        material_props = self.material_db.get(material_name, {})
        # Calculate embodied metrics using coefficients from the material database
        ghg = volume_m3  * material_props.get("Embodied_GHG_Coefficient_(kgCO2e/FU)", 0)
        energy = volume_m3  * material_props.get("Embodied_Energy_Coefficient_(MJ/FU)", 0)
        water = volume_m3  * material_props.get("Embodied_Water_Coefficient_(L/FU)", 0)
        # Calculate material mass (density * volume)
        density = material_props.get("Density_(kg/m³)", 0)
        material_mass = volume_m3 * density  # mass = volume * density (kg)
        return ghg, energy, water, material_mass# ... (keep existing calculate_embodied_metrics from Infraset119)

    def populate_elements(self):
        elements = {
            "Tram_post_0.2tonne_6meters_No": {
                "layers": [
                    {"material": "Painting", "thickness_m": 0.0008},
                    {"material": "Concrete", "thickness_m": 0.09},
                    {"material": "Steel", "thickness_m": 0.017},
                    {"material": "Hot_rolled_structural_steel", "thickness_m": 0.002}
                ],
                "replacement_factor": 1,
                "Operational_GHG_(kgCO2e/No)": 0,
                "Operational_Energy_(MJ/No)": 0,
                "Operational_Water_(L/No)": 0
                
            },
            "Building_Facade_Vol": {  # Example assembly using Glass and Insulation
                "layers": [
                    {"material": "Double_glazing_flat_glass_20mm", "thickness_m": 0.01},
                    {"material": "RockWool_insulation", "thickness_m": 0.05},
                    {"material": "Concrete", "thickness_m": 0.1}
                ],
                "replacement_factor": 1,
                "Operational_GHG_(kgCO2e/No)": 0,
                "Operational_Energy_(MJ/No)": 0,
                "Operational_Water_(L/No)": 0
            },
            "Light_post_0.5tonne_12meters_No": {
                "layers": [
                    {"material": "Painting", "thickness_m": 0.0008},
                    {"material": "Concrete", "thickness_m": 0.07},
                    {"material": "Hot_rolled_structural_steel", "thickness_m": 0.15},
                    {"material": "Polycarbonate", "thickness_m": 0.0025},
                    {"material": "Steel", "thickness_m": 0.007}
                ],
                "replacement_factor": 0.5,
                "Operational_GHG_(kgCO2e/No)": 2.503233,
                "Operational_Energy_(MJ/No)": 0,
                "Operational_Water_(L/No)": 0
            },
            "Sign post_No": {
                "layers": [
                    {"material": "Painting", "thickness_m": 0.2},
                    {"material": "Concrete", "thickness_m": 0.036},
                    {"material": "Steel", "thickness_m": 0.07}
                ],
                "replacement_factor": 2,
                "Operational_GHG_(kgCO2e/No)": 0,
                "Operational_Energy_(MJ/No)": 0,
                "Operational_Water_(L/No)": 0
            },
            "Steel_Railing_No": {
                "layers": [
                    {"material": "Painting", "thickness_m": 0.00008},
                    {"material": "Concrete", "thickness_m": 0.0125},
                    {"material": "Steel", "thickness_m": 0.0022}
                ],
                "replacement_factor": 1,
                "Operational_GHG_(kgCO2e/No)": 0,
                "Operational_Energy_(MJ/No)": 0,
                "Operational_Water_(L/No)": 0
            },
            "Concrete_Planter_box_No": {
                "layers": [
                    {"material": "Concrete", "thickness_m": 0.0145}
                ],
                "replacement_factor": 1,
                "Operational_GHG_(kgCO2e/No)": 0,
                "Operational_Energy_(MJ/No)": 0,
                "Operational_Water_(L/No)": 0
            },
            "Underground_pipes_uPVC_Vol": {
                "layers": [
                    {"material": "uPVC pipe - 114.3 mm outer dia., 4.85 mm thick", "thickness_m": 0.0074},
                    {"material": "uPVC pipe - 225.3 mm outer dia., 11.1 mm thick", "thickness_m": 0.0014}
                ],
                "replacement_factor": 0.5,
                "Operational_GHG_(kgCO2e/No)": 0,
                "Operational_Energy_(MJ/No)": 0,
                "Operational_Water_(L/No)": 0
            },
            "Street_pits_concrete_No": {
                "layers": [
                    {"material": "Concrete_25_MPA", "thickness_m": 0.0003},
                    {"material": "steel", "thickness_m": 0.00002},
                    {"material": "Hot_rolled_structural_steel", "thickness_m": 0.00007}
                ],
                "replacement_factor": 1,
                "Operational_GHG_(kgCO2e/No)": 0,
                "Operational_Energy_(MJ/No)": 0,
                "Operational_Water_(L/No)": 0
            },
            # ───────────────────────────────────────
        # 🏗️ BRIDGE & STRUCTURAL ELEMENTS (Design Life = 100 years)
        # ───────────────────────────────────────
        "Crosshead_50MPa_Vol": {
            "layers": [
                {"material": "Concrete_50_MPA_25pct_SCM", "thickness_m": 1.0},  # ZVR5422S
                {"material": "Steel_Reinforcing_Bar", "thickness_m": 0.046},    # ~512 t / 1517 m³ ≈ 338 kg/m³ → 0.34 m equiv.
                {"material": "Painting", "thickness_m": 0.0008}
            ],
            "replacement_factor": 0,
            "Operational_GHG_(kgCO2e/No)": 0,
            "Operational_Energy_(MJ/No)": 0,
            "Operational_Water_(L/No)": 0
        },
        "Pier_50MPa_Vol": {
            "layers": [
                {"material": "Concrete_50_MPA_25pct_SCM", "thickness_m": 1.0},  # ZVR5418
                {"material": "Steel_Reinforcing_Bar", "thickness_m": 0.046},
                {"material": "Painting", "thickness_m": 0.0008}
            ],
            "replacement_factor": 0,
            "Operational_GHG_(kgCO2e/No)": 0,
            "Operational_Energy_(MJ/No)": 0,
            "Operational_Water_(L/No)": 0
        },
        "Abutment_50MPa_No": {
            "layers": [
                {"material": "Concrete_50_MPA_25pct_SCM", "thickness_m": 1.0},  # VS502VR45
                {"material": "Steel_Reinforcing_Bar", "thickness_m": 0.25},
                {"material": "Painting", "thickness_m": 0.0008}
            ],
            "replacement_factor": 0,
            "Operational_GHG_(kgCO2e/No)": 0,
            "Operational_Energy_(MJ/No)": 0,
            "Operational_Water_(L/No)": 0
        },
        "Precast_Fascia_Panel_50MPa_No": {
            "layers": [
                {"material": "Concrete_50_MPA_25pct_SCM", "thickness_m": 1.0},  # ZVR5025
                {"material": "Steel_Reinforcing_Bar", "thickness_m": 0.08},     # light reo
                {"material": "Painting", "thickness_m": 0.0008}
            ],
            "replacement_factor": 1,
            "Operational_GHG_(kgCO2e/No)": 0,
            "Operational_Energy_(MJ/No)": 0,
            "Operational_Water_(L/No)": 0
        },
        "NVC_Panel_55MPa_No": {
            "layers": [
                {"material": "Concrete_55_MPA_0pct_SCM", "thickness_m": 1.0},   # ZVR55422
                {"material": "Steel_Reinforcing_Bar", "thickness_m": 0.10},
                {"material": "Painting", "thickness_m": 0.0008}
            ],
            "replacement_factor": 0,
            "Operational_GHG_(kgCO2e/No)": 0,
            "Operational_Energy_(MJ/No)": 0,
            "Operational_Water_(L/No)": 0
        },

        # ───────────────────────────────────────
        # 🚧 RETAINING WALLS & FOUNDATIONS (DL = 100 years)
        # ───────────────────────────────────────
        "L_Wall_Base_Slab_Vol": {
            "layers": [
                {"material": "Concrete_40_MPA_25pct_SCM", "thickness_m": 1.0},  # VS402FVR
                {"material": "Steel_Reinforcing_Bar", "thickness_m": 0.29},     # 306 t / 1047 m³
                {"material": "Painting", "thickness_m": 0.0008}
            ],
            "replacement_factor": 1,
            "Operational_GHG_(kgCO2e/No)": 0,
            "Operational_Energy_(MJ/No)": 0,
            "Operational_Water_(L/No)": 0
        },

        # ───────────────────────────────────────
        # ⚡ OHLE & SUPPORT STRUCTURES (DL = 25–50 years) And OHW
        # ───────────────────────────────────────
        "OHLE_Mast_Foundation_Vol": {
            "layers": [
                {"material": "Concrete_50_MPA_25pct_SCM", "thickness_m": 1.0},
                {"material": "Steel_Reinforcing_Bar", "thickness_m": 0.20},
                {"material": "Painting", "thickness_m": 0.0008}
            ],
            "replacement_factor": 0,  # Design life = 25 years → 60/25 ≈ 2.4 → rounded to 2
            "Operational_GHG_(kgCO2e/No)": 0,
            "Operational_Energy_(MJ/No)": 0,
            "Operational_Water_(L/No)": 0
        },
        "Steel_OHLE_Mast_Vol": {
            "layers": [
                {"material": "Hot_rolled_structural_steel", "thickness_m": 1.0},
                {"material": "Painting", "thickness_m": 0.0008}
            ],
            "replacement_factor": 0,
            "Operational_GHG_(kgCO2e/No)": 0,
            "Operational_Energy_(MJ/No)": 0,
            "Operational_Water_(L/No)": 0
        },

        # ───────────────────────────────────────
        # 🛣️ PAVEMENT & PATHS (DL = 15–20 years)
        # ───────────────────────────────────────
        "Road_Pavement_Flexible_Vol": {
            "layers": [
                {"material": "Asphalt", "thickness_m": 0.15},
                {"material": "Crushed_Rock", "thickness_m": 0.30},
                {"material": "Recycled_aggregate", "thickness_m": 0.20}
            ],
            "replacement_factor": 3,  # DL = 20 years → 60/20 = 3
            "Operational_GHG_(kgCO2e/No)": 0,
            "Operational_Energy_(MJ/No)": 0,
            "Operational_Water_(L/No)": 0
        },
        "Pedestrian_Path_Vol": {
            "layers": [
                {"material": "Concrete_25_MPA_30pct_SCM", "thickness_m": 0.12},
                {"material": "Sand", "thickness_m": 0.10},
                {"material": "Crushed_Rock", "thickness_m": 0.15}
            ],
            "replacement_factor": 3,
            "Operational_GHG_(kgCO2e/No)": 0,
            "Operational_Energy_(MJ/No)": 0,
            "Operational_Water_(L/No)": 0
        },

        # ───────────────────────────────────────
        # 🚰 UTILITIES & DRAINAGE
        # ───────────────────────────────────────
        "CSR_Trench_Type_A_1km": {
            "layers": [
                {"material": "Crushed_Rock", "thickness_m": 0.87},
                {"material": "Sand", "thickness_m": 0.10},
                {"material": "PE_Pipe_HDPE", "thickness_m": 0.05}  # representative
            ],
            "replacement_factor": 1,  # DL = 20 years
            "Operational_GHG_(kgCO2e/No)": 0,
            "Operational_Energy_(MJ/No)": 0,
            "Operational_Water_(L/No)": 0
        },
        "RCP_Drainage_Pipe_Vol": {
            "layers": [
                {"material": "Reinforced_Concrete_Pipe_RCP", "thickness_m": 0.10},
                {"material": "Steel_Reinforcing_Bar", "thickness_m": 0.01}
            ],
            "replacement_factor": 1,  # DL = 100 years
            "Operational_GHG_(kgCO2e/No)": 0,
            "Operational_Energy_(MJ/No)": 0,
            "Operational_Water_(L/No)": 0
        },

        # ───────────────────────────────────────
        # 🌿 LANDSCAPE & ANCILLARIES
        # ───────────────────────────────────────
        "Bollard_Vol": {
            "layers": [
                {"material": "Steel_Hot_Rolled", "thickness_m": 0.10},
                {"material": "Painting", "thickness_m": 0.0008}
            ],
            "replacement_factor": 1,  # DL = 15 years
            "Operational_GHG_(kgCO2e/No)": 0,
            "Operational_Energy_(MJ/No)": 0,
            "Operational_Water_(L/No)": 0
        },
                      # ───────────────────────────────────────
    # 🏗️ Belgian Standard Railway Track (Infrabel)
    # ───────────────────────────────────────
     # Rail_Ballast_0_80
     #───────────────────────────────────────
        # 🇧🇪 BELGIAN RAIL ELEMENTS (NEW!)
        # ───────────────────────────────────────
        "Rail_Concrete_Sleeper_No": {
            "layers": [
                {"material": "Concrete_28_MPA", "thickness_m": 0.143}  # per m track
            ],
            "replacement_factor": 1,  # DL = 50 years → 60/50 = 1.2 → use 1 for simplicity
            "Operational_GHG_(kgCO2e/No)": 0,
            "Operational_Energy_(MJ/No)": 0,
            "Operational_Water_(L/No)": 0
        },
        "Rail_Steel_Rail_60kgm": {
            "layers": [
                {"material": "Steel", "thickness_m": 0.0076}  # 60 kg/m ÷ 7850 kg/m³
            ],
            "replacement_factor": 1,
            "Operational_GHG_(kgCO2e/No)": 0,
            "Operational_Energy_(MJ/No)": 0,
            "Operational_Water_(L/No)": 0
        },
        "Rail_Ballast_0_80_No": {
            "layers": [
                {"material": "Rail_Ballast_0_80", "thickness_m": 1.015}  # per m track
            ],
            "replacement_factor": 1,
            "Operational_GHG_(kgCO2e/No)": 0,
            "Operational_Energy_(MJ/No)": 0,
            "Operational_Water_(L/No)": 0
        },
        "Rail_Subballast_0_32_No": {
            "layers": [
                {"material": "Rail_Subballast_0_32", "thickness_m": 1.16}
            ],
            "replacement_factor": 1,
            "Operational_GHG_(kgCO2e/No)": 0,
            "Operational_Energy_(MJ/No)": 0,
            "Operational_Water_(L/No)": 0
        },
        "Rail_Bedding_Asphalt_No": {
            "layers": [
                {"material": "Rail_Bedding_Asphalt", "thickness_m": 0.464}
            ],
            "replacement_factor": 1,
            "Operational_GHG_(kgCO2e/No)": 0,
            "Operational_Energy_(MJ/No)": 0,
            "Operational_Water_(L/No)": 0
        },
                    "OHLE_Mast_Foundation_Assembly-Vol": {
                "layers": [
                
                    {"material": "Concrete_50_MPA_25pct_SCM", "thickness_m": 1.2},
                    {"material": "Steel_Reinforcing_Bar", "thickness_m": 0.25},
                    {"material": "Painting", "thickness_m": 0.0008}
                ],
                "replacement_factor": 1,
                "Operational_GHG_(kgCO2e/No)": 0,
                "Operational_Energy_(MJ/No)": 0,
                "Operational_Water_(L/No)": 0,
            },
                    "OHW_Structure_Element_Vol": {
            "layers": [
                {"material": "Hot_rolled_structural_steel", "thickness_m": 1.0},
                {"material": "Painting", "thickness_m": 0.0008}
            ],
            "replacement_factor": 0,
            "Operational_GHG_(kgCO2e/No)": 0,
            "Operational_Energy_(MJ/No)": 0,
            "Operational_Water_(L/No)": 0
        },
         "Precast_Plank_55MPa_1m3_Vol": {
        "layers": [
            {"material": "Concrete_55_MPA__0pct_SCM", "thickness_m": 1.0},  #// ZVR55422 (324.00 m³ total)
            {"material": "Steel_Reinforcing_Bar", "thickness_m": 0.013}, #// Total Steel (Reo + Strand): 32.57 T / 324.00 m³ ≈ 100.5 kg/m³ → 0.013 m equiv.
            {"material": "Painting", "thickness_m": 0.0008}
        ],
        "replacement_factor": 0,
        "Operational_GHG_(kgCO2e/No)": 0,
        "Operational_Energy_(MJ/No)": 0,
        "Operational_Water_(L/No)": 0
    },
       # ───────────────────────────────────────
    # 🆕 ANCILLARIES - PURE MATERIAL ELEMENTS (1m³ of material = 1m³ of element)
    # ───────────────────────────────────────
    "Element_Aluminum_Screens_No": {
        "layers": [
            {"material": "Aluminum", "thickness_m": 1.0}
        ],
        "replacement_factor": 1, # Assuming 60-year life, Aluminium life span 60 years (0 replacements)
        "Operational_GHG_(kgCO2e/No)": 0,
        "Operational_Energy_(MJ/No)": 0,
        "Operational_Water_(L/No)": 0
    },
    "Element_Shear_Pins_Steel_No": {
        "layers": [
            {"material": "Steel", "thickness_m": 1.0}
        ],
        "replacement_factor": 0,
        "Operational_GHG_(kgCO2e/No)": 0,
        "Operational_Energy_(MJ/No)": 0,
        "Operational_Water_(L/No)": 0
    },
    "Element_FRP_Plate_Polymer_No": {
        "layers": [
            {"material": "General_Polymer", "thickness_m": 1.0}
        ],
        "replacement_factor": 1, # DL = 50 years (1 replacement over 100 years or 0 over 60 years)
        "Operational_GHG_(kgCO2e/No)": 0,
        "Operational_Energy_(MJ/No)": 0,
        "Operational_Water_(L/No)": 0
    },
    "Element_Handrail_Steel_1Tonne": {
        "layers": [
            {"material": "Mild_Steel", "thickness_m": 0.1274}
        ],
        "replacement_factor": 1,
        "Operational_GHG_(kgCO2e/No)": 0,
        "Operational_Energy_(MJ/No)": 0,
        "Operational_Water_(L/No)": 0
    },
        "Element_Mild_Steel_Parts_no": {
        "layers": [
            {"material": "Mild_Steel", "thickness_m": 1.0}
        ],
        "replacement_factor": 1,
        "Operational_GHG_(kgCO2e/No)": 0,
        "Operational_Energy_(MJ/No)": 0,
        "Operational_Water_(L/No)": 0
    },
  # ---------------------------------------
    # NVC PRECAST BEAMS (55MPa, 0% SCM) - RECIPE PER UNIT
    # ---------------------------------------
    "NVC_Beam_25m_No": {
        # Total_Units removed. Recipe represents 1 beam.
        "layers": [
            # Concrete volume for 1 beam: 35.737 m³
            {"material": "Concrete_55_MPA__0pct_SCM", "thickness_m": 35.737, "unit": "m³"},
            # Steel mass for 1 beam: 12147.86 kg -> 12147.86 / 7850 = 1.5475 m³
            {"material": "Steel_Reinforcing_Bar", "thickness_m": 1.5475, "unit": "m³"},
        ],
        "replacement_factor": 1,
        "Operational_GHG_(kgCO2e/No)": 0,
        "Operational_Energy_(MJ/No)": 0,
        "Operational_Water_(L/No)": 0
    },
    "NVC_Beam_27m_No": {
        # Total_Units removed. Recipe represents 1 beam.
        "layers": [
            # Concrete volume for 1 beam: 38.504 m³
            {"material": "Concrete_55_MPA__0pct_SCM", "thickness_m": 38.504, "unit": "m³"},
            # Steel mass for 1 beam: 13022.13 kg -> 13022.13 / 7850 = 1.6589 m³
            {"material": "Steel_Reinforcing_Bar", "thickness_m": 1.6589, "unit": "m³"},
        ],
        "replacement_factor": 1,
        "Operational_GHG_(kgCO2e/No)": 0,
        "Operational_Energy_(MJ/No)": 0,
        "Operational_Water_(L/No)": 0
    },
    "NVC_Beam_32_8m_No": {
        # Total_Units removed. Recipe represents 1 beam.
        "layers": [
            # Concrete volume for 1 beam: 44.828 m³
            {"material": "Concrete_55_MPA__0pct_SCM", "thickness_m": 44.828, "unit": "m³"},
            # Steel mass for 1 beam: 19825.00 kg -> 19825.00 / 7850 = 2.5255 m³
            {"material": "Steel_Reinforcing_Bar", "thickness_m": 2.5255, "unit": "m³"},
        ],
        "replacement_factor": 1,
        "Operational_GHG_(kgCO2e/No)": 0,
        "Operational_Energy_(MJ/No)": 0,
        "Operational_Water_(L/No)": 0
    },
    # ---------------------------------------
    # HUMES PRECAST BEAMS (50MPa, 20% SCM) - RECIPE PER UNIT
    # ---------------------------------------
    "Humes_Beam_25m_No": {
        # Total_Units removed. Recipe represents 1 beam.
        "layers": [
            # Concrete volume for 1 beam: 35.61 m³
            {"material": "Concrete_50_MPA_20pct_SCM", "thickness_m": 35.61, "unit": "m³"},
            # Steel mass for 1 beam: 12064.44 kg -> 12064.44 / 7850 = 1.5369 m³
            {"material": "Steel_Reinforcing_Bar", "thickness_m": 1.5369, "unit": "m³"},
        ],
        "replacement_factor": 1,
        "Operational_GHG_(kgCO2e/No)": 0,
        "Operational_Energy_(MJ/No)": 0,
        "Operational_Water_(L/No)": 0
    },
    "Humes_Beam_27m_No": {
        # Total_Units removed. Recipe represents 1 beam.
        "layers": [
            # Concrete volume for 1 beam: 40.16 m³
            {"material": "Concrete_50_MPA_20pct_SCM", "thickness_m": 40.16, "unit": "m³"},
            # Steel mass for 1 beam: 13029.57 kg -> 13029.57 / 7850 = 1.6598 m³
            {"material": "Steel_Reinforcing_Bar", "thickness_m": 1.6598, "unit": "m³"},
        ],
        "replacement_factor": 1,
        "Operational_GHG_(kgCO2e/No)": 0,
        "Operational_Energy_(MJ/No)": 0,
        "Operational_Water_(L/No)": 0
    },

    # ───────────────────────────────────────
    # ANCILLARIES & ASSEMBLIES (RECIPE PER UNIT)
    # ───────────────────────────────────────
    "Element_Aluminum_Screens_No": {
        # Total_Units removed. Recipe represents 1 m³ of screens (1.0 m³ of Aluminum).
        "layers": [
            # 2700.0 kg -> 2700.0 / 2700 = 1.0 m³
            {"material": "Aluminum", "thickness_m": 1.0000, "unit": "m³"}
        ],
        "replacement_factor": 2, # Project Life (100 years) / Material Life (60 years) = 2
        "Operational_GHG_(kgCO2e/No)": 0,
        "Operational_Energy_(MJ/No)": 0,
        "Operational_Water_(L/No)": 0
    },

    # --- ASSEMBLIES (Recipe represents 1 assembly) ---
    "P9_Trident_Stair_(Moreland)_16.3Tonne_No": {
        # Total_Units removed. Steel mass: 16.3 T * 1000 kg/T = 16300 kg -> 16300 / 7850 = 2.0764 m³
        "layers": [
            {"material": "Mild_Steel", "thickness_m": 2.0764, "unit": "m³"}
        ],
        "replacement_factor": 1,
        "Operational_GHG_(kgCO2e/No)": 0,
        "Operational_Energy_(MJ/No)": 0,
        "Operational_Water_(L/No)": 0
    },
    "P57_Trident_Stair_(Coburg)_16.3Tonne_No": {
        # Total_Units removed. Steel mass: 16.3 T -> 2.0764 m³
        "layers": [
            {"material": "Mild_Steel", "thickness_m": 2.0764, "unit": "m³"}
        ],
        "replacement_factor": 1,
        "Operational_GHG_(kgCO2e/No)": 0,
        "Operational_Energy_(MJ/No)": 0,
        "Operational_Water_(L/No)": 0
    },
    "P9_(East)_Signal_Blister_4.8Tonne_No": {
        # Total_Units removed. Steel mass: 4.8 T -> 4800 / 7850 = 0.6115 m³
        "layers": [
            {"material": "Mild_Steel", "thickness_m": 0.6115, "unit": "m³"}
        ],
        "replacement_factor": 1,
        "Operational_GHG_(kgCO2e/No)": 0,
        "Operational_Energy_(MJ/No)": 0,
        "Operational_Water_(L/No)": 0
    },
    "P16_(West)_Signal_Blister_6.6Tonne_No": {
        # Total_Units removed. Steel mass: 6.6 T -> 6600 / 7850 = 0.8407 m³
        "layers": [
            {"material": "Mild_Steel", "thickness_m": 0.8407, "unit": "m³"}
        ],
        "replacement_factor": 1,
        "Operational_GHG_(kgCO2e/No)": 0,
        "Operational_Energy_(MJ/No)": 0,
        "Operational_Water_(L/No)": 0
    },
    "P57_(East)_Signal_Blister_5.2Tonne_No": {
        # Total_Units removed. Steel mass: 5.2 T -> 5200 / 7850 = 0.6624 m³
        "layers": [
            {"material": "Mild_Steel", "thickness_m": 0.6624, "unit": "m³"}
        ],
        "replacement_factor": 1,
        "Operational_GHG_(kgCO2e/No)": 0,
        "Operational_Energy_(MJ/No)": 0,
        "Operational_Water_(L/No)": 0
    },
    "P65_(East)_Signal_Blister_6.6Tonne_No": {
        # Total_Units removed. Steel mass: 6.6 T -> 0.8407 m³
        "layers": [
            {"material": "Mild_Steel", "thickness_m": 0.8407, "unit": "m³"}
        ],
        "replacement_factor": 1,
        "Operational_GHG_(kgCO2e/No)": 0,
        "Operational_Energy_(MJ/No)": 0,
        "Operational_Water_(L/No)": 0
    },
    "P65_(West)_Signal_Blister_6.6Tonne_No": {
        # Total_Units removed. Steel mass: 6.6 T -> 0.8407 m³
        "layers": [
            {"material": "Mild_Steel", "thickness_m": 0.8407, "unit": "m³"}
        ],
        "replacement_factor": 1,
        "Operational_GHG_(kgCO2e/No)": 0,
        "Operational_Energy_(MJ/No)": 0,
        "Operational_Water_(L/No)": 0
    },
    "Plank_Walkway_(External)_5.6Tonne_No": {
        # Total_Units removed. Steel mass: 5.6 T -> 5600 / 7850 = 0.7134 m³
        "layers": [
            {"material": "Mild_Steel", "thickness_m": 0.7134, "unit": "m³"}
        ],
        "replacement_factor": 1,
        "Operational_GHG_(kgCO2e/No)": 0,
        "Operational_Energy_(MJ/No)": 0,
        "Operational_Water_(L/No)": 0
    },
    "Plank_Maintenance_Walkway_3.6Tonne_No": {
        # Total_Units removed. Steel mass: 3.6 T -> 3600 / 7850 = 0.4586 m³
        "layers": [
            {"material": "Mild_Steel", "thickness_m": 0.4586, "unit": "m³"}
        ],
        "replacement_factor": 1,
        "Operational_GHG_(kgCO2e/No)": 0,
        "Operational_Energy_(MJ/No)": 0,
        "Operational_Water_(L/No)": 0
    },
    "P9_(West)_Station_Extended_Walkway_0.3Tonne_No": {
        # Total_Units removed. Steel mass: 0.3 T -> 300 / 7850 = 0.0382 m³
        "layers": [
            {"material": "Mild_Steel", "thickness_m": 0.0382, "unit": "m³"}
        ],
        "replacement_factor": 1,
        "Operational_GHG_(kgCO2e/No)": 0,
        "Operational_Energy_(MJ/No)": 0,
        "Operational_Water_(L/No)": 0
    },
    "P15_(East)_Station_Extended_Walkway_0.3Tonne_No": {
        # Total_Units removed. Steel mass: 0.3 T -> 0.0382 m³
        "layers": [
            {"material": "Mild_Steel", "thickness_m": 0.0382, "unit": "m³"}
        ],
        "replacement_factor": 1,
        "Operational_GHG_(kgCO2e/No)": 0,
        "Operational_Energy_(MJ/No)": 0,
        "Operational_Water_(L/No)": 0
    },
    "P58_(West)_Station_Extended_Walkway_0.3Tonne_No": {
        # Total_Units removed. Steel mass: 0.3 T -> 0.0382 m³
        "layers": [
            {"material": "Mild_Steel", "thickness_m": 0.0382, "unit": "m³"}
        ],
        "replacement_factor": 1,
        "Operational_GHG_(kgCO2e/No)": 0,
        "Operational_Energy_(MJ/No)": 0,
        "Operational_Water_(L/No)": 0
    },
        # ───────────────────────────────────────
    # Crossheads and Protals
    # ───────────────────────────────────────
       # --- B2M Crosshead Recipes (Specific Types, 50 MPa, 20% SCM) ---
    # Concrete Volume (m³), Reo Weight (ton), Reo Volume (m³) = Reo Weight * 1000 / 7850

    # CC1 (Qty: 41)
    # Concrete Volume: 28.39 m³
    # Reo Volume: 9.57 T * 1000 / 7850 = 1.2191 m³
    "B2M_Crosshead_CC1_9.57Tonne_No": {
        "layers": [
            {"material": "Concrete_50_MPA_20pct_SCM", "thickness_m": 28.39, "unit": "m³"},
            {"material": "Steel_Reinforcing_Bar", "thickness_m": 1.2191, "unit": "m³"},
        ],
        "replacement_factor": 1,
        "Operational_GHG_(kgCO2e/No)": 0,
        "Operational_Energy_(MJ/No)": 0,
        "Operational_Water_(L/No)": 0
    },

    # CC2 (Qty: 10)
    # Concrete Volume: 29.10 m³
    # Reo Volume: 9.57 T * 1000 / 7850 = 1.2191 m³
    "B2M_Crosshead_CC2_9.57Tonne_No": {
        "layers": [
            {"material": "Concrete_50_MPA_20pct_SCM", "thickness_m": 29.10, "unit": "m³"},
            {"material": "Steel_Reinforcing_Bar", "thickness_m": 1.2191, "unit": "m³"},
        ],
        "replacement_factor": 1,
        "Operational_GHG_(kgCO2e/No)": 0,
        "Operational_Energy_(MJ/No)": 0,
        "Operational_Water_(L/No)": 0
    },

    # CC3 (Qty: 1)
    # Concrete Volume: 30.22 m³
    # Reo Volume: 11.61 T * 1000 / 7850 = 1.4789 m³
    "B2M_Crosshead_CC3_11.61Tonne_No": {
        "layers": [
            {"material": "Concrete_50_MPA_20pct_SCM", "thickness_m": 30.22, "unit": "m³"},
            {"material": "Steel_Reinforcing_Bar", "thickness_m": 1.4789, "unit": "m³"},
        ],
        "replacement_factor": 1,
        "Operational_GHG_(kgCO2e/No)": 0,
        "Operational_Energy_(MJ/No)": 0,
        "Operational_Water_(L/No)": 0
    },

    # CC4 (Qty: 1)
    # Concrete Volume: 32.25 m³
    # Reo Volume: 13.34 T * 1000 / 7850 = 1.7001 m³
    "B2M_Crosshead_CC4_13.34Tonne_No": {
        "layers": [
            {"material": "Concrete_50_MPA_20pct_SCM", "thickness_m": 32.25, "unit": "m³"},
            {"material": "Steel_Reinforcing_Bar", "thickness_m": 1.7001, "unit": "m³"},
        ],
        "replacement_factor": 1,
        "Operational_GHG_(kgCO2e/No)": 0,
        "Operational_Energy_(MJ/No)": 0,
        "Operational_Water_(L/No)": 0
    },

    # --- B2M Portal Recipes (Specific Types, 50 MPa, 25% SCM) ---

    # PC1-3 (Qty: 12)
    # Concrete Volume: 46.21 m³
    # Reo Volume: 17.43 T * 1000 / 7850 = 2.2204 m³
    "B2M_Portal_PC1_17.43Tonne_No": {
        "layers": [
            {"material": "Concrete_50_MPA_25pct_SCM", "thickness_m": 46.21, "unit": "m³"},
            {"material": "Steel_Reinforcing_Bar", "thickness_m": 2.2204, "unit": "m³"},
        ],
        "replacement_factor": 1,
        "Operational_GHG_(kgCO2e/No)": 0,
        "Operational_Energy_(MJ/No)": 0,
        "Operational_Water_(L/No)": 0
    },

    # PC4 (Qty: 1)
    # Concrete Volume: 53.07 m³
    # Reo Volume: 18.51 T * 1000 / 7850 = 2.3580 m³
    "B2M_Portal_PC4_18.51Tonne_No": {
        "layers": [
            {"material": "Concrete_50_MPA_25pct_SCM", "thickness_m": 53.07, "unit": "m³"},
            {"material": "Steel_Reinforcing_Bar", "thickness_m": 2.3580, "unit": "m³"},
        ],
        "replacement_factor": 1,
        "Operational_GHG_(kgCO2e/No)": 0,
        "Operational_Energy_(MJ/No)": 0,
        "Operational_Water_(L/No)": 0
    },

    # PC5 (Qty: 1)
    # Concrete Volume: 52.28 m³
    # Reo Volume: 18.51 T * 1000 / 7850 = 2.3580 m³
    "B2M_Portal_PC5_18.51Tonne_No": {
        "layers": [
            {"material": "Concrete_50_MPA_25pct_SCM", "thickness_m": 52.28, "unit": "m³"},
            {"material": "Steel_Reinforcing_Bar", "thickness_m": 2.3580, "unit": "m³"},
        ],
        "replacement_factor": 1,
        "Operational_GHG_(kgCO2e/No)": 0,
        "Operational_Energy_(MJ/No)": 0,
        "Operational_Water_(L/No)": 0
    },
     # --- B2M Precast Pier Recipe (Average of 49 units, 50 MPa, 22.5% SCM) ---
    "B2M_Pier_Average_No": {
        "layers": [
            # Average Concrete Volume (688.50 m³ / 49 Piers)
            {"material": "Concrete_50_MPA_25pct_SCM", "thickness_m": 14.051, "unit": "m³"},
            # Average Steel Volume (27.364 m³ / 49 Piers)
            {"material": "Steel_Reinforcing_Bar", "thickness_m": 0.5584, "unit": "m³"},
        ],
        "replacement_factor": 1,
        "Operational_GHG_(kgCO2e/No)": 0,
        "Operational_Energy_(MJ/No)": 0,
        "Operational_Water_(L/No)": 0
    },
        # ───────────────────────────────────────
    # Pile caps
    # ───────────────────────────────────────
  # --- B2M Pile Caps North ---
    # PCP1 North (Concrete Vol/unit: 40.70 m³, Reo Mass/unit: 10.21 T)
    "PileCapsP1_North_40.7m3_No": {
        "layers": [
            {"material": "Concrete", "thickness_m": 40.70},
            {"material": "Steel", "thickness_m": 1.32} # 10.21 T / 7.74 T/m³ ≈ 1.32 m³
        ],
        "replacement_factor": 1.0,
        "Operational_GHG_(kgCO2e/No)": 0,
        "Operational_Energy_(MJ/No)": 0,
        "Operational_Water_(L/No)": 0
    },

    # PCP5 North (Concrete Vol/unit: 49.60 m³, Reo Mass/unit: 10.99 T)
    "PileCapsP5_North_49.6m3_No": {
        "layers": [
            {"material": "Concrete", "thickness_m": 49.60},
            {"material": "Steel", "thickness_m": 1.42} # 10.99 T / 7.74 T/m³ ≈ 1.42 m³
        ],
        "replacement_factor": 1.0,
        "Operational_GHG_(kgCO2e/No)": 0,
        "Operational_Energy_(MJ/No)": 0,
        "Operational_Water_(L/No)": 0
    },

    # PC (ECC) North (Concrete Vol/unit: 49.39 m³, Reo Mass/unit: 12.64 T)
    "PileCaps_ECC_North_49.39m3_No": {
        "layers": [
            {"material": "Concrete", "thickness_m": 49.39},
            {"material": "Steel", "thickness_m": 1.63} # 12.64 T / 7.74 T/m³ ≈ 1.63 m³
        ],
        "replacement_factor": 1.0,
        "Operational_GHG_(kgCO2e/No)": 0,
        "Operational_Energy_(MJ/No)": 0,
        "Operational_Water_(L/No)": 0
    },

    # --- B2M Pile Caps South ---

    # PCP1 South (Concrete Vol/unit: 40.64 m³, Reo Mass/unit: 10.68 T)
    "PileCapsP1_South_40.64m3_No": {
        "layers": [
            {"material": "Concrete", "thickness_m": 40.64},
            {"material": "Steel", "thickness_m": 1.38} # 10.68 T / 7.74 T/m³ ≈ 1.38 m³
        ],
        "replacement_factor": 1.0,
        "Operational_GHG_(kgCO2e/No)": 0,
        "Operational_Energy_(MJ/No)": 0,
        "Operational_Water_(L/No)": 0
    },

    # PC (ECC) South (Concrete Vol/unit: 40.39 m³, Reo Mass/unit: 12.65 T)
    "PileCaps_ECC_South_40.39m3_No": {
        "layers": [
            {"material": "Concrete", "thickness_m": 40.39},
            {"material": "Steel", "thickness_m": 1.63} # 12.65 T / 7.74 T/m³ ≈ 1.63 m³
        ],
        "replacement_factor": 1.0,
        "Operational_GHG_(kgCO2e/No)": 0,
        "Operational_Energy_(MJ/No)": 0,
        "Operational_Water_(L/No)": 0
    },

    # --- South Pile Cap (CC1) Final Design ---
    # CC1 South (Concrete Vol/unit: 103.34 m³, Reo Mass/unit: 26.22 T)
    "PileCaps_CC1_South_103.34m3_No": {
        "layers": [
            {"material": "Concrete", "thickness_m": 103.34},
            {"material": "Steel", "thickness_m": 3.39} # 26.22 T / 7.74 T/m³ ≈ 3.39 m³
        ],
        "replacement_factor": 1.0,
        "Operational_GHG_(kgCO2e/No)": 0,
        "Operational_Energy_(MJ/No)": 0,
        "Operational_Water_(L/No)": 0
    },
            # ───────────────────────────────────────
    # Abutement Wall
    # ───────────────────────────────────────
        # --- South Abutment Wall ---
    # South Abutment Wall (Concrete Vol/unit: 66.81 m³, Reo Mass/unit: 11.94 T)
    "AbutmentWall_100m3_No": {
        "layers": [
            {"material": "Concrete_40_MPA_25pct_SCM", "thickness_m": 100},
            {"material": "Steel", "thickness_m": 2.4} # 11.94 T / 7.74 T/m³ ≈ 1.54 m³
        ],
        "replacement_factor": 1.0,
        "Operational_GHG_(kgCO2e/No)": 0,
        "Operational_Energy_(MJ/No)": 0,
        "Operational_Water_(L/No)": 0
    },
    # ───────────────────────────────────────
    # Deflection adn Fender Wall
    #───────────────────────────────────────
        # --- Deflection Walls ---
    # South Upper Deflection Wall (Concrete Vol/unit: 14.39 m³, Reo Mass/unit: 6.12 T)
    "DeflectionWall_14.39m3_No": {
        "layers": [
            {"material": "Concrete_40_MPA_25pct_SCM", "thickness_m": 14.39},
            {"material": "Steel", "thickness_m": 0.79} # 6.12 T / 7.74 T/m³ ≈ 0.79 m³
        ],
        "replacement_factor": 1.0,
        "Operational_GHG_(kgCO2e/No)": 0,
        "Operational_Energy_(MJ/No)": 0,
        "Operational_Water_(L/No)": 0
    },

    # South Lower Deflection Wall (Concrete Vol/unit: 37.06 m³, Reo Mass/unit: 6.24 T)
    "DeflectionWall__37.06m3_No": {
        "layers": [
            {"material": "Concrete_40_MPA_25pct_SCM", "thickness_m": 37.06},
            {"material": "Steel", "thickness_m": 0.81} # 6.24 T / 7.74 T/m³ ≈ 0.81 m³
        ],
        "replacement_factor": 1.0,
        "Operational_GHG_(kgCO2e/No)": 0,
        "Operational_Energy_(MJ/No)": 0,
        "Operational_Water_(L/No)": 0
    },

    # --- Fender Wall ---
    # South Lower Fender Wall (Concrete Vol/unit: 0.51 m³, Reo Mass/unit: 0.91 T)
    "FenderWall_0.51m3_No": {
        "layers": [
            {"material": "Concrete_40_MPA_25pct_SCM", "thickness_m": 0.51},
            {"material": "Steel", "thickness_m": 0.12} # 0.91 T / 7.74 T/m³ ≈ 0.12 m³
        ],
        "replacement_factor": 1.0,
        "Operational_GHG_(kgCO2e/No)": 0,
        "Operational_Energy_(MJ/No)": 0,
        "Operational_Water_(L/No)": 0
    },
     # --- South Approach Elements (from QTO) ---
        # ───────────────────────────────────────
    # Approach wall
    #───────────────────────────────────────
    # South Approach Wall (Concrete Vol/unit: 7.67 m³, Reo Mass/unit: 1.40 T)
    "ApproachWall_7.67m3_No": {
        "layers": [
            {"material": "Concrete_40_MPA_25pct_SCM", "thickness_m": 7.67},
            {"material": "Steel", "thickness_m": 0.18} # 1.40 T / 7.74 T/m³ ≈ 0.18 m³
        ],
        "replacement_factor": 1.0,
        "Operational_GHG_(kgCO2e/No)": 0,
        "Operational_Energy_(MJ/No)": 0,
        "Operational_Water_(L/No)": 0
    },

    # South Approach Slabs (Concrete Vol/unit: 10.86 m³, Reo Mass/unit: 2.09 T)
    "ApproachSlab_10.86m3_No": {
        "layers": [
            {"material": "Concrete_40_MPA_25pct_SCM", "thickness_m": 10.86},
            {"material": "Steel", "thickness_m": 0.27} # 2.09 T / 7.74 T/m³ ≈ 0.27 m³
        ],
        "replacement_factor": 1.0,
        "Operational_GHG_(kgCO2e/No)": 0,
        "Operational_Energy_(MJ/No)": 0,
        "Operational_Water_(L/No)": 0
    },

        # ───────────────────────────────────────
    #StitchPour
    #───────────────────────────────────────
    
        # North Stitch Pour 40MPa (Concrete Vol/unit: 11.76 m³, Reo Mass/unit: 0.90 T)
    "StitchPour_40MPa_11.76m3_No": {
        "layers": [
            {"material": "Concrete_40_MPA_25pct_SCM", "thickness_m": 11.76},
            {"material": "Steel", "thickness_m": 0.12} # 0.90 T / 7.74 T/m³ ≈ 0.12 m³
        ],
        "replacement_factor": 1.0,
        "Operational_GHG_(kgCO2e/No)": 0,
        "Operational_Energy_(MJ/No)": 0,
        "Operational_Water_(L/No)": 0
    },

    # North Stitch Pour 50MPa (Concrete Vol/unit: 9.85 m³, Reo Mass/unit: 0.90 T)
    "StitchPour_50MPa_9.85m3_No": {
        "layers": [
            {"material": "Concrete_40_MPA_25pct_SCM", "thickness_m": 9.85},
            {"material": "Steel", "thickness_m": 0.12} # 0.90 T / 7.74 T/m³ ≈ 0.12 m³
        ],
        "replacement_factor": 1.0,
        "Operational_GHG_(kgCO2e/No)": 0,
        "Operational_Energy_(MJ/No)": 0,
        "Operational_Water_(L/No)": 0
    },

    # --- B2M Stitch Pours South ---

    # South Stitch Pour 40MPa (Concrete Vol/unit: 9.53 m³, Reo Mass/unit: 0.90 T)
    "StitchPour_40MPa_9.53m3_No": {
        "layers": [
            {"material": "Concrete_40_MPA_25pct_SCM", "thickness_m": 9.53},
            {"material": "Steel", "thickness_m": 0.12} # 0.90 T / 7.74 T/m³ ≈ 0.12 m³
        ],
        "replacement_factor": 1.0,
        "Operational_GHG_(kgCO2e/No)": 0,
        "Operational_Energy_(MJ/No)": 0,
        "Operational_Water_(L/No)": 0
    },

    # South Stitch Pour 50MPa (Concrete Vol/unit: 9.53 m³, Reo Mass/unit: 0.90 T)
    "StitchPour_50MPa_9.53m3_No": {
        "layers": [
            {"material": "Concrete_40_MPA_25pct_SCM", "thickness_m": 9.53},
            {"material": "Steel", "thickness_m": 0.12} # 0.90 T / 7.74 T/m³ ≈ 0.12 m³
        ],
        "replacement_factor": 1.0,
        "Operational_GHG_(kgCO2e/No)": 0,
        "Operational_Energy_(MJ/No)": 0,
        "Operational_Water_(L/No)": 0
    },
    
        # ───────────────────────────────────────
    #Piles
    #───────────────────────────────────────

    # Monopile (1800mm) - Defined per 1 m³ of concrete volume
    # Average Steel Mass Ratio: 0.2337 T Steel per 1 m³ Concrete (includes Rebar, Starter Cols, 1800mm Extensions)
    "Monopile_1800mm_40MPa_1m3_No": {
        "layers": [
            {"material": "Concrete_40_MPA_25pct_SCM", "thickness_m": 1.00},
            {"material": "Steel", "thickness_m": 0.0302} # 0.2337 T / 7.74 T/m³ ≈ 0.0302 m³
        ],
        "replacement_factor": 1.0,
        "Operational_GHG_(kgCO2e/No)": 0,
        "Operational_Energy_(MJ/No)": 0,
        "Operational_Water_(L/No)": 0
    },

    # Bored Pile (1050mm) - Defined per 1 m³ of concrete volume
    # Average Steel Mass Ratio: 0.2168 T Steel per 1 m³ Concrete (includes Rebar, 1050mm Extensions)
    "BoredPile_1050mm_40MPa_1m3_No": {
        "layers": [
            {"material": "Concrete_40_MPA_25pct_SCM", "thickness_m": 1.00},
            {"material": "Steel", "thickness_m": 0.0280} # 0.2168 T / 7.74 T/m³ ≈ 0.0280 m³
        ],
        "replacement_factor": 1.0,
        "Operational_GHG_(kgCO2e/No)": 0,
        "Operational_Energy_(MJ/No)": 0,
        "Operational_Water_(L/No)": 0
    },
    
            # ───────────────────────────────────────
    #Drainage
    #───────────────────────────────────────
        # --- B2M Drainage Pipes and Culverts (Volume per Linear Meter) ---

    # SRP Slotted Pipes (PE Pipes) - 630.80 m / 39.97 m³ -> 0.0634 m³/m
    "Drainage_SRP_Slotted_1m_No": {
        "layers": [
            {"material": "PE_Pipe_HDPE", "thickness_m": 0.0634}
        ],
        "replacement_factor": 1.0,
        "Operational_GHG_(kgCO2e/No)": 0,
        "Operational_Energy_(MJ/No)": 0,
        "Operational_Water_(L/No)": 0
    },

    # HDPP Pipes (PE Pipes) - 719.17 m / 194.25 m³ -> 0.2701 m³/m
    "Drainage_HDPP_1m_No": {
        "layers": [
            {"material": "PE_Pipe_HDPE", "thickness_m": 0.2701}
        ],
        "replacement_factor": 1.0,
        "Operational_GHG_(kgCO2e/No)": 0,
        "Operational_Energy_(MJ/No)": 0,
        "Operational_Water_(L/No)": 0
    },

    # uPVC Pipes (PE Pipes) - 166.53 m / 5.22 m³ -> 0.0314 m³/m
    "Drainage_uPVC_1m_No": {
        "layers": [
            {"material": "PVC_Pipe", "thickness_m": 0.0314}
        ],
        "replacement_factor": 1.0,
        "Operational_GHG_(kgCO2e/No)": 0,
        "Operational_Energy_(MJ/No)": 0,
        "Operational_Water_(L/No)": 0
    },

    # PVC Pipes (PE Pipes) - 11.34 m / 0.07 m³ -> 0.0062 m³/m
    "Drainage_PVC_1m_No": {
        "layers": [
            {"material": "PVC_Pipe", "thickness_m": 0.0062}
        ],
        "replacement_factor": 1.0,
        "Operational_GHG_(kgCO2e/No)": 0,
        "Operational_Energy_(MJ/No)": 0,
        "Operational_Water_(L/No)": 0
    },

    # RCP Pipes (Reinforced Concrete Pipes) - 167.973 m / 39.829 m³ -> 0.2371 m³/m total
    "Drainage_RCP_1m_No": {
        "layers": [
            {"material": "Concrete_40_MPA_25pct_SCM", "thickness_m": 0.2324}, # 0.2371 * 0.98
            {"material": "Steel", "thickness_m": 0.0047}     # 0.2371 * 0.02
        ],
        "replacement_factor": 1.0,
        "Operational_GHG_(kgCO2e/No)": 0,
        "Operational_Energy_(MJ/No)": 0,
        "Operational_Water_(L/No)": 0
    },

    # Reinforced Concrete Box Culverts (RCBC) - 238.264 m / 61.262 m³ -> 0.2571 m³/m total
    "Drainage_RCBC_1m_No": {
        "layers": [
            {"material": "Concrete_40_MPA_25pct_SCM", "thickness_m": 0.2520}, # 0.2571 * 0.98
            {"material": "Steel", "thickness_m": 0.0051}     # 0.2571 * 0.02
        ],
        "replacement_factor": 1.0,
        "Operational_GHG_(kgCO2e/No)": 0,
        "Operational_Energy_(MJ/No)": 0,
        "Operational_Water_(L/No)": 0
    },
    
                # ───────────────────────────────────────
    #Abutements
    #───────────────────────────────────────
    
    # --- B2M Abutments and Fascia Panels NORTH ---

    # Abutment Wall (NORTH) - 50MPa, VS502VR45, 20% Fly Ash
    # Concrete Vol: 90.00 m³, Rebar Mass: 13.07 T
    "AbutmentWall_North_90m3_No": {
        "layers": [
            {"material": "Concrete", "thickness_m": 90.00},
            {"material": "Steel", "thickness_m": 1.6886} # 13.07 T / 7.74 T/m³ ≈ 1.6886 m³
        ],
        "replacement_factor": 1.0,
        "Operational_GHG_(kgCO2e/No)": 0,
        "Operational_Energy_(MJ/No)": 0,
        "Operational_Water_(L/No)": 0
    },

    # Fender Wall (NORTH) - 40MPa, VS402VR45, 25% Fly Ash
    # Concrete Vol: 7.00 m³, Rebar Mass: 0.83 T
    "FenderWall_North_7m3_No": {
        "layers": [
            {"material": "Concrete", "thickness_m": 7.00},
            {"material": "Steel", "thickness_m": 0.1072} # 0.83 T / 7.74 T/m³ ≈ 0.1072 m³
        ],
        "replacement_factor": 1.0,
        "Operational_GHG_(kgCO2e/No)": 0,
        "Operational_Energy_(MJ/No)": 0,
        "Operational_Water_(L/No)": 0
    },

    # Abutment Pile Cap (NORTH) - 40MPa, VS402FVR, 25% Fly Ash
    # Concrete Vol: 120.10 m³, Rebar Mass: 23.87 T
    "AbutmentPileCap_North_120.1m3_No": {
        "layers": [
            {"material": "Concrete", "thickness_m": 120.10},
            {"material": "Steel", "thickness_m": 3.0839} # 23.87 T / 7.74 T/m³ ≈ 3.0839 m³
        ],
        "replacement_factor": 1.0,
        "Operational_GHG_(kgCO2e/No)": 0,
        "Operational_Energy_(MJ/No)": 0,
        "Operational_Water_(L/No)": 0
    },

    # Precast Fascia Panels (NORTH) - 50MPa, ZVR5025, 24.4% Slag
    # Concrete Vol: 13.55 m³, Rebar Mass: 1.05 T
    "PrecastFasciaPanels_North_13.55m3_No": {
        "layers": [
            {"material": "Concrete", "thickness_m": 13.55},
            {"material": "Steel", "thickness_m": 0.1357} # 1.05 T / 7.74 T/m³ ≈ 0.1357 m³
        ],
        "replacement_factor": 1.0,
        "Operational_GHG_(kgCO2e/No)": 0,
        "Operational_Energy_(MJ/No)": 0,
        "Operational_Water_(L/No)": 0
    },
    
    
                # ───────────────────────────────────────
    #Post panel walles
    #───────────────────────────────────────
    # Post Panel Wall Piles (Concrete and Steel Cages)
    # Concrete Vol: 314.04 m³ (40 MPa, VS401VMWC, 34.76% SCM)
    # Steel Cage Mass: 63.945 T
    "PostPanelWall_Piles_Total_314m3_No": {
        "layers": [
            {"material": "Concrete_40_MPA_25pct_SCM", "thickness_m": 314.04},
            {"material": "Steel", "thickness_m": 8.2616} # 63.945 T / 7.74 T/m³ ≈ 8.2616 m³
        ],
        "replacement_factor": 1.0,
        "Operational_GHG_(kgCO2e/No)": 0,
        "Operational_Energy_(MJ/No)": 0,
        "Operational_Water_(L/No)": 0
    },

    # Post Panel Wall Precast Panels (Concrete and Reinforcement)
    # Concrete Vol: 205.067 m³ (50 MPa, ZVR5025, 24.4% Slag)
    # Rebar Mass: 34.008 T
    "PostPanelWall_Panels_Total_205m3_No": {
        "layers": [
            {"material": "Concrete_40_MPA_25pct_SCM", "thickness_m": 205.067},
            {"material": "Steel", "thickness_m": 4.3938} # 34.008 T / 7.74 T/m³ ≈ 4.3938 m³
        ],
        "replacement_factor": 1.0,
        "Operational_GHG_(kgCO2e/No)": 0,
        "Operational_Energy_(MJ/No)": 0,
        "Operational_Water_(L/No)": 0
    },

    # Post Panel Wall Galvanised Steel Posts
    # Galvanised Steel Mass: 45.58 T (Mapped to 'Steel' material)
    "PostPanelWall_GalvanisedPosts_Total_45.58T_No": {
        "layers": [
            {"material": "Steel", "thickness_m": 5.8889} # 45.58 T / 7.74 T/m³ ≈ 5.8889 m³
        ],
        "replacement_factor": 1.0,
        "Operational_GHG_(kgCO2e/No)": 0,
        "Operational_Energy_(MJ/No)": 0,
        "Operational_Water_(L/No)": 0
    },
    
# ───────────────────────────────────────
    #Retaining Walls 
#───────────────────────────────────────
    # Reinforced Concrete Retaining Wall (General RC unit, 2.0% Rebar Mass Ratio)
    # Defined per 1 m³ of concrete volume (assuming 1.4 T/m³ Concrete density)
    # Steel Mass Ratio: 0.028 T Steel per 1 m³ Concrete (0.028 T / 7.74 T/m³ ≈ 0.0036 m³)
    "RetainingWall_RC_1m3_No": {
        "layers": [
            {"material": "Concrete_50_MPA_25pct_SCM", "thickness_m": 0.30},
            {"material": "Steel_Reinforcing_Bar", "thickness_m": 0.0109},
            {"material": "Crushed_Rock", "thickness_m": 0.46}
        ],
        "replacement_factor": 1.0,
        "Operational_GHG_(kgCO2e/No)": 0,
        "Operational_Energy_(MJ/No)": 0,
        "Operational_Water_(L/No)": 0
    },
    
    # ───────────────────────────────────────
    #Roadworks, SUP&Kerb Channel
#───────────────────────────────────────
        "BridgeDeck_RC_1m3_No": {
        "layers": [
            {"material": "Concrete_50_MPA_25pct_SCM", "thickness_m": 1.00},
            {"material": "Steel", "thickness_m": 0.012}
        ],
        "replacement_factor": 1.0,
        "Operational_GHG_(kgCO2e/No)": 0,
        "Operational_Energy_(MJ/No)": 0,
        "Operational_Water_(L/No)": 0
    },
    "Pavement_Asphalt_1m2_No": {
        "layers": [
            {"material": "Asphalt", "thickness_m": 0.15},
            {"material": "Granular_Base", "thickness_m": 0.30}
        ],
        "replacement_factor": 1.0,
        "Operational_GHG_(kgCO2e/No)": 0,
        "Operational_Energy_(MJ/No)": 0,
        "Operational_Water_(L/No)": 0
    },
    "TrafficBarrier_Steel_1m_No": {
        "layers": [
            {"material": "Steel", "thickness_m": 0.005}
        ],
        "replacement_factor": 1.0,
        "Operational_GHG_(kgCO2e/No)": 0,
        "Operational_Energy_(MJ/No)": 0,
        "Operational_Water_(L/No)": 0
    }
        }

        for element_name, element_data in elements.items():
            total_ghg = total_energy = total_water = total_mass = 0
            replacement_factor = element_data.get("replacement_factor", 1)
            material_masses = OrderedDict([
                ("Concrete and plaster products", 0),
                ("Plastics", 0),
                ("Metals", 0),
                ("Miscellaneous", 0),
                ("Sand, stone and ceramics", 0),
                ("Timber", 0),
                ("Glass", 0),
                ("Insulation", 0)
            ])
            
            # Add dictionaries for category breakdowns
            category_ghg = copy.deepcopy(material_masses)
            category_energy = copy.deepcopy(material_masses)
            category_water = copy.deepcopy(material_masses)

            replacement_factor = element_data.get("replacement_factor", 1)

            for layer in element_data["layers"]:
                material = layer["material"]
                thickness_m = layer["thickness_m"]
                ghg, energy, water, mass = self.calculate_embodied_metrics(material, thickness_m)
                
                # Get material category
                category = next((mat["Categories"] for mat in MATERIAL_DATA if mat["Material"] == material), "Miscellaneous")
                

                
                # Accumulate totals
                total_ghg += ghg
                total_energy += energy
                total_water += water
                total_mass += mass
                
                            #Calculate maintenance values by multiplying with replacement factor
                maintenance_mass = total_mass * replacement_factor
                maintenance_ghg = total_ghg * replacement_factor
                maintenance_energy = total_energy * replacement_factor
                maintenance_water = total_water * replacement_factor

                
                # Accumulate category values
                material_masses[category] += mass
                category_ghg[category] += ghg
                category_energy[category] += energy
                category_water[category] += water

            # Calculate maintenance values per category
            maintenance_ghg = OrderedDict()
            maintenance_energy = OrderedDict()
            maintenance_water = OrderedDict()
            for cat in material_masses.keys():
                maintenance_ghg[cat] = category_ghg[cat] * replacement_factor
                maintenance_energy[cat] = category_energy[cat] * replacement_factor
                maintenance_water[cat] = category_water[cat] * replacement_factor
                
                
            total_maintenance_energy = sum(maintenance_energy.values())
            total_maintenance_water = sum(maintenance_water.values())
            total_maintenance_ghg = sum(maintenance_ghg.values())




            # Build result dictionary with category breakdowns
            self.element_db[element_name] = {
                # Totals
                "Initial_Embodied_GHG_(kgCO2e)": total_ghg,
                "Initial_Embodied_Energy_(MJ)": total_energy,
                "Initial_Embodied_Water_(L)": total_water,
                "Total_Mass_(kg)": total_mass,

                        # Total Maintenance Impacts
                "Maintenance_Mass_(kg)": maintenance_mass,
                "Maintenance_Embodied_GHG_(kgCO2e)": total_maintenance_ghg,
                "Maintenance_Embodied_Energy_(MJ)": total_maintenance_energy,
                "Maintenance_Embodied_Water_(L)": total_maintenance_water,
                # Category breakdowns - Mass
                "Concrete and plaster products_Mass_(kg)": material_masses["Concrete and plaster products"],
                "Plastics_Mass_(kg)": material_masses["Plastics"],
                "Metals_Mass_(kg)": material_masses["Metals"],
                "Miscellaneous_Mass_(kg)": material_masses["Miscellaneous"],
                "Sand, stone and ceramics_Mass_(kg)": material_masses["Sand, stone and ceramics"],
                "Glass_Mass_(kg)": material_masses["Glass"],
                "Timber_Mass_(kg)": material_masses["Timber"],
                "Insulation_Mass_(kg)": material_masses["Insulation"],
                
                # Category breakdowns - Initial GHG
                "Concrete and plaster products_Initial_Embodied_GHG_(kgCO2e)": category_ghg["Concrete and plaster products"],
                "Plastics_Initial_Embodied_GHG_(kgCO2e)": category_ghg["Plastics"],
                "Metals_Initial_Embodied_GHG_(kgCO2e)": category_ghg["Metals"],
                "Miscellaneous_Initial_Embodied_GHG_(kgCO2e)": category_ghg["Miscellaneous"],
                "Sand, stone and ceramics_Initial_Embodied_GHG_(kgCO2e)": category_ghg["Sand, stone and ceramics"],
                "Glass_Initial_Embodied_GHG_(kgCO2e)": category_ghg["Glass"],
                "Timber_Initial_Embodied_GHG_(kgCO2e)": category_ghg["Timber"],
                "Insulation_Initial_Embodied_GHG_(kgCO2e)": category_ghg["Insulation"],
                # ... (add all other categories similarly)
                
                # Category breakdowns - Maintenance GHG
                "Concrete and plaster products_Maintenance_Embodied_GHG_(kgCO2e)": maintenance_ghg["Concrete and plaster products"],
                "Plastics_Maintenance_Embodied_GHG_(kgCO2e)": maintenance_ghg["Plastics"],
                "Metals_Maintenance_Embodied_GHG_(kgCO2e)": maintenance_ghg["Metals"],
                "Miscellaneous_Maintenance_Embodied_GHG_(kgCO2e)": maintenance_ghg["Miscellaneous"],
                "Sand, stone and ceramics_Maintenance_Embodied_GHG_(kgCO2e)": maintenance_ghg["Sand, stone and ceramics"],
                "Glass_Maintenance_Embodied_GHG_(kgCO2e)": maintenance_ghg["Glass"],
                "Timber_Maintenance_Embodied_GHG_(kgCO2e)": maintenance_ghg["Timber"],
                "Insulation_Maintenance_Embodied_GHG_(kgCO2e)": maintenance_ghg["Insulation"],
                
                # Category breakdowns - Initial Energy
                "Concrete and plaster products_Initial_Embodied_energy_(MJ)": category_energy["Concrete and plaster products"],
                "Plastics_Initial_Embodied_energy_(MJ)": category_energy["Plastics"],
                "Metals_Initial_Embodied_energy_(MJ)": category_energy["Metals"],
                "Miscellaneous_Initial_Embodied_energy_(MJ)": category_energy["Miscellaneous"],
                "Sand, stone and ceramics_Initial_Embodied_energy_(MJ)": category_energy["Sand, stone and ceramics"],
                "Glass_Initial_Embodied_energy_(MJ)": category_energy["Glass"],
                "Timber_Initial_Embodied_energy_(MJ)": category_energy["Timber"],
                "Insulation_Initial_Embodied_energy_(MJ)": category_energy["Insulation"],
                # ... (add all other categories similarly)
                # Category breakdowns - Maintenance Energy
                "Concrete and plaster products_Maintenance_Embodied_energy_(MJ)": category_energy["Concrete and plaster products"],
                "Plastics_Maintenance_Embodied_energy_(MJ)": category_energy["Plastics"],
                "Metals_Maintenance_Embodied_energy_(MJ)": category_energy["Metals"],
                "Miscellaneous_Maintenance_Embodied_energy_(MJ)": category_energy["Miscellaneous"],
                "Sand, stone and ceramics_Maintenance_Embodied_energy_(MJ)": category_energy["Sand, stone and ceramics"],
                "Glass_Maintenance_Embodied_energy_(MJ)": category_energy["Glass"],
                "Timber_Maintenance_Embodied_energy_(MJ)": category_energy["Timber"],
                "Insulation_Maintenance_Embodied_energy_(MJ)": category_energy["Insulation"],
                # Category breakdowns - Initial Water
                "Concrete and plaster products_Initial_embodied_water_(L)": category_water["Concrete and plaster products"],
                "Plastics_Initial_Embodied_water_(L)": category_water["Plastics"],
                "Metals_Initial_Embodied_water_(L)": category_water["Metals"],
                "Miscellaneous_Initial_Embodied_water_(L)": category_water["Miscellaneous"],
                "Sand, stone and ceramics_Initial_Embodied_water_(L)": category_water["Sand, stone and ceramics"],
                "Glass_Initial_Embodied_water_(L)": category_water["Glass"],
                "Timber_Initial_Embodied_water_(L)": category_water["Timber"],
                "Insulation_Initial_Embodied_water_(L)": category_water["Insulation"],
                # ... (add all other categories similarly)
                # Category breakdowns - Maintenance Water
                "Concrete and plaster products_Maintenance_Embodied_Water_(L)": maintenance_water["Concrete and plaster products"],
                "Plastics_Maintenance_Embodied_Water_(L)": maintenance_water["Plastics"],
                "Metals_Maintenance_Embodied_Water_(L)": maintenance_water["Metals"],
                "Miscellaneous_Maintenance_Embodied_Water_(L)": maintenance_water["Miscellaneous"],
                "Sand, stone and ceramics_Maintenance_Embodied_Water_(L)": maintenance_water["Sand, stone and ceramics"],
                "Glass_Maintenance_Embodied_Water_(L)": maintenance_water["Glass"],
                "Timber_Maintenance_Embodied_Water_(L)": maintenance_water["Timber"],
                "Insulation_Maintenance_Embodied_Water_(L)": maintenance_water["Insulation"],
                # ... (repeat for Energy and Water metrics)
            }
    def print_element_db(self):
        print("Element Database:")
        for element_name, metrics in self.element_db.items():
            print(element_name + ":")
            for key, value in metrics.items():
                print("  " + str(key) + ": " + str(value))
            print()

# ... (keep rest of Infraset119 code)


class AssemblyDatabase:
    def __init__(self, material_db):
        self.material_db = material_db
        self.assembly_db = {}
        self.maintenance_factor = 1  # Constant factor for maintenance applied to pavement layer

    def calculate_embodied_metrics(self, material_name, thickness_m):
        volume_m3 = thickness_m * 1  # Assume 1 m² area
        material_props = self.material_db.get(material_name, {})
        
        ghg = volume_m3 * 1000 * material_props.get("Embodied_GHG_Coefficient_(kgCO2e/FU)", 0)
        energy = volume_m3 * 1000 * material_props.get("Embodied_Energy_Coefficient_(MJ/FU)", 0)
        water = volume_m3 * 1000 * material_props.get("Embodied_Water_Coefficient_(L/FU)", 0)
        density = material_props.get("Density_(kg/m³)", 0)
        mass = volume_m3 * density
        
        return ghg, energy, water, mass

    def populate_assemblies(self):
        assemblies = {
            "Concrete_Highway": {
                "layers": [
                    {"material": "Recycled aggregate", "thickness_m": 0.3},
                    {"material": "Cement", "thickness_m": 0.3},
                    {"pavement_material": "Concrete", "thickness_m": 0.1}
                ],
                "replacement_factor": 1,
                "Operational_GHG_(kgCO2e/No)": 0,
                "Operational_Energy_(MJ/No)": 0,
                "Operational_Water_(L/No)": 0,
                "PKT_million_60_years" : 2850
            },
            "Asphalt_Highway": {
                "layers": [
                    {"material": "Recycled aggregate", "thickness_m": 0.3},
                    {"material": "Recycled aggregate", "thickness_m": 0.3},
                    {"material": "Gravel", "thickness_m": 0.3},
                    {"pavement_material": "Asphalt", "thickness_m": 0.4}
                ],
                "replacement_factor": 1,
                "Operational_GHG_(kgCO2e/No)": 0,
                "Operational_Energy_(MJ/No)": 0,
                "Operational_Water_(L/No)": 0,
                "PKT_million_60_years" : 2850
            },
            "Urban_Street_Asphalt": {
                "layers": [
                    {"pavement_material": "Asphalt", "thickness_m": 0.15},
                    {"material": "Recycled aggregate", "thickness_m": 0.28},
                    {"material": "Gravel", "thickness_m": 0.5},
                    {"material": "Sand", "thickness_m": 0.43}
                ],
                "replacement_factor": 1,
                "Operational_GHG_(kgCO2e/No)": 0,
                "Operational_Energy_(MJ/No)": 0,
                "Operational_Water_(L/No)": 0,
                "Embodied_GHG_Coefficient_pavement": 0.2,
                "Embodied_Energy_Coefficient_pavement": 4.2,
                "Embodied_Water_Coefficient_pavement": 2.9,
                "replacement_factor_pavement": 1.2,
                "PKT_million_60_years" : 192
            },
            "Pedestrian_Way_Concrete": {
                "layers": [
                    {"pavement_material": "Concrete_25_MPA", "thickness_m": 0.04},
                    {"material": "Recycled aggregate", "thickness_m": 0.0025},
                    {"material": "Gravel", "thickness_m": 0.3},
                    {"material": "Sand", "thickness_m": 0.14}
                ],
                "replacement_factor": 1,
                "Operational_GHG_(kgCO2e/No)": 0,
                "Operational_Energy_(MJ/No)": 0,
                "Operational_Water_(L/No)": 0,
                "Embodied_GHG_Coefficient_pavement": 0.15,
                "Embodied_Energy_Coefficient_pavement": 1.07,
                "Embodied_Water_Coefficient_pavement": 1.74,
                "replacement_factor_pavement": 0.45,
                "PKT_million_60_years": 8.2
            },
            "Bicycle_path_Concrete": {
                "layers": [
                    {"pavement_material": "Concrete_25_MPA", "thickness_m": 0.04},
                    {"material": "Recycled aggregate", "thickness_m": 0.002},
                    {"material": "Gravel", "thickness_m": 0.3},
                    {"material": "Sand", "thickness_m": 0.14}
                ],
                "replacement_factor": 1,
                "Operational_GHG_(kgCO2e/No)": 0,
                "Operational_Energy_(MJ/No)": 0,
                "Operational_Water_(L/No)": 0,
                "Embodied_GHG_Coefficient_pavement": 0.15,
                "Embodied_Energy_Coefficient_pavement": 1.07,
                "Embodied_Water_Coefficient_pavement": 1.74,
                "replacement_factor_pavement": 0.45,
                "PKT_million_60_years": 11.4
            },
             # ───────────────────────────────────────
        # 🌉 STRUCTURAL ASSEMBLIES (NO PAVEMENT)
        # ───────────────────────────────────────
        "Bell_Moreland_Viaduct_Segment": {
                "layers": [
                {"pavement_material": "Concrete_25_MPA", "thickness_m": 0.00},
                    {"material": "Concrete_50_MPA_25pct_SCM", "thickness_m": 1.0},
                    {"material": "Steel_Reinforcing_Bar", "thickness_m": 0.042 },
                    {"material": "Painting", "thickness_m": 0.0008}
                ],
                "replacement_factor": 1,
                "Operational_GHG_(kgCO2e/No)": 0,
                "Operational_Energy_(MJ/No)": 0,
                "Operational_Water_(L/No)": 0,
                "PKT_million_60_years": 2850
            },
            "Noise_Wall_NVC_Panel": {
                "layers": [
                {"pavement_material": "Concrete_25_MPA", "thickness_m": 0.00},
                    {"material": "Concrete_55_MPA_0pct_SCM", "thickness_m": 0.25},
                    {"material": "Steel_Reinforcing_Bar", "thickness_m": 0.025},
                    {"material": "Painting", "thickness_m": 0.0008}
                ],
                "replacement_factor": 1,
                "Operational_GHG_(kgCO2e/No)": 0,
                "Operational_Energy_(MJ/No)": 0,
                "Operational_Water_(L/No)": 0,
                "PKT_million_60_years": 2850
            },
"Retaining_Wall_L_Shaped": {
    "layers": [
    {"pavement_material": "Concrete_25_MPA", "thickness_m": 0.00},
        {"material": "Concrete_40_MPA_25pct_SCM", "thickness_m": 0.8},
        {"material": "Steel_Reinforcing_Bar", "thickness_m": 0.25},
        {"material": "Painting", "thickness_m": 0.0008}
    ],
    "replacement_factor": 1,
    "Operational_GHG_(kgCO2e/No)": 0,
    "Operational_Energy_(MJ/No)": 0,
    "Operational_Water_(L/No)": 0,
    "PKT_million_60_years": 2850
},  # ← And this } and comma
            "Urban_Road_Flexible": {
                "layers": [
                    {"pavement_material": "Asphalt", "thickness_m": 0.15},
                    {"material": "Crushed_Rock", "thickness_m": 0.30},
                    {"material": "Recycled_aggregate", "thickness_m": 0.20}
                ],
                "replacement_factor": 1,
                "Operational_GHG_(kgCO2e/No)": 0,
                "Operational_Energy_(MJ/No)": 0,
                "Operational_Water_(L/No)": 0,
                "Embodied_GHG_Coefficient_pavement": 0.53,
                "Embodied_Energy_Coefficient_pavement": 1.1258,
                "Embodied_Water_Coefficient_pavement": 7.672,
                "replacement_factor_pavement": 1.20,
                "PKT_million_60_years": 2850
            },
            "Pedestrian_Path_Concrete": {
                "layers": [
                    {"pavement_material": "Concrete_25_MPA_30pct_SCM", "thickness_m": 0.12},
                    {"material": "Sand", "thickness_m": 0.10},
                    {"material": "Crushed_Rock", "thickness_m": 0.15}
                ],
                "replacement_factor": 1,
                "Operational_GHG_(kgCO2e/No)": 0,
                "Operational_Energy_(MJ/No)": 0,
                "Operational_Water_(L/No)": 0,
                "Embodied_GHG_Coefficient_pavement": 0.336 * 0.7,
                "Embodied_Energy_Coefficient_pavement": 3.64 * 0.7,
                "Embodied_Water_Coefficient_pavement": 5.18 * 0.7,
                "replacement_factor_pavement": 0.0,
                "PKT_million_60_years": 8.2
            },
            "Bicycle_path_Concrete": {
                "layers": [
                    {"pavement_material": "Concrete_25_MPA_30pct_SCM", "thickness_m": 0.125},
                    {"material": "Crushed_Rock", "thickness_m": 0.075},
                    {"material": "Recycled_aggregate", "thickness_m": 0.05}
                ],
                "replacement_factor": 1,
                "Operational_GHG_(kgCO2e/No)": 0,
                "Operational_Energy_(MJ/No)": 0,
                "Operational_Water_(L/No)": 0,
                "Embodied_GHG_Coefficient_pavement": 0.336 * 0.7,
                "Embodied_Energy_Coefficient_pavement": 3.64 * 0.7,
                "Embodied_Water_Coefficient_pavement": 5.18 * 0.7,
                "replacement_factor_pavement": 0.0,
                "PKT_million_60_years": 11.4
            },
            "CSR_Trench_Type_A_1km": {
                "layers": [
                {"pavement_material": "Concrete_25_MPA", "thickness_m": 0.00},
                    {"material": "Crushed_Rock", "thickness_m": 0.282},
                    {"material": "Sand", "thickness_m": 0.031},
                    {"material": "PE_Pipe_HDPE", "thickness_m": 0.02}
                ],
                "replacement_factor": 1,
                "Operational_GHG_(kgCO2e/No)": 0,
                "Operational_Energy_(MJ/No)": 0,
                "Operational_Water_(L/No)": 0,
                                "Embodied_GHG_Coefficient_pavement": 0.336 * 0.7,
                "Embodied_Energy_Coefficient_pavement": 3.64 * 0.7,
                "Embodied_Water_Coefficient_pavement": 5.18 * 0.7,
                "replacement_factor_pavement": 0.0,
                "PKT_million_60_years": 192
            },
            "Drainage_Trench_RCP": {
                "layers": [
                {"pavement_material": "Concrete_25_MPA", "thickness_m": 0.00},
                    {"material": "Reinforced_Concrete_Pipe_RCP", "thickness_m": 0.15},
                    {"material": "Crushed_Rock", "thickness_m": 0.30}
                ],
                "replacement_factor": 1,
                "Operational_GHG_(kgCO2e/No)": 0,
                "Operational_Energy_(MJ/No)": 0,
                "Operational_Water_(L/No)": 0,
                                "Embodied_GHG_Coefficient_pavement": 0.336 * 0.7,
                "Embodied_Energy_Coefficient_pavement": 3.64 * 0.7,
                "Embodied_Water_Coefficient_pavement": 5.18 * 0.7,
                "replacement_factor_pavement": 0.0,
                "PKT_million_60_years": 192
            },
            "OHLE_Mast_Foundation_Assembly": {
                "layers": [
                {"pavement_material": "Concrete_25_MPA", "thickness_m": 0.00},
                    {"material": "Concrete_50_MPA_25pct_SCM", "thickness_m": 1.2},
                    {"material": "Steel_Reinforcing_Bar", "thickness_m": 0.25},
                    {"material": "Painting", "thickness_m": 0.0008}
                ],
                "replacement_factor": 1,
                "Operational_GHG_(kgCO2e/No)": 0,
                "Operational_Energy_(MJ/No)": 0,
                "Operational_Water_(L/No)": 0,
                                                "Embodied_GHG_Coefficient_pavement": 0.336 * 0.7,
                "Embodied_Energy_Coefficient_pavement": 3.64 * 0.7,
                "Embodied_Water_Coefficient_pavement": 5.18 * 0.7,
                "replacement_factor_pavement": 0.0,
                "PKT_million_60_years": 2850
            },
            "Demolish_Redundant_Footing": {
                "layers": [
                {"pavement_material": "Concrete_25_MPA", "thickness_m": 0.00},
                    {"material": "Concrete", "thickness_m": 1.0},
                    {"material": "Steel_Reinforcing_Bar", "thickness_m": 0.15}
                ],
                "replacement_factor": 1,
                "Operational_GHG_(kgCO2e/No)": 0,
                "Operational_Energy_(MJ/No)": 0,
                "Operational_Water_(L/No)": 0,
                                                "Embodied_GHG_Coefficient_pavement": 0.336 * 0.7,
                "Embodied_Energy_Coefficient_pavement": 3.64 * 0.7,
                "Embodied_Water_Coefficient_pavement": 5.18 * 0.7,
                "replacement_factor_pavement": 0.0,
                "PKT_million_60_years": 1
            },
            "Abutment_50MPa": {
    "layers": [
        {"pavement_material": "Concrete_25_MPA", "thickness_m": 0.00},
        {"material": "Concrete_50_MPA_25pct_SCM", "thickness_m": 1.0},
        {"material": "Steel_Reinforcing_Bar", "thickness_m": 0.25},
        {"material": "Painting", "thickness_m": 0.0008}
    ],
    "replacement_factor": 1,
    "Operational_GHG_(kgCO2e/No)": 0,
    "Operational_Energy_(MJ/No)": 0,
    "Operational_Water_(L/No)": 0
},
"Railway_Track_Classical_1km_150m3": {
    "layers": [
                {"pavement_material": "Steel", "thickness_m":  0.0132},
                    {"material": "Concrete_25_MPA", "thickness_m": 0.165},  # 0.464 × 1.689
                    {"material": "Crushed_Rock", "thickness_m": 1.43},
                    {"material": "Asphalt", "thickness_m": 0.0099},
                    {"material": "Steel_Reinforcing_Bar", "thickness_m": 0.0099}
                ],
                "replacement_factor": 1,
                "Operational_GHG_(kgCO2e/No)": 0,
                "Operational_Energy_(MJ/No)": 0,
                "Operational_Water_(L/No)": 0,
                "Embodied_GHG_Coefficient_pavement": 1.47,
                "Embodied_Energy_Coefficient_pavement": 23.8,
                "Embodied_Water_Coefficient_pavement": 26.3,
                "replacement_factor_pavement": 1,
                "PKT_million_60_years": 384
},
                        # ───────────────────────────────────────
            # 🇧🇪 BELGIAN RAILWAY ASSEMBLIES (per 1 meter of track)
            # ───────────────────────────────────────
            "BE_Single_Track_Classical_Ballast_1Km": {
                "layers": [
                {"pavement_material": "Steel", "thickness_m": 0.0152},
                    {"material": "Rail_Ballast_0_80", "thickness_m": 2.03},      # 35 cm ballast → 2.03 m³/m (5.8 m width × 0.35 m)
                    {"material": "Rail_Subballast_0_32", "thickness_m": 1.16},   # 20 cm sub-ballast → 5.8 × 0.20 = 1.16 m³/m
                    {"material": "Concrete_25_MPA", "thickness_m": 0.143},              # Sleepers (~0.143 m³/m)
                    {"material": "Steel", "thickness_m": 0}                 # Rails (60 kg/m → 0.0152 m³/m)
                ],
                "replacement_factor": 1,
                "Operational_GHG_(kgCO2e/No)": 0,
                "Operational_Energy_(MJ/No)": 0,
                "Operational_Water_(L/No)": 0,
                "Embodied_GHG_Coefficient_pavement": 1.47,
                "Embodied_Energy_Coefficient_pavement": 23.8,
                "Embodied_Water_Coefficient_pavement": 26.3,
                "replacement_factor_pavement": 1,
                "PKT_million_60_years": 192  # ISCA value for rail corridor
            },
            "BE_Single_Track_Asphalt_Bedding_1Km": {
                "layers": [
                {"pavement_material": "Steel", "thickness_m": 0.0152},
                    {"material": "Rail_Bedding_Asphalt", "thickness_m": 0.464},  # 8 cm asphalt → 5.8 × 0.08 = 0.464 m³/m
                    {"material": "Rail_Subballast_0_32", "thickness_m": 1.74},   # 30 cm sub-ballast → 5.8 × 0.30 = 1.74 m³/m
                    {"material": "Concrete_25_MPA", "thickness_m": 0.143},
                    {"material": "Steel", "thickness_m": 0.0}
                ],
                "replacement_factor": 1,
                "Operational_GHG_(kgCO2e/No)": 0,
                "Operational_Energy_(MJ/No)": 0,
                "Operational_Water_(L/No)": 0,
                "Embodied_GHG_Coefficient_pavement": 1.47,
                "Embodied_Energy_Coefficient_pavement": 23.8,
                "Embodied_Water_Coefficient_pavement": 26.3,
                "replacement_factor_pavement": 1,
                "PKT_million_60_years": 192
            },
            "BE_Double_Track_Classical_Ballast_1Km": {
                "layers": [
                {"pavement_material": "Steel", "thickness_m": 0.0308},
                    {"material": "Rail_Ballast_0_80", "thickness_m": 3.43},      # 2.03 × 1.689 ≈ 3.43
                    {"material": "Rail_Subballast_0_32", "thickness_m": 1.96},   # 1.16 × 1.689 ≈ 1.96
                    {"material": "Concrete", "thickness_m": 0.286},              # 2 tracks → 0.143 × 2
                    {"material": "Steel", "thickness_m": 0.0}                 # 2 tracks → 0.0154 * 2
                ],
                "replacement_factor": 1,
                "Operational_GHG_(kgCO2e/No)": 0,
                "Operational_Energy_(MJ/No)": 0,
                "Operational_Water_(L/No)": 0,
                "Embodied_GHG_Coefficient_pavement": 1.47,
                "Embodied_Energy_Coefficient_pavement": 23.8,
                "Embodied_Water_Coefficient_pavement": 26.3,
                "replacement_factor_pavement": 1,
                "PKT_million_60_years": 384  # Approx. double single track
            },
            "BE_Double_Track_Asphalt_Bedding_1Km": {
                "layers": [
                {"pavement_material": "Steel", "thickness_m": 00.0308},
                    {"material": "Rail_Bedding_Asphalt", "thickness_m": 0.784},  # 0.464 × 1.689
                    {"material": "Rail_Subballast_0_32", "thickness_m": 2.94},   # 1.74 × 1.689
                    {"material": "Concrete_25_MPA", "thickness_m": 0.286},
                    {"material": "Steel", "thickness_m": 0.0}
                ],
                "replacement_factor": 1,
                "Operational_GHG_(kgCO2e/No)": 0,
                "Operational_Energy_(MJ/No)": 0,
                "Operational_Water_(L/No)": 0,
                "Embodied_GHG_Coefficient_pavement": 1.47,
                "Embodied_Energy_Coefficient_pavement": 23.8,
                "Embodied_Water_Coefficient_pavement": 26.3,
                "replacement_factor_pavement": 1,
                "PKT_million_60_years": 384
            },
            
                                    # ───────────────────────────────────────
            # 🇧🇪 Moreland station
            # ───────────────────────────────────────
               "MorelandStation_Structure_520m3_No": {
        "description": "Aggregated Station Structure (Lifts, Slabs, Coping, and Steel Frames) - based on combined concrete and structural steel quantities. Thickness represents volume fraction within the 1m³ structure unit.",
        "layers": [{"pavement_material": "Painting", "thickness_m": 0.001},
            {
                "material": "Concrete", 
                "thickness_m": 0.9054, 
                "note": "Aggregated volume of 32MPa, 40MPa, and 50MPa mixes (includes SCM mixes)."
            },
            {
                "material": "Steel_Reinforcing_Bar", 
                "thickness_m": 0.0546, 
                "note": "Aggregated volume of Rebar and Structural Steel (Plates, Sections, etc.)."
            }
        ],
        "replacement_factor": 1.0,
        "Operational_GHG_(kgCO2e/No)": 0,
        "Operational_Energy_(MJ/No)": 0,
        "Operational_Water_(L/No)": 0,
                        "replacement_factor": 1,
                "Operational_GHG_(kgCO2e/No)": 0,
                "Operational_Energy_(MJ/No)": 0,
                "Operational_Water_(L/No)": 0,
                "Embodied_GHG_Coefficient_pavement": 1.47,
                "Embodied_Energy_Coefficient_pavement": 23.8,
                "Embodied_Water_Coefficient_pavement": 26.3,
                "replacement_factor_pavement": 1,
                "PKT_million_60_years": 384
    },
                                                # ───────────────────────────────────────
            # 🇧🇪 Coburg station
            # ───────────────────────────────────────
                "CoburgStation_Structure_1541m3_No": {
        "description": "Aggregated Station Structure (Platform, Concourse, Footings, and Steel Framing) - based on combined concrete, hot-mix asphalt, and structural/reinforcement steel quantities. Thickness represents volume fraction within the 1m³ structure unit (Total estimated volume: 1541.01 m³).",
        "layers": [{"pavement_material": "Painting", "thickness_m": 0.001},
            {
                "material": "Concrete", 
                "thickness_m": 1.3, 
                "note": "Aggregated volume of all 20, 32, 40, and 50 MPa mixes (1288.92 m³ total volume)."
            },
            {
                "material": "Asphalt", 
                "thickness_m": 0.19, 
                "note": "Aggregated volume of Platform Hot Mix Asphalt (189.32 m³ total volume)."
            },
            {
                "material": "Steel_Reinforcing_Bar", 
                "thickness_m": 0.063, 
                "note": "Aggregated volume of Structural Steel and Rebar (492.78 t total mass, converted to 62.77 m³ volume @ 7850 kg/m³)."
            }
        ],
                "replacement_factor": 1,
                "Operational_GHG_(kgCO2e/No)": 0,
                "Operational_Energy_(MJ/No)": 0,
                "Operational_Water_(L/No)": 0,
                "Embodied_GHG_Coefficient_pavement": 1.47,
                "Embodied_Energy_Coefficient_pavement": 23.8,
                "Embodied_Water_Coefficient_pavement": 26.3,
                "replacement_factor_pavement": 1,
                "PKT_million_60_years": 384
    }
        }


        for assembly_name, assembly_data in assemblies.items():
            total_ghg = total_energy = total_water = total_mass = 0
            replacement_factor = assembly_data.get("replacement_factor", 1)
            PKT = assembly_data.get("PKT_million_60_years", 1)

            material_masses = {
                "Concrete and plaster products": 0,
                "Plastics": 0,
                "Metals": 0,
                "Miscellaneous": 0,
                "Sand, stone and ceramics": 0,
                "Timber": 0,
                "Glass": 0,
                "Insulation": 0
            }

            category_ghg = {cat: 0 for cat in material_masses}
            category_energy = {cat: 0 for cat in material_masses}
            category_water = {cat: 0 for cat in material_masses}

            maintenance_ghg = {cat: 0 for cat in material_masses}
            maintenance_energy = {cat: 0 for cat in material_masses}
            maintenance_water = {cat: 0 for cat in material_masses}

            for layer in assembly_data["layers"]:
                material = layer.get("material", layer.get("pavement_material"))
                thickness_m = layer["thickness_m"]
                ghg, energy, water, mass = self.calculate_embodied_metrics(material, thickness_m)

                total_ghg += ghg
                total_energy += energy
                total_water += water
                total_mass += mass

                category = next((mat["Categories"] for mat in MATERIAL_DATA if mat["Material"] == material), None)
                if category:
                    material_masses[category] += mass
                    category_ghg[category] += ghg
                    category_energy[category] += energy
                    category_water[category] += water

            for cat in material_masses:
                category_ghg[cat] *= replacement_factor
                category_energy[cat] *= replacement_factor
                category_water[cat] *= replacement_factor

            total_ghg = sum(category_ghg.values())
            total_energy = sum(category_energy.values())
            total_water = sum(category_water.values())

            pavement_material = None
            for layer in assembly_data["layers"]:
                if "pavement_material" in layer:
                    pavement_material = layer["pavement_material"]
                    break
            if not pavement_material:
                raise ValueError("Pavement material not defined for %s" % assembly_name)

            pavement_mass = 0
            for layer in assembly_data["layers"]:
                material = layer.get("material", layer.get("pavement_material"))
                if material == pavement_material:
                    _, _, _, mass = self.calculate_embodied_metrics(material, layer["thickness_m"])
                    pavement_mass += mass

            emb_ghg_coeff = assembly_data.get("Embodied_GHG_Coefficient_pavement", 0)
            emb_energy_coeff = assembly_data.get("Embodied_Energy_Coefficient_pavement", 0)
            emb_water_coeff = assembly_data.get("Embodied_Water_Coefficient_pavement", 0)
            rep_factor_pavement = assembly_data.get("replacement_factor_pavement", 0)

            maintenance_mass = rep_factor_pavement * pavement_mass
            maintenance_ghg_val = rep_factor_pavement * pavement_mass * emb_ghg_coeff * 1000
            maintenance_energy_val = rep_factor_pavement * pavement_mass * emb_energy_coeff
            maintenance_water_val = rep_factor_pavement * pavement_mass * emb_water_coeff

            pavement_category = next((mat["Categories"] for mat in MATERIAL_DATA if mat["Material"] == pavement_material), None)
            if pavement_category:
                maintenance_ghg[pavement_category] = maintenance_ghg_val
                maintenance_energy[pavement_category] = maintenance_energy_val
                maintenance_water[pavement_category] = maintenance_water_val

            self.assembly_db[assembly_name] = {
                "Initial_Embodied_GHG_(kgCO2e)": total_ghg,
                "Initial_Embodied_Energy_(MJ)": total_energy,
                "Initial_Embodied_Water_(L)": total_water,
                "Total_Mass_(kg)": total_mass,
                "Maintenance_Mass_(kg)": maintenance_mass,
                "Maintenance_Embodied_GHG_(kgCO2e)": maintenance_ghg_val,
                "Maintenance_Embodied_Energy_(MJ)": maintenance_energy_val,
                "Maintenance_Embodied_Water_(L)": maintenance_water_val,

                "Concrete and plaster products_Mass_(kg)": material_masses["Concrete and plaster products"],
                "Plastics_Mass_(kg)": material_masses["Plastics"],
                "Metals_Mass_(kg)": material_masses["Metals"],
                "Miscellaneous_Mass_(kg)": material_masses["Miscellaneous"],
                "Sand, stone and ceramics_Mass_(kg)": material_masses["Sand, stone and ceramics"],
                "Timber_Mass_(kg)": material_masses["Timber"],
                "Glass_Mass_(kg)": material_masses["Glass"],
                "Insulation_Mass_(kg)": material_masses["Insulation"],

                "Concrete and plaster products_Initial_Embodied_GHG_(kgCO2e)": category_ghg["Concrete and plaster products"],
                "Plastics_Initial_Embodied_GHG_(kgCO2e)": category_ghg["Plastics"],
                "Metals_Initial_Embodied_GHG_(kgCO2e)": category_ghg["Metals"],
                "Miscellaneous_Initial_Embodied_GHG_(kgCO2e)": category_ghg["Miscellaneous"],
                "Sand, stone and ceramics_Initial_Embodied_GHG_(kgCO2e)": category_ghg["Sand, stone and ceramics"],
                "Timber_Initial_Embodied_GHG_(kgCO2e)": category_ghg["Timber"],
                "Glass_Initial_Embodied_GHG_(kgCO2e)": category_ghg["Glass"],
                "Insulation_Initial_Embodied_GHG_(kgCO2e)": category_ghg["Insulation"],

                "Concrete and plaster products_Maintenance_Embodied_GHG_(kgCO2e)": maintenance_ghg["Concrete and plaster products"],
                "Plastics_Maintenance_Embodied_GHG_(kgCO2e)": maintenance_ghg["Plastics"],
                "Metals_Maintenance_Embodied_GHG_(kgCO2e)": maintenance_ghg["Metals"],
                "Miscellaneous_Maintenance_Embodied_GHG_(kgCO2e)": maintenance_ghg["Miscellaneous"],
                "Sand, stone and ceramics_Maintenance_Embodied_GHG_(kgCO2e)": maintenance_ghg["Sand, stone and ceramics"],
                "Timber_Maintenance_Embodied_GHG_(kgCO2e)": maintenance_ghg["Timber"],
                "Glass_Maintenance_Embodied_GHG_(kgCO2e)": maintenance_ghg["Glass"],
                "Insulation_Maintenance_Embodied_GHG_(kgCO2e)": maintenance_ghg["Insulation"],

                # Category breakdowns - Initial Energy
                "Concrete and plaster products_Initial_Embodied_energy_(MJ)": category_energy["Concrete and plaster products"],
                "Plastics_Initial_Embodied_energy_(MJ)": category_energy["Plastics"],
                "Metals_Initial_Embodied_energy_(MJ)": category_energy["Metals"],
                "Miscellaneous_Initial_Embodied_energy_(MJ)": category_energy["Miscellaneous"],
                "Sand, stone and ceramics_Initial_Embodied_energy_(MJ)": category_energy["Sand, stone and ceramics"],
                "Glass_Initial_Embodied_energy_(MJ)": category_energy["Glass"],
                "Timber_Initial_Embodied_energy_(MJ)": category_energy["Timber"],
                "Insulation_Initial_Embodied_energy_(MJ)": category_energy["Insulation"],
                # ... (add all other categories similarly)
                # Category breakdowns - Maintenance Energy
                "Concrete and plaster products_Maintenance_Embodied_energy_(MJ)": maintenance_energy["Concrete and plaster products"],
                "Plastics_Maintenance_Embodied_energy_(MJ)": maintenance_energy["Plastics"],
                "Metals_Maintenance_Embodied_energy_(MJ)": maintenance_energy["Metals"],
                "Miscellaneous_Maintenance_Embodied_energy_(MJ)": maintenance_energy["Miscellaneous"],
                "Sand, stone and ceramics_Maintenance_Embodied_energy_(MJ)": maintenance_energy["Sand, stone and ceramics"],
                "Glass_Maintenance_Embodied_energy_(MJ)": maintenance_energy["Glass"],
                "Timber_Maintenance_Embodied_energy_(MJ)": maintenance_energy["Timber"],
                "Insulation_Maintenance_Embodied_energy_(MJ)": maintenance_energy["Insulation"],
                # Category breakdowns - Initial Water
                "Concrete and plaster products_Initial_embodied_water_(L)": category_water["Concrete and plaster products"],
                "Plastics_Initial_Embodied_water_(L)": category_water["Plastics"],
                "Metals_Initial_Embodied_water_(L)": category_water["Metals"],
                "Miscellaneous_Initial_Embodied_water_(L)": category_water["Miscellaneous"],
                "Sand, stone and ceramics_Initial_Embodied_water_(L)": category_water["Sand, stone and ceramics"],
                "Glass_Initial_Embodied_water_(L)": category_water["Glass"],
                "Timber_Initial_Embodied_water_(L)": category_water["Timber"],
                "Insulation_Initial_Embodied_water_(L)": category_water["Insulation"],
                # ... (add all other categories similarly)
                # Category breakdowns - Maintenance Water
                "Concrete and plaster products_Maintenance_Embodied_Water_(L)": maintenance_water["Concrete and plaster products"],
                "Plastics_Maintenance_Embodied_Water_(L)": maintenance_water["Plastics"],
                "Metals_Maintenance_Embodied_Water_(L)": maintenance_water["Metals"],
                "Miscellaneous_Maintenance_Embodied_Water_(L)": maintenance_water["Miscellaneous"],
                "Sand, stone and ceramics_Maintenance_Embodied_Water_(L)": maintenance_water["Sand, stone and ceramics"],
                "Glass_Maintenance_Embodied_Water_(L)": maintenance_water["Glass"],
                "Timber_Maintenance_Embodied_Water_(L)": maintenance_water["Timber"],
                "Insulation_Maintenance_Embodied_Water_(L)": maintenance_water["Insulation"],
                "Operational_GHG_(kgCO2e/No)": assembly_data["Operational_GHG_(kgCO2e/No)"],
                "Operational_Energy_(MJ/No)": assembly_data["Operational_Energy_(MJ/No)"],
                "Operational_Water_(L/No)": assembly_data["Operational_Water_(L/No)"],
                "PKT_million_60_years": PKT
            }

    def print_assembly_db(self):
        print("Assembly Database:")
        for assembly_name, metrics in self.assembly_db.items():
            print("%s: %s" % (assembly_name, str(metrics)))

class InfrastructureDatabase(object):
    def __init__(self, assembly_db):
        self.assembly_db = assembly_db
        self.infrastructure_db = {}

    def populate_infrastructure_db(self):
        highways = ["Concrete_Highway", "Asphalt_Highway"]
        for highway in highways:
            assembly_data = self.assembly_db.assembly_db.get(highway, {})
            replacement_factor = 2
            total_ghg = assembly_data.get("Initial_Embodied_GHG_(kgCO2e)", 0) * replacement_factor
            total_energy = assembly_data.get("Initial_Embodied_Energy_(MJ)", 0) * replacement_factor
            total_water = assembly_data.get("Initial_Embodied_Water_(L)", 0) * replacement_factor

            self.infrastructure_db[highway] = {
                "Initial_Embodied_GHG_(kgCO2e)": total_ghg,
                "Initial_Embodied_Energy_(MJ)": total_energy,
                "Initial_Embodied_Water_(L)": total_water
            }

    def print_infrastructure_db(self):
        print("Infrastructure Database:")
        for key, value in self.infrastructure_db.items():
            print(str(key) + ": " + str(value))


# Instantiate and populate Material Database
material_db = MaterialDatabase()
material_db.print_material_db()

# Instantiate and populate Element Database
element_db = ElementDatabase(material_db.material_db)
element_db.populate_elements()
element_db.print_element_db()

# Instantiate and populate Assembly Database
assembly_db = AssemblyDatabase(material_db.material_db)
assembly_db.populate_assemblies()
assembly_db.print_assembly_db()

# Instantiate and populate Infrastructure Database
infrastructure_db = InfrastructureDatabase(assembly_db)
infrastructure_db.populate_infrastructure_db()
infrastructure_db.print_infrastructure_db()