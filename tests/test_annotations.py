# Copyright (c) 2024, Plinder Development Team
# Distributed under the terms of the Apache License 2.0
import shutil
import requests
from io import StringIO

from pathlib import Path
import pytest
import gemmi
from biotite import structure as struc
from biotite.structure.io.pdbx import PDBxFile, get_structure
from rdkit import Chem
import numpy as np
import pandas as pd
from collections import Counter
import tempfile

from plinder.data.utils.annotations.interface_gap import annotate_interface_gaps
from plinder.data.structure.atoms import (
    add_hydrogen_to_lig_array,
    extract_bsite_metal,
    extract_bsite_water,
    get_morgan_fingerprint,
)
from plinder.data.utils.annotations.interface_gap import annotate_interface_gaps
from plinder.data.utils.annotations.aggregate_annotations import Entry
from plinder.data.utils.annotations.protein_utils import read_mmcif_container
from plinder.data.utils.annotations.interaction_utils import get_covalent_connections
from plinder.data.utils.annotations.ligand_utils import get_smiles_from_cif
from plinder.data.utils.annotations.extras import (
    add_extra_loop_to_bioassembly,
    convert_chain,
    extract_rcsb_info,
    extract_rdk_mol_from_cif,
    extract_small_mol_entities,
    generate_bio_assembly,
    get_all_bound_molecules,
    get_chain_mapping,
    get_ec,
    get_entity_type,
    get_selected_residues_pdb_block,
    get_specific_bound_molecules,
    read_mmcif_file,
    sequence_mapping,
)
from plinder.data.utils.annotations.interface_gap import annotate_interface_gaps
from plinder.data.utils.annotations.mmpdb_utils import add_mmp_clusters_to_data
from plinder.data.get_system_annotations import GetPlinderAnnotation
from plinder.data.utils.annotations.extras import sort_ccd_codes



@pytest.fixture(autouse=True)
def mock_ccd_lookups(monkeypatch):
    monkeypatch.setattr(
        "plinder.data.utils.annotations.ligand_utils.LIST_OF_CCD_SYNONYMS",
        [{'B1F', 'B2F'}, {'OY5', 'OY8'}, {'N1B', '4LA'}, {'C2H', 'ETD'}, {'FMT', 'CBX'}, {'NFO', 'NFB'}, {'MBR', 'B4M'}, {'PGH', 'PGC'}, {'BXA', 'BRM'}, {'2PL', 'PGA'}, {'CRY', 'GOL'}, {'VKN', 'YLL'}, {'VDW', '0P0', 'GTT'}, {'AKG', '2OG'}, {'GGL', 'GLU'}, {'FGA', 'DGL'}, {'ACA', 'AHA'}, {'GCG', 'TS3'}, {'HPG', 'PDO'}, {'148', 'BTB'}, {'EDO', 'EGL'}, {'PIG', 'PGE'}, {'P2K', 'P6G'}, {'SEA', 'DHL'}, {'BME', 'SEO'}, {'CS0', 'OCY'}, {'DHN', 'AA4'}, {'ABK', 'FKI'}, {'ASP', 'IAS'}, {'PAS', 'PHD', 'ASQ'}, {'SER', 'SEG'}, {'BTC', 'FCY', 'CYS'}, {'CAY', 'CCS'}, {'CSO', 'CEA'}, {'CSE', 'SEC'}, {'ICT', 'ICI'}, {'GLR', 'KGR'}, {'GAL', 'GLB'}, {'G4S', 'GSA'}, {'Z4Y', 'TWG'}, {'GS4', 'SGC', 'GSD'}, {'SGN', 'YJM'}, {'AGC', 'GLC'}, {'ADG', 'TOA'}, {'NT2', 'GU4'}, {'L1L', 'GP1'}, {'BFP', 'FBP'}, {'I8Z', 'I9X'}, {'HSU', 'BDR'}, {'RDP', 'R1P'}, {'HNP', 'H5P'}, {'DSP', 'DAS'}, {'DMR', 'MLT'}, {'3PG', 'MP3'}, {'PAG', '2PG'}, {'GPH', 'GPO', '0AL'}, {'R51', 'R52'}, {'PA4', 'IDG'}, {'KPI', 'MCL'}, {'EUG', 'H7Y'}, {'2H3', 'CBU', 'INS'}, {'I6P', 'IHP', 'KGN'}, {'GUR', 'GLL'}, {'0AU', 'IU'}, {'GCD', 'DGC'}, {'CYL', 'ACI', 'CMN'}, {'TZA', 'ACZ'}, {'LC', '0C'}, {'C', 'C25', 'C5P'}, {'0U', 'LHU'}, {'2AU', 'U2N'}, {'U', 'U25', 'U5P'}, {'U37', 'T31'}, {'S4U', '4SU'}, {'PH2', 'HHP'}, {'PCA', '5HP', 'PCC'}, {'HAC', 'ALC'}, {'CHG', 'CUC'}, {'H2U', 'DHU'}, {'DOX', 'DIO'}, {'DXD', 'DXN'}, {'ORP', 'D1P'}, {'C32', 'CBR'}, {'I5C', 'C38'}, {'5IU', '5IT'}, {'DCM', 'DC'}, {'C7S', 'C7R'}, {'DU', 'UMP'}, {'IGU', '0UH'}, {'B1P', 'AAB'}, {'MNM', 'NOZ'}, {'NOJ', 'DNJ'}, {'TSO', 'TSA', 'BAR'}, {'UYA', '0AZ'}, {'DFC', '0DC'}, {'HSZ', 'XYP'}, {'XYB', 'BXP'}, {'DDM', 'DMJ'}, {'FLH', 'FOR'}, {'PVL', 'MIE'}, {'LIN', 'AAE'}, {'3NK', 'LL8'}, {'CHH', 'NWB'}, {'GCM', 'GLM', 'F3V'}, {'CNM', 'ACM'}, {'1ZT', 'SC2'}, {'YYR', 'RTV'}, {'SIA', 'SI2', 'NAN'}, {'7BN', '7BO'}, {'16G', '0AT'}, {'NAG', 'HSR'}, {'1NA', 'MAG'}, {'NGL', 'ASG'}, {'5G0', 'OGN'}, {'TYL', 'NNS'}, {'ACY', 'CM', 'CBM'}, {'CKC', 'LYM'}, {'OTB', 'BOC'}, {'BUG', 'TBG', 'HV5'}, {'ISB', 'ALQ'}, {'FPG', 'F3P'}, {'UIC', 'GRL'}, {'CLE', 'NLW'}, {'LEP', '0FA'}, {'YLV', 'YM1'}, {'YKA', 'YKD'}, {'YKY', 'YL7'}, {'YMD', 'YMG'}, {'YMS', 'YMV'}, {'Y8Y', 'Y91'}, {'Y51', 'Y71'}, {'Y7G', 'Y4P'}, {'YLD', 'YLJ'}, {'YKS', 'YKV'}, {'OLE', '1LU'}, {'XAO', 'GCL'}, {'HMP', 'HMI'}, {'PLH', 'HAP'}, {'PLU', 'PLE'}, {'BAT', 'DSX'}, {'CCK', 'ATW'}, {'IPA', 'IOH'}, {'ISP', 'MIP'}, {'VME', '0AA'}, {'CPV', 'VAS'}, {'961', '395'}, {'HIE', 'E0G'}, {'MQ7', '7MQ'}, {'REA', '3KV'}, {'RAW', 'ECH'}, {'45H', '45D'}, {'DRB', 'LRB'}, {'RFB', 'RFA'}, {'5PY', 'T36'}, {'LCH', 'LCC'}, {'DRT', '0DT'}, {'HDP', 'XTR'}, {'T0N', 'T0Q'}, {'NYM', 'T37'}, {'TMP', 'DT', 'T'}, {'THP', 'PTP'}, {'PST', 'TS'}, {'5MU', 'RT'}, {'U18', 'F89'}, {'BJ5', '0UE'}, {'4JU', '2MH'}, {'MCB', 'ACE', 'ACU'}, {'YI2', '5YI'}, {'CL1', 'CL2'}, {'CBG', 'PNL'}, {'NBU', 'BUT', 'SBU'}, {'NP6', 'BA4'}, {'YMY', 'YN1'}, {'YMM', 'YMJ'}, {'PEI', 'LEA'}, {'CRC', 'DKA'}, {'LAU', 'DAO'}, {'PLM', 'FAT'}, {'3PH', '2SP'}, {'QEH', 'LP3'}, {'C8E', 'OTE'}, {'OLA', 'OLI'}, {'HQ', 'HQO'}, {'13H', '243'}, {'LYW', 'EJM'}, {'1ZD', '2NC'}, {'0AM', '0SP'}, {'2PI', 'RON', 'NVA', 'BTA'}, {'EOX', 'EOH', 'OHE'}, {'P3G', '6JZ'}, {'XL1', 'SCC'}, {'ITU', 'SEU'}, {'1NI', 'LP2', 'LP1'}, {'ABA', 'AB7'}, {'CHC', 'IU6'}, {'DCI', 'MBA'}, {'0EZ', 'PI6'}, {'INY', 'CRP'}, {'T0M', 'EMT'}, {'NET', 'E4N'}, {'F22', 'HXA'}, {'GXJ', 'I0E'}, {'PYJ', 'N2B'}, {'NC', 'NME'}, {'MLY', 'TRG'}, {'R5A', 'R5B'}, {'3MU', 'UR3'}, {'VSB', 'VSE'}, {'PTC', 'AY0'}, {'M4C', '4OC'}, {'SAR', 'MGY'}, {'YNM', 'N9K'}, {'A34', '6MC', '6MA', '6MT'}, {'A35', 'A40'}, {'6OO', 'OKQ'}, {'A2M', '0AV', 'A39'}, {'MMA', 'MAM'}, {'MGA', 'MBG'}, {'G32', '6OG'}, {'1CR', '0CR'}, {'3DQ', '9ZT'}, {'ROL', '4RR', '4SR'}, {'1IS', '1IR'}, {'GB', 'PPM'}, {'577', 'IIM'}, {'CYM', 'SMC'}, {'K7J', '0ZO'}, {'PIA', 'AYG'}, {'CRW', 'MDO'}, {'YKP', 'YKM'}, {'WLD', 'WH7'}, {'PGO', 'PGQ'}, {'HBL', 'HBI'}, {'BH4', 'THB', 'H4B'}, {'98', '986'}, {'PYL', 'PYH'}, {'JRC', 'JQL'}, {'KOL', 'MER'}, {'1GL', 'BRI'}, {'6CT', 'T32'}, {'MEP', 'T23'}, {'AGL', 'RV7'}, {'G6D', 'GLW'}, {'ARE', '5SA'}, {'DDB', 'MDA'}, {'53P', '5P8', 'QB4'}, {'STO', 'STU'}, {'INH', '8MI'}, {'DLA', 'LAC'}, {'AMV', 'MMR'}, {'DHO', 'DXC'}, {'HP3', 'PGR'}, {'HPB', 'PR0'}, {'TRB', 'TB9'}, {'RAA', 'RAM'}, {'MFU', 'MFA'}, {'FUL', 'AFL'}, {'SAA', 'APG'}, {'OET', 'ETH'}, {'HGC', 'MMC'}, {'POC', 'PC'}, {'MOT', 'COE'}, {'SOM', 'MPS'}, {'TTH', 'GER'}, {'TBM', 'TMB'}, {'PDL', 'PP3'}, {'PLA', 'AMA'}, {'THQ', 'TZP'}, {'RIC', 'RBZ'}, {'MDI', 'N0U'}, {'MJQ', '6LX'}, {'RNY', 'AQZ'}, {'267', '263'}, {'NEV', 'NVP', 'NIV'}, {'PYD', 'YF1'}, {'G33', '8MG'}, {'0SN', '88N'}, {'7CP', 'MB0'}, {'HIC', 'MH1', 'NEM'}, {'HDZ', 'TFH'}, {'QTR', 'OXO', 'HOH', 'DIS', 'O', 'OX', 'MTO'}, {'FEO', 'F2O'}, {'O2', 'OXY'}, {'2MO', 'MM4'}, {'PI', 'IPS'}, {'S', 'H2S'}, {'BRO', 'BR'}, {'IDS', '2SI'}, {'BHD', 'DOH'}, {'UEV', 'I7P'}, {'CLO', 'CL'}, {'FLO', 'F'}, {'MH6', 'SRI'}, {'672', 'Q72'}, {'YJC', '424'}, {'1MA', 'MAD'}, {'IDO', 'IOD'}, {'NH4', 'NGN'}, {'NMO', 'NO'}, {'SUL', 'SO4'}, {'HYD', 'OH'}, {'B51', 'WCC'}, {'ZN', 'ZN2'}, {'FIB', 'IBF'}, {'PGS', 'SPG'}, {'ANE', 'ADE'}, {'PCQ', 'NEW'}, {'EGG', 'KDH'}, {'G1Z', 'G1T'}, {'B7D', 'TRU'}, {'P5P', 'PR5'}, {'9HE', 'KS1'}, {'DHY', 'HAA'}, {'TY3', 'DAH'}, {'LNR', 'LT4'}, {'NAH', 'NAD'}, {'MTY', 'EHP'}, {'PIX', 'TF6'}, {'CSY', 'GYS'}, {'FA', 'FOL'}, {'TYS', 'STY'}, {'YAP', '69X'}, {'CBP', '345'}, {'GHP', 'DGH', 'NTY'}, {'CR2', 'CQR'}, {'WAK', 'WB8'}, {'KSB', 'QHL'}, {'BPC', 'BP', 'BAP'}, {'6AB', 'BE2'}, {'L0H', 'L0F'}, {'BEZ', 'BOX'}, {'FSL', 'F9V'}, {'PPY', '1PY'}, {'P6S', 'BGG'}, {'CBZ', 'BZO'}, {'PMS', 'IOX'}, {'PHM', 'PCS'}, {'LLA', 'LOF', 'HFA'}, {'TPH', 'HPH'}, {'PUK', 'FRF'}, {'0AC', 'FOG'}, {'638', 'XV6'}, {'BIC', 'MOL'}, {'D8W', '3DB'}, {'PGY', 'PG9'}, {'119', 'P4P'}, {'86Q', 'DRG'}, {'89E', 'LIG'}, {'GPR', 'CYP'}, {'URY', 'K0I'}, {'TRP', 'LTR'}, {'V7F', 'V70'}, {'QNC', 'QND'}, {'0TN', 'RKP'}, {'QX', 'QUI'}, {'AC4', 'AMZ'}, {'D5M', 'DA'}, {'A', 'AMP'}, {'0DG', 'DFG'}, {'LG', '0G'}, {'DCG', 'DGP', 'DG'}, {'DI', 'OIP'}, {'5GP', 'G25', 'G', 'CPG'}, {'IMP', 'I'}, {'GTO', 'GCP'}, {'GNP', 'GTN'}],
    )
    monkeypatch.setattr(
        "plinder.data.utils.annotations.ligand_utils.CCD_SYNONYMS_DICT",
        {'B1F': 'B1F', 'B2F': 'B1F', 'OY5': 'OY5', 'OY8': 'OY5', '4LA': 'N1B', 'N1B': 'N1B', 'C2H': 'C2H', 'ETD': 'C2H', 'CBX': 'CBX', 'FMT': 'CBX', 'NFB': 'NFB', 'NFO': 'NFB', 'B4M': 'B4M', 'MBR': 'B4M', 'PGC': 'PGC', 'PGH': 'PGC', 'BRM': 'BRM', 'BXA': 'BRM', '2PL': 'PGA', 'PGA': 'PGA', 'CRY': 'CRY', 'GOL': 'CRY', 'VKN': 'VKN', 'YLL': 'VKN', '0P0': 'GTT', 'GTT': 'GTT', 'VDW': 'GTT', '2OG': 'AKG', 'AKG': 'AKG', 'GGL': 'GGL', 'GLU': 'GGL', 'DGL': 'DGL', 'FGA': 'DGL', 'ACA': 'ACA', 'AHA': 'ACA', 'GCG': 'GCG', 'TS3': 'GCG', 'HPG': 'HPG', 'PDO': 'HPG', '148': 'BTB', 'BTB': 'BTB', 'EDO': 'EDO', 'EGL': 'EDO', 'PGE': 'PGE', 'PIG': 'PGE', 'P2K': 'P2K', 'P6G': 'P2K', 'DHL': 'DHL', 'SEA': 'DHL', 'BME': 'BME', 'SEO': 'BME', 'CS0': 'CS0', 'OCY': 'CS0', 'AA4': 'AA4', 'DHN': 'AA4', 'ABK': 'ABK', 'FKI': 'ABK', 'ASP': 'ASP', 'IAS': 'ASP', 'ASQ': 'ASQ', 'PAS': 'ASQ', 'PHD': 'ASQ', 'SEG': 'SEG', 'SER': 'SEG', 'BTC': 'BTC', 'CYS': 'BTC', 'FCY': 'BTC', 'CAY': 'CAY', 'CCS': 'CAY', 'CEA': 'CEA', 'CSO': 'CEA', 'CSE': 'CSE', 'SEC': 'CSE', 'ICI': 'ICI', 'ICT': 'ICI', 'GLR': 'GLR', 'KGR': 'GLR', 'GAL': 'GAL', 'GLB': 'GAL', 'G4S': 'G4S', 'GSA': 'G4S', 'TWG': 'TWG', 'Z4Y': 'TWG', 'GS4': 'GS4', 'GSD': 'GS4', 'SGC': 'GS4', 'SGN': 'SGN', 'YJM': 'SGN', 'AGC': 'AGC', 'GLC': 'AGC', 'ADG': 'ADG', 'TOA': 'ADG', 'GU4': 'GU4', 'NT2': 'GU4', 'GP1': 'GP1', 'L1L': 'GP1', 'BFP': 'BFP', 'FBP': 'BFP', 'I8Z': 'I8Z', 'I9X': 'I8Z', 'BDR': 'BDR', 'HSU': 'BDR', 'R1P': 'R1P', 'RDP': 'R1P', 'H5P': 'H5P', 'HNP': 'H5P', 'DAS': 'DAS', 'DSP': 'DAS', 'DMR': 'DMR', 'MLT': 'DMR', '3PG': 'MP3', 'MP3': 'MP3', '2PG': 'PAG', 'PAG': 'PAG', '0AL': 'GPH', 'GPH': 'GPH', 'GPO': 'GPH', 'R51': 'R51', 'R52': 'R51', 'IDG': 'IDG', 'PA4': 'IDG', 'KPI': 'KPI', 'MCL': 'KPI', 'EUG': 'EUG', 'H7Y': 'EUG', '2H3': 'CBU', 'CBU': 'CBU', 'INS': 'CBU', 'I6P': 'I6P', 'IHP': 'I6P', 'KGN': 'I6P', 'GLL': 'GLL', 'GUR': 'GLL', '0AU': 'IU', 'IU': 'IU', 'DGC': 'DGC', 'GCD': 'DGC', 'ACI': 'ACI', 'CMN': 'ACI', 'CYL': 'ACI', 'ACZ': 'ACZ', 'TZA': 'ACZ', '0C': 'LC', 'LC': 'LC', 'C': 'C25', 'C25': 'C25', 'C5P': 'C25', '0U': 'LHU', 'LHU': 'LHU', '2AU': 'U2N', 'U2N': 'U2N', 'U': 'U25', 'U25': 'U25', 'U5P': 'U25', 'T31': 'T31', 'U37': 'T31', '4SU': 'S4U', 'S4U': 'S4U', 'HHP': 'HHP', 'PH2': 'HHP', '5HP': 'PCA', 'PCA': 'PCA', 'PCC': 'PCA', 'ALC': 'ALC', 'HAC': 'ALC', 'CHG': 'CHG', 'CUC': 'CHG', 'DHU': 'DHU', 'H2U': 'DHU', 'DIO': 'DIO', 'DOX': 'DIO', 'DXD': 'DXD', 'DXN': 'DXD', 'D1P': 'D1P', 'ORP': 'D1P', 'C32': 'C32', 'CBR': 'C32', 'C38': 'C38', 'I5C': 'C38', '5IT': '5IT', '5IU': '5IT', 'DC': 'DCM', 'DCM': 'DCM', 'C7R': 'C7R', 'C7S': 'C7R', 'DU': 'UMP', 'UMP': 'UMP', '0UH': 'IGU', 'IGU': 'IGU', 'AAB': 'AAB', 'B1P': 'AAB', 'MNM': 'MNM', 'NOZ': 'MNM', 'DNJ': 'DNJ', 'NOJ': 'DNJ', 'BAR': 'BAR', 'TSA': 'BAR', 'TSO': 'BAR', '0AZ': 'UYA', 'UYA': 'UYA', '0DC': 'DFC', 'DFC': 'DFC', 'HSZ': 'HSZ', 'XYP': 'HSZ', 'BXP': 'BXP', 'XYB': 'BXP', 'DDM': 'DDM', 'DMJ': 'DDM', 'FLH': 'FLH', 'FOR': 'FLH', 'MIE': 'MIE', 'PVL': 'MIE', 'AAE': 'AAE', 'LIN': 'AAE', '3NK': 'LL8', 'LL8': 'LL8', 'CHH': 'CHH', 'NWB': 'CHH', 'F3V': 'F3V', 'GCM': 'F3V', 'GLM': 'F3V', 'ACM': 'ACM', 'CNM': 'ACM', '1ZT': 'SC2', 'SC2': 'SC2', 'RTV': 'RTV', 'YYR': 'RTV', 'NAN': 'NAN', 'SI2': 'NAN', 'SIA': 'NAN', '7BN': '7BN', '7BO': '7BN', '0AT': '0AT', '16G': '0AT', 'HSR': 'HSR', 'NAG': 'HSR', '1NA': 'MAG', 'MAG': 'MAG', 'ASG': 'ASG', 'NGL': 'ASG', '5G0': 'OGN', 'OGN': 'OGN', 'NNS': 'NNS', 'TYL': 'NNS', 'ACY': 'ACY', 'CBM': 'ACY', 'CM': 'ACY', 'CKC': 'CKC', 'LYM': 'CKC', 'BOC': 'BOC', 'OTB': 'BOC', 'BUG': 'BUG', 'HV5': 'BUG', 'TBG': 'BUG', 'ALQ': 'ALQ', 'ISB': 'ALQ', 'F3P': 'F3P', 'FPG': 'F3P', 'GRL': 'GRL', 'UIC': 'GRL', 'CLE': 'CLE', 'NLW': 'CLE', '0FA': 'LEP', 'LEP': 'LEP', 'YLV': 'YLV', 'YM1': 'YLV', 'YKA': 'YKA', 'YKD': 'YKA', 'YKY': 'YKY', 'YL7': 'YKY', 'YMD': 'YMD', 'YMG': 'YMD', 'YMS': 'YMS', 'YMV': 'YMS', 'Y8Y': 'Y8Y', 'Y91': 'Y8Y', 'Y51': 'Y51', 'Y71': 'Y51', 'Y4P': 'Y4P', 'Y7G': 'Y4P', 'YLD': 'YLD', 'YLJ': 'YLD', 'YKS': 'YKS', 'YKV': 'YKS', '1LU': 'OLE', 'OLE': 'OLE', 'GCL': 'GCL', 'XAO': 'GCL', 'HMI': 'HMI', 'HMP': 'HMI', 'HAP': 'HAP', 'PLH': 'HAP', 'PLE': 'PLE', 'PLU': 'PLE', 'BAT': 'BAT', 'DSX': 'BAT', 'ATW': 'ATW', 'CCK': 'ATW', 'IOH': 'IOH', 'IPA': 'IOH', 'ISP': 'ISP', 'MIP': 'ISP', '0AA': 'VME', 'VME': 'VME', 'CPV': 'CPV', 'VAS': 'CPV', '395': '395', '961': '395', 'E0G': 'E0G', 'HIE': 'E0G', '7MQ': 'MQ7', 'MQ7': 'MQ7', '3KV': 'REA', 'REA': 'REA', 'ECH': 'ECH', 'RAW': 'ECH', '45D': '45D', '45H': '45D', 'DRB': 'DRB', 'LRB': 'DRB', 'RFA': 'RFA', 'RFB': 'RFA', '5PY': 'T36', 'T36': 'T36', 'LCC': 'LCC', 'LCH': 'LCC', '0DT': 'DRT', 'DRT': 'DRT', 'HDP': 'HDP', 'XTR': 'HDP', 'T0N': 'T0N', 'T0Q': 'T0N', 'NYM': 'NYM', 'T37': 'NYM', 'DT': 'TMP', 'T': 'TMP', 'TMP': 'TMP', 'PTP': 'PTP', 'THP': 'PTP', 'PST': 'PST', 'TS': 'PST', '5MU': 'RT', 'RT': 'RT', 'F89': 'F89', 'U18': 'F89', '0UE': 'BJ5', 'BJ5': 'BJ5', '2MH': '2MH', '4JU': '2MH', 'ACE': 'ACE', 'ACU': 'ACE', 'MCB': 'ACE', '5YI': 'YI2', 'YI2': 'YI2', 'CL1': 'CL1', 'CL2': 'CL1', 'CBG': 'CBG', 'PNL': 'CBG', 'BUT': 'BUT', 'NBU': 'BUT', 'SBU': 'BUT', 'BA4': 'BA4', 'NP6': 'BA4', 'YMY': 'YMY', 'YN1': 'YMY', 'YMJ': 'YMJ', 'YMM': 'YMJ', 'LEA': 'LEA', 'PEI': 'LEA', 'CRC': 'CRC', 'DKA': 'CRC', 'DAO': 'DAO', 'LAU': 'DAO', 'FAT': 'FAT', 'PLM': 'FAT', '2SP': '2SP', '3PH': '2SP', 'LP3': 'LP3', 'QEH': 'LP3', 'C8E': 'C8E', 'OTE': 'C8E', 'OLA': 'OLA', 'OLI': 'OLA', 'HQ': 'HQO', 'HQO': 'HQO', '13H': '13H', '243': '13H', 'EJM': 'EJM', 'LYW': 'EJM', '1ZD': '1ZD', '2NC': '1ZD', '0AM': '0AM', '0SP': '0AM', '2PI': 'BTA', 'BTA': 'BTA', 'NVA': 'BTA', 'RON': 'BTA', 'EOH': 'EOH', 'EOX': 'EOH', 'OHE': 'EOH', '6JZ': 'P3G', 'P3G': 'P3G', 'SCC': 'SCC', 'XL1': 'SCC', 'ITU': 'ITU', 'SEU': 'ITU', '1NI': 'LP1', 'LP1': 'LP1', 'LP2': 'LP1', 'AB7': 'AB7', 'ABA': 'AB7', 'CHC': 'CHC', 'IU6': 'CHC', 'DCI': 'DCI', 'MBA': 'DCI', '0EZ': 'PI6', 'PI6': 'PI6', 'CRP': 'CRP', 'INY': 'CRP', 'EMT': 'EMT', 'T0M': 'EMT', 'E4N': 'E4N', 'NET': 'E4N', 'F22': 'F22', 'HXA': 'F22', 'GXJ': 'GXJ', 'I0E': 'GXJ', 'N2B': 'N2B', 'PYJ': 'N2B', 'NC': 'NME', 'NME': 'NME', 'MLY': 'MLY', 'TRG': 'MLY', 'R5A': 'R5A', 'R5B': 'R5A', '3MU': 'UR3', 'UR3': 'UR3', 'VSB': 'VSB', 'VSE': 'VSB', 'AY0': 'AY0', 'PTC': 'AY0', '4OC': 'M4C', 'M4C': 'M4C', 'MGY': 'MGY', 'SAR': 'MGY', 'N9K': 'N9K', 'YNM': 'N9K', '6MA': 'A34', '6MC': 'A34', '6MT': 'A34', 'A34': 'A34', 'A35': 'A35', 'A40': 'A35', '6OO': 'OKQ', 'OKQ': 'OKQ', '0AV': 'A2M', 'A2M': 'A2M', 'A39': 'A2M', 'MAM': 'MAM', 'MMA': 'MAM', 'MBG': 'MBG', 'MGA': 'MBG', '6OG': 'G32', 'G32': 'G32', '0CR': '0CR', '1CR': '0CR', '3DQ': '3DQ', '9ZT': '3DQ', '4RR': 'ROL', '4SR': 'ROL', 'ROL': 'ROL', '1IR': '1IR', '1IS': '1IR', 'GB': 'PPM', 'PPM': 'PPM', '577': 'IIM', 'IIM': 'IIM', 'CYM': 'CYM', 'SMC': 'CYM', '0ZO': 'K7J', 'K7J': 'K7J', 'AYG': 'AYG', 'PIA': 'AYG', 'CRW': 'CRW', 'MDO': 'CRW', 'YKM': 'YKM', 'YKP': 'YKM', 'WH7': 'WH7', 'WLD': 'WH7', 'PGO': 'PGO', 'PGQ': 'PGO', 'HBI': 'HBI', 'HBL': 'HBI', 'BH4': 'BH4', 'H4B': 'BH4', 'THB': 'BH4', '98': '986', '986': '986', 'PYH': 'PYH', 'PYL': 'PYH', 'JQL': 'JQL', 'JRC': 'JQL', 'KOL': 'KOL', 'MER': 'KOL', '1GL': 'BRI', 'BRI': 'BRI', '6CT': 'T32', 'T32': 'T32', 'MEP': 'MEP', 'T23': 'MEP', 'AGL': 'AGL', 'RV7': 'AGL', 'G6D': 'G6D', 'GLW': 'G6D', '5SA': 'ARE', 'ARE': 'ARE', 'DDB': 'DDB', 'MDA': 'DDB', '53P': 'QB4', '5P8': 'QB4', 'QB4': 'QB4', 'STO': 'STO', 'STU': 'STO', '8MI': 'INH', 'INH': 'INH', 'DLA': 'DLA', 'LAC': 'DLA', 'AMV': 'AMV', 'MMR': 'AMV', 'DHO': 'DHO', 'DXC': 'DHO', 'HP3': 'HP3', 'PGR': 'HP3', 'HPB': 'HPB', 'PR0': 'HPB', 'TB9': 'TB9', 'TRB': 'TB9', 'RAA': 'RAA', 'RAM': 'RAA', 'MFA': 'MFA', 'MFU': 'MFA', 'AFL': 'AFL', 'FUL': 'AFL', 'APG': 'APG', 'SAA': 'APG', 'ETH': 'ETH', 'OET': 'ETH', 'HGC': 'HGC', 'MMC': 'HGC', 'PC': 'POC', 'POC': 'POC', 'COE': 'COE', 'MOT': 'COE', 'MPS': 'MPS', 'SOM': 'MPS', 'GER': 'GER', 'TTH': 'GER', 'TBM': 'TBM', 'TMB': 'TBM', 'PDL': 'PDL', 'PP3': 'PDL', 'AMA': 'AMA', 'PLA': 'AMA', 'THQ': 'THQ', 'TZP': 'THQ', 'RBZ': 'RBZ', 'RIC': 'RBZ', 'MDI': 'MDI', 'N0U': 'MDI', '6LX': 'MJQ', 'MJQ': 'MJQ', 'AQZ': 'AQZ', 'RNY': 'AQZ', '263': '263', '267': '263', 'NEV': 'NEV', 'NIV': 'NEV', 'NVP': 'NEV', 'PYD': 'PYD', 'YF1': 'PYD', '8MG': 'G33', 'G33': 'G33', '0SN': '0SN', '88N': '0SN', '7CP': 'MB0', 'MB0': 'MB0', 'HIC': 'HIC', 'MH1': 'HIC', 'NEM': 'HIC', 'HDZ': 'HDZ', 'TFH': 'HDZ', 'DIS': 'DIS', 'HOH': 'DIS', 'MTO': 'DIS', 'O': 'DIS', 'OX': 'DIS', 'OXO': 'DIS', 'QTR': 'DIS', 'F2O': 'F2O', 'FEO': 'F2O', 'O2': 'OXY', 'OXY': 'OXY', '2MO': 'MM4', 'MM4': 'MM4', 'IPS': 'IPS', 'PI': 'IPS', 'H2S': 'H2S', 'S': 'H2S', 'BR': 'BRO', 'BRO': 'BRO', '2SI': 'IDS', 'IDS': 'IDS', 'BHD': 'BHD', 'DOH': 'BHD', 'I7P': 'I7P', 'UEV': 'I7P', 'CL': 'CLO', 'CLO': 'CLO', 'F': 'FLO', 'FLO': 'FLO', 'MH6': 'MH6', 'SRI': 'MH6', '672': 'Q72', 'Q72': 'Q72', '424': 'YJC', 'YJC': 'YJC', '1MA': 'MAD', 'MAD': 'MAD', 'IDO': 'IDO', 'IOD': 'IDO', 'NGN': 'NGN', 'NH4': 'NGN', 'NMO': 'NMO', 'NO': 'NMO', 'SO4': 'SO4', 'SUL': 'SO4', 'HYD': 'HYD', 'OH': 'HYD', 'B51': 'B51', 'WCC': 'B51', 'ZN': 'ZN2', 'ZN2': 'ZN2', 'FIB': 'FIB', 'IBF': 'FIB', 'PGS': 'PGS', 'SPG': 'PGS', 'ADE': 'ADE', 'ANE': 'ADE', 'NEW': 'NEW', 'PCQ': 'NEW', 'EGG': 'EGG', 'KDH': 'EGG', 'G1T': 'G1T', 'G1Z': 'G1T', 'B7D': 'B7D', 'TRU': 'B7D', 'P5P': 'P5P', 'PR5': 'P5P', '9HE': 'KS1', 'KS1': 'KS1', 'DHY': 'DHY', 'HAA': 'DHY', 'DAH': 'DAH', 'TY3': 'DAH', 'LNR': 'LNR', 'LT4': 'LNR', 'NAD': 'NAD', 'NAH': 'NAD', 'EHP': 'EHP', 'MTY': 'EHP', 'PIX': 'PIX', 'TF6': 'PIX', 'CSY': 'CSY', 'GYS': 'CSY', 'FA': 'FOL', 'FOL': 'FOL', 'STY': 'STY', 'TYS': 'STY', '69X': 'YAP', 'YAP': 'YAP', '345': 'CBP', 'CBP': 'CBP', 'DGH': 'DGH', 'GHP': 'DGH', 'NTY': 'DGH', 'CQR': 'CQR', 'CR2': 'CQR', 'WAK': 'WAK', 'WB8': 'WAK', 'KSB': 'KSB', 'QHL': 'KSB', 'BAP': 'BAP', 'BP': 'BAP', 'BPC': 'BAP', '6AB': 'BE2', 'BE2': 'BE2', 'L0F': 'L0F', 'L0H': 'L0F', 'BEZ': 'BEZ', 'BOX': 'BEZ', 'F9V': 'F9V', 'FSL': 'F9V', '1PY': 'PPY', 'PPY': 'PPY', 'BGG': 'BGG', 'P6S': 'BGG', 'BZO': 'BZO', 'CBZ': 'BZO', 'IOX': 'IOX', 'PMS': 'IOX', 'PCS': 'PCS', 'PHM': 'PCS', 'HFA': 'HFA', 'LLA': 'HFA', 'LOF': 'HFA', 'HPH': 'HPH', 'TPH': 'HPH', 'FRF': 'FRF', 'PUK': 'FRF', '0AC': 'FOG', 'FOG': 'FOG', '638': 'XV6', 'XV6': 'XV6', 'BIC': 'BIC', 'MOL': 'BIC', '3DB': 'D8W', 'D8W': 'D8W', 'PG9': 'PG9', 'PGY': 'PG9', '119': 'P4P', 'P4P': 'P4P', '86Q': 'DRG', 'DRG': 'DRG', '89E': 'LIG', 'LIG': 'LIG', 'CYP': 'CYP', 'GPR': 'CYP', 'K0I': 'K0I', 'URY': 'K0I', 'LTR': 'LTR', 'TRP': 'LTR', 'V70': 'V70', 'V7F': 'V70', 'QNC': 'QNC', 'QND': 'QNC', '0TN': 'RKP', 'RKP': 'RKP', 'QUI': 'QUI', 'QX': 'QUI', 'AC4': 'AC4', 'AMZ': 'AC4', 'D5M': 'D5M', 'DA': 'D5M', 'A': 'AMP', 'AMP': 'AMP', '0DG': 'DFG', 'DFG': 'DFG', '0G': 'LG', 'LG': 'LG', 'DCG': 'DCG', 'DG': 'DCG', 'DGP': 'DCG', 'DI': 'OIP', 'OIP': 'OIP', '5GP': 'CPG', 'CPG': 'CPG', 'G': 'CPG', 'G25': 'CPG', 'I': 'IMP', 'IMP': 'IMP', 'GCP': 'GCP', 'GTO': 'GCP', 'GNP': 'GNP', 'GTN': 'GNP'},
    )
    monkeypatch.setattr(
        "plinder.data.utils.annotations.ligand_utils.COFACTORS",
        {'JM2', 'PCD', 'CAA', 'NCA', 'HEM', '0XU', 'RGE', 'NAX', 'LPB', 'AMX', 'TXP', 'SCO', 'MQ7', 'FNS', 'MQ9', 'FMN', 'PLR', 'CHL', 'WSD', 'TD7', 'TPQ', 'SDX', 'GVX', 'TS5', 'EB4', 'ENA', 'NDE', '1CZ', '2MD', 'CYP', '1JO', 'PP9', 'GS8', 'TDM', 'C2F', 'NPL', 'UP3', '8EL', 'AMP', '4LU', '1DG', 'DCQ', '2CP', 'GBP', 'NAQ', 'HDE', '62X', 'NDP', 'CCH', 'TD6', 'SCD', 'TXD', 'UU3', 'M6T', '3HC', 'SFD', 'NHM', '66S', 'TMP', 'ODP', '3CP', 'CLA', 'CL7', '1TY', 'NBD', 'C', 'COM', 'T6F', 'MSS', '1CV', 'MCN', 'ASC', 'SA8', 'WCA', 'S1T', 'GF5', 'IRF', 'CPG', 'MCA', '36A', 'ISW', 'GIP', 'TYQ', 'PMP', 'CL2', 'FCG', 'UTP', '1R4', 'NAP', 'HDD', 'FDE', 'GTX', 'CDP', 'CA8', '1U0', '76K', 'GGC', 'AGQ', 'XP9', 'FON', 'ZEM', '1YJ', 'PQN', '76J', 'IBG', 'UEG', '5GP', '1VU', '3H9', 'LPM', 'BCA', 'VWW', 'FAS', 'DPM', '3CD', 'NA0', 'TTP', '6J4', 'DT', '48T', 'GTS', '4LS', 'TDT', 'HMG', 'THG', 'TDL', '6NR', 'FSH', 'G27', 'TGG', 'THV', 'BYC', '2TP', 'FA8', 'EN0', 'HXC', '2NE', 'T1G', 'DU', '7AP', 'THM', 'TZD', 'N1T', 'PAU', 'ADP', 'DLZ', 'A3D', 'COB', 'ECH', 'TYY', 'MTV', '7HE', '29P', 'HAS', 'G', '3AA', 'UMP', 'BTN', 'H4B', 'YNC', 'CA5', 'C5P', '0ET', 'CA3', 'C25', 'TP8', 'FOZ', 'CNC', 'TC6', 'DDH', '4CA', 'MNH', 'U', '76L', 'G25', 'JM7', 'FDA', 'A', '07D', 'P2Q', 'NHW', 'COT', '4YP', 'DTB', 'GSN', 'COO', 'ZNH', 'BPH', 'NPW', 'COH', 'GDS', 'L9X', 'DG1', 'PAD', 'MNR', 'GDN', 'SX0', None, 'NDC', 'BCL', 'COW', 'TXZ', '8EF', 'WWF', 'MGD', 'PZP', 'GRA', 'HTL', 'FRE', '0HH', 'FAA', 'TP7', 'AT5', 'BYG', 'SRM', 'MDE', 'EAD', 'TPU', '4CO', 'P3Q', 'TRQ', 'GMP', 'M43', 'LEE', 'CTP', 'PXL', 'ABY', 'SAH', 'HIF', 'GTY', 'TT8', 'SMM', 'COF', 'ZBF', 'FAM', 'T', 'COA', '8ID', 'GSF', '76M', 'DN4', 'FAD', '5AU', '0WD', 'COZ', 'CRW', '76H', 'SND', 'FNR', 'UDP', 'BHS', '6V0', 'CYC', 'ATP', 'BYT', 'EPY', 'THF', 'GSH', 'MQE', 'COY', 'HAX', '1JP', '37H', 'NBP', 'ZID', 'MFN', 'SOP', 'TPP', 'PDP', 'PQQ', 'GPR', 'GTP', 'CA6', 'DHE', 'SHT', 'F42', '0Y1', 'MTQ', 'H2B', '6FA', '6HE', 'THB', 'CP3', 'SFG', 'CAJ', 'DCC', 'TD9', '8PA', 'NDO', 'THY', 'N3T', 'MH0', 'FMI', 'AP0', 'GBI', 'UQ1', 'H4M', 'LZ6', 'FCX', 'NAJ', 'MDO', 'FAE', 'S0N', 'HBI', 'SAD', 'TDK', 'TDW', '18W', 'BIO', 'UQ2', '1C4', 'GPS', 'FED', 'NHQ', 'TQQ', 'XP8', '2TY', 'G9R', 'ACO', 'TDP', 'UAH', 'U5P', 'ESG', 'FAO', '7MQ', 'CND', 'D7K', '8FL', 'CO6', 'PUB', 'HCC', 'SAE', 'AHE', '4IK', 'Y7Y', '488', 'TAP', 'RAW', 'DCA', 'BOB', 'NAI', 'TXE', 'HEC', 'BCR', 'MYA', 'HBL', 'P1H', '01A', 'UQ6', 'ATA', 'NHD', 'B12', 'FAB', '1HA', 'MCD', 'TYD', 'SAM', '8JD', 'PLQ', 'GTD', 'UP2', '0UM', 'NOP', 'GBX', 'COD', 'THD', 'NAH', 'NAE', 'CMC', '4AB', 'SCA', '8EO', 'ZOZ', 'BH4', 'OXK', 'MLC', 'LPA', 'ICY', 'GSM', 'HEA', '1CP', '1XE', 'GNB', 'JM5', 'XAX', 'P5F', 'H4Z', 'EEM', 'GDP', 'PLP', 'FFO', 'SH0', 'PNY', '5GY', 'MQ8', 'EQ3', 'CO8', 'HSC', 'BSJ', 'MTE', 'CIC', 'SE8', 'PEB', 'TPZ', 'GTB', '0AF', '0Y2', 'R1T', 'MPL', '01K', 'U25', 'CL0', 'HQE', 'RBF', 'FYN', 'CMX', 'THW', 'HAG', 'MEF', 'CL1', 'PXP', 'TAD', 'T5X', 'N01', '1TP', 'TD8', 'MMP', 'K15', 'NAD', 'RFL', 'BTI', 'BCO', 'GSO', 'UQ5', 'GSB', '0HG', '3GC', 'NMX', 'THH', 'HEB', 'PNS', 'TOQ', 'F43', '8Q1', '8Z2', 'CAO', 'TPW', 'BCB', '0Y0', 'LNC'},
    )
    monkeypatch.setattr(
        "plinder.data.utils.annotations.ligand_utils.ARTIFACTS",
        {'OTE', 'BNG', 'GYF', 'MES', 'HEX', 'PX2', '2OP', 'UMQ', '1PS', 'SIN', 'VX', 'C8E', 'ETF', 'GOL', 'CAC', 'O4B', 'MBO', '9YU', 'PC8', 'OGA', 'PVO', 'CN6', 'PGR', 'DDR', 'AGA', '33O', 'B3H', 'MPD', 'DTU', 'P03', 'CXS', 'QLB', 'KDO', '3HR', 'DIO', 'THE', 'RG1', 'F09', 'HTG', 'SP5', 'BOX', 'CN3', 'L1P', 'DOX', 'MPO', 'TAM', '1PG', '543', '7PE', 'FW5', 'PE5', 'TAR', 'LMT', 'DHJ', 'PX4', 'FJO', 'P25', 'P33', 'HT3', 'Y69', 'TRD', 'DMF', 'DTT', 'P4G', 'MRD', 'PGO', '144', 'PGE', 'TCN', 'MYR', 'MAC', 'LMU', 'L3P', 'P22', 'TCE', 'BET', 'HTO', 'ETX', 'BAM', 'DTD', 'DAO', 'TRS', 'CE1', 'LUT', 'TOE', 'PEG', 'HP3', '1PE', '7PH', 'TLA', 'PE4', 'DKA', 'P2K', 'PA8', '1EM', '7I7', 'P6G', 'IPH', 'BE7', 'QGT', 'L4P', '9JE', 'DMR', 'BDN', 'TMA', 'I6P', 'DD9', 'MC3', 'XPE', 'OP2', 'SOG', 'PG0', 'E4N', 'PD7', 'DET', 'NBN', 'PE7', 'CIT', 'HZA', 'N8E', 'BEN', '32M', 'LI1', 'DR6', 'D12', 'P4C', 'LIN', 'BU1', 'C10', 'D22', 'CRC', '2NV', 'CHT', 'CXE', 'XP4', 'PE8', 'DDQ', '15P', 'L2P', 'PTD', '148', 'EAP', '12P', 'NHE', 'TBU', 'PIG', 'MGY', 'HSH', 'IHS', 'LAU', 'HAI', '13P', 'PG5', 'DHB', 'FTT', '3V3', 'SAR', 'ICI', '3PG', 'PUT', 'LAC', 'SGM', 'NET', 'D1D', 'PG6', '7PG', '2JC', '2DP', 'PQE', 'LMR', 'CPS', 'IOX', 'HSG', 'BXC', 'EPE', '02U', 'MB3', 'L2C', 'DTV', 'BOG', 'NEX', 'PE3', 'PHQ', 'PE6', 'CE9', 'C14', 'CD4', 'SRT', 'GLV', 'BHG', 'I3C', 'DLA', 'ICT', 'TAU', 'RWB', 'LDA', 'PGF', '7E8', 'HCA', 'QJE', '7E9', 'BTB', 'SPZ', 'HED', 'PGQ', 'P1O', 'TEA', 'IMD', 'MP3', 'JDJ', 'HTH', 'V1J', '6JZ', 'AUC', 'DEP', 'M2M', 'PG8', 'MBN', 'CAQ', 'B4T', 'HAE', 'P15', 'UND', '9FO', 'DMI', 'XPA', 'PEP', 'TFA', 'HEZ', 'MLA', 'DRE', 'PEX', 'AKR', 'XAT', 'PLC', 'SPD', 'MLT', 'F4R', 'SPM', 'BGL', 'AAE', 'AE3', 'P3G', 'SPJ', 'CRY', 'PPI', 'PEU', 'MAE', 'PHB', 'DPG', 'B4X', 'OCT', 'ETE', 'BNZ', 'IHP', 'PMS', 'B3P', 'PQ9', '3SY', 'AE4', 'CAD', '2PE', 'OES', 'GVT', 'K12', 'PG4', 'EEE', 'SQU', 'D10', 'BCN', '7N5', '90A', 'ME2', 'KGN', '16P', 'MLI', '6PE', 'P4K', 'BEZ', 'PL9', 'HP6'},
    )
    monkeypatch.setattr(
        "plinder.data.utils.annotations.ligand_utils.KINASE_INHIBITORS",
        {'4DF', '2NR', '36R', 'XJ0', 'S4Q', '8BQ', '79Y', 'ZOI', 'EBD', '1JI', '7AE', '07Z', 'PZ4', '0WM', 'JRQ', 'YD7', 'RMF', 'MZJ', 'LM4', 'XZN', '3EY', 'GW7', '469', '2KD', 'H52', 'Z67', 'C5Z', 'P30', '29Z', 'Y5D', 'EK9', 'YIR', 'MT3', '1UK', '74K', 'A9R', 'N4D', 'OJ5', '78W', 'SBC', '6UY', 'AWK', '8GR', 'I2O', 'AAX', 'SU2', '9XA', '1EH', 'HK0', 'Q17', '30K', 'I0A', '6HH', 'E5J', 'T2O', 'FW3', '8E1', '5X4', 'EUX', 'MMH', 'L10', '47X', 'SIQ', 'YEE', 'UNJ', 'ZRK', 'AMP', '46C', 'R5D', '86K', 'HCW', 'Q1Y', 'YIX', '7GV', 'BI1', 'C6F', '7DZ', '8BS', '6NP', 'C2V', '4JZ', 'AFE', 'Q9B', '4MK', 'NN5', '0HD', 'X85', 'SCW', 'A3K', 'L09', '2QT', 'FS8', '1UJ', 'SS6', 'X6G', '0VG', 'B7V', 'XL5', 'QX1', '8FX', '7VT', 'C85', '63N', 'AVZ', 'IFC', '4UT', '6PF', 'DXM', '7ZC', '5BN', 'ZY6', 'R4V', 'AP2', 'UIW', '54Z', 'F8I', 'OQM', 'C52', '4VD', 'DBQ', '1D1', 'TV4', 'NU6', 'EA7', 'X6B', 'KZJ', '3UI', 'R73', '6NC', '0B0', 'SQM', 'VEH', 'X69', 'JGG', 'AFM', '4RM', '0JJ', '6KC', '1YZ', '5JE', 'OOU', 'R1W', '3QS', 'A8H', 'DO0', '8UV', 'WI2', 'NBW', 'X40', 'CK9', 'J8S', '2HW', '85A', 'QUP', 'MHR', '4CV', 'EZJ', 'P01', '363', 'TID', 'CUR', 'EHB', 'S92', 'OQJ', 'Y8L', 'GUB', '090', '4Z8', '28D', '5W6', '8GU', 'WB8', 'NQ2', 'J9D', 'I3K', '1JC', 'QH1', 'EX9', '13V', '514', 'UT5', 'YQ2', '4FT', 'P02', 'FB8', '07J', 'JSN', 'SM6', 'X3V', 'FOI', '6H3', '60K', 'T3C', '4ZB', 'J3H', 'T1T', 'HZ6', 'GCC', 'MTW', 'B4U', '7HK', '3BM', '16X', '50H', 'Z3A', 'LB4', '74L', '9IS', 'XPY', 'C87', 'ACK', '5Y6', '3RW', 'IXQ', '1IJ', 'LIA', 'VFC', '0K0', '19A', '5JG', 'HVH', 'H5R', 'QXW', 'E91', '37Q', 'Y3L', 'YIS', 'YOR', 'JOZ', 'JSW', 'EVK', '3GF', '253', 'DLN', 'QP7', 'CX4', 'B4J', '1CK', 'EDJ', 'P47', '857', 'KA7', 'R6R', '0F4', 'EMW', 'CKG', 'TJF', 'RO6', '23D', '319', 'FGE', 'TBK', 'NU5', '547', '70I', 'U0T', 'ASH', 'H8H', 'J3N', 'J6F', '38M', 'L90', 'CGI', 'C75', '6RF', '8OV', '2QV', '19K', '4W5', 'Z68', 'HUH', 'SVK', '6QZ', '4VQ', '7TH', 'GYL', '31Y', 'BR2', '3Z2', 'NRA', 'ON6', 'K88', 'AXU', 'PIT', 'OWQ', 'D15', 'NJD', 'F4A', 'C4E', '04Z', 'ZOQ', 'KSH', 'OY2', 'E0X', 'K0E', '5GX', 'MWF', 'LZC', '770', 'BNB', '24Z', '7AV', 'QI6', 'P49', '4Q2', 'PY1', 'AGI', 'DJX', 'X6K', 'LOQ', 'YY7', 'MKP', 'IEA', 'Q2H', 'AGY', '1LE', 'G6K', 'QQ2', 'BD2', 'I17', 'OOM', 'ACP', 'R74', 'NBK', 'N14', 'EXX', '54G', 'A6Z', 'TXV', 'X01', '5ZH', 'FLZ', '3E4', 'IDZ', 'P31', '8I1', '14K', '6Z2', 'E2O', 'QG5', 'GEN', 'SVQ', 'DW1', 'Z30', 'LIE', 'N9R', '2OQ', '2WJ', '3WN', 'X7G', 'VZG', '54J', '4E3', 'KR8', 'QZ8', '2M2', 'FPW', '0CK', 'SM7', 'DF1', '99Z', 'HVK', 'HK6', 'PDR', '4T6', 'CD2', 'CG4', '21Z', '6BF', 'R7D', 'NL2', 'FZJ', 'JZH', '3G5', 'SMH', 'LY4', 'T2A', 'RSW', 'V3S', '92C', 'R4Y', 'N53', 'VGK', '3ND', '14S', '9A6', 'NQB', '0GW', 'UB6', 'N0V', '26L', '5TF', '1RJ', '027', '0MY', 'HVQ', 'M0R', 'X86', 'KLP', '1K2', 'ZRR', 'XGK', 'BA1', 'X19', '5Q4', 'UOE', '7GT', '7GJ', '06N', 'VJK', 'IQ6', 'A65', 'SWD', '29L', '8LN', 'K0B', 'CK7', 'N17', '30E', '7KF', 'AAZ', '9D8', 'LWH', 'FQM', 'LU2', 'EQT', 'NIL', 'EJP', 'M97', '4ST', 'C2J', 'DFZ', 'I6C', '5XV', 'FH0', '9HR', 'HET', '0VN', 'X21', '5SZ', 'DZC', 'YY4', 'RKO', 'FBY', '446', 'RYU', '0OP', 'ATU', '2SC', '10Z', '5DN', '3HK', 'IPK', '622', '8IQ', 'WFE', 'ZSB', 'L9M', 'F4G', 'MMG', 'G8E', 'MP6', 'ZRT', '7G9', 'NAR', 'RXZ', '877', '3QH', 'P16', 'IM9', 'XW3', 'KDI', 'V55', 'H7C', 'RVH', '362', '5VC', 'UZD', 'K6Y', '19R', 'OZ8', '5U4', '3YO', 'BRQ', '77V', '5YZ', 'D0A', 'KWD', 'SQ4', 'IE8', 'FSS', 'VZ2', 'BXJ', '3P0', 'BWP', 'RO9', 'MJG', 'A6E', '5OE', '13K', 'R9B', 'GYQ', 'FER', 'JTQ', 'KC0', 'XZ9', 'WZZ', 'SFY', '3DL', 'YXJ', 'F29', 'TOV', '0SX', 'Y4O', 'A27', 'DZO', 'IM6', 'CKJ', 'O3E', '9Y5', '7QQ', 'L0M', '7GB', 'RHZ', '3NC', '912', '6V4', '5IE', '7M0', 'P37', 'DT2', 'ZRL', 'HYW', '6DC', '580', '0BG', '8FI', '04G', 'E28', 'KRQ', '4B0', 'FDW', 'POX', 'P5J', 'VGH', '7X5', '2C3', '8DS', 'W39', 'GUQ', '35F', 'ZZM', 'A5Z', 'HC4', '36N', 'UC8', '796', 'F8H', 'CKN', '4T5', 'NR9', '481', 'AD5', '22T', 'GD9', '8OK', 'HKK', '3DK', 'B0K', 'R6H', 'JLC', '4S3', '596', 'UH3', '38O', '2R4', '80U', '8OT', 'M1J', '6ID', '0XG', 'KJD', 'M4G', '0SO', 'URF', 'JKW', 'UU6', 'LDN', 'SO9', 'HVE', 'QWQ', 'T3U', '222', 'P5V', 'JVD', 'LTY', 'L12', 'TVT', '1TT', 'L4Y', 'VP7', '31W', '8OW', 'QZ2', 'ZOV', '61Y', '628', 'W2R', '59U', '614', '65C', '1HK', '8X2', 'E3Z', 'QB8', 'SCE', '0C5', 'LOK', '0XH', '8CC', 'L0Q', 'ITQ', 'TZX', '4SB', '390', 'J2V', 'QF8', 'K4W', 'C98', 'C96', 'ZD6', '8GS', '9XK', 'R6V', 'UJ3', 'H4K', '35Z', '86E', 'CJ5', '1WY', 'VIN', 'IXH', 'G5D', '6CY', '4RJ', 'L91', '30T', '5Y8', '3YV', 'C7Y', '1R9', '7EY', 'A7K', '5XH', 'UCW', '0TZ', 'FU6', '7KD', '215', 'SWN', '6YD', 'WXV', 'LI8', '37J', 'AK7', '2BZ', 'RYA', 'WFY', '0SW', 'RXE', 'YAM', '9CT', '3XL', '4O7', '9VS', 'GEZ', 'OOQ', 'M92', 'CCK', 'VEW', '6UK', 'L7C', 'XZS', 'MH7', 'QS7', 'YPH', 'B5E', 'QFK', '6P8', 'QDW', 'DTD', '5BS', '60O', '679', 'UNW', 'P36', '6JV', 'WYE', '38P', 'ULY', 'J2M', 'CK1', '3PS', '9AJ', '96Y', 'JMZ', '0FK', 'W7W', '02Z', 'VSB', 'CK3', 'O43', 'EBI', '9JI', 'G4E', '0Q2', 'BI9', 'G0K', '5UY', '8ET', 'WY3', 'V5U', 'M33', '9FS', '34I', '3Q6', 'P5W', 'M19', 'S5E', '7CS', '4UQ', 'N5Q', '706', 'TC0', 'KEP', 'QIG', 'HYK', 'KHH', 'JFS', 'V6E', '66X', 'KJR', '5E2', 'ME3', 'EVQ', '0VF', '7XU', '25J', 'MMY', 'L1K', 'QMN', 'K11', 'S9H', 'N58', 'JNZ', 'QBB', '5W9', '66L', 'HJF', '932', 'BVI', '3RZ', '1J5', '467', '4FJ', '3JZ', '0SQ', '0C9', 'N99', '71M', 'XU0', '0Y4', 'B0R', 'OOS', 'B6N', 'O44', 'W4D', 'S4W', 'BXI', '464', 'XAZ', 'BEN', 'L3G', '6T2', 'US0', '6GE', '5DF', 'IRE', 'BFF', 'GHT', '0FS', '24N', 'EYI', '14I', 'L64', '430', '30G', 'X14', '718', '90W', 'WZU', 'LWX', '0C8', 'FCS', '38Z', 'FZ9', 'P7B', 'ZS2', 'M3A', '91E', 'KEY', 'W38', 'O23', 'DFY', 'JH8', '6H4', 'GJG', 'A07', 'J8A', 'RNF', 'LI7', 'AW5', 'MQY', 'C72', 'L9N', 'IR2', '2HB', 'KVC', 'NHU', 'FTU', 'L3Z', '35W', 'FLJ', 'X2L', 'SYY', '0S0', 'OQS', 'KE7', '64M', 'X3S', 'UF8', '3U1', 'FML', 'AQ4', 'QO7', 'HVB', 'O7I', 'C74', '1HX', 'CUE', '904', 'FZ8', 'AWF', '751', 'IQU', 'P66', 'IQR', 'KSS', 'A5B', 'DVJ', '5BM', '1XZ', '5ID', '1V5', '3Q2', 'B6J', 'R93', 'M9T', 'SWB', '35X', '3B3', 'YXD', 'I4M', 'NXI', 'R0X', 'F67', '0SC', 'JRJ', 'N13', '4VE', 'SQG', 'B1E', '38W', 'AT8', 'C53', 'PVB', 'SQ7', 'CPB', 'AAV', 'HKN', '8MZ', 'Q18', 'SQY', 'YO4', 'FE7', '0V0', '88Z', '3C8', 'OZN', 'EZV', 'AZ7', 'E6Q', 'R85', 'ZZP', 'R28', '5Y2', 'R1L', '979', '3YX', 'D6Q', 'QFO', 'KIH', '8ZT', '79T', 'BHO', 'LVU', 'FH3', 'VSA', '7GX', '5OQ', 'G93', 'Q7H', 'YK2', '855', 'R1S', '8MW', '3DW', 'TJZ', '112', '8XN', 'DT1', 'QU6', '437', 'X66', 'RP9', 'DFW', '3VE', 'X8J', 'LZE', 'BZ9', '7H4', '9T6', 'SQK', 'N4F', '1NP', '77A', 'EZN', 'ESN', 'FP3', '9KO', '0OM', 'XHM', 'EQZ', '627', 'SZW', '74J', '5CV', 'VY0', '2GI', 'B5S', '6XL', 'EAZ', 'E6T', 'T4X', 'R7O', 'Q8T', 'AM5', '6SF', 'FPH', 'ZOP', '609', 'ZGD', '7IH', 'FAZ', 'T92', 'E46', 'JND', '6DA', '7HF', '1UL', '7Z0', '3AM', 'LW3', 'RPW', '4V9', 'A9W', '6BB', 'R48', 'AS6', 'NVX', '7GL', 'R70', 'H6W', 'M0Y', '3Q4', '0FR', 'SNJ', '44X', '094', 'WEJ', 'F7I', 'E2F', 'SRJ', 'MS9', '29A', '2X6', '2PU', 'G6T', 'KEV', 'KQ7', 'A4B', 'S26', 'AK8', 'AU8', 'MW8', 'T20', '3Q3', 'LHJ', 'NKJ', 'RUW', 'FC8', 'G4H', '3EW', '6FB', '2RL', 'SQV', 'NW1', '8XB', 'D5Q', 'VNS', 'QFV', 'IG3', '6CD', 'WP1', 'P1E', 'BW1', 'OOV', '0FN', '26Z', 'ZXH', '7X7', 'PUP', '71G', 'VJZ', 'K4A', 'NK0', 'OV5', 'J0E', 'A58', '3RC', '75H', '0TP', 'CK6', 'SVH', 'YT0', 'X88', 'RUI', '03K', 'DYQ', '55S', 'GXA', '460', 'AWJ', 'NTQ', '8N2', 'KHR', 'OT5', 'CG5', 'KJ8', 'L0C', 'H2K', 'VLV', 'IRD', '6T5', '3QX', 'SMY', '1BQ', '4S2', 'QMY', 'IC8', '9IK', 'M0F', 'YRZ', '67U', 'NM7', 'XIN', '0FY', 'C9O', '0RF', 'S4E', '9I5', '6ZK', '6HL', 'KAV', 'EVR', 'LAJ', '4W1', 'LCW', '0JE', '99J', '4K7', '41B', 'DF3', '2A2', 'IQ7', 'G4Y', 'T7Z', 'NNN', '8E8', '8M1', '59N', '8QK', 'D6I', 'Y5G', '3R0', '3A3', 'M1O', 'F8B', 'BQR', 'LY2', '07R', '2W6', '3X7', '6YE', '66K', 'JSB', 'LOE', 'YK1', '0WN', '0PF', '3SC', '8OR', 'F8M', 'H3E', '5XG', '504', 'QKG', '304', 'U0K', '4IH', 'AX7', 'LCI', 'Z62', 'B96', 'SYP', 'L20', 'KES', '373', 'L2V', 'P79', 'EVC', '91K', '734', '86H', 'LI3', 'E1B', 'KF4', 'XIT', 'X06', '1QO', '20K', '9FV', '17V', 'K9Y', 'LGX', '1J6', '01I', '4OK', 'G4N', 'KLM', '3C3', 'XBJ', 'G8N', 'ZZN', '45R', '746', 'RXT', '18E', 'T95', 'LU8', '6UM', '07C', '9K5', 'B5G', '84R', 'HRA', 'OOY', 'C4F', '06Z', '0SS', 'FLY', 'KIN', 'J4M', 'ICQ', 'WKC', 'WQ6', 'RJI', 'KSF', 'UF4', 'G92', '0X6', 'LWJ', 'X03', '8PV', 'A4U', 'UWZ', 'E52', 'OG5', 'MB9', 'CT7', 'XXK', '1E8', 'H5I', 'T3M', 'GR9', 'F3W', 'DL1', '1BU', 'YM8', 'PQ5', '2I8', '919', '0FO', 'RJZ', 'H99', '0LI', 'X64', '6V5', '4S1', 'DTQ', 'HDU', 'R3L', '9O5', 'TWH', 'XM1', 'LZN', '953', 'AK1', '98D', '1C7', '9Y8', 'JMM', '7KV', '90K', 'CJT', '3Q1', 'P0F', 'KUY', '0F5', 'OQ8', 'VX6', '1LC', 'L0F', 'EMO', 'SU6', 'FJI', 'NKZ', '2D2', 'HHB', '324', '1O5', 'K0N', 'EZQ', 'ZUQ', 'QJI', '729', '5H2', 'RMX', 'LB5', 'Z86', '351', '3T3', '5Z5', '889', '8ZW', 'X73', 'H7U', '3NU', 'L0G', 'OG8', '6BJ', 'R24', 'FI4', 'A', '0G1', 'E63', '8BP', 'J0B', '31L', 'FRV', 'N8O', 'VX3', 'Y3I', 'STV', 'JX4', 'VEK', '534', 'X9F', '2K5', 'G0N', 'G2G', 'VXY', '5W2', 'I5S', '79C', 'F92', 'X07', '4DO', 'AFV', 'QYE', 'YOS', '1IX', 'ED8', 'FP4', 'NVV', '839', '0UU', '8DW', 'WAL', '9LL', 'H8K', 'ZYS', 'RTX', '77C', 'MUJ', '8LY', 'SVM', 'FEW', 'DVO', 'R0O', 'GWH', '4WG', 'FAR', 'BV9', 'R25', 'RBQ', '40L', '8GQ', 'C5I', '7U5', 'M61', 'DJ8', 'W9D', '8V4', '8PR', 'QFB', '1UO', '3U9', '3K3', 'M56', 'T0L', 'GK1', '7KC', 'BH9', '8N5', 'ST8', 'U55', 'ATP', '4T9', 'BR9', 'R7S', 'NKB', 'FTZ', '748', 'YQY', '8DV', '3Z4', 'MR9', 'ODJ', 'OFZ', 'JWY', '85V', '0XZ', 'ZZK', 'WTP', '6A6', 'G7K', '1BM', '4RV', '3S1', '20Z', '032', '584', 'ZZO', 'LCB', '5JZ', 'U4W', 'Z6V', 'W3N', '0C3', 'Q6W', 'OS1', 'HK9', 'AP9', 'NF5', 'PD1', '8QB', 'F8P', '5N4', '3R1', '8UB', 'HMW', 'X9I', 'Q9G', '4DK', 'Y49', 'OZU', '0O7', 'N61', 'IDV', '6HJ', 'GQL', 'I9W', 'KZQ', 'DXK', '738', 'QR7', 'NS9', 'VGM', 'N9G', '9ZP', 'Z48', '9FC', 'ZB9', '4QX', 'NRR', 'O8T', '1B4', '24R', 'XEZ', '5SF', '3Z5', 'KIM', 'QDZ', '79R', 'Z92', 'PXN', 'LZB', 'U8P', '5JR', '7YG', 'HGW', '0WC', 'Z46', '5WF', '6G2', 'N7C', '7KW', '60B', 'L7O', 'QWW', '0MX', 'L7W', '5I9', 'M59', 'CAQ', 'J67', '6SL', 'GKB', '5QS', 'TW2', '242', '634', 'MRA', '9NQ', 'P48', '7CE', '9WG', 'T6Q', '8OH', 'RSI', '406', 'YM3', 'TFA', 'UNL', 'ZQV', 'W4A', '8BM', '74Q', '9OO', 'RMM', 'IIW', 'O6X', '3WH', 'CQ3', 'D37', 'J07', '66T', 'X67', '1SB', '4DT', 'BI5', '9YY', 'YA7', '80C', 'ZWE', '5HK', 'A3E', 'KBM', 'R09', 'AQG', '8DY', 'N15', '86G', 'O21', 'YR7', 'UM4', 'E4S', '5P6', '07S', 'LZ1', 'TQA', 'DZ6', 'SIX', '76Z', '74N', 'ODO', 'HEW', 'B4B', 'HDY', 'VL1', 'ZL1', 'I5R', 'L7R', '1BK', 'L0N', '3TI', 'L51', 'RW6', 'QQC', 'T75', '5NW', '7AU', 'TJW', '69Z', 'KK8', 'EJS', 'AU2', '4OR', '0SJ', '2O6', '2VT', 'G7W', '2IJ', 'EDB', '6QH', '9QK', '057', 'S69', 'A0X', 'FXB', '517', '358', 'A42', '1C8', 'AX0', 'OEB', 'DXH', '61E', 'D0S', '862', '52P', '87B', '7MJ', 'ANP', '0WB', '5PB', 'RC8', 'L1E', '4OQ', 'BIM', 'VRV', '42Q', '0ST', '495', 'AQ8', 'DUK', 'S3N', 'RFG', 'NZ5', 'EK3', 'N97', 'FG9', '4CK', 'ZZG', '4RU', 'F1S', '3FV', 'EJY', '0KD', '2YK', 'F82', 'N0U', '287', 'SL0', 'FEF', 'Z0O', 'AQE', '5XJ', 'OVC', 'A96', 'HK4', '2VX', '10N', '8ZQ', 'KE8', '7IK', '7TZ', 'LQQ', 'H3R', 'E8V', '8ZH', '6QY', '0YJ', 'JK1', 'QIV', 'X36', '76C', 'GDH', 'U82', 'Z6P', 'F10', 'RPS', '82B', '1EL', 'NB3', 'XSE', 'KEX', 'W3R', 'A5H', 'A6W', 'DFS', '1N1', 'QDE', 'IHH', 'AGS', 'M2B', 'X9B', 'L1Z', 'S4T', '7HD', 'CQ8', 'X44', '1CD', '5S8', 'LBE', 'H88', 'ADZ', 'CDK', '6F2', 'AV9', '5QQ', 'G9B', 'AFK', 'GJD', 'N41', '65L', 'PYZ', 'OG2', '36Q', 'B9C', 'R6S', 'EUN', 'LVF', '0C6', 'HH5', '18K', 'LZ2', '9YV', '4P4', '74H', 'YQB', 'KH8', '5H5', 'SGV', 'ZIP', 'A82', 'Q6K', '809', 'GXK', 'L1X', 'BYZ', 'AJR', 'V4Z', 'IC2', 'X9H', 'E57', '4J7', 'Q7Z', 'IB5', 'EK4', 'LKG', 'G4V', 'AFU', 'G02', 'CXS', '50Z', '5MT', 'FI3', 'CT8', 'EKU', 'WBT', 'QFQ', 'V0G', 'IZA', 'RUY', 'WJV', '891', '1N6', '0CI', '9ES', 'NXP', '5Q3', 'HV2', 'N7B', '0RX', '3DV', 'F0E', 'HFS', '50F', 'QQ1', '63M', 'OFW', '0JK', '6GY', '39Z', 'QIH', '647', 'CJM', 'WGK', '3FX', '2HK', '97B', 'ZYR', 'XYW', '279', 'NHJ', 'U32', 'SB4', '0O8', 'QAR', 'SU1', 'JZO', 'AUG', 'D94', '41A', 'H8Z', '6V3', '1AO', '3D3', 'WPH', 'C1V', 'QMV', '0K1', '1RA', 'EDH', 'JHW', 'NVB', '3WR', 'CVY', 'CIG', '8FY', 'H7K', 'I47', 'R6P', '5X1', 'N78', 'SN4', 'S91', '6UF', '6K4', 'WNK', '29Y', 'OL2', 'S9A', 'EXF', '0OO', 'ZFS', 'QRR', '5Y7', '65R', '7GI', '6AE', '4LO', 'JK3', 'D4Z', 'HOW', '50D', 'WQK', 'OJL', '052', 'BI3', 'T0X', 'L6A', 'RU9', '76A', '0KF', '63E', '16W', 'D42', '0OK', 'F4N', 'LC0', '47W', 'CK8', '900', 'EK2', 'ZZL', 'G8B', 'KI7', '10K', 'SKI', 'C0N', '4HZ', '2TT', 'G1W', 'HHW', 'TZ1', '2WK', 'EGJ', 'VO7', '4Y0', 'VSF', '72B', '7G7', 'MIH', 'R61', '45B', 'VSY', 'LHL', 'A98', 'WTJ', 'G0E', 'OWN', '13L', 'ODH', '2WE', '306', 'W47', 'SW5', 'RI8', 'EQW', 'A1K', 'CQU', '6S1', '4QE', 'K9T', 'QYK', 'C07', 'ZO6', 'F88', 'YRA', 'A28', 'OD1', '9YQ', 'KSR', '6CB', 'N5U', 'FGF', '4WD', '3E8', '63A', 'MS7', 'IEO', 'HBM', 'DFN', 'X8D', 'AY4', '9YE', 'B8L', 'KZL', '3Z6', 'S22', '19P', 'X20', 'KGZ', 'VFS', 'B4W', '4VF', '46K', '8X7', 'LN4', '15T', 'XV0', '7X8', '048', 'GW8', 'WG1', 'HOK', '3O0', 'TIY', 'YTX', 'LIB', 'BI4', 'AK5', 'SJL', '3C9', 'CWT', 'CCX', 'MH4', 'KHE', 'MK2', '03Z', '8IL', '934', 'OD4', 'TBN', '79O', 'YM7', 'LZM', '633', '8EN', '3T8', 'O8Q', 'KHC', '0F9', '01P', 'S8W', 'VEN', 'WGF', '3O4', 'R0N', 'A4N', '50Y', 'TK5', 'KQK', 'N3F', 'EKH', 'XFE', '92P', 'FHX', '1Y6', 'XK9', 'HB9', 'NJV', 'YFV', '9IV', '2NQ', 'V81', 'FMK', 'X96', 'MWL', 'KF1', '9HB', '3HN', 'SC9', 'SAV', '0JH', 'SCJ', 'JL2', 'LS4', 'T8L', '9Z2', '04L', '6P6', 'T3E', 'QD2', 'LO8', '349', 'R78', 'DUI', 'RQ9', '422', 'SLY', 'LNH', '07U', 'SQP', 'F87', 'G4W', 'KZM', 'F6J', 'Q8B', 'DKG', '80E', 'FZ5', 'N1A', 'LZ4', 'Z20', 'ML8', '3RA', 'G97', 'J30', 'SW7', 'TO7', '3OV', '73Q', '3OK', 'BXM', 'Y7W', '537', 'QM2', 'DRG', 'L8I', 'A5Q', 'F18', 'X0A', '22Z', '6Q1', 'F46', 'QL7', '34W', '6A7', '3DX', '79D', '4K4', '6VK', '88O', 'AUH', 'W8U', 'A3F', 'F4C', 'RVQ', 'UGX', 'LPZ', '4KT', '4MH', 'AYS', '3YT', 'ESJ', '3RT', 'Q8K', 'ZLE', 'EG7', 'HKQ', '1M3', 'SD5', '1PP', 'HKI', 'M5W', 'SWK', '21O', '207', 'A9E', 'U6S', 'XY3', 'AAK', 'JRE', 'SNB', '19Q', '8GV', '6NB', '519', '0U0', '91X', '2C4', 'WQ2', '3DC', '9WU', '54F', 'IQY', 'R2S', '1G0', 'BGE', 'KZI', 'AIZ', '70T', 'PP2', 'BD4', 'LZ9', 'IRG', 'ABQ', '2WC', 'FS9', '9Z4', '39P', '38G', 'ERZ', 'G6J', 'KWP', '1DT', '0WH', 'C5W', 'OL8', 'YCF', '1HW', 'UES', '5E5', 'FH5', 'UEX', 'F3Z', 'Y3O', 'N7K', 'D05', '3V0', '03P', 'S4Z', '0NT', '5WE', 'LXX', 'KRL', 'QRD', 'LZ3', '6PV', 'SB2', '1N3', 'BI2', 'SV5', 'UPX', 'N6Z', 'DF2', '4DL', '38R', '62E', 'C9Z', '3UR', '3ZC', 'HQB', 'LI4', '9WS', '55E', 'CJQ', 'V04', '9OF', 'FJ0', '4KA', '86L', '8KF', 'ZXP', '09H', 'WEG', '8TN', 'J4B', 'LJF', '73T', 'QXZ', 'SCQ', '0JL', 'A6H', 'ZYQ', '6U1', '1LT', 'BYL', 'LYG', '5B4', 'CK5', 'P06', '7CU', '3FF', 'HMD', 'SVJ', 'J27', 'JWN', 'OFG', 'CG9', '507', 'PBU', 'M4P', 'YY9', 'RGY', 'SU7', 'JK2', '58C', 'G62', '7TW', '0XF', '42P', 'N92', '400', 'A9B', 'F8S', 'G5X', '8DK', 'VRU', 'XIP', 'G6I', '3FN', '42I', '34L', '8R7', 'ZO8', 'J60', 'XI2', '0WR', 'S4K', '99K', 'JZY', 'H96', 'OFT', 'W2P', 'RV6', 'WJ9', 'NBS', 'IH7', 'EU4', '0SY', 'JZW', 'YFY', 'C5N', '589', 'C1I', '7XH', '21I', 'C73', '2HV', 'H3N', '68R', 'KWT', 'XWA', '0J9', '044', '66A', 'LVD', 'VZJ', '32W', '1P5', 'VVT', 'CKO', 'IIM', 'SMV', 'TQ1', 'W19', 'FCP', '3NG', 'OKZ', '50W', 'FQD', 'DWT', '466', '55U', 'S0L', 'ABJ', 'LH0', '9XO', 'G6A', '4L6', 'G54', 'O4B', 'P9K', 'D4Q', '84P', 'N42', 'LCD', 'H0K', '5W3', '5Y4', '50E', 'LKQ', '5KW', '0NF', 'ANK', '5SC', 'SVE', 'KF6', 'GS3', 'XA0', '0BQ', 'JBI', 'A7N', 'YY3', '4QG', 'O92', 'H3Q', '83P', 'RW4', 'O2K', 'R2E', 'P7C', '8LU', 'UNE', 'KWY', 'HGK', '34U', 'SM9', 'IWU', 'K82', 'RW3', 'X11', 'IE0', '63K', 'SSY', '63I', '75E', 'E62', 'KCI', 'X9G', '6T3', 'F62', '292', 'NYX', 'FVC', '27D', '4H5', '8QZ', '4EF', 'A06', 'PDX', 'WCX', '337', '50J', 'LBB', 'WXQ', 'VM1', '925', 'HB4', '9I8', 'O4U', 'AY7', 'RKW', '7AA', 'LIF', '1IM', 'JYZ', '45Q', '6Z5', 'JWE', 'A53', '5O4', 'PWU', 'SNV', 'SQ8', 'WF7', 'U0C', '2TA', 'G5T', 'MDI', '09J', 'ET8', '8DJ', 'LI2', '7LV', 'KSM', 'AK2', '49J', 'KY9', 'F0H', '5TL', '91L', '86C', 'TCE', 'RQS', 'K3R', '3WA', 'OQ2', 'R4S', 'CQE', 'RR9', 'X8E', 'X3W', '1JX', 'XK3', 'EKT', 'A7H', 'NPZ', 'EFP', '6U7', '9YS', '8FU', 'X46', '8QH', '6TE', 'G5C', 'ADP', 'AM7', 'IGV', '9N8', '4HW', '3IU', 'B4K', 'XTT', '3I7', '5B1', '0T2', '1P6', 'PZW', '8R4', 'PZO', 'XL8', 'J88', 'I6P', 'VSH', '6TP', 'NZ4', '7O3', '8N8', 'AJK', 'N1Q', '5W8', '5U3', 'KXY', 'PJC', 'P4N', 'BYU', '50O', 'PG0', '5O7', 'OKO', 'ESK', 'FMY', 'N96', '1K3', '05B', 'P38', '107', '6XT', '12C', 'JZJ', 'DJW', '5E6', 'RTJ', 'C92', 'DT4', 'BA0', 'NM8', 'PMU', 'X9P', '31X', 'RSU', 'VS0', '1BR', '7L0', 'A9T', '093', 'P7N', 'N3X', 'IV7', 'AUE', '981', 'FYV', 'X3R', 'LTJ', 'TZ0', 'B8Z', 'K1H', 'HRM', '84M', '9TO', 'R6M', '3LH', 'K8K', '11K', '92J', '8NZ', 'J0P', '65U', 'N1J', '3SM', 'A4Q', 'VOY', 'EO5', 'NJ6', 'FMD', 'ZW3', '5R1', '24V', 'KK7', '08Z', '6OJ', 'P40', 'UGK', 'G4K', '85S', 'PFY', 'BRY', 'C9R', 'XXF', 'IR1', 'HJ9', '1SK', 'M5V', '6ZF', '1E0', 'V62', '831', '61U', 'LD5', 'ZRM', 'WXH', 'HBD', 'F9N', 'QX2', 'WZ8', 'EMU', '8CG', '54R', 'B6I', 'F48', 'NQ1', '19E', 'HHQ', 'XTI', '8D6', '6S3', '6SH', '80H', '1DR', '9DB', 'F8Z', 'DG7', 'LO5', 'AWO', '6SN', 'N5B', 'N6N', '8ST', 'Q7Q', 'VK2', 'YDJ', 'LXG', 'Q7M', '0WP', 'IE4', 'FKY', 'N9F', 'LGV', '7GS', 'E2L', 'S19', '6HF', '9EM', 'W40', 'L87', '1RO', 'RQU', 'H3K', 'RLC', '3HQ', 'B97', 'L0P', 'P5O', 'OO7', '49B', '7GZ', 'P9J', 'H9K', 'GUK', 'D31', 'UUF', '0JG', 'LN3', 'O0H', 'IXM', 'J2Y', '0K6', 'DHC', 'CV4', '3KZ', 'HUL', '7X1', 'MFZ', '7X6', 'AQT', 'N29', '0XP', '98A', '1QG', 'WG8', '34Y', '7PY', '1B5', '46G', '6UJ', 'KQE', '4VC', 'GX3', 'X65', 'GS2', '0G3', 'FMW', 'C0M', '740', 'B5Z', 'CQW', 'A5W', '90T', 'HO8', 'XUZ', 'GJ7', 'LB8', '980', '3EH', '276', '7GY', '6SD', '816', 'N9J', 'GDW', '7KG', '1OB', '1RS', 'D1A', '03Q', 'GOD', 'ATK', 'ER8', '2VL', '96M', 'KQZ', 'R7B', 'T1L', '8QT', 'LZA', 'DT5', 'I1P', '5O1', 'JZX', '8OU', 'LSV', 'F1B', 'QGY', 'XKU', 'IDW', 'Z87', 'RK2', '7IF', 'ZTV', '1QN', 'CIY', 'OBY', 'AY3', '4TW', 'FLS', 'KHD', '54S', '2K2', '8ZK', '5LK', '994', 'HJK', '18Z', 'Y8H', 'VVX', 'IJB', '1GK', 'WPB', 'JHK', 'K81', '6ZZ', '6U2', '0S9', 'D7D', '2VU', 'WPX', 'DTJ', 'R6N', 'N82', '1PU', 'R0T', 'A03', '7IQ', 'FAV', 'O97', 'G41', 'W9X', 'EFQ', '533', 'LCQ', '31K', 'GDK', 'SLQ', '3VD', '6VM', '1NX', 'X3Y', 'RNU', 'R5Y', 'BRK', 'QGR', '0BY', 'KFD', 'VY1', '5RC', '530', 'QJZ', 'HSJ', 'B6Q', 'YEX', 'PFQ', 'SVD', '57N', '046', '90Z', '46A', 'R7P', 'JVE', '3HJ', 'TSK', '1J4', 'A5E', '4T3', '1KP', 'X7Y', 'B4Q', '477', 'KKR', 'TSW', '7XR', '17G', 'X87', 'Z60', 'HKC', 'JVT', 'KA2', '74O', 'KMP', '19S', 'G98', 'FZO', 'F97', 'EYQ', 'I5G', 'SJV', '0TB', 'XWW', '1J3', 'AWX', 'OXW', 'ZS3', 'RQL', '1BJ', '6RG', '8XK', 'M4I', 'L1W', '0YO', 'N9L', '4EL', 'GYW', '6UE', 'B4V', 'T12', '4CW', 'X3G', 'MT4', '83H', 'JPZ', '74F', 'QH9', 'AEQ', 'H7R', '9JS', 'B6H', 'LW4', '937', '8MQ', 'LX9', '79Q', '9QT', '0US', 'F4B', 'I85', 'QYW', '0WA', '199', '3VC', 'KSC', '4L7', '6XP', '799', 'KZP', 'MPZ', 'LUE', 'O9C', '4RK', '3QW', '0F0', 'QT9', 'UIK', '0OA', 'XVI', 'HVY', 'V5W', '6CP', 'SR4', 'Z2M', 'QY2', 'FKT', '0S8', '6K2', 'K1B', '6R0', 'N3O', '6HK', 'AOW', '4GF', 'JRT', '82A', '3JB', '6YN', '3SB', 'MFP', '1AU', 'E0P', '9ZB', '456', 'IQO', 'VQE', 'OND', 'NX0', '844', '5N3', 'VBS', '5WR', 'EK6', 'S03', '62K', 'MFE', 'LQ5', 'OLO', '4E2', 'YM5', 'DKI', 'L0D', 'A4T', 'CG7', 'WTI', 'JQW', 'X2M', 'UN4', '1N9', 'RJ5', '70W', '91O', 'FCQ', 'EAQ', 'CK2', 'IHX', '2TR', 'ELZ', 'CK4', '1FN', '8IW', '0NR', '7AJ', 'AHK', 'USF', 'MI5', 'KSE', '039', '7X3', '8V7', '5PW', 'LOT', '4VZ', 'SOJ', 'GVP', '37O', '6N9', '308', 'E2C', 'S4R', 'BPK', 'QTX', 'UJC', 'JVP', 'ZIG', 'V5J', '2WF', 'QCT', 'QC0', 'JNF', 'PHU', 'QFE', 'EX4', '8XE', 'X9S', '55Y', 'TAK', 'ITI', 'VSE', 'AWR', 'H1N', 'F47', '5QO', '0SE', 'JGM', 'IRB', 'FKN', '0VE', 'B5W', 'HGQ', 'YK7', 'B7W', 'U73', 'FE5', 'G4T', '1PF', 'O17', 'CHU', '0JF', 'X75', '2V1', '3UL', 'ZZQ', '48B', 'U4N', '2YE', 'LTI', 'NQ5', 'YB4', 'MVS', 'HY7', 'BWY', 'N8L', 'FU9', 'JYG', 'RXQ', 'O1K', 'TZY', '0EI', 'AVK', '04K', '583', '573', 'FKB', 'QBE', 'T77', '4DN', 'RI9', 'KJ7', 'Q7K', 'M8Z', 'NKW', 'N4U', 'VTA', '3K7', 'HDT', 'GJJ', 'FZC', '4DQ', '3FE', 'GIG', '1VI', 'NB5', 'F4J', '1M8', 'X5E', 'X3K', '4TT', '4QZ', 'V5T', 'HH8', '3I6', '106', 'I46', '72L', 'YFS', '2IE', 'F9J', '35R', 'FWU', '3Z1', 'MT8', '7XO', 'UO5', '5EZ', 'A25', 'PQA', '9OL', 'Q8Q', 'VY4', '992', '6K5', '971', 'B90', '4VG', '4AU', 'A9U', 'FPX', 'Z83', 'M5D', 'ULV', 'UE9', 'HK1', 'G7T', '571', 'WT3', '5L4', 'B7B', 'AM8', 'GUI', 'HCK', 'KEC', '9DP', 'SMR', 'Z0W', '8CD', 'AWN', 'G0U', 'XGQ', '0OL', 'JN5', '1PH', 'EK5', 'FZP', 'D1E', '7A7', '85X', 'IK1', 'XIZ', 'H7X', '60E', 'AQ5', 'NTW', '2NK', '4TV', '9YZ', 'U0N', 'G11', 'PQ8', 'UQX', 'A0T', 'B2D', 'DQX', 'H72', 'FZF', '8RH', 'BFK', 'O10', 'EK0', 'T28', 'EWH', 'M57', 'OLP', 'E26', 'E2U', 'J87', 'QIA', 'YVQ', '55F', 'AK3', '8ON', 'MVG', 'EE4', '6TT', 'X63', 'AFW', 'D6Z', 'J2I', '40M', '2JZ', 'DJK', '8ZN', 'FMM', 'SJM', 'A7O', 'M77', 'UAU', 'RYW', '37W', 'EUI', 'Q8J', 'R6K', '9WX', '45K', 'P3Y', 'A3W', '1UH', '1N8', '0JA', 'SJJ', '90N', '99M', '26D', '6YL', 'VQP', 'X3N', 'VAR', 'FQG', '42J', 'C95', 'S25', 'LS5', 'A5K', 'S59', 'FJY', '54P', 'LUN', 'GAB', 'F7D', 'X37', 'I19', '7G8', 'H83', '8WH', 'P7A', 'WFD', 'RQ5', '5B2', 'CMG', 'SV4', 'Z0B', 'QS0', 'Z3R', '71N', 'JU8', 'RKZ', 'S93', 'O06', 'CVQ', '4L5', 'RCM', '2CH', 'Z85', 'SR8', 'T9N', '3RF', '6K0', 'L7A', 'RVU', 'QYH', '4ZH', '0RS', 'YUN', 'RK5', 'JWQ', 'SWM', 'JRW', '0SU', '03X', 'SJ0', 'DF6', '5VS', '575', 'I73', '69C', 'LXS', '3WO', 'H6K', 'IS4', '3T9', '2SB', 'HK7', '6SO', 'NKT', 'QYB', 'TXQ', 'KSA', '0SR', '8TK', 'EVL', 'X59', 'OAW', 'S30', '2WI', '4YW', 'JWS', 'OFQ', 'FQJ', 'SZL', 'EAE', 'WAZ', 'DFQ', 'XJ1', '4GD', 'A9K', 'JUW', 'XIJ', 'PM1', 'U0Q', 'BYP', 'O8Z', 'ALH', 'LS1', 'REB', '0YH', '8GY', 'D58', 'P2V', '31J', 'Z31', 'RWE', 'VTD', 'KAO', '25Z', '8BH', '0UN', '3P6', 'L5G', 'SQZ', 'BWI', 'O2H', '631', 'T3X', '8O8', '4ZQ', '8X5', 'P39', 'JMB', 'N6K', 'B18', 'WIQ', 'SCF', '09Z', 'B7S', 'LS7', 'FZR', 'NYI', 'DXV', 'AXI', 'SOV', 'U9P', '3D8', 'JUP', 'UNM', 'GO7', 'OYB', '2HX', 'E9Z', 'AGX', 'MYC', 'FPZ', '56Z', '3CI', 'HK8', '5CN', 'X8I', '16K', 'MK9', '0SB', 'RHT', 'GS7', 'PP1', '09K', '664', '60D', '6LF', '4VB', '0J3', 'KXZ', 'J9G', 'MRI', '4K0', '8ZF', '3D9', 'EM7', 'GC6', '8KQ', '9E1', '3IF', 'E94', '9IO', 'ZZF', 'N8U', 'ES4', 'G68', '89E', 'L0I', '15G', 'GVD', 'KEJ', 'NIO', '08G', '0W7', 'YDA', 'Y8C', '5FI', 'XU1', 'Z19', 'WCJ', 'LCT', 'T74', 'DI1', '7FM', 'L1H', '386', '76Y', '8QW', 'HHN', 'T6E', '1YG', '5BP', 'B6E', '9O2', 'S5M', 'SCZ', '7KA', '98M', '7LY', 'VVQ', '7X2', 'TOJ', 'STJ', '8BV', 'J19', '1F8', 'ZZY', 'XIX', '2QK', 'OOD', 'ERK', 'LCJ', '1C9', 'KVJ', 'O9L', 'MK3', 'LKB', 'N7Z', 'EZR', 'SUU', 'Z63', 'E86', 'AA0', 'FRZ', 'YY5', '3D7', '0H2', '7FC', 'VWN', 'ZYW', 'S4N', '3SG', 'SX8', 'KBI', 'EKK', '4KK', 'ELW', '06F', '51W', '3XM', 'WAK', '5QI', 'BI8', '9I2', '1FV', '7VH', '5LS', 'G4Q', '585', '43A', 'OCJ', 'W5W', '1OA', 'NG2', 'GD5', 'HPP', 'XHS', '3RH', '6MV', '3I3', 'B4Y', 'KGL', 'E71', '31V', '3RE', '71A', 'EK7', '2VV', 'NHI', 'B91', '7LK', 'I90', 'SU9', 'IHZ', '2A8', '984', 'IE6', 'EMH', 'J3Y', 'H80', 'XQQ', 'VFB', 'A17', '8FR', 'ADN', 'KH5', 'K0X', 'W2T', 'X02', 'FDH', 'AU5', 'F6M', 'SVT', 'OHK', 'ZGY', '1H4', '330', 'YMX', 'RH8', 'T1Q', '9E4', '4PV', '2K7', 'VX1', '92M', '00J', 'AQZ', 'Q1A', 'AOK', 'YSO', '255', '9J4', 'VX2', '1KO', '5WH', 'RKK', 'AK4', '9X4', 'FL4', 'QQJ', 'PE5', 'DVD', '2OL', 'AA2', 'RF4', 'X4B', '8H0', 'LID', 'VJH', 'L1N', '4YK', 'SM5', 'BJG', '93J', '6SC', 'MM8', 'DY4', 'N83', 'RWN', '4EJ', 'EML', 'G0Q', 'HO5', '2VW', '626', 'GJA', 'A3H', '6J9', 'Z8O', 'QYZ', 'BX1', '793', '2WG', 'XL7', '887', 'AQW', 'CZ4', 'P08', '43R', '8MY', 'BMI', 'EZE', 'K06', 'G8H', '0X5', '29X', '371', 'E2X', '4HK', 'A8K', '3Z3', 'X9J', 'C58', '2KC', '5T2', 'J99', '99V', 'AKI', 'E0M', '8GX', 'Q55', 'SQE', 'UOW', 'X9V', '551', 'HAU', 'DWF', 'X6A', 'STI', 'RU5', 'PGJ', 'BAX', 'VYN', 'QAQ', 'HKJ', '36O', 'H4N', '553', '33A', '56H', '4F6', 'QP1', '3NE', 'ABO', 'ANW', 'XU2', 'C6O', '7RO', 'PQC', '0R4', '893', '9HP', '9EJ', 'FRT', 'B9K', 'ZRU', '19B', '3JA', '2I5', 'B6B', '3NL', 'F8R', '95U', 'QWS', 'LJE', 'V0K', '4VJ', '4ZR', 'SVG', 'A0Q', 'QZW', 'ROY', '1WS', 'WGZ', '1RU', '5Y3', 'QOP', 'B8I', 'GO4', 'LM3', '3RL', 'P17', '0T8', 'HGF', 'XR1', '0SD', 'C62', '24K', 'Z14', 'YIQ', 'GJK', 'CC9', 'PDY', 'UP9', 'YNZ', 'RXN', 'OE8', 'BMU', 'LGF', '0UV', 'RKN', 'JAK', '6L4', 'OBW', '3L0', 'KRE', '42C', 'OVI', 'ESQ', 'B6Z', 'A6X', 'K47', '9JO', 'MYF', 'JNK', 'UCN', 'R05', 'EQH', 'LWG', 'GG5', '824', '3OU', 'HPM', '3O7', 'AG1', 'CQO', '8PT', 'MBW', 'LG8', 'EZB', 'RJ2', 'MWU', 'EXZ', '4YX', 'FXG', 'T3I', 'LZ8', 'I3H', 'REF', '4V8', 'Q0B', 'NL4', 'G96', '6TD', '07Q', 'P41', '2IX', '4UB', 'BMW', 'AEE', 'STL', 'WVI', '9BD', '3UO', 'XHV', 'MBP', 'KA4', 'RQZ', 'RQE', 'U3E', '2V9', '17P', 'IBI', 'RTZ', 'H7O', 'Q58', 'LZD', '8H1', 'DQ4', 'HNZ', '90F', 'G9E', 'RQQ', 'D1D', 'K0Z', 'L1G', '1AM', '48K', '5B3', 'DJQ', '9NX', 'P5C', '3H8', '939', 'HOT', 'V0L', 'I45', 'QRW', 'KJB', 'ADE', 'X84', 'E1D', 'ZYT', 'N7W', 'V6B', '2P5', 'IZZ', '61K', 'SKE', 'SJX', '39G', '91H', '1RQ', 'OXM', '90E', '8C5', 'Y56', 'IKD', 'H5K', '70S', '4ZJ', '8MB', '7XW', '1OO', 'Q5Z', 'O1S', 'YT8', '1Q4', '67T', 'L8V', 'QUF', '6GD', 'GK6', 'G3B', 'MFQ', '55M', '5I1', '7YS', 'KD6', '4LY', 'A3Q', '0NV', '5P8', 'RG4', 'PP0', '5BE', '65A', 'SB5', '0S7', 'P3J', 'VEQ', 'T2F', '1OC', '1LB', 'FNI', '1IF', '0NU', '9ID', 'PQB', '6XK', 'NKE', '960', '2OO', '4GU', 'L0E', '7UX', 'DJH', 'CC3', '8MT', 'ZYU', 'W49', '7QU', 'RFZ', 'OU2', 'N76', 'N9Z', '499', 'ZC3', 'O8W', 'QP4', 'NZF', 'V1Y', '1IZ', 'LB7', 'Z84', 'AQY', 'M0Z', 'KWV', 'XA4', '6XE', 'B11', 'TL7', 'IAQ', 'INR', 'KJV', 'SB0', 'YIT', '9KI', 'D36', 'STU', '3NV', 'UNQ', 'SJS', 'YDK', 'Q98', 'EX6', 'Z02', '47I', '3FP', '1WU', '81C', '4ZG', '0BX', '6ZV', '4Z5', 'OW6', '7KU', '4SP', 'W32', 'R6D', '6Z7', 'PPI', 'CT9', 'GK5', 'LEV', '6BE', '8Q5', 'AM6', '0ON', '2A6', 'AQ2', 'FKO', 'RAJ', 'L9A', 'RRC', '5JA', '50V', 'IHP', 'N5R', 'W3I', 'P91', 'MMD', 'AUW', 'AWE', 'S9K', '0O9', 'W9Z', 'G0H', 'FYW', 'SQB', 'YTP', 'A0H', 'R7W', '6LQ', 'XBD', '90B', '7MY', '3WK', 'O35', 'KRW', 'O1V', 'X62', '4RB', 'A5G', 'OPW', '0G2', '2NS', '3QY', 'LS3', 'X42', '0UW', 'OV0', 'G95', '1QK', '2WH', '59T', 'TWK', '66P', 'NRM', '320', 'U8J', 'T6X', 'SW8', 'FZW', 'PRC', 'QY8', '3QT', 'JAU', 'IYZ', 'SQQ', 'QQM', 'IED', '3YY', '0TA', '4KH', 'BEZ', 'NY0', 'PCG', 'YDI', 'C94', 'R39', 'T4O', 'ZS4', 'VRM', 'GMG', '7X4', '4DJ', '9M3', 'R6I', 'ERW', 'OE5', 'RUT', 'V58', 'OH8', '6BZ', 'Q6E', 'X43', 'X9M', 'QEW', '2AN', '4WE', '3O8', '58V', 'OD2', 'IER', 'LZ7', 'KRK', '6K1', 'GIN', 'XL9', 'W3C', '6E2', '3GU', 'X5G', '0VM', 'FBL', 'X35', 'YIY', '3OA', 'ZAT', '4E1', '75X', 'UX2', 'QCR', 'RCH', 'FMJ', 'DD8', 'C9U', 'IGJ', 'OOO', 'NZS', 'X1N', 'X76', '4R0', 'FCZ', 'ESW', 'QUU', 'GFJ', 'O1Y', '1ST', 'B10', 'JWK', '0NL', '5I4', '084', '0F2', 'NZ8', 'GMW', 'E3U', '3IP', 'FYH', 'E7M', 'KQW', '6QX', 'N4N', '81G', '9ZS', 'L66', '6JS', 'H3H', '6DP', 'K3D', 'E6W', 'COM', 'X8G', 'L0Z', 'MI1', '29B', 'HJ0', 'Y3M', '0C0', '924', 'QYT', 'F8E', 'E78', 'B98', '3Q0', '1IW', '2AI', '22L', '3U5', '4F2', '71L', 'Z71', '34O', 'LVL', 'B1L', '4LH', 'U35', 'XOJ', '2V3', '3J7', 'P4G', 'E8D', 'GGY', '8QE', 'UWM', 'FLL', 'L80', 'E4V', 'AJG', 'OOJ', 'WAU', 'YIW', '11G', 'BRW', 'E5M', 'O19', '0VH', 'TBS', '6UX', 'HRZ', 'GK4', 'ZUO', 'B7R', 'YQT', '0C4', 'LKT', '529', 'HGH', '35H', '041', '8KZ', 'L11', '6C3', 'OSV', 'E2R', 'N45', '353', 'XL6', 'RHH', '8C1', 'AQ6', '98G', '396', '6BU', 'WBI', 'EFV', 'PFO', 'PDS', 'M4X', 'VFA', 'H91', '7XN', '3UP', '3U6', '8RC', '25Q', '7CP', 'E75', '8XH', 'R9P', 'T3B', 'RKD', 'ND2', '985', 'KSK', 'RJ8', 'UCE', '6ZG', 'KUV', 'X39', 'A7X', 'Q4J', '3Q5', 'BW8', '0CE', '3XK', '710', 'WHQ', '12Z', '7G6', 'KRJ', 'KWJ', '2V2', '1QM', 'R4L', '0X2', '0UJ', 'X3A', 'H7F', 'HHT', '8ZZ', 'P78', '63L', 'UCM', '78L', 'YM4', 'GK3', 'L9S', 'SLS', '63B', 'UGJ', '2K0', 'Q9J', 'B4E', '27Z', 'IKC', 'W3F', 'SJG', 'MPY', 'KSL', 'IPV', 'JIN', '1J2', 'PKE', '3EL', 'FAL', '9K8', 'MMW', '6QB', 'VRZ', 'CQ7', '1Q3', 'B45', '8M8', 'V7Y', 'I94', '608', '6R1', 'BYM', '9VV', 'W4G', 'CQQ', '859', '9EO', '1FM', '7GG', 'GXH', 'UUB', 'RK8', 'E0S', '0BZ', 'CFK', '1SU', 'DYK', 'RKQ', '8JC', '5QM', 'FAP', 'D6W', 'PVT', '39I', 'D23', 'H82', '55J', '7KX', 'HK5', '3HT', 'W2K', 'BLZ', '4US', '0J8', 'IGS', 'FKL', '62M', '4YM', 'S5I', '5U6', 'Y5Y', 'K8A', '741', 'YPW', 'NZU', 'K7S', 'HB1', 'MJF', '0NH', 'OSZ', 'HHL', 'M5J', 'GMQ', 'PY8', 'MLW', 'ZHY', 'H7L', 'GIK', 'X72', 'W3W', '42K', '1SW', 'JYM', 'TMU', 'L9L', '5E1', 'LZ5', '6FD', 'CWS', 'I74', 'KHQ', 'URW', 'TL0', '5CP', 'UIM', 'F76', '22K', 'G5K', 'IQB', 'RKH', 'HK3', 'LMR', '3YR', '8MN', 'V1G', 'ZXL', 'GSH', 'CKK', 'D5P', 'O1Z', '6UI', 'MVE', 'SV8', 'Y27', 'XIY', 'K1E', 'GV0', '64V', 'FPU', 'S1Z', 'OCG', 'N69', 'L8Y', 'H1K', 'AM9', '0VU', '5Q2', 'OWB', 'J72', 'KS1', 'LI9', 'UWP', 'VYP', 'OFI', '2Q7', 'UMN', 'O98', 'X4G', '085', 'J82', '1B6', 'VSG', 'LGW', '5W7', 'P2B', 'ZSO', '03C', 'A1N', 'P2X', 'N7Q', 'QPP', '630', '774', 'PO6', 'U7E', '3KC', 'F9Z', 'V84', 'N20', '3K6', 'ML9', 'MIX', 'C70', '5T1', 'MXE', '3WJ', 'RQT', '933', '2SH', 'PGF', 'AN2', 'DB8', 'SCX', 'SQ9', 'HIZ', 'SO7', 'I39', 'LIC', '6TS', '325', 'KX0', 'LMM', 'EDD', '7LI', '4YV', '0SV', 'JNO', 'CT6', 'G4J', 'FSE', 'R5S', 'MFR', 'O22', 'ZYV', 'FS7', '84X', 'FLW', 'VYH', 'YK4', '7GK', 'SC8', 'SLV', 'QNR', '54E', '18R', 'MTZ', 'UKI', '8BY', '24A', 'CQ0', '76Q', 'YY6', '1QJ', 'ICV', 'PKB', 'O1R', '8AM', 'IIQ', 'KJQ', 'YM6', 'P5K', 'BDY', 'F8Y', '2QU', '4MG', '1JV', 'B5T', 'O38', 'CJN', '88A', 'MSQ', '0KO', 'TVW', 'MYU', 'VK5', 'QUE', 'AM0', '4EK', '6K7', 'WAP', 'M54', '4B7', '274', '3TA', 'A8Q', 'KHT', 'V25', '0C7', '071', 'SK8', 'MP7', '5U5', 'E7N', 'LRS', 'M2Z', '3RJ', 'PO5', '15V', '88C', 'B43', '582', 'CQ6', '6AF', 'L8D', 'AZ5', 'UOH', 'H6X', 'PXK', '50R', 'IPW', 'FZL', '79S', '92D', '5YS', 'LHZ', 'YW5', 'X2K', 'TKB', 'QWN', 'JYO', 'BX7', '13J', 'V5E', '6KD', 'X6D', '685', '19Z', 'N6U', 'A4W', 'WYF', 'SB6', '3NW', '4QV', 'E56', 'Q8W', 'L7I', 'HYM', 'N8S', 'YXT', '404', '84S', 'N66', 'RHW', '68U', 'LI6', 'HYZ', '05J', '3JW', 'X9Y', 'N86', 'E8K', '0B9', 'EU2', 'B49', 'M3Y', 'S7S', 'AK6', '7MP', '76P', 'L2G', '6UH', 'MUH', 'SX7', '6UG', '9G5', 'R34', 'IDK', 'R49', 'LS2', '6VL', '4C9', '5H7', '92Q', 'AUT', 'DQO', 'Q6G', 'T4C', '31S', 'Z04', '26K', 'YSI', 'NSO', 'PFP', '676', 'L9G', '84U', 'E47', '9NH', 'A7Q', '62O', 'P4O', '8MK', 'H2E', 'LOW', 'QGI', 'ZXC', 'QK0'},
    )

def test_ccd_name_sorter():
    assert sort_ccd_codes({'G', 'G25', 'CPG', '5GP'}) == ['CPG', 'G25', 'G', '5GP']


def test_morgan_fingerprint():
    reference = "4P///wAIAAARAAAAAAIAXQYUuFEAGhwdAjS5A40BNPSKeHY="
    fp = get_morgan_fingerprint(Chem.MolFromSmiles("CCCCOOO"))
    assert fp == reference


def test_rcsb_info(cif_4ci1):
    reference = ("2013-12-05", 2.98, "X-RAY DIFFRACTION")
    rcsb_info = extract_rcsb_info(read_mmcif_file(cif_4ci1))
    assert rcsb_info == reference


def test_get_ec(cif_3g32):
    reference = "3.5.2.6"
    extracted_ec = get_ec(read_mmcif_file(cif_3g32), ["A1"])
    assert extracted_ec == reference


def test_convert_chain():
    reference = {"A1": "A", "B1": "B"}
    assert convert_chain(["A1", "B1"]) == reference


def test_chain_mapping(cif_assembly_1qz5):
    reference = {"A1": "A"}
    assert get_chain_mapping(cif_assembly_1qz5) == reference


def test_entity_type(cif_assembly_1qz5):
    reference = "NonPolymer"
    assert get_entity_type(cif_assembly_1qz5, "A1", "500", "KAB") == reference


def test_covalent_linkage(cif_1qz5):
    reference = {"GLU:A:C", "HIC:A:C", "HIC:A:N", "GLY:A:N"}

    assert (
        set(
            get_covalent_connections(read_mmcif_container(cif_1qz5))["covale"][0].keys()
        )
        == reference
    )


def test_bsite_metal(cif_assembly_5a7w):
    reference = {"MN,1356,A1"}
    pdbx_file = read_mmcif_file(cif_assembly_5a7w)
    atm_array = get_structure(pdbx_file, model=1)
    prot = atm_array[struc.filter_amino_acids(atm_array)]
    metal = atm_array[atm_array.res_name == "MN"]
    assert extract_bsite_metal(metal, prot) == reference


def test_bsite_water(cif_assembly_4ci1):
    reference = "HOH,2006,B1"
    pdbx_file = read_mmcif_file(Path(cif_assembly_4ci1))
    atm_array = get_structure(pdbx_file, model=1)
    water = atm_array[(atm_array.res_name == "HOH") & (atm_array.chain_id == "B1")]
    prot = atm_array[struc.filter_amino_acids(atm_array)]
    assert reference in extract_bsite_water(water, prot)


def test_ligand_hydrogenation(cif_assembly_5a7w, sdf_5a7w_lig):
    pdbx_file = read_mmcif_file(cif_assembly_5a7w)
    atm_array = get_structure(pdbx_file, model=1)

    lig = atm_array[
        (atm_array.res_name == "35M")
        & (atm_array.chain_id == "A1")
        & (atm_array.res_id == 1355)
    ]

    reference = next(Chem.SDMolSupplier(str(sdf_5a7w_lig), removeHs=False))
    mol = add_hydrogen_to_lig_array(
        lig,
        "c1cc(ccc1C(=O)Nc2ccc(c(c2)c3cc(ccn3)C(=O)O)O)O",
        lig_resn="35M",
        chain_mapping={"A1": "A"},
        add_h=True,
    )

    assert len(mol.GetAtoms()) == len(reference.GetAtoms())


def test_find_missing_residues(cif_2y4i_system):
    actual = annotate_interface_gaps(
        cif_2y4i_system, protein_chains=None, ligand_chains=None
    )["ligand_interface_gap_annotation"][("C", "A")]
    expected = {
        "interface_atom_gaps_4A": 5,
        "interface_atom_gaps_8A": 39,
        "missing_interface_residues_4A": 0,
        "missing_interface_residues_8A": 0,
    }
    assert actual == expected


def test_read_mmcif(cif_1qz5_unzipped):
    assert isinstance(read_mmcif_file(cif_1qz5_unzipped), PDBxFile)


def test_get_all_bound_molecules(cif_1qz5_unzipped):
    assert list(
        get_all_bound_molecules(
            cif_1qz5_unzipped,
        ).keys()
    ) == [("A376",), ("A380",), ("A500",)]


def test_get_specific_bound_molecules(cif_1qz5_unzipped):
    assert (
        Chem.MolToSmiles(
            get_specific_bound_molecules(cif_1qz5_unzipped, residue_list=[("A", 380)])
        )
        == "[H]OC1([H])C([H])(N2C([H])=NC3=C2N=C([H])N=C3N([H])[H])OC([H])(C([H])([H])OP(=O)(O[H])OP(=O)(O[H])OP(=O)(O[H])O[H])C1([H])O[H]"
    )


def test_get_selected_residues_pdb_block(cif_1qz5_unzipped):
    assert (
        Chem.MolFromPDBBlock(
            get_selected_residues_pdb_block(
                Path(cif_1qz5_unzipped), residue_criteria=[("ATP", 380, "A")]
            )
        )
        .GetAtomWithIdx(0)
        .GetPDBResidueInfo()
        .GetResidueName()
        == "ATP"
    )


def test_generate_bio_assembly(cif_1qz5_unzipped, tmp_path):
    assert generate_bio_assembly(cif_1qz5_unzipped, tmp_path)[1] == {"A": "A1"}


def test_add_extra_loop_to_bioassembly(cif_1qz5, cif_1qz5_unzipped, tmp_path):
    block = gemmi.cif.read(
        str(
            add_extra_loop_to_bioassembly(
                cif_1qz5,
                cif_1qz5_unzipped,
                {"A": "A1"},
                tmp_path / "1qz5-processed.cif",
            )
        )
    )

    assert block.sole_block().find_loop("_pdbx_nonpoly_scheme.mon_id")[2] == "KAB"


def test_extract_rdk_mol_from_cif(cif_1qz5_unzipped):
    assert (
        extract_rdk_mol_from_cif(cif_1qz5_unzipped, "ATP", 380, "A")
        .GetAtomWithIdx(0)
        .GetPDBResidueInfo()
        .GetResidueName()
        == "ATP"
    )


def test_get_covalent_connections_2(cif_1qz5):
    assert sequence_mapping(cif_1qz5, "A1").resi.to_list() == list(range(1, 376))


def test_extract_small_mol_entities(cif_1qz5_processed):
    assert extract_small_mol_entities(cif_1qz5_processed)["A1"][0][0] == [("CA", "376")]


def test_short_noncov_peptide_detection(cif_6i41, mock_alternative_datasets):
    entry_dir = mock_alternative_datasets("6i41")
    plinder_anno = GetPlinderAnnotation(cif_6i41, "", min_polymer_size=10, save_folder=entry_dir)
    plinder_anno.annotate()
    df = plinder_anno.annotated_df
    assert len(df) == 1
    assert df["ligand_is_covalent"].sum() == 0
    assert set(df.ligand_ccd_code.to_list()) == {"LYS-ALA-ASP-THR-THR-THR-PRO"}
    # Note: chain 'B' is ligand = should not be in protein neigh list
    assert df[
        "ligand_neighboring_protein_chains_auth_id"
    ].drop_duplicates().to_list() == ["A"]


def test_synthetic_noncov_peptide_detection(cif_6u6k, mock_alternative_datasets):
    entry_dir = mock_alternative_datasets("6u6k")
    plinder_anno = GetPlinderAnnotation(cif_6u6k, "", save_folder=entry_dir)
    plinder_anno.annotate()
    df = plinder_anno.annotated_df
    assert len(df) == 1
    assert df["ligand_is_covalent"].sum() == 0
    assert set(df.ligand_ccd_code.to_list()) == {
        "ACE-TRP-TRP-ILE-ILE-PRO-ALY-VAL-LYS-ALY-GLY-CYS-NH2"
    }


def test_synthetic_cov_peptide_detection(cif_6lu7, mock_alternative_datasets):
    entry_dir = mock_alternative_datasets("6lu7")
    plinder_anno = GetPlinderAnnotation(cif_6lu7, "", save_folder=entry_dir)
    plinder_anno.annotate()
    df = plinder_anno.annotated_df
    assert len(df) == 2
    # TODO: test 'ligand_covalent_linkages'
    assert df["ligand_is_covalent"].sum() == 2
    # TODO: need to decide if to test for this name or use PRD/BIRD name!
    ligname = df.ligand_ccd_code.to_list()[0]
    assert ligname in ["02J-ALA-VAL-LEU-PJE-010", "PRD_002214"]
    # peptide ligand chain 'B' should not be in protein chains!
    assert (
        sum(["B" in i for i in df["ligand_neighboring_protein_chains_auth_id"].values])
        == 0
    )
    lig = plinder_anno.entry.systems["6lu7__1__1.A_2.A__1.B"].ligands[0]
    assert lig.is_invalid == False
    outsdffile = entry_dir / "6lu7__1__1.A_2.A__1.B/ligand_files/1.B.sdf"
    assert outsdffile.is_file()
    rdmol = Chem.SDMolSupplier(outsdffile, removeHs=True)[0]
    assert (
        Chem.SanitizeMol(rdmol) == Chem.rdmolops.SanitizeFlags.SANITIZE_NONE
    )
    assert (
        len(Chem.MolToSmiles(rdmol).split(".")) == 1
    )

def test_crystal_contact_detection(cif_6lu7, mock_alternative_datasets):
    entry_dir = mock_alternative_datasets("6lu7")
    plinder_anno = GetPlinderAnnotation(cif_6lu7, "", save_folder=entry_dir)
    plinder_anno.annotate()
    df = plinder_anno.annotated_df
    assert len(df) == 2
    assert all(x == 2 for x in df["system_num_atoms_with_crystal_contacts"])
    assert all(x == 1 for x in df["system_num_crystal_contacted_residues"])

def test_simple_covalency_detection(cif_7gl9, mock_alternative_datasets):
    entry_dir = mock_alternative_datasets("7gl9")
    plinder_anno_noncov = GetPlinderAnnotation(cif_7gl9, "", save_folder=entry_dir)
    plinder_anno_noncov.annotate()
    df_noncov = plinder_anno_noncov.annotated_df
    assert df_noncov["ligand_is_covalent"].sum() == 0

def test_simple_covalency_detection_found(cif_7gj7, mock_alternative_datasets):
    entry_dir = mock_alternative_datasets("7gj7")
    plinder_anno_cov = GetPlinderAnnotation(cif_7gj7, "", save_folder=entry_dir)
    plinder_anno_cov.annotate()
    df_cov = plinder_anno_cov.annotated_df
    # TODO: test 'ligand_covalent_linkages'
    assert df_cov["ligand_is_covalent"].sum() == 2


def test_simple_ternary_detection(cif_2p1q, mock_alternative_datasets):
    entry_dir = mock_alternative_datasets("2p1q")
    plinder_anno = GetPlinderAnnotation(cif_2p1q, "", save_folder=entry_dir)
    plinder_anno.annotate()
    df = plinder_anno.annotated_df
    assert sorted(set(df.ligand_ccd_code.to_list())) == ["IAC", "IHP"]
    auxin_entry = df.ligand_ccd_code == "IAC"
    # expect two chains to get this correct!
    assert df[auxin_entry][
        "ligand_neighboring_protein_chains_auth_id"
    ].drop_duplicates().to_list() == ["B;C"]
    # # In the case where a small molecule ligand sits at the interface of a peptide that \
    # # could be a ligand, we still want to treat the peptide as part of receptor \
    # # a could example of this are molecular glue crystal where the second protein is
    # # crystallized as peptides
    # plinder_anno_v2 = GetPlinderAnnotation(cif_2p1q, "", min_polymer_size=20)
    # plinder_anno_v2.annotate()
    # df2 = plinder_anno_v2.annotated_df
    # assert 'GLN-VAL-VAL-GLY-TRP-PRO-PRO-VAL-ARG-ASN-TYR-ARG-LYS' in df2.ligand_ccd_code.to_list()
    # pep_entry2 = df2.ligand_ccd_code == 'GLN-VAL-VAL-GLY-TRP-PRO-PRO-VAL-ARG-ASN-TYR-ARG-LYS'
    # assert df2[pep_entry2]['ligand_neighboring_protein_chains_auth_id'].drop_duplicates().to_list() == ['B']
    # auxin_entry2 = df2.ligand_ccd_code == 'IAC'
    # assert df2[auxin_entry2]['ligand_neighboring_protein_chains_auth_id'].drop_duplicates().to_list() == ['B;C']


def test_plip_entry_binary(cif_4ci1, mock_alternative_datasets, lig_code="EF2"):
    entry_dir = mock_alternative_datasets("4ci1")
    entry = Entry.from_cif_file(
        cif_4ci1,
        neighboring_residue_threshold=6.0,
        neighboring_ligand_threshold=4.0,
        min_polymer_size=10,
        save_folder=entry_dir,
    )

    for system in entry.systems:
        for ligand in entry.systems[system].ligands:
            if ligand.ccd_code == lig_code:
                break

    # assert that expected chain is detected
    assert sorted(ligand.interactions.keys()) == ["1.B"]

    # 10 PLIPs detected:
    # consistent with SWISSMODEL as of 2024-04-18
    # https://swissmodel.expasy.org/templates/4ci1

    # expected_interactions = {
    #     404: ['type:hydrogen_bonds__donortype:Nam__acceptortype:O2__protisdon:False__sidechain:False',
    #           'type:hydrogen_bonds__donortype:Nar__acceptortype:O2__protisdon:True__sidechain:True'],
    #     406: ['type:hydrogen_bonds__donortype:Nam__acceptortype:O2__protisdon:True__sidechain:False', 'type:hydrophobic_contacts'],
    #     377: ['type:hydrogen_bonds__donortype:Nam__acceptortype:O2__protisdon:True__sidechain:True', 'type:hydrophobic_contacts'],
    #     412: ['type:hydrophobic_contacts', 'type:hydrophobic_contacts'],
    #     426: ['type:hydrophobic_contacts'],
    #     428: ['type:hydrophobic_contacts']
    # }
    expected_interactions = {
        404: [
            "type:hydrogen_bonds__protisdon:False__sidechain:False",
            "type:hydrogen_bonds__protisdon:True__sidechain:True",
        ],
        406: [
            "type:hydrogen_bonds__protisdon:True__sidechain:False",
            "type:hydrophobic_contacts",
        ],
        377: [
            "type:hydrogen_bonds__protisdon:True__sidechain:True",
            "type:hydrophobic_contacts",
        ],
        412: ["type:hydrophobic_contacts", "type:hydrophobic_contacts"],
        426: ["type:hydrophobic_contacts"],
        428: ["type:hydrophobic_contacts"],
    }
    # get if the count is right
    assert len(ligand.interactions["1.B"]) == len(expected_interactions)
    # exact report matching
    assert ligand.interactions["1.B"] == expected_interactions


def test_plip_entry_ternary(cif_2p1q, mock_alternative_datasets, lig_code="IAC"):
    entry_dir = mock_alternative_datasets("2p1q")
    entry = Entry.from_cif_file(
        cif_2p1q,
        neighboring_residue_threshold=6.0,
        neighboring_ligand_threshold=4.0,
        min_polymer_size=10,
        save_folder=entry_dir,
    )

    for system in entry.systems:
        for ligand in entry.systems[system].ligands:
            if ligand.ccd_code == lig_code:
                break

    # assert that expected two chains are detected
    assert sorted(ligand.interactions.keys()) == ["2.B", "2.C"]

    # 12 PLIPs detected:
    # consistent with SWISSMODEL as of 2024-04-18
    # https://swissmodel.expasy.org/templates/2p1q.1
    # expected_interactions_2B =  {
    #     438: ['type:hydrogen_bonds__donortype:O.co2__acceptortype:O3__protisdon:False__sidechain:True',
    #           'type:hydrogen_bonds__donortype:O3__acceptortype:O.co2__protisdon:True__sidechain:True'],
    #     79: ['type:hydrophobic_contacts', 'type:hydrophobic_contacts'],
    #     464: ['type:hydrophobic_contacts'],
    #     403: ['type:water_bridges__donortype:Ng+__acceptortype:O.co2__protisdon:True',
    #           'type:water_bridges__donortype:Ng+__acceptortype:O.co2__protisdon:True',
    #           'type:salt_bridges__lig_group:carboxylate__protispos:True'],
    #     78: ['type:salt_bridges__lig_group:carboxylate__protispos:True']
    # }
    expected_interactions_2B = {
        438: [
            "type:hydrogen_bonds__protisdon:True__sidechain:True",
        ],
        439: ['type:hydrogen_bonds__protisdon:False__sidechain:False'],
        79: ["type:hydrophobic_contacts", "type:hydrophobic_contacts"],
        464: ["type:hydrophobic_contacts"],
        403: [
            "type:water_bridges__protisdon:True",
            "type:water_bridges__protisdon:True",
            "type:salt_bridges__protispos:True",
        ],
        78: ["type:salt_bridges__protispos:True"],
    }
    expected_interactions_2C = {
        7: ["type:hydrophobic_contacts", "type:water_bridges__protisdon:False"],
        5: ["type:pi_stacks__stack_type:T"],
    }

    expected_waters = {
        '2.G': {66, 4, 2}
    }

    # get if the count is right
    assert len(ligand.interactions["2.B"]) == len(expected_interactions_2B)
    assert len(ligand.interactions["2.C"]) == len(expected_interactions_2C)

    # exact report matching
    assert ligand.interactions["2.B"] == expected_interactions_2B
    assert ligand.interactions["2.C"] == expected_interactions_2C

    # waters
    assert {k: set(v) for k, v in ligand.waters.items()} == expected_waters


def test_water_saving(cif_2p1q, mock_alternative_datasets):
    from ost import io
    entry_dir = mock_alternative_datasets("2p1q")
    system_tag = "2p1q__2__2.B_2.C__2.E"
    Entry.from_cif_file(cif_2p1q, save_folder=entry_dir)
    for filename in [
        "sequences.fasta",
        "receptor.pdb",
        "system.cif",
        "receptor.cif",
        "chain_mapping.json",
        "water_mapping.json"
    ]:
        assert (entry_dir / system_tag / filename).exists()
    assert (entry_dir / system_tag / "ligand_files" / "2.E.sdf").exists()
    ent = io.LoadPDB(str(entry_dir / system_tag / "receptor.pdb"))
    assert len(ent.FindChain("_").residues) == 3


def test_plip_same_hinge_binders(cif_2gdo, cif_4qyf, mock_alternative_datasets):
    pdb_ids = ["2gdo", "4qyf"]
    mmcifs = [cif_2gdo, cif_4qyf]
    ccd_codes = ["12C", "3DV"]
    hinge_resids = [85, 87]
    interactions_sets = []
    for ccd, cif, pdb_id in zip(ccd_codes, mmcifs, pdb_ids):
        entry_dir = mock_alternative_datasets(pdb_id)
        entry = Entry.from_cif_file(cif, save_folder=entry_dir)
        for system in entry.systems.values():
            for ligand in system.ligands:
                if ligand.ccd_code == ccd:
                    interactions_sets.append(ligand.interactions["1.A"])
                    break

    assert len(interactions_sets) == 2

    for hr in hinge_resids:
        assert len(set(interactions_sets[0][hr]).intersection(interactions_sets[1][hr]))


def test_get_single_ligand_system_annotations(cif_6fx1, mock_alternative_datasets):
    entry_dir = mock_alternative_datasets("6fx1")
    entry = Entry.from_cif_file(cif_6fx1, save_folder=entry_dir)
    ligands = []
    for system in entry.systems:
        for ligand in entry.systems[system].ligands:
            ligands.append(ligand)
    single_ligand_system_result = set(l.ccd_code for l in ligands)
    single_ligand_system_target = {
        "C4W-NAG-BMA-MAN-NAG-FUC",
        "OOA",
        "C4W-NAG-BMA-MAN-FUC",
        "C4W-NAG-BMA-MAN-NAG-MAN-FUC",
        "C4W-NAG-BMA-FUC",
        "C4W-NAG-BMA-MAN-NAG-MAN-NAG-FUC",
        "MLI",
    }
    assert single_ligand_system_result == single_ligand_system_target


def test_system_saving(cif_2y4i, mock_alternative_datasets):
    entry_dir = mock_alternative_datasets("2y4i")
    system_tag = "2y4i__1__1.B__1.E_1.F"
    entry = Entry.from_cif_file(cif_2y4i, save_folder=entry_dir)
    for chain in entry.chains.values():
        assert len(chain.mappings["ECOD"])
    for filename in [
        "sequences.fasta",
        "receptor.pdb",
        "system.cif",
        "receptor.cif",
        "chain_mapping.json",
    ]:
        assert (entry_dir / system_tag / filename).exists()
    for chain in ["1.E", "1.F"]:
        assert (entry_dir / system_tag / "ligand_files" / f"{chain}.sdf").exists()


def test_smiles_from_nextgen(test_dir, smiles_sample_csv):
    from ost import io

    results = []
    pdbids = ["1ppc", "6fx1", "6m92", "2dty", "7gj7", "2e84", "6u6k"]
    for pdbid in pdbids:
        cif_file = test_dir / f"xx/pdb_0000{pdbid}/pdb_0000{pdbid}_xyz-enrich.cif.gz"
        data = read_mmcif_container(cif_file)
        ent = io.LoadMMCIF(str(cif_file))
        pdbid = cif_file.stem.split("_")[1].split("0000")[-1]
        result = get_smiles_from_cif(data, ent)
        result = [(pdbid, k, v) for k, v in result.items()]
        results.extend(result)
    result_df = pd.DataFrame(results, columns=["pdbid", "chain", "smiles"])
    result_df = result_df.sort_values(by=["pdbid", "chain"]).reset_index(drop=True)
    target_df = pd.read_csv(smiles_sample_csv)
    target_df = target_df.sort_values(by=["pdbid", "chain"]).reset_index(drop=True)
    pd.testing.assert_frame_equal(result_df, target_df)


def test_get_validation(
    cif_1qz5,
    validation_1qz5,
    mock_alternative_datasets,
):
    entry_dir = mock_alternative_datasets("1qz5")
    reference_df = pd.DataFrame.from_dict({
        'system_id': '1qz5__1__1.A__1.D',
        'system_ligand_atom_count': 67,
        'system_ligand_average_occupancy': 1.000,
        'system_ligand_average_rscc': 0.958,
        'system_ligand_average_rsr': 0.098,
        'ligand_ccd_code': 'KAB',
        'entry_resolution': 1.45,
        'entry_rfree': 0.19,
        'entry_r': 0.17,
        'entry_clashscore': 3.93,
        'entry_percent_rama_outliers': 0.00,
        'entry_molprobity': 1.408352978496041,
        'entry_r_minus_rfree': 0.01999999999999999,
        'system_pocket_max_alt_count': 2,
        'system_pass_validation_criteria': False,
        'entry_pass_validation_criteria': True}, orient="index").T.infer_objects()
    entry = GetPlinderAnnotation(cif_1qz5,validation_1qz5, save_folder=entry_dir)
    entry.annotate()
    validation_df = entry.annotated_df[reference_df.columns]
    validation_df = validation_df[
        validation_df['system_id'] == '1qz5__1__1.A__1.D'
        ].reset_index(drop=True)

    pd.testing.assert_frame_equal(reference_df, validation_df)


def test_mmp(
    mini_mmp_index,
    mini_mmp_data_annotation,
    mini_mmp_cluster_folder):

    system_df = pd.read_csv(mini_mmp_data_annotation, sep="\t")
    load_mmp_df = pd.read_csv(mini_mmp_index, compression="gzip", sep="\t", header=None)
    load_mmp_df.columns = ["SMILES1", "SMILES2", "id1", "id2", "V1>>V2", "CONSTANT"]
    mmp_data = add_mmp_clusters_to_data(
        load_mmp_df,
        system_df,
        cluster_folder=mini_mmp_cluster_folder,
        protein_metric = "protein_fident_weighted_sum",
        protein_threshold = 95,
        protein_directed=False,
        pocket_metric = "pocket_fident",
        pocket_threshold = 100,
        pocket_directed=True,
        min_constant_size=10
    )
    # All have same pocket-protein id
    assert list(mmp_data.prot_pocket_set_shared.unique()) == ["c1931_c55468"]

    # Minimum constant size is greater than 10
    assert mmp_data.const_size.min() == 18.0

    # Number of unique congeneric ids is equal to number of unique constants
    assert len(mmp_data.congeneric_id.unique()) == len(mmp_data.CONSTANT.unique())


def test_ligand_fix_to_valid_imatinib(cif_2hyy, mock_alternative_datasets):
    entry_dir = mock_alternative_datasets("2hyy")
    entry = Entry.from_cif_file(
        cif_2hyy,
        save_folder=entry_dir,
    )
    lig = entry.systems['2hyy__1__1.A__1.E'].ligands[0]
    #  before fix it is invalid
    assert lig.is_invalid == False
    outsdffile = entry_dir / '2hyy__1__1.A__1.E/ligand_files/1.E.sdf'
    assert outsdffile.is_file()
    rdmol_sdf = Chem.SDMolSupplier(outsdffile, removeHs=True)[0]
    rdmol_smi = Chem.MolFromSmiles(lig.smiles)
    # check that numnber of aromatic rings is undderstood correctly
    # N.B. this is expected to be true for fully resolved systems
    assert (
        Chem.rdMolDescriptors.CalcNumAromaticRings(rdmol_sdf) == \
        Chem.rdMolDescriptors.CalcNumAromaticRings(rdmol_smi)
    )


def test_ligand_fix_to_valid_thalidomide(cif_7bqu, mock_alternative_datasets):
    entry_dir = mock_alternative_datasets("7bqu")
    entry = Entry.from_cif_file(
        cif_7bqu,
        save_folder=entry_dir,
    )
    lig = entry.systems['7bqu__1__1.A_1.B__1.C'].ligands[0]
    assert lig.is_invalid == False
    outsdffile = entry_dir / '7bqu__1__1.A_1.B__1.C/ligand_files/1.C.sdf'
    assert outsdffile.is_file()
    rdmol_sdf = Chem.SDMolSupplier(outsdffile, removeHs=True)[0]
    rdmol_smi = Chem.MolFromSmiles(lig.smiles)
    # check that numnber of aromatic rings is undderstood correctly
    # N.B. this is expected to be true for fully resolved systems
    assert (
        Chem.rdMolDescriptors.CalcNumAromaticRings(rdmol_sdf) == \
        Chem.rdMolDescriptors.CalcNumAromaticRings(rdmol_smi)
    )


def test_partially_resolved_substructure_JEF(cif_1ngx, mock_alternative_datasets):
    entry_dir = mock_alternative_datasets("1ngx")
    entry = Entry.from_cif_file(
        cif_1ngx,
        save_folder=entry_dir,
    )
    lig = entry.systems['1ngx__1__1.A_1.B__1.E'].ligands[0]
    assert lig.is_invalid == False
    assert lig.num_unresolved_heavy_atoms == 13
    outsdffile = entry_dir / '1ngx__1__1.A_1.B__1.E/ligand_files/1.E.sdf'
    assert outsdffile.is_file()
    rdmol = Chem.SDMolSupplier(outsdffile, removeHs=True)[0]
    assert (
        Chem.SanitizeMol(rdmol) == Chem.rdmolops.SanitizeFlags.SANITIZE_NONE
    )
    rdmol_smi = Chem.MolFromSmiles(lig.smiles)
    substruct_matches = rdmol_smi.GetSubstructMatches(rdmol)
    assert len(substruct_matches) == 3
    assert len(substruct_matches[0]) == 28


def test_distorted_molecule_template_fix(cif_3grt, mock_alternative_datasets):
    entry_dir = mock_alternative_datasets("3grt")
    entry = Entry.from_cif_file(
        cif_3grt,
        save_folder=entry_dir,
    )
    lig = entry.systems['3grt__1__1.A_2.A__1.B'].ligands[0]
    assert lig.is_invalid == False
    outsdffile = entry_dir / '3grt__1__1.A_2.A__1.B/ligand_files/1.B.sdf'
    assert outsdffile.is_file()
    rdmol = Chem.SDMolSupplier(outsdffile, removeHs=True)[0]
    assert (
        Chem.SanitizeMol(rdmol) == Chem.rdmolops.SanitizeFlags.SANITIZE_NONE
    )


def test_hydrogen_removed_save(cif_7az3, mock_alternative_datasets):
    entry_dir = mock_alternative_datasets("7az3")
    entry = Entry.from_cif_file(
        cif_7az3,
        save_folder=entry_dir,
    )
    pli_entry = list(entry.systems.keys())[0]
    outsdffile = entry_dir / pli_entry / f'ligand_files/{pli_entry[-3:]}.sdf'
    assert outsdffile.is_file()
    rdmol = Chem.SDMolSupplier(outsdffile, removeHs=False, sanitize=False)[0]
    assert (
        sum([at.GetAtomicNum() == 1 for at in rdmol.GetAtoms()]) == 0
    )
    assert (
        Chem.SanitizeMol(rdmol) == Chem.rdmolops.SanitizeFlags.SANITIZE_NONE
    )


def test_too_many_hydrogens(cif_6ntj, mock_alternative_datasets):
    entry_dir = mock_alternative_datasets("6ntj")
    entry = Entry.from_cif_file(
        cif_6ntj,
        save_folder=entry_dir,
    )
    pli_entry = list(entry.systems.keys())[0]
    outsdffile = entry_dir / pli_entry / f'ligand_files/{pli_entry[-3:]}.sdf'
    assert outsdffile.is_file()
    rdmol = Chem.SDMolSupplier(outsdffile, removeHs=False, sanitize=False)[0]
    assert (
        sum([at.GetAtomicNum() == 1 for at in rdmol.GetAtoms()]) == 0
    )
    assert (
        Chem.SanitizeMol(rdmol) == Chem.rdmolops.SanitizeFlags.SANITIZE_NONE
    )


def test_disconnected_ligand_fix(cif_4nhc, mock_alternative_datasets):
    entry_dir = mock_alternative_datasets("4nhc")
    entry = Entry.from_cif_file(
        cif_4nhc,
        save_folder=entry_dir,
        skip_posebusters=True
    )
    lig = entry.systems['4nhc__1__1.A_1.B__1.C'].ligands[0]
    assert lig.is_invalid == False
    outsdffile = entry_dir / '4nhc__1__1.A_1.B__1.C/ligand_files/1.C.sdf'
    assert outsdffile.is_file()
    rdmol = Chem.SDMolSupplier(outsdffile, removeHs=True)[0]
    assert (
        Chem.SanitizeMol(rdmol) == Chem.rdmolops.SanitizeFlags.SANITIZE_NONE
    )
    assert len(Chem.MolToSmiles(rdmol).split('.')) == 1


def test_binding_affinity(cif_4jvn, mock_alternative_datasets):
    entry_dir = mock_alternative_datasets("4jvn")
    entry = Entry.from_cif_file(
        cif_4jvn,
        save_folder=entry_dir,
        skip_posebusters=True
    )
    target_value = 7.638272164
    affinity = 0.0
    for sys in entry.systems.values():
        if "YUG" in set(l.ccd_code for l in sys.ligands):
            assert sys.has_binding_affinity
        for ligand in sys.ligands:
            if ligand.ccd_code == "YUG":
                affinity = ligand.binding_affinity
    assert affinity == target_value
