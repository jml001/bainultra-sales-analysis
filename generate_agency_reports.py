#!/usr/bin/env python3
"""
Agency Intelligence Report Generator
Generates personalized secret-URL reports for each BainUltra agency
"""

import json
import hashlib
import os
from datetime import datetime
from pathlib import Path

# Territory mapping
TERRITORIES = {
    "Phoenix S G, LLC": "NY/NJ/PA",
    "Alpha Sales": "New England",
    "Premier Decorative Group": "CA/AZ/NV",
    "BU Agent - Ontario": "ON",
    "The Shae Group": "IL/WI/MN",
    "DME Marketing": "BC/AB/SK/MB",
    "ADream Decor": "TX/LA/OK/AR",
    "ClearWater Sales LLC": "MI/OH/W.PA",
    "The Bridge Agency": "NC/SC/AL/MS/TN",
    "VJS Marketing": "MO/IA/KS/NE",
    "Summit Architectural Resource": "CO/NM",
    "Personal Touch Sales": "FL",
    "BainUltra Corporate": "Direct/Other",
    "Greater Montreal": "QC - Montreal",
    "JDL Associates": "VA/MD/DC/WV",
    "The Bridge Agency GA": "GA",
    "D'Antoni Sales Group": "IN/TN/KY",
    "The Rain Company": "WA/OR/ID/MT/AK",
    "Quebec excluding MTL (+ Ottawa Region)": "QC/Ottawa",
    "S & D Lighting Group": "NB/NS/NL/PE",
    "Utah - Wyoming": "UT/WY",
    "Upstate NewYork": "Upstate NY",
    "Mexico": "MX",
    "Hawaii": "HI"
}

# Account-level data: 10-year avg, 2024, 2025
ACCOUNT_DATA = {
    "ADream Decor": {
        "Ferguson Enterprises Euless Br 61": {"ten_year_avg": 89282, "rev_2024": 93916, "rev_2025": 65509},
        "Hollywood Builders Hardware": {"ten_year_avg": 81792, "rev_2024": 82409, "rev_2025": 96802},
        "Ferguson Enterprises Houston": {"ten_year_avg": 64762, "rev_2024": 45934, "rev_2025": 19513},
        "Baths of America": {"ten_year_avg": 62835, "rev_2024": 50198, "rev_2025": 80856},
        "Reece Bath+Kitchen - Dallas": {"ten_year_avg": 57243, "rev_2024": 30341, "rev_2025": 54165},
        "The Jarrell Company - Dallas": {"ten_year_avg": 50772, "rev_2024": 65903, "rev_2025": 67626},
        "Reece Bath+Kitchen - Houston Br. 1134": {"ten_year_avg": 46309, "rev_2024": 0, "rev_2025": 8787},
        "Heatwave Supply - Tulsa": {"ten_year_avg": 45716, "rev_2024": 26962, "rev_2025": 18419},
        "Ferguson Broken Arrow": {"ten_year_avg": 41462, "rev_2024": 29760, "rev_2025": 15479},
        "Acero Bella Inc.": {"ten_year_avg": 40759, "rev_2024": 30114, "rev_2025": 29524},
        "Morrison Supply Fort Worth": {"ten_year_avg": 39323, "rev_2024": 19069, "rev_2025": 0},
        "The Bath & Kitchen Showplace / Moore Suppl...": {"ten_year_avg": 37042, "rev_2024": 0, "rev_2025": 0},
        "Lighting Inc. Hardware": {"ten_year_avg": 36859, "rev_2024": 0, "rev_2025": 24895},
        "Westheimer Plumbing & Hardware Warehouse": {"ten_year_avg": 36806, "rev_2024": 0, "rev_2025": 21621},
        "Westside Kitchen & Bath": {"ten_year_avg": 36736, "rev_2024": 24262, "rev_2025": 37098},
        "Expressions Home Gallery / Morsco Austin": {"ten_year_avg": 35416, "rev_2024": 0, "rev_2025": 0},
        "The Bath & Kitchen Showplace / Moore Suppl...": {"ten_year_avg": 34883, "rev_2024": 0, "rev_2025": 29282},
        "JCR Distributors Dallas": {"ten_year_avg": 34175, "rev_2024": 41227, "rev_2025": 14584},
        "Expressions Home Gallery - Morrison Supply...": {"ten_year_avg": 33784, "rev_2024": 0, "rev_2025": 0},
        "Southern Pipe Metairie": {"ten_year_avg": 31956, "rev_2024": 0, "rev_2025": 6944},
        "Facets of Austin": {"ten_year_avg": 28760, "rev_2024": 34716, "rev_2025": 45751},
        "Apex Supply Dallas": {"ten_year_avg": 26989, "rev_2024": 0, "rev_2025": 0},
    },
    "Alpha Sales": {
        "The Portland Group Billerica": {"ten_year_avg": 279543, "rev_2024": 154645, "rev_2025": 211158},
        "Torrco - Waterbury": {"ten_year_avg": 153735, "rev_2024": 187660, "rev_2025": 165179},
        "Sink & Spout by the Granite Group - Manche...": {"ten_year_avg": 150731, "rev_2024": 189666, "rev_2025": 71110},
        "Republic Plumbing Supply Norwood": {"ten_year_avg": 114424, "rev_2024": 80909, "rev_2025": 98327},
        "White's Plumbing Supplies": {"ten_year_avg": 112122, "rev_2024": 102725, "rev_2025": 102713},
        "Klaff's of South Norwalk": {"ten_year_avg": 107883, "rev_2024": 0, "rev_2025": 0},
        "Supply New England SO. Uxbridge": {"ten_year_avg": 91244, "rev_2024": 91922, "rev_2025": 85484},
        "Waterware Showrooms of Hartford": {"ten_year_avg": 86385, "rev_2024": 134073, "rev_2025": 104814},
        "Modern Plumbing Supply New Milford": {"ten_year_avg": 74806, "rev_2024": 70039, "rev_2025": 81581},
        "Designer Bath / Salem Plumbing Supply": {"ten_year_avg": 56027, "rev_2024": 37485, "rev_2025": 32015},
        "Sink & Spout by the Granite Group - Lowell": {"ten_year_avg": 54697, "rev_2024": 58512, "rev_2025": 48009},
        "Supply New England Warwick": {"ten_year_avg": 49416, "rev_2024": 47074, "rev_2025": 45395},
        "Modern Plumbing Supply Berlin": {"ten_year_avg": 49126, "rev_2024": 28358, "rev_2025": 26743},
        "Sink & Spout by the Granite Group - Concord": {"ten_year_avg": 48210, "rev_2024": 50108, "rev_2025": 65879},
        "Sink & Spout by the Granite Group -  Roche...": {"ten_year_avg": 40900, "rev_2024": 45680, "rev_2025": 15390},
        "The Ultimate Bath Store Worcester - Wholesale": {"ten_year_avg": 40341, "rev_2024": 70409, "rev_2025": 52818},
        "PV Sullivan Co Inc.": {"ten_year_avg": 38776, "rev_2024": 0, "rev_2025": 0},
        "Robinson Plumbing & Heating Supply Co. Inc...": {"ten_year_avg": 33587, "rev_2024": 0, "rev_2025": 0},
        "Republic Plumbing Supply Pembroke": {"ten_year_avg": 31315, "rev_2024": 18029, "rev_2025": 6030},
        "Republic Plumbing Supply North Weymouth": {"ten_year_avg": 29027, "rev_2024": 14798, "rev_2025": 15465},
        "Supply New England Yarmouth": {"ten_year_avg": 27808, "rev_2024": 23782, "rev_2025": 37571},
        "Sink & Spout by the Granite Group - Westerly": {"ten_year_avg": 26689, "rev_2024": 35757, "rev_2025": 27538},
    },
    "BU Agent - Ontario": {
        "Taps Wholesale Bath Centre Inc. Toronto": {"ten_year_avg": 216450, "rev_2024": 162627, "rev_2025": 102113},
        "Canaroma Bath & Tile": {"ten_year_avg": 188305, "rev_2024": 193926, "rev_2025": 103892},
        "Bath Emporium 2271292 Ontario Inc.": {"ten_year_avg": 176888, "rev_2024": 113545, "rev_2025": 131946},
        "Taps Wholesale Bath Center Mississauga": {"ten_year_avg": 116430, "rev_2024": 70583, "rev_2025": 73991},
        "Ginger's International Bath Center Ltd": {"ten_year_avg": 115679, "rev_2024": 57675, "rev_2025": 39186},
        "Tiles Plus dba Cesario  & CO.": {"ten_year_avg": 107249, "rev_2024": 139914, "rev_2025": 83558},
        "Amati Bath Center": {"ten_year_avg": 101971, "rev_2024": 45852, "rev_2025": 54297},
        "London Bath Centre": {"ten_year_avg": 85715, "rev_2024": 102774, "rev_2025": 56003},
        "Plumbing & Parts Home Centre": {"ten_year_avg": 85407, "rev_2024": 83913, "rev_2025": 44758},
        "Plumbing Centre Hamilton": {"ten_year_avg": 70505, "rev_2024": 77957, "rev_2025": 32044},
        "Glenbriar Home Hardware": {"ten_year_avg": 66562, "rev_2024": 33160, "rev_2025": 33036},
        "Taps & Tubs Kitchen & Bath Centre": {"ten_year_avg": 63222, "rev_2024": 0, "rev_2025": 0},
        "Naylor's Kitchen & Bath Cabinet Center": {"ten_year_avg": 59899, "rev_2024": 21083, "rev_2025": 19297},
        "Tapworks Kitchen & Bath Ltd.Scarborough": {"ten_year_avg": 48433, "rev_2024": 25755, "rev_2025": 34249},
        "Penmar Plumbing & Heating Supplies / Mist ...": {"ten_year_avg": 43239, "rev_2024": 50511, "rev_2025": 29007},
        "Crown Bath & Kitchen Inc.": {"ten_year_avg": 34212, "rev_2024": 21884, "rev_2025": 5203},
        "Aquavato - div Emco Corporation": {"ten_year_avg": 28693, "rev_2024": 0, "rev_2025": 16465},
        "Nova Baths Ltd": {"ten_year_avg": 20755, "rev_2024": 12343, "rev_2025": 20272},
        "Plympton Plumbing": {"ten_year_avg": 20343, "rev_2024": 43070, "rev_2025": 39128},
        "Sescolite Lighting - Burlington": {"ten_year_avg": 20302, "rev_2024": 0, "rev_2025": 15662},
        "Central Plumbing Supply Inc. Concord": {"ten_year_avg": 19177, "rev_2024": 22515, "rev_2025": 21284},
        "Bath & Kitchen Studio": {"ten_year_avg": 18489, "rev_2024": 0, "rev_2025": 11534},
    },
    "BainUltra Corporate": {
        "VENT002": {"ten_year_avg": 206254, "rev_2024": 282737, "rev_2025": 281389},
        "VENT001": {"ten_year_avg": 78126, "rev_2024": 97672, "rev_2025": 126757},
        "Z Accounts": {"ten_year_avg": 40844, "rev_2024": 27668, "rev_2025": 42746},
        "Frisbees Inc.": {"ten_year_avg": 19924, "rev_2024": 31462, "rev_2025": 21834},
        "Northern Plumbing Supply Grand Forks": {"ten_year_avg": 14835, "rev_2024": 0, "rev_2025": 12186},
        "City Design - Schanstra Design Group": {"ten_year_avg": 7358, "rev_2024": 0, "rev_2025": 0},
    },
    "ClearWater Sales LLC": {
        "Advance Plumbing": {"ten_year_avg": 357004, "rev_2024": 292771, "rev_2025": 255992},
        "Herald Wholesale - Premier Bath & Hardware": {"ten_year_avg": 283740, "rev_2024": 288303, "rev_2025": 147395},
        "Edelman Plumbing Supply Bedford Heights": {"ten_year_avg": 137497, "rev_2024": 118397, "rev_2025": 77884},
        "Nicklas Supply - Splash Inc.": {"ten_year_avg": 120460, "rev_2024": 75722, "rev_2025": 79267},
        "Crescent Supply of Penna Inc.": {"ten_year_avg": 56384, "rev_2024": 13958, "rev_2025": 13182},
        "Keidel Supply Co. Inc.": {"ten_year_avg": 54380, "rev_2024": 30956, "rev_2025": 48964},
        "Carr Supply Columbus Br. # 00728": {"ten_year_avg": 46380, "rev_2024": 51372, "rev_2025": 11354},
        "Bathworks by Plumbers & Factory Supplies Inc": {"ten_year_avg": 41602, "rev_2024": 41328, "rev_2025": 12750},
        "Worly Plumbing Supply Inc Columbus": {"ten_year_avg": 41474, "rev_2024": 42557, "rev_2025": 29551},
        "Advance Plumbing - Detroit": {"ten_year_avg": 37203, "rev_2024": 50036, "rev_2025": 27309},
        "Progressive Plumbing Supply - H.L. Claeys ...": {"ten_year_avg": 35362, "rev_2024": 15765, "rev_2025": 30013},
        "R. A. Townsend Company Saginaw": {"ten_year_avg": 24050, "rev_2024": 36814, "rev_2025": 20844},
        "Cleveland Plumbing Supply - Chagrin Falls": {"ten_year_avg": 23249, "rev_2024": 47188, "rev_2025": 27134},
        "Maumee Supply - Waterhouse Bath and Kitche...": {"ten_year_avg": 21185, "rev_2024": 0, "rev_2025": 22360},
        "Crescent Supply State College": {"ten_year_avg": 20904, "rev_2024": 22130, "rev_2025": 21137},
        "Crescent Supply Darlington": {"ten_year_avg": 17349, "rev_2024": 31317, "rev_2025": 12968},
        "Builders Plumbing Supply Lansing #317": {"ten_year_avg": 16371, "rev_2024": 19759, "rev_2025": 14612},
        "Richards Kitchen & Bath Experience #311": {"ten_year_avg": 16131, "rev_2024": 25486, "rev_2025": 0},
        "Nicklas Supply Inc. Murrysville": {"ten_year_avg": 13506, "rev_2024": 0, "rev_2025": 0},
        "Richards Plumbing Supply Kalamazoo": {"ten_year_avg": 13380, "rev_2024": 0, "rev_2025": 19370},
        "Vic Bond Sales Fenton": {"ten_year_avg": 12932, "rev_2024": 0, "rev_2025": 0},
        "Carr Supply Dayton": {"ten_year_avg": 12184, "rev_2024": 0, "rev_2025": 0},
    },
    "D'Antoni Sales Group": {
        "Willis Klein Showrooms Louisville": {"ten_year_avg": 40119, "rev_2024": 21201, "rev_2025": 12357},
        "Economy Plumbing Supply": {"ten_year_avg": 36856, "rev_2024": 33741, "rev_2025": 31287},
        "Waterplace - Leep's Supply Crown Point": {"ten_year_avg": 24711, "rev_2024": 14751, "rev_2025": 8876},
        "Lee Supply Carmel": {"ten_year_avg": 22277, "rev_2024": 22772, "rev_2025": 42483},
        "Ferguson Enterprises Jackson": {"ten_year_avg": 17738, "rev_2024": 0, "rev_2025": 0},
        "Hardwood Specialties Inc.": {"ten_year_avg": 14865, "rev_2024": 29825, "rev_2025": 9530},
        "Kenny & Company Nashville": {"ten_year_avg": 14448, "rev_2024": 27873, "rev_2025": 0},
        "Winsupply of Owensboro KY Co.": {"ten_year_avg": 11131, "rev_2024": 17363, "rev_2025": 5074},
        "Talewind Enterprises Inc. dba Thomas Kitch...": {"ten_year_avg": 9686, "rev_2024": 10863, "rev_2025": 5672},
        "Hendersonville Winnelson": {"ten_year_avg": 7794, "rev_2024": 16087, "rev_2025": 17174},
        "Florence Winnelson Co.": {"ten_year_avg": 7268, "rev_2024": 0, "rev_2025": 0},
        "Central Supply Company Indianapolis": {"ten_year_avg": 6938, "rev_2024": 0, "rev_2025": 0},
        "Von Tobel Co - Valparaiso": {"ten_year_avg": 6799, "rev_2024": 0, "rev_2025": 0},
        "Renaissance Tile & Bath Nashville": {"ten_year_avg": 5958, "rev_2024": 0, "rev_2025": 0},
        "Winteriors Bath & Lighting Gallery": {"ten_year_avg": 5289, "rev_2024": 0, "rev_2025": 14168},
    },
    "DME Marketing": {
        "B.A. Robinson Calgary - Robinson Lighting": {"ten_year_avg": 229084, "rev_2024": 197619, "rev_2025": 166609},
        "B.A. Robinson Bath Center - Winnipeg": {"ten_year_avg": 166316, "rev_2024": 83324, "rev_2025": 88947},
        "Robinson Supply Burnaby": {"ten_year_avg": 149570, "rev_2024": 70768, "rev_2025": 44597},
        "Cantu Bathrooms & Hardware Ltd. Vancouver": {"ten_year_avg": 144920, "rev_2024": 94494, "rev_2025": 77182},
        "B.A. Robinson Edmonton": {"ten_year_avg": 131853, "rev_2024": 105993, "rev_2025": 71289},
        "Studio by Wolseley Mechanical - Calgary": {"ten_year_avg": 120020, "rev_2024": 58968, "rev_2025": 49624},
        "Kitchen & Bath Classics Edmonton": {"ten_year_avg": 76950, "rev_2024": 32597, "rev_2025": 30146},
        "Wolseley Mechanical - Kitchen & Bath Class...": {"ten_year_avg": 71406, "rev_2024": 28881, "rev_2025": 34836},
        "Kitchen & Bath Classics Winnipeg/Wolseley ...": {"ten_year_avg": 51222, "rev_2024": 27104, "rev_2025": 21596},
        "Wolseley Plumbing Surrey": {"ten_year_avg": 49095, "rev_2024": 34101, "rev_2025": 11212},
        "B.A. Robinson Co. Ltd. Saskatoon": {"ten_year_avg": 36908, "rev_2024": 32004, "rev_2025": 14124},
        "Kitchen & Bath Classics Victoria": {"ten_year_avg": 33379, "rev_2024": 0, "rev_2025": 20715},
        "Kitchen & Bath Classics Saskatoon": {"ten_year_avg": 29851, "rev_2024": 15195, "rev_2025": 23417},
        "Wolseley Mechanical Red Deer": {"ten_year_avg": 26764, "rev_2024": 20331, "rev_2025": 12069},
        "Kitchen & Bath Classics Nanaimo": {"ten_year_avg": 25164, "rev_2024": 14831, "rev_2025": 17904},
        "Kitchen & Bath Classics Vancouver": {"ten_year_avg": 25123, "rev_2024": 0, "rev_2025": 0},
        "Norburn Lighting & Bath Centre Burnaby": {"ten_year_avg": 17776, "rev_2024": 12689, "rev_2025": 12271},
        "Kitchen & Bath Classics Kelowna": {"ten_year_avg": 17617, "rev_2024": 0, "rev_2025": 13647},
        "Best Plumbing and Heating Supplies Ltd - E...": {"ten_year_avg": 16129, "rev_2024": 36830, "rev_2025": 52076},
        "B.A. Robinson Co. Ltd. Kamloops": {"ten_year_avg": 12028, "rev_2024": 0, "rev_2025": 8341},
        "Wolseley Mechanical Group Langley": {"ten_year_avg": 10513, "rev_2024": 0, "rev_2025": 0},
        "Bartle & Gibson Ltd - Edmonton": {"ten_year_avg": 10405, "rev_2024": 23950, "rev_2025": 28050},
    },
    "Greater Montreal": {
        "Deschênes et Fils": {"ten_year_avg": 94646, "rev_2024": 153152, "rev_2025": 66885},
        "Batimat div. d'Emco Corp.": {"ten_year_avg": 83630, "rev_2024": 53736, "rev_2025": 86885},
        "Ciot Montréal Inc.": {"ten_year_avg": 54529, "rev_2024": 36161, "rev_2025": 25809},
        "Plomberie G. Létourneau / PGL 1957": {"ten_year_avg": 32605, "rev_2024": 14463, "rev_2025": 11990},
        "Vague & Vogue Pierrefonds - Wolseley Inc.": {"ten_year_avg": 26071, "rev_2024": 22577, "rev_2025": 21452},
        "Centre de Plomberie Jean Lépine Inc.": {"ten_year_avg": 18137, "rev_2024": 22361, "rev_2025": 15163},
        "Plomberie Ravary": {"ten_year_avg": 17307, "rev_2024": 11750, "rev_2025": 21343},
        "Plomberie Richard Tetrault Ltee": {"ten_year_avg": 14815, "rev_2024": 12023, "rev_2025": 30869},
        "Salle de Bain Splash Inc.": {"ten_year_avg": 9025, "rev_2024": 0, "rev_2025": 5810},
        "Thalassa Domicile Laval": {"ten_year_avg": 9008, "rev_2024": 0, "rev_2025": 0},
        "La Boutique de plomberie Decoration 25 Inc.": {"ten_year_avg": 8930, "rev_2024": 13897, "rev_2025": 0},
        "Ramacieri Soligo Inc.": {"ten_year_avg": 7463, "rev_2024": 0, "rev_2025": 7314},
        "La Boutique Plomberie Mascouche Inc.": {"ten_year_avg": 6374, "rev_2024": 0, "rev_2025": 0},
        "H. Dagenais & Fils": {"ten_year_avg": 5325, "rev_2024": 0, "rev_2025": 0},
        "Plomberie Martine Inc.": {"ten_year_avg": 5149, "rev_2024": 0, "rev_2025": 5800},
    },
    "JDL Associates": {
        "Thos Somerville Bath & Kitchen Store - Fal...": {"ten_year_avg": 111371, "rev_2024": 61035, "rev_2025": 53553},
        "Thos Somerville Bath & Kitchen Store - Owi...": {"ten_year_avg": 71281, "rev_2024": 38410, "rev_2025": 20133},
        "The Somerville Bath & Kitchen Store - Chev...": {"ten_year_avg": 65476, "rev_2024": 39778, "rev_2025": 23998},
        "Thos Somerville Bath & Kitchen Store - Ann...": {"ten_year_avg": 54549, "rev_2024": 48269, "rev_2025": 19076},
        "CMC Supply Inc. Roanoke": {"ten_year_avg": 44329, "rev_2024": 34586, "rev_2025": 26344},
        "Thos Somerville Bath & Kitchen Store - Ric...": {"ten_year_avg": 26091, "rev_2024": 15000, "rev_2025": 24525},
        "Thos Somerville Bath & Kitchen Store - Lan...": {"ten_year_avg": 22814, "rev_2024": 18825, "rev_2025": 5676},
        "The Somerville Bath & Kitchen Store - Ster...": {"ten_year_avg": 21332, "rev_2024": 39778, "rev_2025": 0},
        "W T Weaver & Sons Inc": {"ten_year_avg": 14902, "rev_2024": 0, "rev_2025": 15117},
        "Inspirations Bath & Kitchen Studio dba Haj...": {"ten_year_avg": 14601, "rev_2024": 21371, "rev_2025": 14527},
        "May Supply Company - Harrisonburg": {"ten_year_avg": 13652, "rev_2024": 12175, "rev_2025": 13435},
        "Northeastern Supply - Harrisonburg": {"ten_year_avg": 9797, "rev_2024": 17246, "rev_2025": 12182},
        "Noland Company Chesapeake": {"ten_year_avg": 9713, "rev_2024": 0, "rev_2025": 0},
        "Atlantic Bath & Brass Inc.": {"ten_year_avg": 9652, "rev_2024": 0, "rev_2025": 0},
        "Koval Building & Plumbing Company Inc.": {"ten_year_avg": 8474, "rev_2024": 33032, "rev_2025": 44120},
        "Renaissance Tile & Bath Inc. Alexandria": {"ten_year_avg": 8464, "rev_2024": 0, "rev_2025": 0},
        "Shank Wholesalers Inc.": {"ten_year_avg": 8383, "rev_2024": 0, "rev_2025": 0},
    },
    "Mexico": {
        "Interiosimo Corporativo": {"ten_year_avg": 5144, "rev_2024": 31604, "rev_2025": 14085},
    },
    "Personal Touch Sales": {
        "Ferguson Enterprises Tamarac Br. 140": {"ten_year_avg": 66759, "rev_2024": 110212, "rev_2025": 55015},
        "The Plumbing Place Inc.": {"ten_year_avg": 42605, "rev_2024": 30877, "rev_2025": 36765},
        "Millers Elegant Hardware LLC": {"ten_year_avg": 42405, "rev_2024": 43728, "rev_2025": 58125},
        "Decorator's Plumbing": {"ten_year_avg": 36294, "rev_2024": 41000, "rev_2025": 40354},
        "Ferguson Enterprises Fort Myers Br 60": {"ten_year_avg": 35668, "rev_2024": 37052, "rev_2025": 35174},
        "Wool Plumbing Supply Sunrise": {"ten_year_avg": 28054, "rev_2024": 0, "rev_2025": 0},
        "Millenia Bath LLC": {"ten_year_avg": 27645, "rev_2024": 58307, "rev_2025": 51113},
        "Farrey's Wholesale Hardware Inc - North Miami": {"ten_year_avg": 27463, "rev_2024": 10138, "rev_2025": 9903},
        "Miller's Fine Decorative Hardware - Jupiter": {"ten_year_avg": 19659, "rev_2024": 15000, "rev_2025": 29537},
        "European Sink Outlet": {"ten_year_avg": 19480, "rev_2024": 20708, "rev_2025": 8009},
        "The Plumbing Gallery Div. of Gorman": {"ten_year_avg": 17806, "rev_2024": 43924, "rev_2025": 55678},
        "Naples Plumbing Studio": {"ten_year_avg": 17350, "rev_2024": 30013, "rev_2025": 12280},
        "Allied Kitchen & Bath Inc.": {"ten_year_avg": 15216, "rev_2024": 14969, "rev_2025": 16564},
        "Sophisticated Hardware & Plumbing Fort Lau...": {"ten_year_avg": 15101, "rev_2024": 21139, "rev_2025": 9004},
        "Cobblestone Court Inc.": {"ten_year_avg": 14971, "rev_2024": 29286, "rev_2025": 7209},
        "Wool Plumbing Supply Miami": {"ten_year_avg": 14592, "rev_2024": 0, "rev_2025": 0},
        "Designer's Plumbing & Hardware Miami": {"ten_year_avg": 14109, "rev_2024": 18460, "rev_2025": 11595},
        "Wool Supply of Tampa": {"ten_year_avg": 11116, "rev_2024": 24517, "rev_2025": 5366},
        "Lawrence Bath and Kitchen Showplace": {"ten_year_avg": 10888, "rev_2024": 0, "rev_2025": 0},
        "Architectural Elegance Incorporated": {"ten_year_avg": 8116, "rev_2024": 0, "rev_2025": 0},
        "Coral Gables Plumbing": {"ten_year_avg": 7634, "rev_2024": 0, "rev_2025": 0},
        "Artisan Kitchen and Bath Gallery": {"ten_year_avg": 6717, "rev_2024": 0, "rev_2025": 0},
    },
    "Phoenix S G, LLC": {
        "Ferguson Bayport": {"ten_year_avg": 535474, "rev_2024": 200227, "rev_2025": 148206},
        "Home and Stone / Quality Bath": {"ten_year_avg": 462926, "rev_2024": 513066, "rev_2025": 470369},
        "Hardware Designs Inc.": {"ten_year_avg": 270361, "rev_2024": 263311, "rev_2025": 271639},
        "Decor Planet - Brooklyn": {"ten_year_avg": 255557, "rev_2024": 186131, "rev_2025": 71571},
        "Richmond Tile & Bath": {"ten_year_avg": 193427, "rev_2024": 50362, "rev_2025": 24963},
        "Ferguson Enterprises Secaucus": {"ten_year_avg": 170457, "rev_2024": 124465, "rev_2025": 45427},
        "Best Plumbing Tile & Stone - Somers - Br. 206": {"ten_year_avg": 129721, "rev_2024": 149917, "rev_2025": 179781},
        "Grand Central Showroom - Spring Valley": {"ten_year_avg": 95944, "rev_2024": 18658, "rev_2025": 8240},
        "Fancy Fixtures Jericho": {"ten_year_avg": 92599, "rev_2024": 0, "rev_2025": 0},
        "C & L Plumbing Supply": {"ten_year_avg": 92252, "rev_2024": 59861, "rev_2025": 48696},
        "AF Supply New York": {"ten_year_avg": 82464, "rev_2024": 146520, "rev_2025": 116689},
        "Ferguson Enterprises Middletown": {"ten_year_avg": 75487, "rev_2024": 54067, "rev_2025": 29708},
        "Three Way Plumbing Bayside": {"ten_year_avg": 69995, "rev_2024": 0, "rev_2025": 0},
        "Central Plumbing Specialties Yonkers": {"ten_year_avg": 66215, "rev_2024": 33041, "rev_2025": 33620},
        "Oasis Showrooms By Apr Supply Co. - Newark": {"ten_year_avg": 65209, "rev_2024": 29274, "rev_2025": 20946},
        "Fancy Fixtures Plainview": {"ten_year_avg": 62251, "rev_2024": 154972, "rev_2025": 119125},
        "Ferguson Enterprises LLC King of Prussia B...": {"ten_year_avg": 46534, "rev_2024": 28040, "rev_2025": 11464},
        "Icon Knobs LLC": {"ten_year_avg": 46196, "rev_2024": 80372, "rev_2025": 26029},
        "Weinstein Supply Willow Grove": {"ten_year_avg": 41497, "rev_2024": 21266, "rev_2025": 14022},
        "Simon's of Water Mill / WaterMill Building...": {"ten_year_avg": 38897, "rev_2024": 42357, "rev_2025": 45526},
        "South Amboy Plumbing": {"ten_year_avg": 31745, "rev_2024": 0, "rev_2025": 0},
        "Waterways Decor Inc.": {"ten_year_avg": 28926, "rev_2024": 62250, "rev_2025": 48835},
    },
    "Premier Decorative Group": {
        "Pirch Inc. - San Diego": {"ten_year_avg": 200663, "rev_2024": 69324, "rev_2025": 0},
        "Western Nevada Supply Sparks": {"ten_year_avg": 136991, "rev_2024": 166070, "rev_2025": 171673},
        "Faucets N' Fixtures Orange": {"ten_year_avg": 106319, "rev_2024": 161820, "rev_2025": 116709},
        "Pirch Inc. - Glendale": {"ten_year_avg": 86662, "rev_2024": 0, "rev_2025": 0},
        "Jack London Kitchen & Bath Gallery - Oakland": {"ten_year_avg": 80566, "rev_2024": 84916, "rev_2025": 46801},
        "General Plumbing Supply Walnut Creek": {"ten_year_avg": 77145, "rev_2024": 41165, "rev_2025": 51758},
        "Sierra Plumbing Supply Inc": {"ten_year_avg": 73873, "rev_2024": 73096, "rev_2025": 63654},
        "Snyder Diamond Santa Monica": {"ten_year_avg": 73627, "rev_2024": 59084, "rev_2025": 65093},
        "Vic's Plumbing Supply Inc.": {"ten_year_avg": 73457, "rev_2024": 65307, "rev_2025": 60443},
        "Ferguson Plumbing - Costa Mesa": {"ten_year_avg": 70747, "rev_2024": 0, "rev_2025": 0},
        "Ferguson Enterprises LLC Sacramento, Br #686": {"ten_year_avg": 62124, "rev_2024": 102303, "rev_2025": 71773},
        "B & C Custom Hardware and Bath - Irvine": {"ten_year_avg": 62116, "rev_2024": 0, "rev_2025": 0},
        "Splashworks a Kitchen & Bath Gallery": {"ten_year_avg": 59148, "rev_2024": 57350, "rev_2025": 25286},
        "Ferguson Las Vegas": {"ten_year_avg": 56597, "rev_2024": 45000, "rev_2025": 134082},
        "Studio 41 Scottsdale": {"ten_year_avg": 54827, "rev_2024": 84242, "rev_2025": 41399},
        "Clyde Hardware Co. Inc.": {"ten_year_avg": 46171, "rev_2024": 46644, "rev_2025": 22750},
        "Central Arizona Supply - Mesa": {"ten_year_avg": 45625, "rev_2024": 83237, "rev_2025": 64115},
        "European Bath Kitchen Tile & Stone": {"ten_year_avg": 45438, "rev_2024": 0, "rev_2025": 0},
        "George's Kitchen and Bath": {"ten_year_avg": 44844, "rev_2024": 0, "rev_2025": 13452},
        "Bathworks Instyle Inc.": {"ten_year_avg": 39222, "rev_2024": 20283, "rev_2025": 35921},
        "Studio Belmont - San Jose": {"ten_year_avg": 39125, "rev_2024": 0, "rev_2025": 0},
        "Premier Bath & Kitchen - Rancho Cordova": {"ten_year_avg": 37924, "rev_2024": 0, "rev_2025": 27452},
    },
    "Quebec excluding MTL (+ Ottawa Region)": {
        "Céramique Décor Inc. Charlesbourg": {"ten_year_avg": 36226, "rev_2024": 0, "rev_2025": 5498},
        "Emco Corporation": {"ten_year_avg": 31543, "rev_2024": 33192, "rev_2025": 29110},
        "Thalassa Domicile Quebec": {"ten_year_avg": 30741, "rev_2024": 0, "rev_2025": 0},
        "Astro Design Center": {"ten_year_avg": 26457, "rev_2024": 20737, "rev_2025": 0},
        "J. & M. Gregoire Inc.": {"ten_year_avg": 16474, "rev_2024": 0, "rev_2025": 0},
        "Maison et Compagnie": {"ten_year_avg": 9869, "rev_2024": 86238, "rev_2025": 12451},
        "Westend Bath & Kitchen": {"ten_year_avg": 9470, "rev_2024": 0, "rev_2025": 0},
        "Plomberie Outaouais Enr.": {"ten_year_avg": 8983, "rev_2024": 0, "rev_2025": 0},
    },
    "S & D Lighting Group": {
        "Eddy Group Ltd Fredericton": {"ten_year_avg": 24387, "rev_2024": 22345, "rev_2025": 33581},
        "Eddy Group Ltd Halifax": {"ten_year_avg": 16696, "rev_2024": 28963, "rev_2025": 12719},
        "Eddy Group Ltd Truro": {"ten_year_avg": 11902, "rev_2024": 0, "rev_2025": 9187},
        "Eddy Group Ltd Bathurst": {"ten_year_avg": 11205, "rev_2024": 18987, "rev_2025": 7110},
        "Eddy Group Ltd St-John": {"ten_year_avg": 6533, "rev_2024": 0, "rev_2025": 17705},
        "Nova Scotia Building Supplies (1982) Ltd.": {"ten_year_avg": 5176, "rev_2024": 0, "rev_2025": 0},
    },
    "Summit Architectural Resource": {
        "Ultra Design Center": {"ten_year_avg": 164905, "rev_2024": 120812, "rev_2025": 126041},
        "Rampart Plumbing & Heating Supply - Div of...": {"ten_year_avg": 161596, "rev_2024": 170200, "rev_2025": 169532},
        "Dahl of Avon": {"ten_year_avg": 57373, "rev_2024": 49349, "rev_2025": 80554},
        "Ferguson Enterprises Steamboat Springs": {"ten_year_avg": 48653, "rev_2024": 47730, "rev_2025": 14736},
        "Rampart Plumbing & Heating Supply Inc. - D...": {"ten_year_avg": 46850, "rev_2024": 26477, "rev_2025": 44362},
        "Dahl Decorative Kitchen & Bath GS #189": {"ten_year_avg": 37524, "rev_2024": 44940, "rev_2025": 42851},
        "Confluence Kitchen & Bath - Closed use KSA...": {"ten_year_avg": 23205, "rev_2024": 21886, "rev_2025": 0},
        "Solutions Bath & Kitchen Div. of Martz Sup...": {"ten_year_avg": 22335, "rev_2024": 16136, "rev_2025": 12799},
        "Christopher's Kitchen & Bath - Englewood": {"ten_year_avg": 21789, "rev_2024": 11079, "rev_2025": 11634},
        "Dahl Decorative Kitchen & Bath Montrose": {"ten_year_avg": 19617, "rev_2024": 16443, "rev_2025": 19829},
        "Santa Fe By Design": {"ten_year_avg": 16196, "rev_2024": 19586, "rev_2025": 0},
        "Doc Savage Supply": {"ten_year_avg": 13020, "rev_2024": 0, "rev_2025": 0},
        "Confluence Kitchen & Bath": {"ten_year_avg": 9423, "rev_2024": 21886, "rev_2025": 39127},
    },
    "The Bridge Agency": {
        "Cregger Company Inc. Bluffton": {"ten_year_avg": 96800, "rev_2024": 145818, "rev_2025": 135534},
        "Wilkinson Supply Company Raleigh": {"ten_year_avg": 72435, "rev_2024": 71199, "rev_2025": 80217},
        "Park Supply Co Inc. Huntsville BR20": {"ten_year_avg": 64723, "rev_2024": 66746, "rev_2025": 25816},
        "Beeson Hardware": {"ten_year_avg": 44817, "rev_2024": 35299, "rev_2025": 19067},
        "Mississippi Coast Supply Co. Inc": {"ten_year_avg": 43198, "rev_2024": 26404, "rev_2025": 18886},
        "The Majestic Bath Division of Hajoca": {"ten_year_avg": 41486, "rev_2024": 12395, "rev_2025": 5164},
        "V & W Supply Company Birmingham Inc.": {"ten_year_avg": 40097, "rev_2024": 53296, "rev_2025": 29559},
        "Bird Decorative Hardware & Bath Inc. Charl...": {"ten_year_avg": 29435, "rev_2024": 42410, "rev_2025": 22866},
        "Prosource LLC Greenville": {"ten_year_avg": 28768, "rev_2024": 23033, "rev_2025": 17791},
        "Bird Decorative Hardware & Bath Inc. Wilmi...": {"ten_year_avg": 25455, "rev_2024": 31339, "rev_2025": 41531},
        "Design on Tap / Div. of Cregger Company Ch...": {"ten_year_avg": 22577, "rev_2024": 11243, "rev_2025": 17230},
        "Gateway Supply Co. - Greenville": {"ten_year_avg": 19971, "rev_2024": 35198, "rev_2025": 27398},
        "Wilkinson Supply Company Carrboro": {"ten_year_avg": 19629, "rev_2024": 29251, "rev_2025": 7107},
        "Fixtures and Finishes LLC": {"ten_year_avg": 17465, "rev_2024": 16057, "rev_2025": 18223},
        "Bird Decorative Hardware & Bath Inc. Charl...": {"ten_year_avg": 17047, "rev_2024": 28184, "rev_2025": 8557},
        "Bella Hardware & Bath": {"ten_year_avg": 16319, "rev_2024": 23587, "rev_2025": 18549},
        "Prosource LLC Hendersonville": {"ten_year_avg": 15724, "rev_2024": 15718, "rev_2025": 36461},
        "Plumbing Distributors - Nashville": {"ten_year_avg": 14967, "rev_2024": 16425, "rev_2025": 35717},
        "Cregger Company Inc. - The Nest - Columbia": {"ten_year_avg": 14893, "rev_2024": 0, "rev_2025": 9957},
        "Ferguson Enterprises Pensacola": {"ten_year_avg": 13100, "rev_2024": 14820, "rev_2025": 9112},
        "Winsupply Mt Pleasant SC CO": {"ten_year_avg": 10205, "rev_2024": 0, "rev_2025": 9373},
        "Ferguson Enterprises Asheville": {"ten_year_avg": 10173, "rev_2024": 0, "rev_2025": 17607},
    },
    "The Bridge Agency GA": {
        "European Kitchen & BathWorks": {"ten_year_avg": 60824, "rev_2024": 55763, "rev_2025": 13845},
        "City Plumbing & Electric Gainesville": {"ten_year_avg": 52081, "rev_2024": 0, "rev_2025": 0},
        "City Plumbing & Electric Blairsville": {"ten_year_avg": 22467, "rev_2024": 91960, "rev_2025": 25564},
        "Plumbing Distributors Inc. - Roswell": {"ten_year_avg": 22140, "rev_2024": 11711, "rev_2025": 62037},
        "W.A. Bragg Co. Evans": {"ten_year_avg": 18874, "rev_2024": 13399, "rev_2025": 8197},
        "Plumbing Distributors Inc. - Atlanta": {"ten_year_avg": 16384, "rev_2024": 12741, "rev_2025": 8222},
        "Sandpiper Supply Inc.": {"ten_year_avg": 13994, "rev_2024": 21443, "rev_2025": 16995},
        "Plumbing Distributors Inc. - Lawrenceville": {"ten_year_avg": 11191, "rev_2024": 0, "rev_2025": 15580},
        "Renaissance Tile & Bath Atlanta": {"ten_year_avg": 9756, "rev_2024": 0, "rev_2025": 11313},
        "Southern Pipe & Supply Rome": {"ten_year_avg": 9621, "rev_2024": 15284, "rev_2025": 6959},
        "Southern Pipe & Supply Garden City": {"ten_year_avg": 8873, "rev_2024": 0, "rev_2025": 0},
        "City Plumbing & Electric Rabun Gap": {"ten_year_avg": 8242, "rev_2024": 0, "rev_2025": 21323},
        "City Plumbing & Electric Cumming": {"ten_year_avg": 7886, "rev_2024": 0, "rev_2025": 0},
    },
    "The Rain Company": {
        "Chown Hardware Portland": {"ten_year_avg": 69151, "rev_2024": 49307, "rev_2025": 31412},
        "Abbrio - MasterSource - Pacific Plumbing": {"ten_year_avg": 57429, "rev_2024": 66995, "rev_2025": 18340},
        "Chown Hardware Inc. Bellevue": {"ten_year_avg": 45603, "rev_2024": 43908, "rev_2025": 25277},
        "Faucet's N' Fixtures": {"ten_year_avg": 8281, "rev_2024": 0, "rev_2025": 0},
        "KIE Supply Corporation - Kennewick": {"ten_year_avg": 6320, "rev_2024": 0, "rev_2025": 0},
    },
    "The Shae Group": {
        "Studio 41(Highland Park) /Remodelers Suppl...": {"ten_year_avg": 599520, "rev_2024": 486243, "rev_2025": 515124},
        "Algor Plumbing & Heating Supply": {"ten_year_avg": 57398, "rev_2024": 14320, "rev_2025": 15457},
        "First Supply - Gerhards The Kitchen and Ba...": {"ten_year_avg": 53605, "rev_2024": 34292, "rev_2025": 24595},
        "Crawford Supply - Itasca #336": {"ten_year_avg": 52882, "rev_2024": 20317, "rev_2025": 15674},
        "Banner Plumbing Supply": {"ten_year_avg": 49834, "rev_2024": 66719, "rev_2025": 54374},
        "First Supply - Gerhards The Kitchen and Ba...": {"ten_year_avg": 48938, "rev_2024": 55535, "rev_2025": 37707},
        "Traditional Floors & Design Center": {"ten_year_avg": 35474, "rev_2024": 26345, "rev_2025": 23076},
        "First Supply - Gerhards The Kitchen and Ba...": {"ten_year_avg": 34082, "rev_2024": 37678, "rev_2025": 33552},
        "First Supply - Gerhards The Kitchen and Ba...": {"ten_year_avg": 27179, "rev_2024": 45111, "rev_2025": 14930},
        "Dakota Supply Group - Plymouth": {"ten_year_avg": 25003, "rev_2024": 0, "rev_2025": 5576},
        "Allied Plumbing & Heating Supply Co.": {"ten_year_avg": 24637, "rev_2024": 30768, "rev_2025": 24774},
        "Fox Home Center Inc.": {"ten_year_avg": 22483, "rev_2024": 15818, "rev_2025": 18419},
        "Ferguson Enterprises LLC West Allis Br. # ...": {"ten_year_avg": 21157, "rev_2024": 0, "rev_2025": 0},
        "First Supply - Gerhards The Kitchen and Ba...": {"ten_year_avg": 18875, "rev_2024": 14337, "rev_2025": 18804},
        "Mid State Supply FDL": {"ten_year_avg": 18669, "rev_2024": 0, "rev_2025": 20020},
        "Minnesota Standard-SPS Showroom St-Louis Park": {"ten_year_avg": 15101, "rev_2024": 0, "rev_2025": 0},
        "Mid State Supply of Wautoma": {"ten_year_avg": 14808, "rev_2024": 0, "rev_2025": 14804},
        "Mid State Supply De Pere": {"ten_year_avg": 14452, "rev_2024": 0, "rev_2025": 0},
        "Connor Company McHenry": {"ten_year_avg": 14080, "rev_2024": 0, "rev_2025": 16715},
        "Bradley Interiors - The Floor to Ceiling S...": {"ten_year_avg": 13737, "rev_2024": 0, "rev_2025": 20990},
        "K & B Galleries Ltd. Northbrook": {"ten_year_avg": 13388, "rev_2024": 0, "rev_2025": 0},
        "First Supply - Gerhards The Kitchen and Ba...": {"ten_year_avg": 13115, "rev_2024": 55535, "rev_2025": 22859},
    },
}


# 10-year revenue data (from Salesforce query)
AGENCY_YEARLY_DATA = {
    "ADream Decor": {
        2015: 1840908, 2016: 1688457, 2017: 1515152, 2018: 1406336, 2019: 1391078,
        2020: 1242748, 2021: 1293982, 2022: 1609017, 2023: 1335992, 2024: 1052664, 2025: 989144
    },
    "Alpha Sales": {
        2015: 1824809, 2016: 1809215, 2017: 1689887, 2018: 1399005, 2019: 1496353,
        2020: 1415004, 2021: 2299412, 2022: 2533397, 2023: 2059569, 2024: 1792908, 2025: 1732280
    },
    "BU Agent - Ontario": {
        2015: 1570645, 2016: 1778916, 2017: 1839712, 2018: 1662684, 2019: 1866501,
        2020: 1504861, 2021: 1983312, 2022: 2123414, 2023: 1660353, 2024: 1535104, 2025: 1168408
    },
    "BainUltra Corporate": {
        2015: 144165, 2016: 139774, 2017: 167539, 2018: 220529, 2019: 179427,
        2020: 308981, 2021: 521776, 2022: 529512, 2023: 457607, 2024: 439785, 2025: 475949
    },
    "ClearWater Sales LLC": {
        2015: 1312640, 2016: 1341114, 2017: 1324554, 2018: 1305721, 2019: 1261017,
        2020: 1054683, 2021: 1390552, 2022: 1603245, 2023: 1215017, 2024: 1258707, 2025: 928555
    },
    "D'Antoni Sales Group": {
        2015: 241392, 2016: 234080, 2017: 260661, 2018: 218381, 2019: 188756,
        2020: 235643, 2021: 229337, 2022: 282622, 2023: 222968, 2024: 242988, 2025: 170917
    },
    "DME Marketing": {
        2015: 1821604, 2016: 1680967, 2017: 1585074, 2018: 1560376, 2019: 1171687,
        2020: 1042157, 2021: 1374454, 2022: 1320489, 2023: 1225413, 2024: 1068560, 2025: 943288
    },
    "Greater Montreal": {
        2015: 302185, 2016: 379970, 2017: 384681, 2018: 281677, 2019: 263840,
        2020: 328375, 2021: 476618, 2022: 431334, 2023: 401597, 2024: 394130, 2025: 317353
    },
    "Hawaii": {
        2015: 10630, 2016: 4284, 2017: 2979, 2018: 4636, 2019: 2205,
        2020: 0, 2021: 8276, 2022: 10361, 2023: 8171, 2024: 15015, 2025: 15120
    },
    "JDL Associates": {
        2015: 559619, 2016: 505187, 2017: 501523, 2018: 480587, 2019: 443498,
        2020: 455472, 2021: 551099, 2022: 517529, 2023: 400408, 2024: 353847, 2025: 305407
    },
    "Mexico": {
        2015: 0, 2016: 0, 2017: 0, 2018: 0, 2019: 0,
        2020: 0, 2021: 0, 2022: 0, 2023: 5751, 2024: 31602, 2025: 14085
    },
    "Personal Touch Sales": {
        2015: 428138, 2016: 551746, 2017: 398063, 2018: 455597, 2019: 411493,
        2020: 483952, 2021: 473817, 2022: 695754, 2023: 567520, 2024: 616383, 2025: 530052
    },
    "Phoenix S G, LLC": {
        2015: 3054402, 2016: 2716761, 2017: 2850077, 2018: 3166851, 2019: 2778057,
        2020: 2610870, 2021: 3803528, 2022: 3648411, 2023: 2646655, 2024: 2506556, 2025: 2025316
    },
    "Premier Decorative Group": {
        2015: 2051853, 2016: 2312562, 2017: 2046706, 2018: 1803617, 2019: 1836056,
        2020: 1840180, 2021: 2414631, 2022: 2715550, 2023: 1837015, 2024: 1650812, 2025: 1509278
    },
    "Quebec excluding MTL (+ Ottawa Region)": {
        2015: 227645, 2016: 226016, 2017: 188036, 2018: 125865, 2019: 113862,
        2020: 119700, 2021: 180392, 2022: 220053, 2023: 156973, 2024: 167443, 2025: 137152
    },
    "S & D Lighting Group": {
        2015: 77087, 2016: 79093, 2017: 60456, 2018: 48635, 2019: 70224,
        2020: 43364, 2021: 91760, 2022: 122607, 2023: 64444, 2024: 93196, 2025: 88738
    },
    "Summit Architectural Resource": {
        2015: 383528, 2016: 504104, 2017: 491875, 2018: 532459, 2019: 520519,
        2020: 597791, 2021: 661376, 2022: 820077, 2023: 588282, 2024: 553182, 2025: 601218
    },
    "The Bridge Agency": {
        2015: 702075, 2016: 674991, 2017: 615462, 2018: 611878, 2019: 650182,
        2020: 670500, 2021: 897745, 2022: 1075421, 2023: 833866, 2024: 833098, 2025: 778170
    },
    "The Bridge Agency GA": {
        2015: 218430, 2016: 266855, 2017: 271999, 2018: 320455, 2019: 243583,
        2020: 219908, 2021: 221970, 2022: 369504, 2023: 211442, 2024: 254298, 2025: 206510
    },
    "The Rain Company": {
        2015: 345770, 2016: 188485, 2017: 136860, 2018: 172661, 2019: 185531,
        2020: 193380, 2021: 186157, 2022: 324528, 2023: 192066, 2024: 185713, 2025: 152049
    },
    "The Shae Group": {
        2015: 1055141, 2016: 1036456, 2017: 1277676, 2018: 1128502, 2019: 979012,
        2020: 1040739, 2021: 1604171, 2022: 1678870, 2023: 1276532, 2024: 1051655, 2025: 1085867
    },
    "Upstate NewYork": {
        2015: 190721, 2016: 101624, 2017: 93362, 2018: 76785, 2019: 100682,
        2020: 110359, 2021: 121887, 2022: 132441, 2023: 65515, 2024: 50693, 2025: 47700
    },
    "Utah - Wyoming": {
        2015: 104957, 2016: 119328, 2017: 93468, 2018: 130427, 2019: 105688,
        2020: 102379, 2021: 98268, 2022: 172276, 2023: 136379, 2024: 87944, 2025: 82267
    },
    "VJS Marketing": {
        2015: 817788, 2016: 766621, 2017: 748882, 2018: 625548, 2019: 619641,
        2020: 500415, 2021: 753406, 2022: 949627, 2023: 754251, 2024: 804480, 2025: 711216
    }
}

def generate_token(agency_name):
    """Generate a unique secret token for each agency"""
    secret = f"bainultra-2026-{agency_name}-secret"
    return hashlib.sha256(secret.encode()).hexdigest()[:12]

def calculate_metrics(agency_name, yearly_data):
    """Calculate all metrics for an agency"""
    years = sorted(yearly_data.keys())

    # Current year and comparisons
    rev_2025 = yearly_data.get(2025, 0)
    rev_2024 = yearly_data.get(2024, 0)

    # 10-year average (2015-2024)
    ten_year_values = [yearly_data.get(y, 0) for y in range(2015, 2025)]
    ten_year_avg = sum(ten_year_values) / len([v for v in ten_year_values if v > 0]) if any(ten_year_values) else 0

    # Pre-COVID average (2015-2019)
    pre_covid_values = [yearly_data.get(y, 0) for y in range(2015, 2020)]
    pre_covid_avg = sum(pre_covid_values) / len([v for v in pre_covid_values if v > 0]) if any(pre_covid_values) else 0

    # COVID peak (2021-2022)
    covid_peak = max(yearly_data.get(2021, 0), yearly_data.get(2022, 0))

    # YoY change
    yoy_change = ((rev_2025 - rev_2024) / rev_2024 * 100) if rev_2024 > 0 else 0

    # vs 10-year average
    vs_ten_year = ((rev_2025 - ten_year_avg) / ten_year_avg * 100) if ten_year_avg > 0 else 0

    # Trend (growing/stable/declining)
    if yoy_change > 3:
        trend = "growing"
    elif yoy_change < -10:
        trend = "declining"
    else:
        trend = "stable"

    return {
        "rev_2025": rev_2025,
        "rev_2024": rev_2024,
        "yoy_change": yoy_change,
        "ten_year_avg": ten_year_avg,
        "vs_ten_year": vs_ten_year,
        "pre_covid_avg": pre_covid_avg,
        "covid_peak": covid_peak,
        "trend": trend,
        "yearly_data": yearly_data
    }

def format_currency(amount):
    """Format number as currency"""
    if amount >= 1000000:
        return f"${amount/1000000:.1f}M"
    elif amount >= 1000:
        return f"${amount/1000:.0f}K"
    else:
        return f"${amount:.0f}"

def generate_account_rows(agency_name):
    """Generate HTML table rows for account data"""
    accounts = ACCOUNT_DATA.get(agency_name, {})
    if not accounts:
        return "<tr><td colspan='6' style='text-align: center; color: var(--text-muted);'>No account data available</td></tr>"

    rows = []
    # Sort by 2025 revenue descending
    sorted_accounts = sorted(accounts.items(), key=lambda x: x[1].get("rev_2025", 0), reverse=True)

    for acct_name, data in sorted_accounts:
        avg = data.get("ten_year_avg", 0)
        rev_2024 = data.get("rev_2024", 0)
        rev_2025 = data.get("rev_2025", 0)

        # Calculate YoY change
        if rev_2024 > 0:
            yoy = ((rev_2025 - rev_2024) / rev_2024) * 100
        else:
            yoy = 100 if rev_2025 > 0 else 0

        # Determine status
        if rev_2025 > rev_2024 * 1.1:
            status = "Growing"
            status_class = "status-growing"
        elif rev_2025 < rev_2024 * 0.5:
            status = "At Risk"
            status_class = "status-at-risk"
        elif rev_2025 < rev_2024 * 0.85:
            status = "Declining"
            status_class = "status-declining"
        else:
            status = "Stable"
            status_class = "status-stable"

        yoy_class = "positive" if yoy > 0 else "negative" if yoy < -5 else "neutral"
        yoy_sign = "+" if yoy > 0 else ""

        rows.append(f'''
            <tr>
                <td style="text-align: left; color: var(--text-primary);">{acct_name}</td>
                <td>${avg:,.0f}</td>
                <td>${rev_2024:,.0f}</td>
                <td style="color: var(--text-primary); font-weight: 500;">${rev_2025:,.0f}</td>
                <td class="{yoy_class}">{yoy_sign}{yoy:.0f}%</td>
                <td class="{status_class}">{status}</td>
            </tr>
        ''')

    return "\n".join(rows)

def generate_html_report(agency_name, metrics, token):
    """Generate HTML report for an agency"""
    territory = TERRITORIES.get(agency_name, "Unknown")

    # Determine trend color
    if metrics["trend"] == "growing":
        trend_color = "#10b981"
        trend_icon = "+"
    elif metrics["trend"] == "declining":
        trend_color = "#ef4444"
        trend_icon = ""
    else:
        trend_color = "#eab308"
        trend_icon = ""

    # Build yearly chart data
    years = sorted(metrics["yearly_data"].keys())
    chart_labels = [str(y) for y in years]
    chart_data = [metrics["yearly_data"][y] / 1000 for y in years]  # In thousands

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BainUltra | {agency_name} Territory Report</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-dark: #0a0a0f;
            --bg-card: #12121a;
            --bg-card-hover: #1a1a25;
            --accent-blue: #3b82f6;
            --accent-green: #10b981;
            --accent-red: #ef4444;
            --accent-yellow: #eab308;
            --accent-purple: #8b5cf6;
            --text-primary: #ffffff;
            --text-secondary: #94a3b8;
            --text-muted: #64748b;
            --border-color: #1e293b;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Inter', -apple-system, sans-serif;
            background: var(--bg-dark);
            color: var(--text-primary);
            line-height: 1.6;
            padding: 2rem;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{
            text-align: center;
            margin-bottom: 3rem;
            padding: 2rem;
            background: linear-gradient(135deg, rgba(59,130,246,0.1), rgba(139,92,246,0.1));
            border-radius: 16px;
            border: 1px solid var(--border-color);
        }}
        .header h1 {{
            font-size: 2.5rem;
            font-weight: 800;
            margin-bottom: 0.5rem;
        }}
        .header .territory {{
            color: var(--text-secondary);
            font-size: 1.25rem;
        }}
        .header .date {{
            color: var(--text-muted);
            font-size: 0.875rem;
            margin-top: 1rem;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}
        @media (max-width: 900px) {{ .metrics-grid {{ grid-template-columns: repeat(2, 1fr); }} }}
        @media (max-width: 500px) {{ .metrics-grid {{ grid-template-columns: 1fr; }} }}
        .metric-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
        }}
        .metric-label {{
            font-size: 0.75rem;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.5rem;
        }}
        .metric-value {{
            font-size: 2rem;
            font-weight: 700;
        }}
        .metric-subtext {{
            font-size: 0.75rem;
            color: var(--text-secondary);
            margin-top: 0.25rem;
        }}
        .positive {{ color: var(--accent-green); }}
        .negative {{ color: var(--accent-red); }}
        .neutral {{ color: var(--accent-yellow); }}
        .chart-container {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 1.5rem;
            margin-bottom: 2rem;
        }}
        .chart-title {{
            font-size: 1.125rem;
            font-weight: 600;
            margin-bottom: 1rem;
        }}
        .section {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 1.5rem;
            margin-bottom: 2rem;
        }}
        .section-title {{
            font-size: 1.25rem;
            font-weight: 700;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        .insight-box {{
            background: rgba(59,130,246,0.1);
            border-left: 4px solid var(--accent-blue);
            padding: 1rem;
            border-radius: 0 8px 8px 0;
            margin: 1rem 0;
        }}
        .insight-box p {{
            color: var(--text-secondary);
            font-size: 0.875rem;
        }}
        .stats-row {{
            display: flex;
            gap: 2rem;
            flex-wrap: wrap;
            margin-top: 1rem;
        }}
        .stat-item {{
            flex: 1;
            min-width: 150px;
        }}
        .stat-label {{
            font-size: 0.75rem;
            color: var(--text-muted);
        }}
        .stat-value {{
            font-size: 1.5rem;
            font-weight: 600;
        }}
        .footer {{
            text-align: center;
            color: var(--text-muted);
            font-size: 0.75rem;
            margin-top: 3rem;
            padding-top: 2rem;
            border-top: 1px solid var(--border-color);
        }}
        .confidential {{
            background: rgba(239,68,68,0.1);
            border: 1px solid rgba(239,68,68,0.3);
            color: #fca5a5;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            font-size: 0.75rem;
            display: inline-block;
            margin-bottom: 1rem;
        }}
        .account-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.875rem;
        }}
        .account-table th {{
            background: rgba(59,130,246,0.1);
            padding: 0.75rem;
            text-align: right;
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-secondary);
            border-bottom: 1px solid var(--border-color);
        }}
        .account-table td {{
            padding: 0.75rem;
            text-align: right;
            border-bottom: 1px solid var(--border-color);
            color: var(--text-secondary);
        }}
        .account-table tr:hover {{
            background: var(--bg-card-hover);
        }}
        .status-growing {{ color: var(--accent-green); font-weight: 600; }}
        .status-stable {{ color: var(--accent-yellow); }}
        .status-declining {{ color: var(--accent-red); }}
        .status-at-risk {{ color: #f97316; font-weight: 600; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="confidential">CONFIDENTIAL - For {agency_name} internal use only</div>

        <div class="header">
            <h1>{agency_name}</h1>
            <div class="territory">Territory: {territory}</div>
            <div class="date">Report Generated: {datetime.now().strftime('%B %d, %Y')}</div>
        </div>

        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">2025 Revenue</div>
                <div class="metric-value">{format_currency(metrics["rev_2025"])}</div>
                <div class="metric-subtext">CY2025 (through Dec 23)</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">vs 2024</div>
                <div class="metric-value {'positive' if metrics['yoy_change'] > 0 else 'negative' if metrics['yoy_change'] < -5 else 'neutral'}">{trend_icon}{metrics["yoy_change"]:.1f}%</div>
                <div class="metric-subtext">{format_currency(abs(metrics["rev_2025"] - metrics["rev_2024"]))} {'more' if metrics["yoy_change"] > 0 else 'less'}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">vs 10-Year Avg</div>
                <div class="metric-value {'positive' if metrics['vs_ten_year'] > 0 else 'negative' if metrics['vs_ten_year'] < -5 else 'neutral'}">{'+' if metrics['vs_ten_year'] > 0 else ''}{metrics["vs_ten_year"]:.1f}%</div>
                <div class="metric-subtext">Avg: {format_currency(metrics["ten_year_avg"])}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Trend</div>
                <div class="metric-value" style="color: {trend_color};">{metrics["trend"].upper()}</div>
                <div class="metric-subtext">Based on 3-year pattern</div>
            </div>
        </div>

        <div class="chart-container">
            <div class="chart-title">10-Year Revenue Trend</div>
            <canvas id="revenueChart"></canvas>
        </div>

        <div class="section">
            <div class="section-title">Key Insights</div>
            <div class="insight-box">
                <p><strong>Context:</strong> {'Your territory is performing above the 10-year average.' if metrics['vs_ten_year'] > 0 else 'Your territory has returned to pre-COVID baseline levels.' if metrics['vs_ten_year'] > -15 else 'Your territory is significantly below historical averages - investigation needed.'}</p>
            </div>
            <div class="stats-row">
                <div class="stat-item">
                    <div class="stat-label">Pre-COVID Avg (2015-2019)</div>
                    <div class="stat-value">{format_currency(metrics["pre_covid_avg"])}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">COVID Peak (2021-22)</div>
                    <div class="stat-value">{format_currency(metrics["covid_peak"])}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Current vs Peak</div>
                    <div class="stat-value negative">{((metrics["rev_2025"] - metrics["covid_peak"]) / metrics["covid_peak"] * 100) if metrics["covid_peak"] > 0 else 0:.0f}%</div>
                </div>
            </div>
        </div>

        <div class="section">
            <div class="section-title">Account Performance Details</div>
            <p style="color: var(--text-secondary); margin-bottom: 1rem; font-size: 0.875rem;">
                Your top accounts with 10-year average, 2024, and 2025 performance. Use this to identify growth opportunities and at-risk accounts.
            </p>
            <div style="overflow-x: auto;">
                <table class="account-table">
                    <thead>
                        <tr>
                            <th style="text-align: left;">Account</th>
                            <th>10-Year Avg</th>
                            <th>2024</th>
                            <th>2025</th>
                            <th>vs 2024</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {generate_account_rows(agency_name)}
                    </tbody>
                </table>
            </div>
        </div>

        <div class="section">
            <div class="section-title">Recommendations</div>
            <ul style="color: var(--text-secondary); padding-left: 1.5rem;">
                {'<li style="margin-bottom: 0.5rem;">Continue current strategy - territory is growing</li>' if metrics["trend"] == "growing" else ''}
                {'<li style="margin-bottom: 0.5rem;">Focus on reactivating dormant accounts</li>' if metrics["trend"] == "declining" else ''}
                <li style="margin-bottom: 0.5rem;">Q1 (Jan-Mar) is historically your strongest period - prepare promotional push</li>
                <li style="margin-bottom: 0.5rem;">Review top 5 accounts for growth opportunities</li>
                <li style="margin-bottom: 0.5rem;">Identify any churned accounts from 2023-2024 for win-back campaigns</li>
            </ul>
        </div>

        <div class="footer">
            <p>BainUltra Agency Intelligence Report</p>
            <p>Data Source: Salesforce CRM | Report ID: {token}</p>
            <p style="margin-top: 0.5rem;">Questions? Contact your BainUltra Territory Manager</p>
        </div>
    </div>

    <script>
        const ctx = document.getElementById('revenueChart').getContext('2d');
        new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: {chart_labels},
                datasets: [{{
                    label: 'Revenue ($K)',
                    data: {chart_data},
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    fill: true,
                    tension: 0.3,
                    pointRadius: 4,
                    pointBackgroundColor: '#3b82f6'
                }}, {{
                    label: '10-Year Average',
                    data: Array({len(years)}).fill({metrics["ten_year_avg"]/1000:.0f}),
                    borderColor: '#94a3b8',
                    borderDash: [5, 5],
                    fill: false,
                    pointRadius: 0
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: true,
                aspectRatio: 2.5,
                plugins: {{
                    legend: {{
                        position: 'top',
                        labels: {{ color: '#94a3b8' }}
                    }},
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                return context.dataset.label + ': $' + context.parsed.y.toLocaleString() + 'K';
                            }}
                        }}
                    }}
                }},
                scales: {{
                    x: {{
                        grid: {{ color: '#1e293b' }},
                        ticks: {{ color: '#94a3b8' }}
                    }},
                    y: {{
                        grid: {{ color: '#1e293b' }},
                        ticks: {{
                            color: '#94a3b8',
                            callback: function(value) {{
                                return '$' + value.toLocaleString() + 'K';
                            }}
                        }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>'''

    return html

def generate_index_page(agencies_data):
    """Generate internal index page with all agency links"""
    rows = ""
    for agency, data in sorted(agencies_data.items(), key=lambda x: x[1]["metrics"]["rev_2025"], reverse=True):
        metrics = data["metrics"]
        trend_class = "positive" if metrics["trend"] == "growing" else "negative" if metrics["trend"] == "declining" else "neutral"
        rows += f'''
            <tr>
                <td><strong>{agency}</strong><br><span style="color: var(--text-muted); font-size: 0.75rem;">{data["territory"]}</span></td>
                <td>{format_currency(metrics["rev_2025"])}</td>
                <td class="{trend_class}">{metrics["yoy_change"]:+.1f}%</td>
                <td><a href="{data["token"]}.html" style="color: var(--accent-blue);">View Report</a></td>
            </tr>'''

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BainUltra | Agency Reports Index (Internal)</title>
    <style>
        :root {{
            --bg-dark: #0a0a0f;
            --bg-card: #12121a;
            --accent-blue: #3b82f6;
            --accent-green: #10b981;
            --accent-red: #ef4444;
            --accent-yellow: #eab308;
            --text-primary: #ffffff;
            --text-secondary: #94a3b8;
            --text-muted: #64748b;
            --border-color: #1e293b;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, sans-serif;
            background: var(--bg-dark);
            color: var(--text-primary);
            padding: 2rem;
        }}
        .container {{ max-width: 1000px; margin: 0 auto; }}
        h1 {{ margin-bottom: 2rem; }}
        .warning {{
            background: rgba(239,68,68,0.1);
            border: 1px solid rgba(239,68,68,0.3);
            color: #fca5a5;
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 2rem;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background: var(--bg-card);
            border-radius: 12px;
            overflow: hidden;
        }}
        th, td {{
            padding: 1rem;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
        }}
        th {{
            background: rgba(59,130,246,0.1);
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-secondary);
        }}
        .positive {{ color: var(--accent-green); }}
        .negative {{ color: var(--accent-red); }}
        .neutral {{ color: var(--accent-yellow); }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Agency Reports Index</h1>
        <div class="warning">
            <strong>INTERNAL USE ONLY</strong> - Do not share this page. Each agency report has a unique secret URL.
        </div>
        <table>
            <thead>
                <tr>
                    <th>Agency</th>
                    <th>2025 Revenue</th>
                    <th>YoY Change</th>
                    <th>Report</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
        <p style="color: var(--text-muted); margin-top: 2rem; font-size: 0.875rem;">
            Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}
        </p>
    </div>
</body>
</html>'''
    return html

def main():
    output_dir = Path("/Users/jm/powerhouse/salesforce-dashboard/ceo-dashboard/sales-analysis-presentation/agency-reports")
    output_dir.mkdir(exist_ok=True)

    agencies_data = {}

    # Process each agency
    for agency_name, yearly_data in AGENCY_YEARLY_DATA.items():
        # Skip agencies with minimal data
        if sum(yearly_data.values()) < 50000:
            continue

        token = generate_token(agency_name)
        metrics = calculate_metrics(agency_name, yearly_data)
        territory = TERRITORIES.get(agency_name, "Unknown")

        agencies_data[agency_name] = {
            "token": token,
            "territory": territory,
            "metrics": metrics
        }

        # Generate HTML report
        html = generate_html_report(agency_name, metrics, token)

        # Write to file
        output_file = output_dir / f"{token}.html"
        with open(output_file, "w") as f:
            f.write(html)

        print(f"Generated: {agency_name} -> {token}.html")

    # Generate index page
    index_html = generate_index_page(agencies_data)
    with open(output_dir / "index.html", "w") as f:
        f.write(index_html)

    print(f"\nGenerated {len(agencies_data)} agency reports")
    print(f"Index page: {output_dir}/_index.html")

    # Print URL mapping
    print("\n=== Agency URL Mapping ===")
    for agency, data in sorted(agencies_data.items()):
        print(f"{agency}: {data['token']}.html")

if __name__ == "__main__":
    main()
