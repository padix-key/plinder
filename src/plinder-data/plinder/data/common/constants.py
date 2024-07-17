# Copyright (c) 2024, Plinder Development Team
# Distributed under the terms of the Apache License 2.0
from __future__ import annotations

from pathlib import Path

from plinder.data import _root

PDB_FILE_COUNT = 615616
CSV_FILE_COUNT = 331541

BASE_DIR = _root

three_to_one_noncanonical_mapping = {
    "004": "X",
    "00C": "C",
    "00I": "X",
    "00S": "X",
    "010": "X",
    "011": "X",
    "01B": "X",
    "01W": "X",
    "02A": "X",
    "02G": "X",
    "02J": "X",
    "02K": "A",
    "02V": "X",
    "02Y": "X",
    "03Y": "C",
    "05N": "P",
    "0A9": "X",
    "0AF": "W",
    "0AH": "S",
    "0E5": "T",
    "0EA": "Y",
    "0EH": "X",
    "0HQ": "X",
    "0JU": "X",
    "0JY": "X",
    "0LF": "X",
    "0MG": "X",
    "0OB": "X",
    "0QE": "X",
    "0QL": "X",
    "0UO": "X",
    "11Q": "X",
    "13E": "X",
    "143": "C",
    "175": "A",
    "19W": "X",
    "1AC": "X",
    "1BO": "X",
    "1C3": "X",
    "1E3": "X",
    "1HB": "X",
    "1HD": "X",
    "1MH": "X",
    "1OL": "X",
    "1OP": "Y",
    "1PA": "F",
    "1TQ": "W",
    "1TX": "X",
    "1TY": "Y",
    "1U8": "X",
    "1ZN": "X",
    "200": "F",
    "22G": "X",
    "23F": "F",
    "23P": "X",
    "24M": "X",
    "24O": "X",
    "28H": "X",
    "28J": "X",
    "28K": "X",
    "2A1": "X",
    "2CO": "C",
    "2GX": "X",
    "2JH": "X",
    "2JN": "X",
    "2KK": "K",
    "2KP": "K",
    "2L5": "X",
    "2MR": "R",
    "2N2": "X",
    "2OP": "X",
    "2PP": "X",
    "2RX": "X",
    "2SO": "X",
    "2TL": "T",
    "2TY": "Y",
    "2UC": "X",
    "2UE": "X",
    "2X0": "X",
    "30F": "X",
    "32L": "X",
    "36D": "X",
    "3A0": "X",
    "3A5": "X",
    "3AZ": "X",
    "3BY": "X",
    "3CF": "F",
    "3CN": "X",
    "3CT": "X",
    "3FB": "X",
    "3GL": "E",
    "3PA": "X",
    "3PX": "X",
    "3TY": "X",
    "3V7": "X",
    "3V8": "X",
    "3X9": "X",
    "3ZH": "X",
    "3ZL": "X",
    "41H": "X",
    "45F": "X",
    "45W": "X",
    "48V": "X",
    "4AK": "X",
    "4AR": "X",
    "4BA": "X",
    "4BF": "Y",
    "4CF": "F",
    "4CG": "X",
    "4CY": "M",
    "4DB": "X",
    "4DP": "W",
    "4FB": "P",
    "4FO": "X",
    "4H0": "X",
    "4HL": "X",
    "4HT": "W",
    "4II": "F",
    "4IN": "W",
    "4KY": "X",
    "4L0": "X",
    "4L8": "X",
    "4LZ": "X",
    "4MM": "X",
    "4N7": "X",
    "4N8": "X",
    "4N9": "X",
    "4WQ": "X",
    "54C": "W",
    "562": "X",
    "56A": "H",
    "56C": "X",
    "56J": "X",
    "5CT": "K",
    "5GM": "X",
    "5JP": "X",
    "5OL": "X",
    "5OM": "X",
    "5OW": "K",
    "5PG": "G",
    "5PV": "X",
    "5R0": "X",
    "5R5": "X",
    "5XU": "X",
    "60H": "X",
    "66D": "X",
    "6A0": "X",
    "6CW": "W",
    "6D6": "X",
    "6E4": "X",
    "6F5": "X",
    "6FH": "X",
    "6G4": "K",
    "6L3": "X",
    "6L9": "X",
    "6NA": "X",
    "6RK": "X",
    "6VO": "X",
    "6ZS": "X",
    "73C": "X",
    "73N": "R",
    "73O": "Y",
    "73P": "K",
    "74P": "X",
    "7BB": "X",
    "7GA": "X",
    "7NF": "X",
    "7NW": "X",
    "7NX": "X",
    "7XC": "X",
    "81R": "X",
    "81S": "X",
    "823": "X",
    "85G": "X",
    "85J": "X",
    "8BB": "X",
    "8LJ": "X",
    "8MC": "X",
    "8SN": "X",
    "8TQ": "X",
    "92B": "X",
    "99Y": "X",
    "9AT": "X",
    "9BB": "X",
    "9DK": "X",
    "9DQ": "X",
    "9DT": "X",
    "9DW": "X",
    "9DZ": "X",
    "9E7": "X",
    "9FZ": "X",
    "9G2": "X",
    "9KK": "X",
    "9KP": "K",
    "9PR": "X",
    "9R1": "X",
    "9R4": "X",
    "9R7": "X",
    "9WV": "X",
    "A0A": "X",
    "A1G": "X",
    "A5R": "X",
    "A8E": "X",
    "AA1": "X",
    "AAR": "R",
    "ABA": "A",
    "ABN": "X",
    "ABU": "X",
    "AC5": "X",
    "ACA": "X",
    "ACB": "D",
    "ACE": "X",
    "ACY": "X",
    "AEA": "C",
    "AEI": "D",
    "AG2": "X",
    "AGQ": "X",
    "AGT": "C",
    "AH0": "X",
    "AHH": "X",
    "AHO": "A",
    "AHP": "A",
    "AIB": "A",
    "AJE": "X",
    "AKR": "X",
    "AKZ": "D",
    "ALA": "A",
    "ALC": "A",
    "ALN": "A",
    "ALO": "T",
    "ALQ": "X",
    "ALT": "A",
    "ALV": "A",
    "ALY": "K",
    "AME": "X",
    "AMP": "X",
    "AMU": "X",
    "APK": "K",
    "AQ7": "X",
    "AR0": "X",
    "AR7": "R",
    "ARG": "R",
    "ASA": "D",
    "ASB": "D",
    "ASJ": "X",
    "ASL": "D",
    "ASN": "N",
    "ASP": "D",
    "ASX": "B",
    "AY0": "X",
    "AYA": "A",
    "AYE": "X",
    "AZK": "K",
    "B27": "X",
    "B2A": "A",
    "B2F": "F",
    "B2I": "I",
    "B2V": "V",
    "B3A": "A",
    "B3D": "D",
    "B3E": "E",
    "B3K": "K",
    "B3L": "X",
    "B3Q": "X",
    "B3T": "X",
    "B3Y": "Y",
    "B8R": "X",
    "BAL": "X",
    "BB6": "C",
    "BB7": "C",
    "BB8": "F",
    "BB9": "C",
    "BBC": "C",
    "BBS": "X",
    "BE2": "X",
    "BEZ": "X",
    "BF9": "X",
    "BFD": "D",
    "BH2": "D",
    "BHD": "D",
    "BIF": "F",
    "BIL": "X",
    "BLE": "L",
    "BMT": "T",
    "BNO": "X",
    "BOC": "X",
    "BOR": "R",
    "BP4": "X",
    "BP5": "X",
    "BPE": "C",
    "BSE": "S",
    "BTK": "X",
    "BTN": "X",
    "BVK": "X",
    "BW5": "X",
    "BWV": "X",
    "BXT": "S",
    "C1J": "X",
    "C1X": "K",
    "C4G": "X",
    "C67": "X",
    "C6D": "X",
    "CAF": "C",
    "CAS": "C",
    "CCS": "C",
    "CDE": "X",
    "CE7": "X",
    "CEV": "X",
    "CF0": "X",
    "CFT": "X",
    "CG6": "C",
    "CGU": "E",
    "CGV": "X",
    "CH6": "M",
    "CHG": "X",
    "CHS": "X",
    "CIR": "R",
    "CKC": "X",
    "CLG": "K",
    "CLH": "K",
    "CLR": "X",
    "CME": "C",
    "CMH": "C",
    "CMT": "C",
    "CNT": "X",
    "CPI": "X",
    "CR2": "G",
    "CRO": "T",
    "CS1": "C",
    "CSA": "C",
    "CSD": "C",
    "CSI": "X",
    "CSO": "C",
    "CSP": "C",
    "CSS": "C",
    "CSU": "C",
    "CSX": "C",
    "CXM": "M",
    "CXP": "X",
    "CY1": "C",
    "CY3": "C",
    "CY4": "C",
    "CYF": "C",
    "CYG": "C",
    "CYJ": "K",
    "CYQ": "C",
    "CYR": "C",
    "CYS": "C",
    "D4P": "X",
    "DA2": "R",
    "DAB": "A",
    "DAH": "F",
    "DAL": "A",
    "DAM": "X",
    "DAO": "X",
    "DAR": "R",
    "DAS": "D",
    "DBB": "T",
    "DBH": "X",
    "DBU": "T",
    "DBY": "Y",
    "DC0": "X",
    "DCL": "X",
    "DCY": "C",
    "DDE": "H",
    "DDZ": "A",
    "DFF": "X",
    "DFI": "X",
    "DFO": "X",
    "DGL": "E",
    "DGN": "Q",
    "DHA": "S",
    "DHI": "H",
    "DHL": "X",
    "DI7": "Y",
    "DI8": "X",
    "DIL": "I",
    "DIP": "X",
    "DIV": "V",
    "DIX": "X",
    "DIY": "X",
    "DKA": "X",
    "DLE": "L",
    "DLS": "K",
    "DLY": "K",
    "DMG": "X",
    "DMH": "N",
    "DMK": "D",
    "DMT": "X",
    "DNP": "A",
    "DNW": "X",
    "DOA": "X",
    "DPN": "F",
    "DPP": "A",
    "DPQ": "Y",
    "DPR": "P",
    "DQK": "X",
    "DSE": "S",
    "DSG": "N",
    "DSN": "S",
    "DTH": "T",
    "DTR": "W",
    "DTY": "Y",
    "DUG": "X",
    "DVA": "V",
    "DYL": "X",
    "DYS": "C",
    "DYW": "X",
    "E2G": "X",
    "ECC": "Q",
    "ECQ": "X",
    "EFC": "C",
    "EJA": "X",
    "ELY": "X",
    "EOE": "X",
    "ESB": "Y",
    "ESC": "M",
    "ESD": "X",
    "ETA": "X",
    "EX8": "X",
    "EXB": "X",
    "EYZ": "X",
    "F2F": "F",
    "F6N": "S",
    "F75": "G",
    "F7P": "X",
    "F7S": "X",
    "F7V": "X",
    "FAK": "K",
    "FBE": "X",
    "FC0": "F",
    "FCL": "F",
    "FDL": "X",
    "FE3": "X",
    "FGA": "E",
    "FGL": "G",
    "FGP": "S",
    "FHL": "K",
    "FHO": "K",
    "FLT": "Y",
    "FME": "M",
    "FMT": "X",
    "FOR": "X",
    "FP9": "P",
    "FPA": "X",
    "FPR": "X",
    "FQA": "X",
    "FRD": "X",
    "FT6": "W",
    "FTR": "W",
    "FTY": "Y",
    "FZN": "K",
    "G1X": "Y",
    "G2Z": "X",
    "G5G": "X",
    "GG7": "X",
    "GGL": "E",
    "GHG": "Q",
    "GIC": "X",
    "GLJ": "E",
    "GLK": "E",
    "GLN": "Q",
    "GLU": "E",
    "GLX": "Z",
    "GLY": "G",
    "GLZ": "G",
    "GMA": "E",
    "GME": "X",
    "GNC": "X",
    "GOA": "X",
    "GPL": "K",
    "GRN": "X",
    "GVE": "X",
    "GYS": "S",
    "GZB": "X",
    "GZJ": "X",
    "H14": "F",
    "HAO": "X",
    "HCI": "X",
    "HCS": "X",
    "HIA": "H",
    "HIC": "H",
    "HIP": "H",
    "HIS": "H",
    "HIX": "X",
    "HMB": "X",
    "HMF": "X",
    "HMR": "R",
    "HNC": "X",
    "HOA": "X",
    "HOX": "X",
    "HPE": "F",
    "HPH": "F",
    "HQA": "A",
    "HR7": "R",
    "HRG": "R",
    "HS9": "H",
    "HSE": "S",
    "HSL": "S",
    "HSV": "H",
    "HT7": "W",
    "HTI": "C",
    "HTR": "W",
    "HY1": "X",
    "HYP": "P",
    "HZP": "P",
    "IAS": "D",
    "IBU": "X",
    "IIL": "I",
    "IL0": "X",
    "ILE": "I",
    "IML": "I",
    "IP8": "X",
    "IPG": "G",
    "IPI": "X",
    "IVA": "X",
    "IYR": "Y",
    "IZO": "M",
    "JG3": "X",
    "JJJ": "C",
    "JJK": "C",
    "JJL": "C",
    "JLP": "K",
    "KCQ": "X",
    "KCR": "X",
    "KCX": "K",
    "KFP": "X",
    "KGC": "K",
    "KHB": "X",
    "KI2": "X",
    "KPF": "K",
    "KPI": "K",
    "KPY": "K",
    "KYN": "W",
    "KYQ": "K",
    "L2O": "X",
    "L3O": "L",
    "L5P": "X",
    "LA2": "K",
    "LAC": "X",
    "LAV": "X",
    "LAY": "L",
    "LCK": "K",
    "LDH": "K",
    "LET": "K",
    "LEU": "L",
    "LGY": "X",
    "LHE": "X",
    "LHV": "X",
    "LLP": "K",
    "LNT": "X",
    "LOV": "X",
    "LP6": "K",
    "LPD": "P",
    "LPH": "X",
    "LPL": "X",
    "LRK": "X",
    "LSO": "K",
    "LTA": "X",
    "LYF": "K",
    "LYK": "K",
    "LYN": "K",
    "LYP": "X",
    "LYR": "K",
    "LYS": "K",
    "LYT": "X",
    "LYX": "K",
    "LYZ": "K",
    "M0H": "C",
    "M2L": "K",
    "M3L": "K",
    "M9P": "X",
    "MAA": "A",
    "MAZ": "X",
    "MBN": "X",
    "MCM": "X",
    "MDO": "A",
    "ME0": "X",
    "MEA": "F",
    "MEN": "N",
    "MEQ": "Q",
    "MET": "M",
    "MH6": "S",
    "MH8": "X",
    "MHO": "M",
    "MHT": "X",
    "MHU": "F",
    "MHV": "X",
    "MHW": "X",
    "MIS": "S",
    "MK8": "L",
    "MKD": "X",
    "MKE": "X",
    "ML3": "K",
    "MLE": "L",
    "MLI": "X",
    "MLL": "L",
    "MLU": "X",
    "MLY": "K",
    "MLZ": "K",
    "MME": "M",
    "MN1": "X",
    "MN2": "X",
    "MN7": "X",
    "MN8": "X",
    "MOZ": "X",
    "MP8": "P",
    "MPQ": "G",
    "MPT": "X",
    "MSA": "G",
    "MSE": "M",
    "MSO": "M",
    "MSU": "X",
    "MUB": "X",
    "MVA": "V",
    "MX3": "X",
    "MX4": "X",
    "MX5": "X",
    "MY0": "X",
    "MY1": "X",
    "MY2": "X",
    "MY3": "X",
    "MY5": "X",
    "MYK": "X",
    "MYR": "X",
    "N10": "S",
    "N2C": "X",
    "N7P": "P",
    "N80": "P",
    "NA8": "A",
    "NAK": "X",
    "NAL": "A",
    "NCY": "X",
    "NEH": "X",
    "NEP": "H",
    "NH2": "X",
    "NIT": "X",
    "NIY": "Y",
    "NLE": "L",
    "NLG": "X",
    "NLW": "L",
    "NLY": "X",
    "NMC": "G",
    "NME": "X",
    "NMM": "R",
    "NVA": "V",
    "NYS": "C",
    "NZC": "T",
    "OAR": "R",
    "OAS": "S",
    "OBF": "X",
    "OBS": "K",
    "OCQ": "X",
    "OCS": "C",
    "ODA": "X",
    "OHI": "H",
    "OHS": "D",
    "OIC": "X",
    "OMH": "X",
    "OMT": "M",
    "ONL": "X",
    "OPR": "R",
    "ORN": "A",
    "ORQ": "R",
    "OSL": "X",
    "OTT": "X",
    "OTZ": "G",
    "P1L": "C",
    "P2Q": "X",
    "P9S": "C",
    "PAQ": "Y",
    "PAT": "W",
    "PBE": "X",
    "PBF": "F",
    "PCA": "Q",
    "PCS": "F",
    "PDF": "X",
    "PDW": "X",
    "PEA": "X",
    "PF5": "F",
    "PFF": "F",
    "PGA": "X",
    "PH6": "P",
    "PH8": "X",
    "PHA": "F",
    "PHD": "D",
    "PHE": "F",
    "PHI": "F",
    "PHL": "F",
    "PHQ": "X",
    "PIA": "A",
    "PIV": "X",
    "PJE": "X",
    "PJJ": "X",
    "PLF": "X",
    "PLJ": "X",
    "PLW": "X",
    "PM3": "F",
    "PN2": "X",
    "PPI": "X",
    "PPN": "F",
    "PR4": "X",
    "PR9": "P",
    "PRK": "X",
    "PRO": "P",
    "PRQ": "X",
    "PRS": "P",
    "PRV": "G",
    "PRW": "X",
    "PSA": "F",
    "PTM": "Y",
    "PTR": "Y",
    "PUK": "X",
    "PVA": "X",
    "PVH": "H",
    "PVO": "X",
    "PYL": "O",
    "PYR": "X",
    "PYX": "C",
    "Q8X": "C",
    "QCS": "C",
    "QMM": "Q",
    "QPA": "C",
    "QSC": "X",
    "R0K": "E",
    "R1A": "C",
    "RGL": "R",
    "RNG": "X",
    "RTY": "X",
    "RVX": "S",
    "S6F": "X",
    "SAC": "S",
    "SAR": "G",
    "SBG": "X",
    "SC2": "X",
    "SCH": "C",
    "SCY": "C",
    "SDP": "S",
    "SE7": "A",
    "SEB": "S",
    "SEC": "U",
    "SEN": "S",
    "SEP": "S",
    "SER": "S",
    "SET": "S",
    "SGB": "S",
    "SGR": "X",
    "SGX": "X",
    "SHV": "X",
    "SIC": "D",
    "SIN": "X",
    "SLL": "X",
    "SLZ": "K",
    "SMC": "C",
    "SME": "M",
    "SMF": "F",
    "SNC": "C",
    "SNM": "S",
    "SNN": "N",
    "SRZ": "S",
    "STA": "X",
    "SUI": "D",
    "SUJ": "X",
    "SUN": "S",
    "SVA": "S",
    "SVV": "S",
    "SVW": "S",
    "SVY": "S",
    "SVZ": "S",
    "SXE": "S",
    "SYS": "U",
    "TA2": "X",
    "TBG": "V",
    "TCQ": "Y",
    "TEE": "X",
    "TH5": "T",
    "TH6": "T",
    "THC": "T",
    "THR": "T",
    "TIG": "X",
    "TIH": "A",
    "TIS": "X",
    "TLX": "X",
    "TLY": "X",
    "TMD": "T",
    "TNQ": "X",
    "TOQ": "W",
    "TOX": "X",
    "TOZ": "G",
    "TPO": "T",
    "TPQ": "Y",
    "TQQ": "W",
    "TRF": "W",
    "TRM": "X",
    "TRN": "W",
    "TRO": "W",
    "TRP": "W",
    "TRQ": "W",
    "TRW": "W",
    "TSY": "C",
    "TTQ": "W",
    "TTS": "Y",
    "TVA": "X",
    "TY2": "Y",
    "TY8": "X",
    "TY9": "X",
    "TYC": "X",
    "TYI": "Y",
    "TYJ": "Y",
    "TYO": "Y",
    "TYQ": "Y",
    "TYR": "Y",
    "TYS": "Y",
    "TYT": "Y",
    "TYW": "Y",
    "TYY": "Y",
    "TYZ": "X",
    "U2X": "X",
    "U3X": "X",
    "UNK": "X",
    "URE": "X",
    "URV": "X",
    "USC": "X",
    "UU4": "X",
    "UU5": "X",
    "V9C": "X",
    "VAD": "V",
    "VAI": "X",
    "VAL": "V",
    "VLM": "X",
    "VME": "X",
    "W6Q": "X",
    "WFP": "X",
    "WLU": "L",
    "WPA": "F",
    "WRP": "W",
    "WVL": "V",
    "X5H": "X",
    "XCN": "C",
    "XCP": "X",
    "XFW": "X",
    "XOK": "X",
    "XPC": "X",
    "XSN": "N",
    "XW1": "X",
    "XY1": "X",
    "XY5": "X",
    "XYC": "X",
    "YCM": "C",
    "YCP": "X",
    "YNM": "X",
    "YOF": "Y",
    "YTF": "Q",
    "Z3E": "X",
    "ZAE": "X",
    "ZAL": "A",
    "ZCL": "F",
    "ZGL": "X",
    "ZS8": "X",
    "ZSC": "X",
    "ZSN": "X",
    "ZXW": "X",
    "ZYJ": "X",
    "ZYK": "X",
    "ZZJ": "A",
}

BB_ATOMS = ["N", "CA", "C", "O"]
SC_ATOMS = [
    "CE3",
    "CZ",
    "SD",
    "CD1",
    "CB",
    "NH1",
    "OG1",
    "CE1",
    "OE1",
    "CZ2",
    "OH",
    "CG",
    "CZ3",
    "NE",
    "CH2",
    "OD1",
    "NH2",
    "ND2",
    "OG",
    "CG2",
    "OE2",
    "CD2",
    "ND1",
    "NE2",
    "NZ",
    "CD",
    "CE2",
    "CE",
    "OD2",
    "SG",
    "NE1",
    "CG1",
    "OXT",
]
SC_ATOM_POSNS = {a: i for i, a in enumerate(SC_ATOMS)}

AA3LetterCode = [
    "ALA",
    "ARG",
    "ASN",
    "ASP",
    "ASX",
    "CYS",
    "GLU",
    "GLN",
    "GLX",
    "GLY",
    "HIS",
    "ILE",
    "LEU",
    "LYS",
    "MET",
    "PHE",
    "PRO",
    "SER",
    "THR",
    "TRP",
    "TYR",
    "VAL",
    "UNK",
]
AA1LetterCode = [
    "A",
    "R",
    "N",
    "D",
    "B",
    "C",
    "E",
    "Q",
    "Z",
    "G",
    "H",
    "I",
    "L",
    "K",
    "M",
    "F",
    "P",
    "S",
    "T",
    "W",
    "Y",
    "V",
    "X",
    "-",
]

NAT_AA_SET = set(AA1LetterCode[:-1])
VALID_AA_3_LETTER = set(AA3LetterCode)
VALID_AA_1_LETTER = set(AA1LetterCode)

ALL_ATOMS = BB_ATOMS + SC_ATOMS

ALL_ATOM_POSNS = {a: i for i, a in enumerate(ALL_ATOMS)}

THREE_TO_ONE = {three: one for three, one in zip(AA3LetterCode, AA1LetterCode)}
ONE_TO_THREE = {one: three for three, one in THREE_TO_ONE.items()}


AA_TO_INDEX = {
    "ALA": 0,
    "ARG": 1,
    "ASN": 2,
    "ASP": 3,
    "CYS": 4,
    "GLN": 5,
    "GLU": 6,
    "GLY": 7,
    "HIS": 8,
    "ILE": 9,
    "LEU": 10,
    "LYS": 11,
    "MET": 12,
    "PHE": 13,
    "PRO": 14,
    "SER": 15,
    "THR": 16,
    "TRP": 17,
    "TYR": 18,
    "VAL": 19,
    "UNK": 20,
}
AA_TO_INDEX.update({THREE_TO_ONE[aa]: v for aa, v in AA_TO_INDEX.items()})
INDEX_TO_AA_ONE = {AA_TO_INDEX[a]: a for a in AA_TO_INDEX.keys() if len(a) == 1}
INDEX_TO_AA_THREE = {AA_TO_INDEX[a]: a for a in AA_TO_INDEX.keys() if len(a) == 3}


AA_TO_SC_ATOMS: dict[str, list[str]] = {
    "MET": ["CB", "CE", "CG", "SD"],
    "ILE": ["CB", "CD1", "CG1", "CG2"],
    "LEU": ["CB", "CD1", "CD2", "CG"],
    "VAL": ["CB", "CG1", "CG2"],
    "THR": ["CB", "CG2", "OG1"],
    "ALA": ["CB"],
    "ARG": ["CB", "CD", "CG", "CZ", "NE", "NH1", "NH2"],
    "SER": ["CB", "OG"],
    "LYS": ["CB", "CD", "CE", "CG", "NZ"],
    "HIS": ["CB", "CD2", "CE1", "CG", "ND1", "NE2"],
    "GLU": ["CB", "CD", "CG", "OE1", "OE2"],
    "ASP": ["CB", "CG", "OD1", "OD2"],
    "PRO": ["CB", "CD", "CG"],
    "GLN": ["CB", "CD", "CG", "NE2", "OE1"],
    "TYR": ["CB", "CD1", "CD2", "CE1", "CE2", "CG", "CZ", "OH"],
    "TRP": ["CB", "CD1", "CD2", "CE2", "CE3", "CG", "CH2", "CZ2", "CZ3", "NE1"],
    "CYS": ["CB", "SG"],
    "ASN": ["CB", "CG", "ND2", "OD1"],
    "PHE": ["CB", "CD1", "CD2", "CE1", "CE2", "CG", "CZ"],
    "GLY": [],
    "UNK": [],
}


def update_letters(
    x: dict[str, list[str]], is_three: bool = True
) -> dict[str, list[str]]:
    mapping = THREE_TO_ONE if is_three else ONE_TO_THREE
    x.update({mapping[res]: value for res, value in x.items()})
    return x


AA_TO_SC_ATOMS = update_letters(AA_TO_SC_ATOMS)

ELE2NUM = {
    "C": 0,
    "C1": 0,
    "H": 1,
    "O": 2,
    "N": 3,
    "S": 4,
    "SE": 5,
    "other": 6,
    "filler": 7,
    "F": 8,
    "CL": 9,
    "BR": 10,
    "P": 4,
    "I": 11,
}

LIGAND_VALIDATION_ATTRIBUTES = [
    "validation_pocket_ID",
    "ligand_rscc",
    "ligand_rsr",
    "ligand_owab",
    "ligand_avgoccu",
    "ligand_NatomsEDS",
    "ligand_mogul-ignore",
    "ligand_model",
    "ligand_auth_chain",
    "ligand_auth_resnum",
    "ligand_said",
    "ligand_ent",
    "ligand_seq",
    "ligand_icode",
    "ligand_altcode",
    "ligand_ost_match_alt",
    "prox_rsr",
    "prox_rsrz",
    "prox_rscc",
    "prox_avgoccu",
    "prox_B_factors",
    "prox_has_clashing_partial_O",
    "prox_altcodes",
    "prox_conop_atom_count_heavy",
    "prox_pdbx_atom_count_heavy",
    "prox_ost_atom_count_heavy",
    "prox_conop_chem_type",
    "prox_conop_chem_class",
    "prox_type",
    "prox_ost_match_alt",
    "prox_id",
    "prox_O_lt_.9",
    "prox_O_null",
    "prox_alternative_configuration_residues",
    "prox_unknown_residues",
    "prox_atom_count_unknown",
    "prox_missing_XML_residues",
    "prox_alternative_configuration_residues_flag",
    "ligand_asym_chain",
    "ligand_asym_resnum",
    "ligand_entity_id",
    "ligand_ost_atom_count",
    "ligand_ost_atom_count_heavy",
    "ligand_O_lt_.9",
    "ligand_O_has_null",
    "ligand_B_factors",
    "ligand_nh_B_factors_atom",
    "ligand_nh_B_factors_nh_median",
    "ligand_has_clashing_partial_O",
    "ligand_pdbx_atom_count",
    "ligand_pdbx_atom_count_heavy",
    "ligand_atom_count_unknown",
    "ligand_elapsed_time",
    "entry_elapsed_time",
    "entry_resolution_x",
    "entry_rfree",
    "entry_r",
    "entry_clashscore",
    "entry_percent_rama_outliers",
    "entry_attempted_validation_steps",
    "entry_data_completeness",
    "entry_percent_RSRZ_outliers",
    "entry_atom_count",
    "entry_molprobity",
    "entry_mean_b_factor",
    "entry_median_b_factor",
    "entry_pdbx_resolution",
    "entry_pdbx_reflns_resolution",
    "entry_meanI_over_sigI_obs",
    "entry_pdb_id_x",
    "ligand_num-H-reduce",
    "ligand_mogul_bonds_rmsz",
    "ligand_mogul_rmsz_numbonds",
    "ligand_mogul_angles_rmsz",
    "ligand_mogul_rmsz_numangles",
    "ligand_clash.atom",
    "ligand_clash.dist",
    "ligand_clash.clashmag",
    "ligand_clash.cid",
    "ligand_mog-bond-outlier.atoms",
    "ligand_mog-bond-outlier.numobs",
    "ligand_mog-bond-outlier.mean",
    "ligand_mog-bond-outlier.stdev",
    "ligand_mog-bond-outlier.mindiff",
    "ligand_mog-bond-outlier.Zscore",
    "ligand_mog-bond-outlier.obsval",
    "ligand_mog-angle-outlier.atoms",
    "ligand_mog-angle-outlier.numobs",
    "ligand_mog-angle-outlier.mean",
    "ligand_mog-angle-outlier.stdev",
    "ligand_mog-angle-outlier.mindiff",
    "ligand_mog-angle-outlier.Zscore",
    "ligand_mog-angle-outlier.obsval",
    "ligand_mog-torsion-outlier.atoms",
    "ligand_mog-torsion-outlier.numobs",
    "ligand_mog-torsion-outlier.mean",
    "ligand_mog-torsion-outlier.stdev",
    "ligand_mog-torsion-outlier.mindiff",
    "ligand_mog-torsion-outlier.local_density",
    "ligand_mog-torsion-outlier.obsval",
    "EDS_available",
    "entry_r_minus_rfree",
    "ligand_pass_iridium_criteria",
    "ligand_pass_validation_criteria",
    "joint_pocket_ID",
]
