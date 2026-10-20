"""
backend/services/indian_cities_geo.py — Geographic Transit Nodes & City Resolution Engine
Provides high-accuracy offline matching of GPS coordinates along Indian logistics
corridors to actual Indian cities, freight terminals, and highway checkpoints.
"""

import os
import re
import math
import logging
from typing import Optional, List, Tuple, Dict, Set
import numpy as np

logger = logging.getLogger(__name__)

# ── Primary Curated Indian Logistics Cities & Expressway Hubs ──
# (city_name, lat, lon)
PRIMARY_TRANSIT_NODES: List[Tuple[str, float, float]] = [
    # ── Maharashtra Corridor (NH48, Samruddhi, NH65, NH66, NH53) ──
    ("Mumbai", 18.9220, 72.8347),
    ("Navi Mumbai", 19.0330, 73.0297),
    ("Thane", 19.2183, 72.9781),
    ("Kalyan", 19.2403, 73.1305),
    ("Bhiwandi", 19.3002, 73.0635),
    ("Panvel", 18.9894, 73.1175),
    ("Khalapur", 18.8310, 73.2842),
    ("Khopoli", 18.7891, 73.3444),
    ("Khandala", 18.7613, 73.3725),
    ("Lonavala", 18.7557, 73.4091),
    ("Kamshet", 18.7562, 73.5591),
    ("Talegaon", 18.7350, 73.6757),
    ("Dehu Road", 18.7180, 73.7280),
    ("Pimpri-Chinchwad", 18.6298, 73.7997),
    ("Pune", 18.5204, 73.8567),
    ("Hadapsar", 18.5089, 73.9260),
    ("Uruli Kanchan", 18.4870, 74.1332),
    ("Daund", 18.4650, 74.5822),
    ("Shirwal", 18.1345, 73.9877),
    ("Khandala (Satara)", 18.0435, 74.0252),
    ("Satara", 17.6805, 73.9930),
    ("Karad", 17.2890, 74.1812),
    ("Islampur", 17.0514, 74.2678),
    ("Sangli", 16.8524, 74.5815),
    ("Miraj", 16.8273, 74.6468),
    ("Kolhapur", 16.7050, 74.2433),
    ("Kagal", 16.5772, 74.3168),
    ("Solapur", 17.6599, 75.9064),
    ("Mohol", 17.7082, 75.6480),
    ("Tembhurni", 17.9048, 75.2285),
    ("Indapur", 18.1154, 75.0322),
    ("Baramati", 18.1517, 74.5773),
    ("Pandharpur", 17.6775, 75.3236),
    ("Ahmednagar", 19.0952, 74.7496),
    ("Shirdi", 19.7645, 74.4762),
    ("Nashik", 19.9975, 73.7898),
    ("Sinnar", 19.8458, 73.9984),
    ("Igatpuri", 19.6974, 73.5627),
    ("Shahapur", 19.4533, 73.3275),
    ("Kasara", 19.6485, 73.4862),
    ("Malegaon", 20.5538, 74.5304),
    ("Dhule", 20.9042, 74.7749),
    ("Jalgaon", 21.0077, 75.5626),
    ("Bhusawal", 21.0455, 75.7885),
    ("Chhatrapati Sambhaji Nagar", 19.8762, 75.3433),
    ("Jalna", 19.8410, 75.8864),
    ("Beed", 18.9891, 75.7601),
    ("Parbhani", 19.2686, 76.7748),
    ("Nanded", 19.1383, 77.3210),
    ("Latur", 18.4088, 76.5604),
    ("Osmanabad", 18.1755, 76.0408),
    ("Akola", 20.7002, 77.0082),
    ("Khamgaon", 20.6865, 76.5746),
    ("Amravati", 20.9320, 77.7523),
    ("Wardha", 20.7453, 78.6022),
    ("Nagpur", 21.1458, 79.0882),
    ("Butibori", 20.9234, 78.9950),
    ("Bhandara", 21.1714, 79.6540),
    ("Gondia", 21.4602, 80.1961),
    ("Chandrapur", 19.9615, 79.2961),
    ("Yavatmal", 20.3888, 78.1204),
    ("Pen", 18.7360, 73.0900),
    ("Nagothane", 18.5360, 73.1360),
    ("Roha", 18.4360, 73.1180),
    ("Mangaon", 18.2520, 73.2870),
    ("Mahad", 18.0830, 73.4180),
    ("Chiplun", 17.5320, 73.5180),
    ("Ratnagiri", 16.9902, 73.3120),
    ("Kankavli", 16.2700, 73.7140),
    ("Kudal", 16.0120, 73.6880),
    ("Sawantwadi", 15.9060, 73.8200),
    ("Palghar", 19.6967, 72.7699),
    ("Dahanu", 19.9700, 72.7300),
    ("Talasari", 20.1260, 72.9200),

    # ── Delhi NCR & Northern Corridors (NH44, NH48, Yamuna Exp, NH19) ──
    ("Delhi", 28.6139, 77.2090),
    ("New Delhi", 28.6139, 77.2090),
    ("Noida", 28.5355, 77.3910),
    ("Greater Noida", 28.4744, 77.5040),
    ("Ghaziabad", 28.6692, 77.4538),
    ("Modinagar", 28.8340, 77.5750),
    ("Meerut", 28.9845, 77.7064),
    ("Hapur", 28.7306, 77.7759),
    ("Bulandshahr", 28.4070, 77.8498),
    ("Khurja", 28.2544, 77.8540),
    ("Aligarh", 27.8974, 78.0880),
    ("Hathras", 27.5980, 78.0510),
    ("Jewar", 28.1270, 77.5560),
    ("Gurugram", 28.4595, 77.0266),
    ("Manesar", 28.3540, 76.9380),
    ("Faridabad", 28.4089, 77.3178),
    ("Ballabhgarh", 28.3370, 77.3240),
    ("Palwal", 28.1487, 77.3320),
    ("Hodal", 27.8940, 77.3680),
    ("Kosi Kalan", 27.7940, 77.4320),
    ("Chhata", 27.7210, 77.5030),
    ("Vrindavan", 27.5806, 77.7006),
    ("Mathura", 27.4924, 77.6737),
    ("Farah", 27.3240, 77.7600),
    ("Agra", 27.1767, 78.0081),
    ("Tundla", 27.2060, 78.2410),
    ("Firozabad", 27.1593, 78.3957),
    ("Shikohabad", 27.1080, 78.5840),
    ("Etawah", 26.7769, 79.0305),
    ("Auraiya", 26.4674, 79.5165),
    ("Akbarpur (UP)", 26.4320, 80.0330),
    ("Kanpur", 26.4499, 80.3319),
    ("Unnao", 26.5393, 80.4878),
    ("Lucknow", 26.8467, 80.9462),
    ("Barabanki", 26.9270, 81.1830),
    ("Ayodhya", 26.7922, 82.1998),
    ("Basti", 26.7960, 82.7480),
    ("Khalilabad", 26.7780, 83.0380),
    ("Gorakhpur", 26.7606, 83.3732),
    ("Fatehpur", 25.9280, 80.8130),
    ("Prayagraj", 25.4358, 81.8463),
    ("Mirzapur", 25.1337, 82.5644),
    ("Varanasi", 25.3176, 82.9739),
    ("Pt. Deen Dayal Upadhyaya Nagar", 25.2818, 83.1192),
    ("Chandauli", 25.2600, 83.2700),
    ("Jaunpur", 25.7464, 82.6837),
    ("Sultanpur", 26.2648, 82.0727),
    ("Rae Bareli", 26.2236, 81.2409),
    ("Shahjahanpur", 27.8805, 79.9120),
    ("Bareilly", 28.3670, 79.4304),
    ("Rampur", 28.8154, 79.0256),
    ("Moradabad", 28.8354, 78.7747),
    ("Amroha", 28.9040, 78.4680),
    ("Sambhal", 28.5850, 78.5710),
    ("Saharanpur", 29.9679, 77.5452),
    ("Muzaffarnagar", 29.4727, 77.7085),
    ("Roorkee", 29.8543, 77.8880),
    ("Haridwar", 29.9457, 78.1642),
    ("Rishikesh", 30.0869, 78.2676),
    ("Dehradun", 30.3165, 78.0322),
    ("Sonipat", 28.9931, 77.0151),
    ("Ganaur", 29.1310, 77.0210),
    ("Samalkha", 29.2390, 76.9940),
    ("Panipat", 29.3909, 76.9635),
    ("Gharaunda", 29.5390, 76.9710),
    ("Karnal", 29.6857, 76.9905),
    ("Kurukshetra", 29.9695, 76.8783),
    ("Shahbad Markanda", 30.1680, 76.8710),
    ("Ambala", 30.3782, 76.7767),
    ("Rajpura", 30.4840, 76.5940),
    ("Sirhind", 30.6420, 76.3840),
    ("Khanna", 30.7071, 76.2166),
    ("Ludhiana", 30.9010, 75.8573),
    ("Phagwara", 31.2240, 75.7708),
    ("Jalandhar", 31.3260, 75.5762),
    ("Beas", 31.5160, 75.2970),
    ("Amritsar", 31.6340, 74.8723),
    ("Pathankot", 32.2684, 75.6529),
    ("Jammu", 32.7266, 74.8570),
    ("Udhampur", 32.9250, 75.1400),
    ("Srinagar", 34.0837, 74.7973),
    ("Panchkula", 30.6942, 76.8606),
    ("Chandigarh", 30.7333, 76.7794),
    ("Mohali", 30.7046, 76.7179),
    ("Shimla", 31.1048, 77.1734),
    ("Baddi", 30.9578, 76.7914),
    ("Solan", 30.9045, 77.0967),
    ("Rohtak", 28.8955, 76.6066),
    ("Hisar", 29.1492, 75.7217),
    ("Bhiwani", 28.7932, 76.1390),
    ("Rewari", 28.1828, 76.6191),
    ("Bawal", 28.0830, 76.5860),
    ("Dharuhera", 28.2060, 76.7930),
    ("Bahadurgarh", 28.6924, 76.9240),

    # ── Rajasthan Corridor (NH48, NH52, NH62, NH27) ──
    ("Behror", 27.8880, 76.2820),
    ("Neemrana", 27.9880, 76.3880),
    ("Kotputli", 27.7020, 76.1970),
    ("Paota", 27.5680, 76.1040),
    ("Shahpura (Jaipur)", 27.3880, 75.9610),
    ("Chandwaji", 27.2020, 75.9270),
    ("Amer", 26.9855, 75.8513),
    ("Jaipur", 26.9124, 75.7873),
    ("Bagru", 26.8120, 75.5460),
    ("Dudu", 26.6800, 75.2340),
    ("Kishangarh", 26.5746, 74.8647),
    ("Ajmer", 26.4499, 74.6399),
    ("Beawar", 26.1013, 74.3197),
    ("Bhim", 25.7240, 74.0880),
    ("Bhilwara", 25.3475, 74.6408),
    ("Chittorgarh", 24.8887, 74.6269),
    ("Udaipur", 24.5854, 73.7125),
    ("Kherwara", 23.9910, 73.5950),
    ("Ratanpur Border", 23.8640, 73.5350),
    ("Kota", 25.2138, 75.8648),
    ("Bundi", 25.4415, 75.6429),
    ("Tonk", 26.1664, 75.7885),
    ("Jodhpur", 26.2389, 73.0243),
    ("Pali", 25.7711, 73.3234),
    ("Sirohi", 24.8853, 72.8625),
    ("Abu Road", 24.4820, 72.7810),
    ("Bikaner", 28.0229, 73.3119),
    ("Sikar", 27.6094, 75.1398),
    ("Alwar", 27.5530, 76.6346),
    ("Bharatpur", 27.2152, 77.5030),
    ("Dholpur", 26.7025, 77.8934),

    # ── Gujarat Corridor (NH48, NH27, NH56) ──
    ("Himatnagar", 23.5977, 72.9698),
    ("Gandhinagar", 23.2156, 72.6369),
    ("Ahmedabad", 23.0225, 72.5714),
    ("Sanand", 22.9926, 72.3813),
    ("Nadiad", 22.6916, 72.8634),
    ("Anand", 22.5645, 72.9289),
    ("Vadodara", 22.3072, 73.1812),
    ("Bharuch", 21.7051, 72.9959),
    ("Ankleshwar", 21.6264, 73.0034),
    ("Surat", 21.1702, 72.8311),
    ("Navsari", 20.9467, 72.9520),
    ("Valsad", 20.5992, 72.9342),
    ("Vapi", 20.3707, 72.9106),
    ("Daman", 20.3974, 72.8328),
    ("Silvassa", 20.2763, 73.0083),
    ("Morbi", 22.8120, 70.8384),
    ("Rajkot", 22.3039, 70.8022),
    ("Jamnagar", 22.4707, 70.0577),
    ("Bhavnagar", 21.7645, 72.1519),
    ("Junagadh", 21.5222, 70.4579),
    ("Porbandar", 21.6417, 69.6293),
    ("Gandhidham", 23.0753, 70.1337),
    ("Kandla", 23.0033, 70.2186),
    ("Bhuj", 23.2420, 69.6669),
    ("Mehsana", 23.5880, 72.3693),
    ("Palanpur", 24.1724, 72.4346),
    ("Deesa", 24.2588, 72.1793),

    # ── Madhya Pradesh Corridor (NH44, NH46, NH52, NH30) ──
    ("Gwalior", 26.2183, 78.1828),
    ("Morena", 26.4950, 77.9940),
    ("Dabra", 25.8940, 78.3320),
    ("Datia", 25.6690, 78.4600),
    ("Jhansi", 25.4484, 78.5685),
    ("Babina", 25.2470, 78.4730),
    ("Lalitpur", 24.6890, 78.4140),
    ("Malthone", 24.3030, 78.5240),
    ("Sagar", 23.8388, 78.7378),
    ("Narsinghpur", 22.9470, 79.1980),
    ("Lakhnadon", 22.5950, 79.6050),
    ("Seoni", 22.0869, 79.5435),
    ("Bhopal", 23.2599, 77.4126),
    ("Mandideep", 23.0600, 77.5200),
    ("Sehore", 23.2000, 77.0800),
    ("Hoshangabad", 22.7519, 77.7289),
    ("Itarsi", 22.6120, 77.7600),
    ("Indore", 22.7196, 75.8577),
    ("Pithampur", 22.6100, 75.6800),
    ("Mhow", 22.5530, 75.7600),
    ("Dewas", 22.9676, 76.0534),
    ("Ujjain", 23.1765, 75.7885),
    ("Ratlam", 23.3315, 75.0367),
    ("Shivpuri", 25.4320, 77.6580),
    ("Guna", 24.6480, 77.3120),
    ("Biaora", 23.9160, 76.9180),
    ("Jabalpur", 23.1815, 79.9864),
    ("Katni", 23.8343, 80.3992),
    ("Satna", 24.6005, 80.8322),
    ("Rewa", 24.5362, 81.3037),
    ("Chhindwara", 22.0574, 78.9382),

    # ── Karnataka Corridor (NH48, NH44, NH50, NH75, NH66) ──
    ("Nipani", 16.3980, 74.3820),
    ("Sankeshwar", 16.2620, 74.4820),
    ("Hukkeri", 16.2300, 74.6000),
    ("Belagavi", 15.8497, 74.4977),
    ("Kittur", 15.6020, 74.7920),
    ("Dharwad", 15.4589, 75.0078),
    ("Hubballi", 15.3647, 75.1240),
    ("Haveri", 14.7963, 75.3991),
    ("Ranibennur", 14.6220, 75.6260),
    ("Harihar", 14.5120, 75.8030),
    ("Davangere", 14.4644, 75.9218),
    ("Chitradurga", 14.2251, 76.3980),
    ("Sira", 13.7440, 76.9040),
    ("Tumakuru", 13.3409, 77.1010),
    ("Nelamangala", 13.0980, 77.3910),
    ("Bengaluru", 12.9716, 77.5946),
    ("Electronic City", 12.8452, 77.6602),
    ("Devanahalli", 13.2480, 77.7120),
    ("Hoskote", 13.0710, 77.7980),
    ("Bidadi", 12.7960, 77.3850),
    ("Ramanagara", 12.7210, 77.2810),
    ("Channapatna", 12.6510, 77.2040),
    ("Maddur", 12.5840, 77.0450),
    ("Mandya", 12.5220, 76.8970),
    ("Srirangapatna", 12.4180, 76.6950),
    ("Mysuru", 12.2958, 76.6394),
    ("Nanjangud", 12.1180, 76.6800),
    ("Hassan", 13.0072, 76.1029),
    ("Chikkamagaluru", 13.3161, 75.7720),
    ("Shivamogga", 13.9299, 75.5681),
    ("Bhadravati", 13.8450, 75.7040),
    ("Mangaluru", 12.9141, 74.8560),
    ("Udupi", 13.3409, 74.7421),
    ("Kundapura", 13.6260, 74.6920),
    ("Bhatkal", 13.9780, 74.5660),
    ("Honnavar", 14.2800, 74.4440),
    ("Kumta", 14.4250, 74.4090),
    ("Ankola", 14.6640, 74.3030),
    ("Karwar", 14.8185, 74.1350),
    ("Ballari", 15.1394, 76.9214),
    ("Hosapete", 15.2710, 76.3910),
    ("Koppal", 15.3480, 76.1550),
    ("Gadag", 15.4290, 75.6320),
    ("Bagalkot", 16.1875, 75.6980),
    ("Vijayapura", 16.8302, 75.7100),
    ("Kalaburagi", 17.3297, 76.8343),
    ("Bidar", 17.9104, 77.5199),
    ("Raichur", 16.2076, 77.3463),
    ("Chikkaballapur", 13.4325, 77.7275),
    ("Bagepalli", 13.7840, 77.7940),
    ("Kolar", 13.1367, 78.1340),

    # ── Tamil Nadu Corridor (NH44, NH48, NH544, NH32) ──
    ("Hosur", 12.7409, 77.8253),
    ("Krishnagiri", 12.5186, 78.2137),
    ("Bargur", 12.5480, 78.3610),
    ("Natrampalli", 12.6040, 78.5320),
    ("Vaniyambadi", 12.6840, 78.6180),
    ("Ambur", 12.7904, 78.7166),
    ("Pallikonda", 12.8760, 78.9480),
    ("Vellore", 12.9165, 79.1325),
    ("Arcot", 12.9040, 79.3330),
    ("Ranipet", 12.9290, 79.3320),
    ("Walajapet", 12.9260, 79.3810),
    ("Kanchipuram", 12.8342, 79.7036),
    ("Sriperumbudur", 12.9699, 79.9405),
    ("Poonamallee", 13.0480, 80.0920),
    ("Chennai", 13.0827, 80.2707),
    ("Tambaram", 12.9249, 80.1000),
    ("Chengalpattu", 12.6840, 79.9830),
    ("Tindivanam", 12.2340, 79.6540),
    ("Viluppuram", 11.9401, 79.4861),
    ("Ulundurpet", 11.6910, 79.2940),
    ("Perambalur", 11.2340, 78.8820),
    ("Tiruchirappalli", 10.7905, 78.7047),
    ("Dharmapuri", 12.1211, 78.1582),
    ("Thoppur", 11.9470, 78.0640),
    ("Omalur", 11.7450, 78.0410),
    ("Salem", 11.6643, 78.1460),
    ("Sankari", 11.4840, 77.8680),
    ("Bhavani", 11.4520, 77.6830),
    ("Erode", 11.3410, 77.7172),
    ("Perundurai", 11.2780, 77.5840),
    ("Tirupur", 11.1085, 77.3411),
    ("Avinashi", 11.1940, 77.2680),
    ("Coimbatore", 11.0168, 76.9558),
    ("Pollachi", 10.6609, 77.0048),
    ("Namakkal", 11.2189, 78.1674),
    ("Paramathi Velur", 11.0540, 78.0080),
    ("Karur", 10.9601, 78.0766),
    ("Dindigul", 10.3673, 77.9803),
    ("Vadipatti", 10.0840, 78.0120),
    ("Madurai", 9.9252, 78.1198),
    ("Thirumangalam", 9.8240, 77.9880),
    ("Virudhunagar", 9.5680, 77.9624),
    ("Sattur", 9.3640, 77.9250),
    ("Kovilpatti", 9.1720, 77.8680),
    ("Kayathar", 8.9540, 77.7730),
    ("Tirunelveli", 8.7139, 77.7567),
    ("Nanguneri", 8.4890, 77.6540),
    ("Valliyur", 8.3780, 77.6140),
    ("Kanyakumari", 8.0883, 77.5385),
    ("Nagercoil", 8.1833, 77.4119),
    ("Thoothukudi", 8.7642, 78.1348),
    ("Thanjavur", 10.7870, 79.1378),

    # ── Andhra Pradesh & Telangana Corridor (NH44, NH16, NH65) ──
    ("Adilabad", 19.6641, 78.5320),
    ("Nirmal", 19.0964, 78.3430),
    ("Armoor", 18.7910, 78.2910),
    ("Nizamabad", 18.6725, 78.0941),
    ("Kamareddy", 18.3240, 78.3410),
    ("Medchal", 17.6300, 78.4810),
    ("Hyderabad", 17.3850, 78.4867),
    ("Secunderabad", 17.4399, 78.4983),
    ("Cyberabad", 17.4435, 78.3772),
    ("Shamshabad", 17.2543, 78.4312),
    ("Shadnagar", 17.0670, 78.2080),
    ("Jadcherla", 16.7720, 78.1430),
    ("Mahbubnagar", 16.7488, 77.9856),
    ("Bhootpur", 16.6970, 78.0560),
    ("Pebbair", 16.2080, 77.9940),
    ("Alampur", 15.8780, 78.1320),
    ("Kurnool", 15.8281, 78.0373),
    ("Dhone", 15.4180, 77.8740),
    ("Gooty", 15.1180, 77.6340),
    ("Anantapur", 14.6819, 77.6006),
    ("Dharmavaram", 14.4140, 77.7210),
    ("Penukonda", 14.0840, 77.5950),
    ("Suryapet", 17.1439, 79.6239),
    ("Kodad", 16.9980, 79.9680),
    ("Nandigama", 16.7740, 80.2920),
    ("Khammam", 17.2473, 80.1514),
    ("Warangal", 17.9689, 79.5941),
    ("Karimnagar", 18.4386, 79.1288),
    ("Ramagundam", 18.7610, 79.5140),
    ("Ichchapuram", 19.1120, 84.6930),
    ("Srikakulam", 18.2949, 83.8938),
    ("Vizianagaram", 18.1067, 83.3956),
    ("Visakhapatnam", 17.6868, 83.2185),
    ("Anakapalle", 17.6913, 83.0039),
    ("Yellamanchili", 17.5520, 82.8590),
    ("Tuni", 17.3580, 82.5480),
    ("Annavaram", 17.2810, 82.4040),
    ("Samalkota", 17.0510, 82.1700),
    ("Kakinada", 16.9891, 82.2475),
    ("Rajahmundry", 17.0005, 81.8040),
    ("Tanuku", 16.7580, 81.6810),
    ("Tadepalligudem", 16.8120, 81.5280),
    ("Eluru", 16.7107, 81.0952),
    ("Hanuman Junction", 16.6340, 80.8920),
    ("Gannavaram", 16.5410, 80.8030),
    ("Vijayawada", 16.5062, 80.6480),
    ("Mangalagiri", 16.4320, 80.5680),
    ("Guntur", 16.3067, 80.4365),
    ("Chilakaluripet", 16.0890, 80.1670),
    ("Ongole", 15.5057, 80.0499),
    ("Singarayakonda", 15.2530, 80.0270),
    ("Kavali", 14.9130, 79.9920),
    ("Nellore", 14.4426, 79.9865),
    ("Gudur", 14.1460, 79.8500),
    ("Naidupeta", 13.9100, 79.9040),
    ("Sullurpeta", 13.7020, 80.0210),
    ("Tirupati", 13.6288, 79.4192),
    ("Chittoor", 13.2172, 79.1003),
    ("Kadapa", 14.4673, 78.8242),

    # ── Kerala Corridor (NH66, NH544) ──
    ("Kasaragod", 12.4996, 74.9869),
    ("Kanhangad", 12.3160, 75.0930),
    ("Payyanur", 12.1020, 75.2040),
    ("Kannur", 11.8745, 75.3704),
    ("Thalassery", 11.7490, 75.4890),
    ("Vadakara", 11.6080, 75.5910),
    ("Kozhikode", 11.2588, 75.7804),
    ("Tirur", 10.9160, 75.9240),
    ("Ponnani", 10.7740, 75.9250),
    ("Chavakkad", 10.5840, 76.0240),
    ("Guruvayur", 10.5950, 76.0370),
    ("Thrissur", 10.5276, 76.2144),
    ("Chalakudy", 10.3070, 76.3330),
    ("Angamaly", 10.1960, 76.3860),
    ("Aluva", 10.1076, 76.3516),
    ("Kochi", 9.9312, 76.2673),
    ("Ernakulam", 9.9816, 76.2999),
    ("Cherthala", 9.6840, 76.3310),
    ("Alappuzha", 9.4981, 76.3388),
    ("Ambalapuzha", 9.3820, 76.3570),
    ("Haripad", 9.2880, 76.4620),
    ("Kayamkulam", 9.1720, 76.5010),
    ("Karunagappally", 9.0540, 76.5360),
    ("Kollam", 8.8932, 76.6141),
    ("Attingal", 8.6960, 76.8140),
    ("Thiruvananthapuram", 8.5241, 76.9366),
    ("Palakkad", 10.7867, 76.6548),
    ("Malappuram", 11.0510, 76.0711),
    ("Kottayam", 9.5916, 76.5222),

    # ── West Bengal & Eastern Corridors (NH16, NH19, NH12, NH27) ──
    ("Kolkata", 22.5726, 88.3639),
    ("Howrah", 22.5958, 88.2636),
    ("Dankuni", 22.6840, 88.2980),
    ("Uluberia", 22.4740, 88.1100),
    ("Kolaghat", 22.4270, 87.8720),
    ("Panskura", 22.4180, 87.7280),
    ("Kharagpur", 22.3460, 87.2320),
    ("Belda", 22.0830, 87.3510),
    ("Bardhaman", 23.2324, 87.8615),
    ("Panagarh", 23.4540, 87.4390),
    ("Durgapur", 23.5204, 87.3119),
    ("Raniganj", 23.6190, 87.1320),
    ("Asansol", 23.6739, 86.9524),
    ("Barakar", 23.7480, 86.8200),
    ("Krishnanagar", 23.4010, 88.5020),
    ("Baharampur", 24.0984, 88.2514),
    ("Murshidabad", 24.1750, 88.2810),
    ("Farakka", 24.8140, 87.9120),
    ("Malda", 25.0108, 88.1411),
    ("Gazole", 25.2180, 88.1920),
    ("Itahar", 25.4480, 88.1670),
    ("Raiganj", 25.6174, 88.1250),
    ("Dalkhola", 25.8540, 87.8480),
    ("Kishanganj", 26.0967, 87.9400),
    ("Islampur", 26.2670, 88.1960),
    ("Siliguri", 26.7271, 88.3953),
    ("Jalpaiguri", 26.5405, 88.7196),
    ("Mainaguri", 26.5670, 88.8240),
    ("Dhupguri", 26.5980, 89.0140),
    ("Falakata", 26.5320, 89.2080),
    ("Cooch Behar", 26.3452, 89.4482),
    ("Alipurduar", 26.4919, 89.5271),
    ("Haldia", 22.0620, 88.0700),
    ("Purulia", 23.3322, 86.3652),
    ("Bankura", 23.2324, 87.0715),

    # ── Bihar & Jharkhand Corridors (NH19, NH22, NH27, NH33) ──
    ("Patna", 25.5941, 85.1376),
    ("Danapur", 25.6320, 85.0420),
    ("Hajipur", 25.6858, 85.2146),
    ("Muzaffarpur", 26.1209, 85.3647),
    ("Darbhanga", 26.1542, 85.8918),
    ("Samastipur", 25.8628, 85.7811),
    ("Begusarai", 25.4182, 86.1272),
    ("Barauni", 25.4670, 85.9780),
    ("Bhagalpur", 25.2425, 87.0139),
    ("Purnia", 25.7771, 87.4753),
    ("Araria", 26.1360, 87.5180),
    ("Forbesganj", 26.2990, 87.2560),
    ("Gaya", 24.7914, 85.0002),
    ("Jehanabad", 25.2140, 84.9870),
    ("Aurangabad (BR)", 24.7539, 84.3743),
    ("Dehri-on-Sone", 24.9080, 84.1840),
    ("Sasaram", 24.9518, 84.0315),
    ("Mohania", 25.1680, 83.6180),
    ("Ranchi", 23.3441, 85.3096),
    ("Ramgarh", 23.6320, 85.5180),
    ("Hazaribagh", 23.9930, 85.3620),
    ("Barhi", 24.2980, 85.4210),
    ("Bagodar", 24.0840, 85.8340),
    ("Dumri", 23.9870, 86.0120),
    ("Topchanchi", 23.9040, 86.2080),
    ("Govindpur", 23.8340, 86.5180),
    ("Dhanbad", 23.7957, 86.4304),
    ("Bokaro Steel City", 23.6693, 86.1511),
    ("Jamshedpur", 22.8046, 86.2029),
    ("Ghatshila", 22.5830, 86.4820),
    ("Baharagora", 22.2810, 86.7210),

    # ── Odisha & Chhattisgarh Corridor (NH16, NH53, NH30) ──
    ("Jaleswar", 21.8020, 87.2140),
    ("Baleshwar", 21.4934, 86.9135),
    ("Bhadrak", 21.0574, 86.4959),
    ("Jajpur", 20.8524, 86.3377),
    ("Chandikhole", 20.6720, 86.1340),
    ("Cuttack", 20.4625, 85.8828),
    ("Bhubaneswar", 20.2961, 85.8245),
    ("Khordha", 20.1840, 85.6180),
    ("Balugaon", 19.7480, 85.2040),
    ("Chatrapur", 19.3540, 84.9920),
    ("Brahmapur", 19.3150, 84.7941),
    ("Rourkela", 22.2604, 84.8536),
    ("Jharsuguda", 21.8550, 84.0060),
    ("Sambalpur", 21.4669, 83.9812),
    ("Bargarh", 21.3340, 83.6210),
    ("Saraipali", 21.3280, 83.0030),
    ("Arang", 21.1960, 81.9680),
    ("Raipur", 21.2514, 81.6296),
    ("Bhilai", 21.1938, 81.3509),
    ("Durg", 21.1904, 81.2849),
    ("Rajnandgaon", 21.0970, 81.0360),
    ("Bilaspur (CG)", 22.0797, 82.1409),
    ("Korba", 22.3595, 82.7501),
    ("Raigarh", 21.8974, 83.3950),
    ("Jagdalpur", 19.0730, 82.0280),

    # ── Assam & North-East Corridors (NH27, NH37) ──
    ("Bongaigaon", 26.5020, 90.5480),
    ("Goalpara", 26.1780, 90.6280),
    ("Barpeta", 26.3210, 91.0080),
    ("Nalbari", 26.4460, 91.4390),
    ("Rangia", 26.4520, 91.6240),
    ("Jalukbari", 26.1480, 91.6620),
    ("Guwahati", 26.1445, 91.7362),
    ("Dispur", 26.1408, 91.7907),
    ("Nagaon", 26.3452, 92.6840),
    ("Tezpur", 26.6528, 92.7926),
    ("Jorhat", 26.7509, 94.2037),
    ("Sivasagar", 26.9826, 94.6426),
    ("Dibrugarh", 27.4728, 94.9120),
    ("Tinsukia", 27.5011, 95.3620),
    ("Silchar", 24.8333, 92.7789),
    ("Shillong", 25.5788, 91.8933),
    ("Agartala", 23.8315, 91.2868),
    ("Dimapur", 25.9060, 93.7270),
    ("Kohima", 25.6751, 94.1086),
    ("Imphal", 24.8170, 93.9368),
    ("Aizawl", 23.7271, 92.7176),
    ("Gangtok", 27.3389, 88.6065),
    ("Itanagar", 27.0844, 93.6053),
]

# Pre-compile primary node coordinates for instant vectorized distance lookup
_PRIMARY_NAMES: List[str] = [item[0] for item in PRIMARY_TRANSIT_NODES]
_PRIMARY_LATS: np.ndarray = np.array([item[1] for item in PRIMARY_TRANSIT_NODES], dtype=np.float64)
_PRIMARY_LONS: np.ndarray = np.array([item[2] for item in PRIMARY_TRANSIT_NODES], dtype=np.float64)
_PRIMARY_LATS_RAD: np.ndarray = np.radians(_PRIMARY_LATS)
_PRIMARY_LONS_RAD: np.ndarray = np.radians(_PRIMARY_LONS)

# Optional secondary nodes from railway station junctions dataset
_SECONDARY_LOADED = False
_SEC_NAMES: List[str] = []
_SEC_LATS_RAD: np.ndarray = np.array([], dtype=np.float64)
_SEC_LONS_RAD: np.ndarray = np.array([], dtype=np.float64)


def _clean_station_name(raw_name: str) -> str:
    """Clean railway junction names to human-readable city/town names."""
    if not isinstance(raw_name, str):
        return ""
    name = raw_name.strip()
    # Remove common railway tags
    name = re.sub(r"\b(JN|JUNCTION|CABIN|HALT|PH|FLAG|TERMINUS|CENTRAL|ROAD|TOWN|CITY)\b", "", name, flags=re.IGNORECASE)
    # Remove digits and extra punctuation
    name = re.sub(r"[0-9\(\)\/\-\.]+", " ", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name.title()


def _ensure_secondary_nodes():
    """Lazy-load Indian Railway junction dataset if available to complement remote routes."""
    global _SECONDARY_LOADED, _SEC_NAMES, _SEC_LATS_RAD, _SEC_LONS_RAD
    if _SECONDARY_LOADED:
        return
    _SECONDARY_LOADED = True

    try:
        csv_path = os.path.join(
            os.path.dirname(__file__), "..", "data", "raw", "railway_network", "india_railway_stations.csv"
        )
        if not os.path.exists(csv_path):
            return

        import pandas as pd
        df = pd.read_csv(csv_path)
        junc = df[df.get("is_junction", False) == True].dropna(subset=["latitude", "longitude"]).copy()
        if len(junc) == 0:
            return

        sec_names = []
        sec_lats = []
        sec_lons = []
        primary_set = {n.lower() for n in _PRIMARY_NAMES}

        for _, row in junc.iterrows():
            c_name = _clean_station_name(str(row["station_name"]))
            if not c_name or len(c_name) < 3 or c_name.lower() in primary_set:
                continue
            lat = float(row["latitude"])
            lon = float(row["longitude"])
            sec_names.append(c_name)
            sec_lats.append(lat)
            sec_lons.append(lon)

        if sec_names:
            _SEC_NAMES = sec_names
            _SEC_LATS_RAD = np.radians(np.array(sec_lats, dtype=np.float64))
            _SEC_LONS_RAD = np.radians(np.array(sec_lons, dtype=np.float64))
            logger.info("Loaded %d secondary railway transit junctions for waypoint naming.", len(_SEC_NAMES))
    except Exception as e:
        logger.debug("Secondary junction loading skipped: %s", e)


def fast_haversine_vector(lat_deg: float, lon_deg: float, lats_rad: np.ndarray, lons_rad: np.ndarray) -> np.ndarray:
    """Calculate Great Circle distance in km from a single coordinate to an array of coordinates."""
    if len(lats_rad) == 0:
        return np.array([], dtype=np.float64)
    q_lat_rad = math.radians(lat_deg)
    q_lon_rad = math.radians(lon_deg)
    dlat = lats_rad - q_lat_rad
    dlon = lons_rad - q_lon_rad
    a = np.sin(dlat / 2.0) ** 2 + math.cos(q_lat_rad) * np.cos(lats_rad) * np.sin(dlon / 2.0) ** 2
    c = 2.0 * np.arctan2(np.sqrt(np.clip(a, 0.0, 1.0)), np.sqrt(np.clip(1.0 - a, 0.0, 1.0)))
    return 6371.0 * c


def find_nearest_transit_city(
    lat: float,
    lon: float,
    max_distance_km: float = 45.0,
    exclude_names: Optional[Set[str]] = None
) -> Tuple[Optional[str], float]:
    """
    Find the closest Indian city or logistics node within max_distance_km.
    Returns (city_name, distance_km). If no city found within radius, returns (None, min_dist).
    """
    _ensure_secondary_nodes()
    exclude = {n.strip().lower() for n in exclude_names} if exclude_names else set()

    # 1. Primary curated hubs
    dists = fast_haversine_vector(lat, lon, _PRIMARY_LATS_RAD, _PRIMARY_LONS_RAD)
    sorted_indices = np.argsort(dists)

    for idx in sorted_indices:
        d = float(dists[idx])
        if d > max_distance_km:
            break
        cand_name = _PRIMARY_NAMES[idx]
        if cand_name.lower() not in exclude:
            return cand_name, round(d, 1)

    # 2. Check secondary railway junctions if available and within radius
    if len(_SEC_LATS_RAD) > 0:
        sec_dists = fast_haversine_vector(lat, lon, _SEC_LATS_RAD, _SEC_LONS_RAD)
        sec_sorted = np.argsort(sec_dists)
        for s_idx in sec_sorted:
            d = float(sec_dists[s_idx])
            if d > max_distance_km:
                break
            cand_name = _SEC_NAMES[s_idx]
            if cand_name.lower() not in exclude:
                return cand_name, round(d, 1)

    # Fallback to closest primary even if slightly beyond max_distance
    closest_idx = sorted_indices[0]
    return _PRIMARY_NAMES[closest_idx], round(float(dists[closest_idx]), 1)


def get_adaptive_leg_step(total_distance_km: float) -> float:
    """
    Determine optimal waypoint sampling step (in km) to ensure route legs
    represent natural intercity transit hops (e.g. 3 to 12 city hops).
    """
    if total_distance_km <= 70.0:
        return 18.0   # ~2-4 short city hops (e.g. Mumbai -> Thane -> Kalyan)
    elif total_distance_km <= 200.0:
        return 28.0   # ~4-7 intercity legs (e.g. Mumbai -> Lonavala -> Pune)
    elif total_distance_km <= 600.0:
        return 50.0   # ~5-11 highway hubs (e.g. Delhi -> Jaipur)
    elif total_distance_km <= 1300.0:
        return 85.0   # ~7-14 major regional transit checkpoints
    else:
        return 130.0  # ~10-16 long-haul corridor nodes
