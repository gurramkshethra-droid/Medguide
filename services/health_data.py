"""
MediGuide AI - Curated Health Information Service
Contains evidence-based, educational health guidance for all 41 conditions
predicted by the symptom classifier model.
Sources: NHS UK, CDC, WHO, MedlinePlus (U.S. National Library of Medicine).
"""

import re

# Comprehensive dictionary covering all 41 model classes exactly
CONDITIONS_DATA = {
    "(vertigo) Paroymsal  Positional Vertigo": {
        "title": "Benign Paroxysmal Positional Vertigo (BPPV)",
        "slug": "benign-paroxysmal-positional-vertigo",
        "description": "Benign Paroxysmal Positional Vertigo (BPPV) is a common inner-ear disorder causing brief, recurrent episodes of spinning sensation (vertigo) triggered by specific changes in head position.",
        "symptoms": ["Sudden spinning sensation (vertigo)", "Loss of balance or unsteadiness", "Nausea or vomiting", "Abnormal rhythmic eye movements (nystagmus)"],
        "causes": ["Dislodged calcium carbonate crystals (otoconia) migrating into the semicircular canals of the inner ear", "Head trauma", "Inner ear infections or prolonged bed rest"],
        "prevention": ["Avoid sudden extreme head extensions", "Use two pillows while sleeping if prone to episodes", "Stand up slowly from reclining positions"],
        "self_care": ["Sit down immediately when dizziness starts", "Perform canalith repositioning exercises (such as Epley maneuver) under clinical instruction", "Ensure well-lit hallways to prevent falls"],
        "warning_signs": ["Sudden severe headache", "Double vision or loss of vision", "Numbness, weakness, or difficulty speaking (signs of stroke)"],
        "specialty": "Otolaryngology (ENT) / Neurology",
        "sources": [
            {"name": "NHS UK - Benign Paroxysmal Positional Vertigo", "url": "https://www.nhs.uk/conditions/vertigo/"},
            {"name": "MedlinePlus - BPPV", "url": "https://medlineplus.gov/ency/article/000778.htm"}
        ]
    },
    "AIDS": {
        "title": "Acquired Immunodeficiency Syndrome (AIDS)",
        "slug": "aids",
        "description": "AIDS is the advanced stage of infection caused by the Human Immunodeficiency Virus (HIV), which attacks and severely weakens the body's immune defense system.",
        "symptoms": ["Rapid unexplained weight loss", "Recurring fever or profuse night sweats", "Chronic fatigue", "Prolonged swelling of the lymph glands", "Chronic diarrhea"],
        "causes": ["Untreated human immunodeficiency virus (HIV) infection destroying CD4 helper T-cells"],
        "prevention": ["Practice safe barrier sex", "Avoid sharing needles or injection equipment", "Use pre-exposure prophylaxis (PrEP) if at high risk", "Routine HIV screening"],
        "self_care": ["Strict adherence to prescribed Antiretroviral Therapy (ART)", "Maintain balanced nutrition and food safety to avoid opportunistic pathogens", "Stay up to date with non-live immunizations"],
        "warning_signs": ["High unremitting fever", "Severe shortness of breath or persistent dry cough", "Severe persistent headache with neck stiffness or confusion"],
        "specialty": "Infectious Disease Specialist / Immunology",
        "sources": [
            {"name": "WHO - HIV and AIDS", "url": "https://www.who.int/news-room/fact-sheets/detail/hiv-aids"},
            {"name": "CDC - HIV Basics", "url": "https://www.cdc.gov/hiv/basics/index.html"}
        ]
    },
    "Acne": {
        "title": "Acne Vulgaris",
        "slug": "acne",
        "description": "Acne is a very common skin condition that occurs when hair follicles become plugged with sebum oil and dead skin cells, causing pimples, blackheads, and cysts.",
        "symptoms": ["Whiteheads and blackheads", "Papules (small red, tender bumps)", "Pimples (pustules)", "Painful cysts under the skin"],
        "causes": ["Excess sebum production", "Follicular hyperkeratinization", "Colonization by Cutibacterium acnes bacteria", "Hormonal fluctuations (androgens)"],
        "prevention": ["Wash face twice daily with a gentle, non-comedogenic cleanser", "Avoid heavy oil-based cosmetic products", "Do not pick, squeeze, or pop blemishes"],
        "self_care": ["Apply over-the-counter benzoyl peroxide or salicylic acid topical washes", "Use non-comedogenic oil-free moisturizer and sunscreen", "Keep hair clean and off the face"],
        "warning_signs": ["Severe cystic acne causing deep scarring", "Signs of secondary bacterial infection (hot, spreading redness or intense pain)", "Sudden severe flare with fever"],
        "specialty": "Dermatology",
        "sources": [
            {"name": "NHS UK - Acne", "url": "https://www.nhs.uk/conditions/acne/"},
            {"name": "American Academy of Dermatology - Acne", "url": "https://www.aad.org/public/diseases/acne"}
        ]
    },
    "Alcoholic hepatitis": {
        "title": "Alcoholic Hepatitis",
        "slug": "alcoholic-hepatitis",
        "description": "Alcoholic hepatitis is inflammatory liver damage caused by chronic, heavy consumption of alcohol, which can progress to liver cirrhosis and hepatic failure.",
        "symptoms": ["Jaundice (yellowing of skin and eyes)", "Loss of appetite and nausea", "Abdominal pain and tenderness over the liver", "Fatigue and low-grade fever"],
        "causes": ["Toxic metabolic byproducts of excessive, chronic alcohol breakdown causing hepatocyte injury and oxidative stress"],
        "prevention": ["Complete abstinence from alcohol", "Moderation guidelines (if not dependent)", "Regular health check-ups and hepatitis vaccination"],
        "self_care": ["Total lifelong cessation of alcohol consumption", "High-protein, calorie-rich diet under clinical supervision to counteract malnutrition", "Never take hepatotoxic medications like high-dose acetaminophen"],
        "warning_signs": ["Confusion, drowsiness, or slurred speech (hepatic encephalopathy)", "Vomiting blood or black tarry stools", "Rapid abdominal swelling (ascites)"],
        "specialty": "Gastroenterology / Hepatology",
        "sources": [
            {"name": "NHS UK - Alcohol-related liver disease", "url": "https://www.nhs.uk/conditions/alcohol-related-liver-disease-arld/"},
            {"name": "MedlinePlus - Alcoholic Liver Disease", "url": "https://medlineplus.gov/ency/article/000281.htm"}
        ]
    },
    "Allergy": {
        "title": "Allergic Reaction",
        "slug": "allergy",
        "description": "An allergic reaction is an immune system overreaction to a normally harmless environmental foreign substance (allergen) such as pollen, pet dander, foods, or insect stings.",
        "symptoms": ["Sneezing, runny or stuffy nose", "Itchy, watery, red eyes", "Skin rash, hives (urticaria), or itching", "Wheezing or mild coughing"],
        "causes": ["Immunoglobulin E (IgE)-mediated hypersensitivity to specific airborne, contact, or food allergens"],
        "prevention": ["Identify and avoid known allergens", "Keep windows closed during high pollen seasons", "Use dust-mite proof bedding covers"],
        "self_care": ["Over-the-counter non-drowsy antihistamines", "Saline nasal sprays to rinse allergens", "Cool compresses for itching or urticaria"],
        "warning_signs": ["Swelling of lips, tongue, throat, or face", "Difficulty breathing or severe wheezing", "Dizziness, faintness, or collapse (Anaphylaxis - call emergency services immediately)"],
        "specialty": "Allergy & Clinical Immunology",
        "sources": [
            {"name": "NHS UK - Allergies", "url": "https://www.nhs.uk/conditions/allergies/"},
            {"name": "CDC - Allergies", "url": "https://www.cdc.gov/climateandhealth/effects/allergen.htm"}
        ]
    },
    "Arthritis": {
        "title": "Arthritis",
        "slug": "arthritis",
        "description": "Arthritis is the inflammation of one or more joints, causing pain, stiffness, and reduced range of motion, commonly encompassing rheumatoid arthritis, gout, or related conditions.",
        "symptoms": ["Joint pain and aching", "Stiffness, especially in the morning", "Swelling and warmth around joints", "Decreased range of motion"],
        "causes": ["Autoimmune attack against synovial lining (rheumatoid arthritis)", "Uric acid crystal deposition (gout)", "Joint infection"],
        "prevention": ["Maintain a healthy body weight to reduce joint load", "Engage in regular low-impact exercise (swimming, cycling)", "Protect joints from acute sports injuries"],
        "self_care": ["Hot and cold compress therapy", "Gentle range-of-motion stretching", "Anti-inflammatory dietary habits rich in omega-3s"],
        "warning_signs": ["Hot, acutely red, swollen single joint with fever (signs of septic arthritis requiring emergency drainage)", "Inability to bear weight"],
        "specialty": "Rheumatology",
        "sources": [
            {"name": "NHS UK - Arthritis", "url": "https://www.nhs.uk/conditions/arthritis/"},
            {"name": "CDC - Arthritis Basics", "url": "https://www.cdc.gov/arthritis/basics/index.html"}
        ]
    },
    "Bronchial Asthma": {
        "title": "Bronchial Asthma",
        "slug": "bronchial-asthma",
        "description": "Bronchial asthma is a chronic respiratory condition characterized by hyper-reactive airways, chronic bronchial inflammation, bronchospasm, and variable airflow obstruction.",
        "symptoms": ["Shortness of breath and breathlessness", "Chest tightness", "Wheezing on exhalation", "Coughing, especially at night or early morning"],
        "causes": ["Genetic predisposition combined with environmental triggers: cold air, smoke, pollen, viral respiratory infections, exercise, stress"],
        "prevention": ["Avoid known airborne triggers and tobacco smoke", "Get annual influenza and pneumococcal vaccines", "Use preventive inhalers strictly as prescribed"],
        "self_care": ["Always carry a fast-acting rescue inhaler (e.g., albuterol/salbutamol)", "Follow a written asthma action plan", "Monitor peak expiratory flow rate at home"],
        "warning_signs": ["Severe breathlessness speaking only in single words", "Rescue inhaler provides no relief or wears off in under 2 hours", "Blue tint to lips or fingertips (Cyanosis - call emergency services)"],
        "specialty": "Pulmonology / Respiratory Medicine",
        "sources": [
            {"name": "WHO - Asthma Fact Sheet", "url": "https://www.who.int/news-room/fact-sheets/detail/asthma"},
            {"name": "NHS UK - Asthma", "url": "https://www.nhs.uk/conditions/asthma/"}
        ]
    },
    "Cervical spondylosis": {
        "title": "Cervical Spondylosis",
        "slug": "cervical-spondylosis",
        "description": "Cervical spondylosis is age-related wear and tear affecting the cervical spine discs and joints in the neck, which can cause chronic stiffness and nerve compression.",
        "symptoms": ["Neck pain and stiffness", "Headaches originating from the base of the skull", "Grinding or popping noise when turning the neck", "Numbness or tingling radiating into shoulders and hands"],
        "causes": ["Dehydration of intervertebral discs", "Herniated cervical discs", "Bone spurs (osteophytes) narrowing the spinal canal or foramina"],
        "prevention": ["Maintain ergonomic workstation postures with screens at eye level", "Avoid cradling phones between shoulder and ear", "Do regular neck-strengthening and flexibility exercises"],
        "self_care": ["Apply heating pads or cold ice packs for 15-minute intervals", "Use a supportive cervical contour pillow", "Gentle neck retraction and stretching exercises"],
        "warning_signs": ["Sudden loss of bladder or bowel control", "Progressive loss of coordination in hands or walking unsteadiness (cervical myelopathy)"],
        "specialty": "Orthopedics / Neurology / Physical Therapy",
        "sources": [
            {"name": "NHS UK - Cervical Spondylosis", "url": "https://www.nhs.uk/conditions/cervical-spondylosis/"},
            {"name": "MedlinePlus - Cervical Spondylosis", "url": "https://medlineplus.gov/ency/article/000436.htm"}
        ]
    },
    "Chicken pox": {
        "title": "Chickenpox (Varicella)",
        "slug": "chicken-pox",
        "description": "Chickenpox is a highly contagious viral infection caused by the Varicella-zoster virus, causing an itchy vesicular blister rash, fever, and fatigue.",
        "symptoms": ["Itchy red spots that blister and crust over", "Fever and mild flu-like aches", "Loss of appetite", "General malaise"],
        "causes": ["Varicella-zoster virus (VZV) transmitted through airborne droplets or direct contact with fluid from blisters"],
        "prevention": ["Varicella vaccine (two doses offer >90% protection)", "Isolate infected individuals until all blisters have completely crusted"],
        "self_care": ["Calamine lotion on spots to relieve itchiness", "Tepid oatmeal baths", "Trim fingernails to prevent skin excoriation and secondary bacterial infection", "Never give aspirin to children with viral infections (risk of Reye's syndrome)"],
        "warning_signs": ["Skin around blisters becomes intensely red, swollen, hot, or leaks pus (cellulitis)", "Persistent high fever, confusion, or difficulty breathing"],
        "specialty": "Pediatrics / Infectious Disease",
        "sources": [
            {"name": "CDC - Chickenpox (Varicella)", "url": "https://www.cdc.gov/chickenpox/index.html"},
            {"name": "NHS UK - Chickenpox", "url": "https://www.nhs.uk/conditions/chickenpox/"}
        ]
    },
    "Chronic cholestasis": {
        "title": "Chronic Cholestasis",
        "slug": "chronic-cholestasis",
        "description": "Chronic cholestasis is a medical condition where bile flow from the liver to the duodenum is chronically impaired or stalled, leading to bile acid buildup in blood and liver tissue.",
        "symptoms": ["Intense generalized pruritus (itching) without primary rash", "Jaundice (yellowing of eyes and skin)", "Dark tea-colored urine", "Pale or clay-colored stools", "Fatigue"],
        "causes": ["Primary biliary cholangitis (PBC)", "Primary sclerosing cholangitis (PSC)", "Gallstone obstruction", "Drug-induced liver injury"],
        "prevention": ["Avoid excessive alcohol", "Prompt treatment of biliary tract infections and gallstones", "Periodic liver function testing during high-risk medications"],
        "self_care": ["Moisturize skin with cool emollient creams to mitigate severe pruritus", "Take fat-soluble vitamin supplements (A, D, E, K) as clinically directed", "Avoid alcohol completely"],
        "warning_signs": ["High fever with chills and severe right upper quadrant abdominal pain (acute cholangitis - emergency)", "Vomiting blood or altered mental status"],
        "specialty": "Gastroenterology / Hepatology",
        "sources": [
            {"name": "MedlinePlus - Cholestasis", "url": "https://medlineplus.gov/ency/article/000215.htm"},
            {"name": "NIH NIDDK - Liver Disease & Cholestasis", "url": "https://www.niddk.nih.gov/health-information/liver-disease"}
        ]
    },
    "Common Cold": {
        "title": "Common Cold (Viral Upper Respiratory Infection)",
        "slug": "common-cold",
        "description": "The common cold is a self-limiting viral infection of the upper respiratory tract primarily affecting the nose, sinuses, and throat.",
        "symptoms": ["Sneezing and nasal congestion", "Runny nose (clear to thickened mucus)", "Sore throat", "Mild dry cough", "Low-grade fever or mild headache"],
        "causes": ["Rhinoviruses (>50% of cases), Coronaviruses, Respiratory Syncytial Virus (RSV), or Adenoviruses"],
        "prevention": ["Frequent handwashing with soap for 20 seconds", "Avoid touching eyes, nose, and mouth with unwashed hands", "Disinfect high-touch surfaces"],
        "self_care": ["Get plenty of rest and sleep", "Drink abundant fluids (water, warm broths, herbal teas)", "Saline nasal sprays and warm salt water gargles", "Humidify room air"],
        "warning_signs": ["Symptoms lasting more than 10-14 days without improvement", "High fever (>102°F / 39°C)", "Shortness of breath or severe chest pain"],
        "specialty": "General Medicine / Family Practice",
        "sources": [
            {"name": "CDC - Common Cold", "url": "https://www.cdc.gov/dotw/common-cold/index.html"},
            {"name": "NHS UK - Common Cold", "url": "https://www.nhs.uk/conditions/common-cold/"}
        ]
    },
    "Dengue": {
        "title": "Dengue Fever",
        "slug": "dengue",
        "description": "Dengue is a mosquito-borne viral infection transmitted by female Aedes mosquitoes, causing sudden high fever, severe headache, and intense retro-orbital and bone pain ('breakbone fever').",
        "symptoms": ["Sudden onset high fever (104°F / 40°C)", "Severe pain behind the eyes", "Severe joint and muscle pains", "Skin rash appearing 2-5 days after fever", "Mild bleeding from nose or gums"],
        "causes": ["Dengue virus (DENV, serotypes 1-4) transmitted through the bite of an infected Aedes aegypti or Aedes albopictus mosquito"],
        "prevention": ["Eliminate standing water in flowerpots, buckets, and discarded tires", "Use DEET-containing insect repellent", "Wear long-sleeved clothing and use mosquito screens"],
        "self_care": ["Complete physical rest", "Aggressive oral hydration with oral rehydration solution (ORS) and coconut water", "Take acetaminophen/paracetamol for fever", "AVOID NSAIDs (aspirin, ibuprofen) due to increased bleeding risk"],
        "warning_signs": ["Severe persistent abdominal pain", "Persistent vomiting", "Bleeding gums or nose, vomiting blood", "Extreme lethargy or restlessness (signs of Severe Dengue / Dengue Hemorrhagic Fever - emergency)"],
        "specialty": "Infectious Disease / Tropical Medicine",
        "sources": [
            {"name": "WHO - Dengue and Severe Dengue", "url": "https://www.who.int/news-room/fact-sheets/detail/dengue-and-severe-dengue"},
            {"name": "CDC - Dengue Fever", "url": "https://www.cdc.gov/dengue/index.html"}
        ]
    },
    "Diabetes": {
        "title": "Diabetes Mellitus",
        "slug": "diabetes",
        "description": "Diabetes mellitus is a chronic metabolic disorder marked by elevated blood glucose levels resulting from insulin deficiency, insulin resistance, or both.",
        "symptoms": ["Frequent urination (polyuria)", "Increased thirst (polydipsia)", "Excessive hunger (polyphagia)", "Unexplained weight loss", "Blurred vision", "Slow-healing sores"],
        "causes": ["Autoimmune beta-cell destruction (Type 1)", "Insulin resistance, obesity, sedentary lifestyle, and genetic predisposition (Type 2)"],
        "prevention": ["Maintain a healthy BMI", "Engage in 150 minutes of moderate aerobic exercise per week", "Adopt a balanced diet low in refined carbohydrates and sugary beverages"],
        "self_care": ["Routine self-monitoring of blood glucose", "Adhere strictly to prescribed insulin or oral hypoglycemics", "Inspect feet daily for cuts or sores", "Regular HbA1c and retinal check-ups"],
        "warning_signs": ["Fruity-smelling breath, nausea, confusion, deep rapid breathing (Diabetic Ketoacidosis - emergency)", "Blood glucose > 300 mg/dL with extreme lethargy"],
        "specialty": "Endocrinology / Internal Medicine",
        "sources": [
            {"name": "WHO - Diabetes", "url": "https://www.who.int/news-room/fact-sheets/detail/diabetes"},
            {"name": "ADA - American Diabetes Association", "url": "https://diabetes.org/"}
        ]
    },
    "Dimorphic hemmorhoids(piles)": {
        "title": "Hemorrhoids (Piles)",
        "slug": "hemorrhoids-piles",
        "description": "Hemorrhoids are swollen, inflamed veins in the lower rectum and anus, causing rectal bleeding, pain, itching, or prolapsing tissue during bowel movements.",
        "symptoms": ["Painless bright red rectal bleeding during bowel movements", "Anal itching or irritation", "Pain or discomfort around the anus", "Sensitive or painful lump near the anus"],
        "causes": ["Straining during bowel movements", "Chronic constipation or diarrhea", "Prolonged sitting on the toilet", "Pregnancy and heavy lifting"],
        "prevention": ["Eat high-fiber foods (fruits, vegetables, whole grains)", "Drink 2 to 3 liters of water daily", "Do not delay bowel movements or strain"],
        "self_care": ["Take warm sitz baths for 15 minutes twice daily", "Apply over-the-counter witch hazel pads or hydrocortisone ointments temporarily", "Use stool softeners if stools are hard"],
        "warning_signs": ["Large amounts of rectal bleeding or dizziness/faintness", "Extremely painful, firm dark-blue lump (thrombosed external hemorrhoid)"],
        "specialty": "Colorectal Surgery / Proctology / Gastroenterology",
        "sources": [
            {"name": "NHS UK - Piles (Hemorrhoids)", "url": "https://www.nhs.uk/conditions/piles-haemorrhoids/"},
            {"name": "MedlinePlus - Hemorrhoids", "url": "https://medlineplus.gov/hemorrhoids.html"}
        ]
    },
    "Drug Reaction": {
        "title": "Adverse Drug Reaction",
        "slug": "drug-reaction",
        "description": "An adverse drug reaction is an unwanted or harmful reaction experienced following the administration of a drug or therapeutic compound.",
        "symptoms": ["Skin rash, hives, or erythema", "Itching", "Mild fever", "Nausea or gastrointestinal upset"],
        "causes": ["Allergic immune hypersensitivity to medication (e.g. penicillin, sulfa)", "Non-allergic medication side effect or toxicity"],
        "prevention": ["Always inform doctors and pharmacists of past drug allergies", "Wear a medical alert bracelet for severe drug allergies", "Never share prescription medications"],
        "self_care": ["Immediately stop taking the suspected non-essential medication and contact your prescribing clinician", "Apply cool compresses for mild cutaneous itching", "Keep the exact drug packaging to show medical staff"],
        "warning_signs": ["Facial, lip, or airway swelling (Anaphylaxis)", "Widespread blistering or skin peeling with mucosal detachment (Stevens-Johnson Syndrome / TEN - emergency)", "High fever and difficulty swallowing"],
        "specialty": "Allergy & Clinical Immunology / Dermatology",
        "sources": [
            {"name": "MedlinePlus - Drug Allergies", "url": "https://medlineplus.gov/ency/article/000819.htm"},
            {"name": "NHS UK - Drug Allergies", "url": "https://www.nhs.uk/conditions/allergies/symptoms/"}
        ]
    },
    "Fungal infection": {
        "title": "Superficial Fungal Skin Infection",
        "slug": "fungal-infection",
        "description": "A superficial fungal infection (such as ringworm, athlete's foot, or tinea versicolor) is a dermatophyte or yeast infection affecting the keratin of the skin, hair, or nails.",
        "symptoms": ["Itchy, red, circular or scaling rash with raised edges", "Peeling or cracking skin between toes", "Discolored skin patches (lighter or darker)", "Nail thickening and discoloration"],
        "causes": ["Overgrowth of dermatophytes (Trichophyton, Microsporum) or yeasts (Candida, Malassezia) in warm, moist environments"],
        "prevention": ["Keep skin clean and completely dry", "Wear breathable cotton clothing", "Never walk barefoot in communal showers, locker rooms, or pool decks", "Do not share towels or personal grooming tools"],
        "self_care": ["Apply over-the-counter topical antifungal creams (clotrimazole, terbinafine, miconazole) consistently for the full instructed course", "Wash gym clothes and socks in hot water"],
        "warning_signs": ["Spreading redness, increased heat, severe swelling or pus (secondary bacterial cellulitis)", "Infection in individuals with diabetes or immunosuppression"],
        "specialty": "Dermatology / General Practice",
        "sources": [
            {"name": "CDC - Fungal Diseases", "url": "https://www.cdc.gov/fungal/diseases/index.html"},
            {"name": "NHS UK - Ringworm", "url": "https://www.nhs.uk/conditions/ringworm/"}
        ]
    },
    "GERD": {
        "title": "Gastroesophageal Reflux Disease (GERD)",
        "slug": "gerd",
        "description": "GERD is a chronic digestive condition where stomach acid and digestive enzymes flow back into the esophagus, irritating its sensitive lining.",
        "symptoms": ["Heartburn (burning sensation in the chest behind breastbone)", "Acid regurgitation into throat or mouth", "Difficulty or pain when swallowing", "Chronic dry cough or hoarseness", "Sensation of a lump in the throat"],
        "causes": ["Dysfunction or transient relaxation of the lower esophageal sphincter (LES)", "Hiatal hernia", "Obesity, pregnancy, smoking"],
        "prevention": ["Avoid lying down within 3 hours of eating", "Limit acidic, fatty, spicy foods, caffeine, and alcohol", "Maintain healthy weight"],
        "self_care": ["Elevate the head of your bed by 6 inches", "Eat smaller, more frequent meals rather than large dinners", "Wear loose clothing around the abdomen", "Antacids or H2 blockers for occasional relief under guidance"],
        "warning_signs": ["Food getting stuck in the chest (progressive dysphagia)", "Vomiting blood or coffee-ground material", "Severe chest pain radiating to jaw or left arm (evaluate for heart attack first)"],
        "specialty": "Gastroenterology",
        "sources": [
            {"name": "NIH NIDDK - Acid Reflux (GER & GERD)", "url": "https://www.niddk.nih.gov/health-information/digestive-diseases/acid-reflux-ger-gerd-adults"},
            {"name": "NHS UK - Heartburn and acid reflux", "url": "https://www.nhs.uk/conditions/heartburn-and-acid-reflux/"}
        ]
    },
    "Gastroenteritis": {
        "title": "Gastroenteritis (Stomach Flu)",
        "slug": "gastroenteritis",
        "description": "Gastroenteritis is an inflammation of the lining of the stomach and intestines, commonly characterized by acute watery diarrhea, vomiting, and abdominal cramps.",
        "symptoms": ["Watery, non-bloody diarrhea", "Nausea and vomiting", "Abdominal cramps and stomach pain", "Low-grade fever and body aches"],
        "causes": ["Viral pathogens (Norovirus, Rotavirus)", "Bacterial foodborne toxins (Salmonella, E. coli, Campylobacter)", "Parasitic water contamination (Giardia)"],
        "prevention": ["Strict hand hygiene before eating and after using the restroom", "Thoroughly cook meats and wash raw produce", "Drink safe, treated, or boiled water while traveling"],
        "self_care": ["Sip Oral Rehydration Salts (ORS) or electrolyte solutions frequently", "Avoid dairy, alcohol, caffeine, and fatty foods until recovered", "Reintroduce bland foods gradually (bananas, rice, applesauce, toast)"],
        "warning_signs": ["Signs of severe dehydration (dizziness on standing, sunken eyes, dry mouth, little or no urination)", "Bloody diarrhea or high fever (>102°F / 39°C)", "Inability to keep liquids down for >24 hours"],
        "specialty": "Gastroenterology / Internal Medicine",
        "sources": [
            {"name": "CDC - Viral Gastroenteritis", "url": "https://www.cdc.gov/norovirus/index.html"},
            {"name": "NHS UK - Diarrhoea and vomiting", "url": "https://www.nhs.uk/conditions/diarrhoea-and-vomiting/"}
        ]
    },
    "Heart attack": {
        "title": "Acute Myocardial Infarction (Heart Attack)",
        "slug": "heart-attack",
        "description": "A heart attack occurs when blood flow to a portion of the heart muscle is abruptly blocked, typically by a ruptured atherosclerotic plaque and thrombus.",
        "symptoms": ["Crushing chest pain, pressure, fullness, or squeezing in center of chest", "Pain radiating to jaw, neck, back, stomach, or one or both arms", "Cold sweat and dizziness", "Shortness of breath and nausea"],
        "causes": ["Coronary artery disease (CAD)", "Atherosclerotic plaque rupture and thrombosis", "Coronary artery spasm"],
        "prevention": ["Manage blood pressure, cholesterol, and diabetes", "Quit smoking and avoid secondhand smoke", "Regular aerobic cardiovascular exercise and Mediterranean diet"],
        "self_care": ["CALL EMERGENCY SERVICES (911/112/999) IMMEDIATELY - DO NOT DRIVE YOURSELF", "Chew an adult aspirin (325 mg) if advised by emergency dispatch and not allergic", "Rest in a seated position while awaiting emergency paramedics"],
        "warning_signs": ["THIS IS A LIFE-THREATENING MEDICAL EMERGENCY. Immediate emergency response is vital to prevent irreversible myocardial necrosis."],
        "specialty": "Cardiology / Emergency Medicine",
        "sources": [
            {"name": "American Heart Association - Heart Attack", "url": "https://www.heart.org/en/health-topics/heart-attack"},
            {"name": "NHS UK - Heart attack", "url": "https://www.nhs.uk/conditions/heart-attack/"}
        ]
    },
    "Hepatitis B": {
        "title": "Hepatitis B",
        "slug": "hepatitis-b",
        "description": "Hepatitis B is a viral infection that attacks the liver and can cause both acute and lifelong chronic disease, liver cirrhosis, and hepatocellular carcinoma.",
        "symptoms": ["Fatigue and joint pain", "Nausea, vomiting, and abdominal pain", "Dark urine and pale stools", "Jaundice (yellow skin and sclera)"],
        "causes": ["Hepatitis B virus (HBV) transmitted through infected blood, perinatal mother-to-child transmission, or unprotected sexual contact"],
        "prevention": ["Complete the Hepatitis B vaccine series (three doses)", "Screening during pregnancy", "Avoid needle sharing and ensure sterile tattoo/medical equipment"],
        "self_care": ["Refrain completely from alcohol to preserve liver parenchyma", "Eat a balanced diet and avoid hepatotoxic medications", "Schedule routine liver enzyme and viral load monitoring"],
        "warning_signs": ["Vomiting blood or black stools", "Fluid accumulation in abdomen (ascites)", "Confusion, memory lapses, or excessive sleepiness (hepatic encephalopathy)"],
        "specialty": "Hepatology / Infectious Disease",
        "sources": [
            {"name": "WHO - Hepatitis B Fact Sheet", "url": "https://www.who.int/news-room/fact-sheets/detail/hepatitis-b"},
            {"name": "CDC - Hepatitis B Basics", "url": "https://www.cdc.gov/hepatitis/hbv/index.htm"}
        ]
    },
    "Hepatitis C": {
        "title": "Hepatitis C",
        "slug": "hepatitis-c",
        "description": "Hepatitis C is a bloodborne viral infection that causes liver inflammation, often remaining clinically silent for decades until severe liver cirrhosis develops.",
        "symptoms": ["Often asymptomatic for years", "Chronic fatigue and joint pain", "Loss of appetite and mild nausea", "Late stage: Jaundice, dark urine, easy bruising"],
        "causes": ["Hepatitis C virus (HCV) transmitted primarily through exposure to contaminated blood"],
        "prevention": ["Never share needles, syringes, or personal grooming items (razors)", "Use regulated sterile piercing and tattooing facilities", "Routine blood donor screening"],
        "self_care": ["Complete course of direct-acting antiviral (DAA) medications (now >95% cure rate)", "Abstain entirely from alcohol", "Receive Hepatitis A and B immunizations to prevent co-infection"],
        "warning_signs": ["Abdominal fluid distention (ascites)", "Confusion or altered sleep cycles (encephalopathy)", "Gastrointestinal bleeding"],
        "specialty": "Hepatology / Gastroenterology",
        "sources": [
            {"name": "WHO - Hepatitis C", "url": "https://www.who.int/news-room/fact-sheets/detail/hepatitis-c"},
            {"name": "CDC - Hepatitis C", "url": "https://www.cdc.gov/hepatitis/hcv/index.htm"}
        ]
    },
    "Hepatitis D": {
        "title": "Hepatitis D (Delta Hepatitis)",
        "slug": "hepatitis-d",
        "description": "Hepatitis D is a liver infection caused by the hepatitis delta virus (HDV), which requires the presence of Hepatitis B virus (HBV) to replicate.",
        "symptoms": ["Similar to Hepatitis B but often more severe and rapid in progression", "Severe fatigue", "Jaundice", "Abdominal discomfort"],
        "causes": ["HDV infection occurring as either a coinfection with HBV or a superinfection on chronic HBV carriers"],
        "prevention": ["Hepatitis B vaccination (effectively prevents HDV as well since HDV cannot survive without HBV)", "Safe injection and sexual practices"],
        "self_care": ["Strict medical follow-up with a hepatologist", "Total alcohol cessation", "Adherence to antiviral treatment plans"],
        "warning_signs": ["Rapid onset of liver decompensation (rapid jaundice, bleeding diathesis, mental confusion)"],
        "specialty": "Hepatology",
        "sources": [
            {"name": "WHO - Hepatitis D", "url": "https://www.who.int/news-room/fact-sheets/detail/hepatitis-d"},
            {"name": "CDC - Hepatitis D", "url": "https://www.cdc.gov/hepatitis/hdv/index.htm"}
        ]
    },
    "Hepatitis E": {
        "title": "Hepatitis E",
        "slug": "hepatitis-e",
        "description": "Hepatitis E is an enterically transmitted viral liver infection mainly spread through drinking water contaminated with fecal matter.",
        "symptoms": ["Fever, fatigue, and malaise", "Anorexia and nausea", "Jaundice with dark urine and pale stools", "Tender hepatomegaly"],
        "causes": ["Hepatitis E virus (HEV) transmitted primarily via the fecal-oral route through contaminated water or undercooked pork/game meat"],
        "prevention": ["Drink clean, treated, or boiled water", "Maintain proper sanitation and sewage treatment", "Cook pork and shellfish thoroughly"],
        "self_care": ["Most cases are self-limiting: rest and adequate hydration", "Avoid alcohol and unnecessary liver-metabolized drugs"],
        "warning_signs": ["Infection during pregnancy (high risk of fulminant hepatic failure in 3rd trimester requiring emergency obstetric care)", "Severe persistent vomiting"],
        "specialty": "Infectious Disease / Hepatology",
        "sources": [
            {"name": "WHO - Hepatitis E", "url": "https://www.who.int/news-room/fact-sheets/detail/hepatitis-e"},
            {"name": "CDC - Hepatitis E", "url": "https://www.cdc.gov/hepatitis/hev/index.htm"}
        ]
    },
    "Hypertension": {
        "title": "Hypertension (High Blood Pressure)",
        "slug": "hypertension",
        "description": "Hypertension is a chronic cardiovascular condition in which the systemic arterial blood pressure is persistently elevated (>= 130/80 mmHg), increasing cardiovascular strain.",
        "symptoms": ["Usually asymptomatic ('Silent Killer')", "Occasional morning headaches", "Shortness of breath or nosebleeds during severe blood pressure spikes"],
        "causes": ["Primary (essential) hypertension: age, genetics, excess sodium intake, physical inactivity, obesity", "Secondary: kidney disease, sleep apnea, endocrine disorders"],
        "prevention": ["Adopt the DASH diet (rich in fruits, vegetables, low-fat dairy, low sodium <2g/day)", "Maintain healthy weight", "Limit alcohol and exercise regularly"],
        "self_care": ["Monitor blood pressure with a calibrated home upper-arm cuff", "Take antihypertensive medication daily without skipping doses", "Practice stress management"],
        "warning_signs": ["Hypertensive Crisis (BP > 180/120 mmHg) accompanied by severe headache, chest pain, visual changes, or numbness (emergency)"],
        "specialty": "Cardiology / Internal Medicine",
        "sources": [
            {"name": "WHO - Hypertension", "url": "https://www.who.int/news-room/fact-sheets/detail/hypertension"},
            {"name": "AHA - High Blood Pressure", "url": "https://www.heart.org/en/health-topics/high-blood-pressure"}
        ]
    },
    "Hyperthyroidism": {
        "title": "Hyperthyroidism",
        "slug": "hyperthyroidism",
        "description": "Hyperthyroidism is an endocrine condition where the thyroid gland produces an excessive amount of thyroid hormones (T3 and T4), accelerating body metabolism.",
        "symptoms": ["Unexplained weight loss despite increased appetite", "Rapid heartbeat (tachycardia) or palpitations", "Nervousness, anxiety, and fine hand tremors", "Heat intolerance and profuse sweating", "Frequent bowel movements"],
        "causes": ["Graves' disease (autoimmune stimulation of TSH receptors)", "Toxic multinodular goiter", "Thyroiditis"],
        "prevention": ["No proven lifestyle prevention for autoimmune Graves' disease; early screening for those with family history is essential"],
        "self_care": ["Follow prescribed antithyroid medications (methimazole) or beta-blockers", "Avoid excess dietary iodine (kelp, seaweeds) unless instructed", "Eye drops for thyroid eye symptoms"],
        "warning_signs": ["Thyroid Storm: extreme fever, rapid irregular pulse, agitation, delirium (life-threatening emergency)"],
        "specialty": "Endocrinology",
        "sources": [
            {"name": "NIH NIDDK - Hyperthyroidism", "url": "https://www.niddk.nih.gov/health-information/endocrine-diseases/hyperthyroidism"},
            {"name": "NHS UK - Overactive thyroid (hyperthyroidism)", "url": "https://www.nhs.uk/conditions/overactive-thyroid-hyperthyroidism/"}
        ]
    },
    "Hypoglycemia": {
        "title": "Hypoglycemia (Low Blood Sugar)",
        "slug": "hypoglycemia",
        "description": "Hypoglycemia occurs when blood glucose levels fall dangerously below normal parameters (typically $<70$ mg/dL), depriving the brain and muscles of vital fuel.",
        "symptoms": ["Shakiness and trembling", "Sweating, chills, and clamminess", "Fast or pounding heartbeat", "Dizziness, lightheadedness, and intense hunger", "Irritability or confusion"],
        "causes": ["Excessive insulin or sulfonylurea dose in diabetics", "Delayed or skipped meals following medication", "Unaccustomed intense physical activity", "Excess alcohol on an empty stomach"],
        "prevention": ["Eat meals on a regular schedule", "Monitor blood glucose before and after exercise", "Carry fast-acting carbohydrates at all times"],
        "self_care": ["Follow the 15-15 Rule: consume 15 grams of fast-acting carbs (half cup juice, 4 glucose tablets), wait 15 minutes, recheck blood sugar"],
        "warning_signs": ["Inability to swallow", "Seizures or loss of consciousness (requires immediate intramuscular glucagon and emergency services)"],
        "specialty": "Endocrinology / Emergency Medicine",
        "sources": [
            {"name": "ADA - Hypoglycemia (Low Blood Glucose)", "url": "https://diabetes.org/living-with-diabetes/treatment-care/hypoglycemia"},
            {"name": "CDC - Low Blood Sugar", "url": "https://www.cdc.gov/diabetes/basics/low-blood-sugar-hypoglycemia.html"}
        ]
    },
    "Hypothyroidism": {
        "title": "Hypothyroidism (Underactive Thyroid)",
        "slug": "hypothyroidism",
        "description": "Hypothyroidism is a disorder in which the thyroid gland does not produce enough vital thyroid hormones, causing body functions to slow down.",
        "symptoms": ["Fatigue and lethargy", "Unexplained weight gain or difficulty losing weight", "Cold intolerance", "Constipation", "Dry skin and thinning hair", "Depressed mood and memory fog"],
        "causes": ["Hashimoto's thyroiditis (autoimmune destruction)", "Previous radioactive iodine treatment or thyroidectomy", "Iodine deficiency (globally)"],
        "prevention": ["Adequate dietary iodine consumption (iodized salt); autoimmune thyroiditis cannot be specifically prevented"],
        "self_care": ["Take prescribed levothyroxine on an empty stomach with plain water at least 30-60 minutes before breakfast", "Maintain balanced physical activity and fiber intake"],
        "warning_signs": ["Myxedema Coma: severe hypothermia, profound confusion, slowed breathing, shock (emergency)"],
        "specialty": "Endocrinology",
        "sources": [
            {"name": "NIH NIDDK - Hypothyroidism", "url": "https://www.niddk.nih.gov/health-information/endocrine-diseases/hypothyroidism"},
            {"name": "NHS UK - Underactive thyroid (hypothyroidism)", "url": "https://www.nhs.uk/conditions/underactive-thyroid-hypothyroidism/"}
        ]
    },
    "Impetigo": {
        "title": "Impetigo",
        "slug": "impetigo",
        "description": "Impetigo is a highly contagious superficial bacterial skin infection that predominantly affects infants and young children, causing honey-colored crusts.",
        "symptoms": ["Red sores that quickly rupture, ooze for a few days, and form honey-colored crusts", "Typically located around nose, mouth, hands, and feet", "Itching and mild soreness"],
        "causes": ["Staphylococcus aureus or Streptococcus pyogenes bacteria invading small breaks in the skin"],
        "prevention": ["Wash hands frequently", "Keep children's fingernails short and clean", "Do not share towels, washcloths, or clothing with an infected person"],
        "self_care": ["Gently wash affected areas with mild soap and water", "Apply prescribed topical antibiotic ointment (mupirocin)", "Cover sores with loose gauze to prevent scratching and spreading"],
        "warning_signs": ["Fever or signs of spreading infection (cellulitis: expanding red warm borders, streaks)", "Kidney symptoms: cola-colored urine after strep impetigo"],
        "specialty": "Dermatology / Pediatrics",
        "sources": [
            {"name": "CDC - Impetigo", "url": "https://www.cdc.gov/groupastrep/diseases-public/impetigo.html"},
            {"name": "NHS UK - Impetigo", "url": "https://www.nhs.uk/conditions/impetigo/"}
        ]
    },
    "Jaundice": {
        "title": "Jaundice",
        "slug": "jaundice",
        "description": "Jaundice is a clinical manifestation characterized by a yellowish discoloration of the skin, mucous membranes, and whites of the eyes (sclera) caused by elevated bilirubin levels in the blood.",
        "symptoms": ["Yellowing of skin and whites of the eyes", "Dark, tea-colored urine", "Pale or clay-colored feces", "Generalized skin itching (pruritus)"],
        "causes": ["Pre-hepatic: hemolysis (breakdown of red blood cells)", "Hepatic: hepatitis, cirrhosis, drug toxicity", "Post-hepatic: gallstones or pancreatic tumors obstructing bile ducts"],
        "prevention": ["Hepatitis A and B vaccinations", "Avoid excessive alcohol intake", "Careful medication dosing avoiding hepatotoxic overdosages"],
        "self_care": ["Seek immediate medical investigation to determine root cause", "Complete abstinence from alcohol", "Stay hydrated and avoid high-fat meals"],
        "warning_signs": ["Fever and severe right upper quadrant abdominal pain (ascending cholangitis)", "Vomiting blood or extreme confusion"],
        "specialty": "Gastroenterology / Hepatology / Internal Medicine",
        "sources": [
            {"name": "NHS UK - Jaundice", "url": "https://www.nhs.uk/conditions/jaundice/"},
            {"name": "MedlinePlus - Jaundice", "url": "https://medlineplus.gov/jaundice.html"}
        ]
    },
    "Malaria": {
        "title": "Malaria",
        "slug": "malaria",
        "description": "Malaria is a life-threatening, preventable mosquito-borne disease caused by Plasmodium parasites transmitted to humans through the bites of infected female Anopheles mosquitoes.",
        "symptoms": ["High cyclical fevers and violent shivering chills", "Profuse sweating as fever breaks", "Severe headache, muscle aches, and fatigue", "Nausea, vomiting, and diarrhea"],
        "causes": ["Plasmodium parasites (P. falciparum, P. vivax, P. malariae, P. ovale) infecting red blood cells"],
        "prevention": ["Sleep under insecticide-treated bed nets (ITNs)", "Apply DEET insect repellent", "Take prescribed prophylactic antimalarial medications before traveling to endemic areas"],
        "self_care": ["Seek immediate medical evaluation for blood smear / rapid antigen test", "Complete the full course of prescribed artemisinin-based combination therapy (ACT)", "Oral rehydration"],
        "warning_signs": ["Cerebral Malaria: impaired consciousness, seizures, coma", "Severe anemia, respiratory distress, black urine (blackwater fever)"],
        "specialty": "Infectious Disease / Tropical Medicine",
        "sources": [
            {"name": "WHO - Malaria", "url": "https://www.who.int/news-room/fact-sheets/detail/malaria"},
            {"name": "CDC - Malaria", "url": "https://www.cdc.gov/malaria/index.html"}
        ]
    },
    "Migraine": {
        "title": "Migraine Headache",
        "slug": "migraine",
        "description": "Migraine is a complex neurological disorder characterized by recurrent, moderate-to-severe throbbing headaches, typically unilateral, and often accompanied by sensory sensitivities.",
        "symptoms": ["Throbbing or pulsating headache on one side of head", "Extreme sensitivity to light (photophobia) and sound (phonophobia)", "Nausea and vomiting", "Visual aura (zigzag flashes, blind spots) prior to headache"],
        "causes": ["Neurovascular dysfunction, trigeminovascular system activation, and calcitonin gene-related peptide (CGRP) release triggered by stress, hormonal changes, or lack of sleep"],
        "prevention": ["Maintain consistent sleep, hydration, and meal schedules", "Identify and avoid dietary triggers (aged cheeses, MSG, nitrates)", "Prescribed preventive medications if headaches are frequent"],
        "self_care": ["Rest in a quiet, dark room at the earliest onset", "Apply a cold compress across forehead or back of neck", "Take triptans or approved abortive medications early in the attack"],
        "warning_signs": ["Sudden onset 'thunderclap' headache reaching peak intensity in seconds (rule out subarachnoid hemorrhage - emergency)", "Headache with fever, stiff neck, or focal neurological deficits"],
        "specialty": "Neurology",
        "sources": [
            {"name": "NHS UK - Migraine", "url": "https://www.nhs.uk/conditions/migraine/"},
            {"name": "American Migraine Foundation", "url": "https://americanmigrainefoundation.org/"}
        ]
    },
    "Osteoarthristis": {
        "title": "Osteoarthritis",
        "slug": "osteoarthritis",
        "description": "Osteoarthritis is the most common form of arthritis, characterized by the gradual mechanical breakdown of protective articular cartilage that cushions the ends of bones.",
        "symptoms": ["Joint pain during or after movement", "Joint stiffness upon awakening or following inactivity (<30 mins)", "Loss of joint flexibility", "Grating or crackling sensation (crepitus) on movement", "Bone spurs around joint"],
        "causes": ["Age-related degeneration, cumulative joint wear and tear, previous joint trauma, obesity"],
        "prevention": ["Maintain a healthy weight to reduce load on knees and hips", "Regular low-impact strengthening exercise (swimming, cycling)", "Avoid repetitive joint injury"],
        "self_care": ["Apply alternating heat and cold to affected joints", "Low-impact physical therapy to strengthen supporting muscles", "Use assistive devices (canes, braces) if needed"],
        "warning_signs": ["Acute joint redness, warmth, and inability to bear weight (exclude septic arthritis or gout)"],
        "specialty": "Orthopedics / Rheumatology",
        "sources": [
            {"name": "CDC - Osteoarthritis", "url": "https://www.cdc.gov/arthritis/basics/osteoarthritis.htm"},
            {"name": "NHS UK - Osteoarthritis", "url": "https://www.nhs.uk/conditions/osteoarthritis/"}
        ]
    },
    "Paralysis (brain hemorrhage)": {
        "title": "Hemorrhagic Stroke & Hemiplegia",
        "slug": "hemorrhagic-stroke-paralysis",
        "description": "A hemorrhagic stroke occurs when a weakened blood vessel inside or around the brain ruptures, causing localized bleeding (intracranial hemorrhage), elevated intracranial pressure, and rapid tissue damage leading to paralysis.",
        "symptoms": ["Sudden unilateral weakness or paralysis of face, arm, or leg", "Sudden severe 'worst headache of life'", "Difficulty speaking, slurred speech, or trouble understanding speech", "Sudden loss of balance, dizziness, or vision loss in one or both eyes"],
        "causes": ["Uncontrolled chronic hypertension", "Cerebral aneurysms", "Arteriovenous malformations (AVMs)", "Head trauma or anticoagulant therapy"],
        "prevention": ["Strict control of blood pressure", "Stop smoking and limit alcohol", "Manage cardiovascular disease risk factors"],
        "self_care": ["CALL EMERGENCY MEDICAL SERVICES IMMEDIATELY (ACT B.E. F.A.S.T.) - Time is brain", "Keep patient lying down comfortably on their side with airway clear", "Do not give any food, water, or aspirin"],
        "warning_signs": ["THIS IS A CRITICAL MEDICAL EMERGENCY REQUIRING IMMEDIATE HOSPITAL EMERGENCY RESUSCITATION AND NEUROSURGICAL EVALUATION."],
        "specialty": "Neurology / Neurosurgery / Emergency Medicine",
        "sources": [
            {"name": "American Stroke Association - Hemorrhagic Stroke", "url": "https://www.stroke.org/en/about-stroke/types-of-stroke/hemorrhagic-strokes-bleeds"},
            {"name": "NHS UK - Stroke", "url": "https://www.nhs.uk/conditions/stroke/"}
        ]
    },
    "Peptic ulcer diseae": {
        "title": "Peptic Ulcer Disease",
        "slug": "peptic-ulcer-disease",
        "description": "Peptic ulcer disease is a condition characterized by painful open sores (ulcers) that develop on the inner mucosal lining of the stomach (gastric ulcer) or the upper small intestine (duodenal ulcer).",
        "symptoms": ["Burning stomach pain located between navel and breastbone", "Pain temporarily improved by eating or taking antacids (especially duodenal)", "Bloating, belching, and feeling full quickly", "Nausea"],
        "causes": ["Infection with Helicobacter pylori bacteria", "Long-term, frequent use of Nonsteroidal Anti-inflammatory Drugs (NSAIDs: ibuprofen, naproxen, aspirin)"],
        "prevention": ["Avoid regular unprescribed NSAID use; discuss gastroprotective co-prescription (PPIs) with your doctor", "Quit smoking and moderate alcohol intake", "Practice good food hygiene to avoid H. pylori transmission"],
        "self_care": ["Complete prescribed antibiotic eradication regimens and proton pump inhibitors (PPIs) exactly as directed", "Avoid caffeine, alcohol, and spicy foods that aggravate symptoms"],
        "warning_signs": ["Vomiting red blood or material resembling dark coffee grounds", "Dark, sticky, tarry stools (melena - signs of internal gastrointestinal hemorrhage)", "Sudden, sharp, agonizing abdominal pain (gastric perforation - emergency)"],
        "specialty": "Gastroenterology",
        "sources": [
            {"name": "NIH NIDDK - Peptic Ulcers (Stomach Ulcers)", "url": "https://www.niddk.nih.gov/health-information/digestive-diseases/peptic-ulcers-stomach-ulcers"},
            {"name": "NHS UK - Stomach ulcer", "url": "https://www.nhs.uk/conditions/stomach-ulcer/"}
        ]
    },
    "Pneumonia": {
        "title": "Pneumonia",
        "slug": "pneumonia",
        "description": "Pneumonia is an acute inflammatory infection of one or both lungs that causes the microscopic air sacs (alveoli) to fill with inflammatory exudate and fluid.",
        "symptoms": ["Cough productive of greenish, yellow, or rust-colored phlegm", "High fever, sweating, and shaking chills", "Sharp, stabbing chest pain on deep inspiration or coughing (pleuritic pain)", "Shortness of breath and rapid breathing", "Fatigue"],
        "causes": ["Bacterial infection (Streptococcus pneumoniae)", "Viral pathogens (Influenza, RSV, SARS-CoV-2)", "Aspiration of foreign material"],
        "prevention": ["Pneumococcal and annual influenza vaccinations", "Quit smoking to restore pulmonary ciliary defense", "Proper oral hygiene"],
        "self_care": ["Complete the entire course of prescribed antibiotics or antivirals", "Drink plenty of warm liquids to thin secretions", "Get plenty of rest and avoid exertion until cleared"],
        "warning_signs": ["Severe shortness of breath or persistent chest pain", "Confusion or disorientation (especially in elderly patients)", "Cyanosis (bluish tint to lips or nailbeds - emergency)"],
        "specialty": "Pulmonology / Internal Medicine",
        "sources": [
            {"name": "CDC - Pneumonia", "url": "https://www.cdc.gov/pneumonia/index.html"},
            {"name": "NHS UK - Pneumonia", "url": "https://www.nhs.uk/conditions/pneumonia/"}
        ]
    },
    "Psoriasis": {
        "title": "Psoriasis",
        "slug": "psoriasis",
        "description": "Psoriasis is a chronic, non-contagious autoimmune skin disease that accelerates the lifecycle of skin cells, leading to thick, red patches covered with silvery scales.",
        "symptoms": ["Red patches of skin covered with thick, silvery scales (plaques)", "Dry, cracked skin that may itch or bleed", "Burning or soreness", "Pitted, discolored, or thickened nails", "Stiff, swollen joints (psoriatic arthritis)"],
        "causes": ["T-cell mediated autoimmune dysregulation causing rapid keratinocyte hyperproliferation, triggered by stress, skin injury, infections, and cold weather"],
        "prevention": ["Keep skin moisturized daily", "Avoid known individual triggers: stress, alcohol, smoking, skin lacerations (Koebner phenomenon)"],
        "self_care": ["Apply fragrance-free thick emollients immediately after bathing", "Take warm baths with colloidal oatmeal or Epsom salts", "Careful, brief natural sunlight exposure under clinical guidance"],
        "warning_signs": ["Widespread bright redness and shedding skin over large parts of the body with fever (erythrodermic psoriasis - medical emergency)", "Severe joint pain and morning stiffness"],
        "specialty": "Dermatology",
        "sources": [
            {"name": "National Psoriasis Foundation", "url": "https://www.psoriasis.org/"},
            {"name": "NHS UK - Psoriasis", "url": "https://www.nhs.uk/conditions/psoriasis/"}
        ]
    },
    "Tuberculosis": {
        "title": "Tuberculosis (TB)",
        "slug": "tuberculosis",
        "description": "Tuberculosis is a contagious, potentially severe bacterial infection primarily affecting the lungs (pulmonary TB), though it can spread to bones, lymph nodes, and kidneys.",
        "symptoms": ["Persistent cough lasting 3 weeks or longer", "Coughing up blood (hemoptysis) or sputum", "Drenching night sweats", "Unintentional weight loss and loss of appetite", "Low-grade fever and chest pain"],
        "causes": ["Mycobacterium tuberculosis transmitted through airborne droplet nuclei generated when an active pulmonary TB patient coughs or speaks"],
        "prevention": ["Bacille Calmette-Guérin (BCG) vaccination in endemic regions", "Ensure well-ventilated indoor spaces", "Screening and treatment of latent TB infections"],
        "self_care": ["Strict, uninterrupted adherence to the 6 to 9 month multidrug regimen (Rifampin, Isoniazid, Pyrazinamide, Ethambutol) to prevent antibiotic resistance", "Wear appropriate N95 masks while active"],
        "warning_signs": ["Massive hemoptysis (coughing up large volumes of blood)", "Severe respiratory distress or high persistent fever"],
        "specialty": "Pulmonology / Infectious Disease",
        "sources": [
            {"name": "WHO - Tuberculosis Fact Sheet", "url": "https://www.who.int/news-room/fact-sheets/detail/tuberculosis"},
            {"name": "CDC - Tuberculosis (TB)", "url": "https://www.cdc.gov/tb/index.html"}
        ]
    },
    "Typhoid": {
        "title": "Typhoid Fever",
        "slug": "typhoid",
        "description": "Typhoid fever is a life-threatening systemic bacterial infection spread through contaminated food and water, causing sustained high fever, abdominal symptoms, and severe fatigue.",
        "symptoms": ["Step-ladder rising fever reaching 104°F (40°C)", "Severe headache and general body malaise", "Abdominal pain, constipation early on or 'pea-soup' diarrhea later", "Faint rose-colored spots on chest and abdomen", "Enlarged spleen and liver"],
        "causes": ["Salmonella enterica serotype Typhi (S. Typhi) transmitted through the fecal-oral route via contaminated food or water supplies"],
        "prevention": ["Typhoid vaccination prior to traveling to high-incidence regions", "Drink only bottled, boiled, or chemically treated water", "'Boil it, cook it, peel it, or forget it' rule for food"],
        "self_care": ["Immediate diagnosis via blood culture and completion of prescribed antibiotics", "Adequate oral fluid and electrolyte rehydration", "Strict handwashing to prevent spreading to household contacts"],
        "warning_signs": ["Sudden acute severe abdominal pain with rigidity (intestinal perforation - surgical emergency)", "Delirium, confusion, or severe intestinal hemorrhage"],
        "specialty": "Infectious Disease / Tropical Medicine",
        "sources": [
            {"name": "WHO - Typhoid", "url": "https://www.who.int/news-room/fact-sheets/detail/typhoid"},
            {"name": "CDC - Typhoid Fever", "url": "https://www.cdc.gov/typhoid-fever/index.html"}
        ]
    },
    "Urinary tract infection": {
        "title": "Urinary Tract Infection (UTI)",
        "slug": "urinary-tract-infection",
        "description": "A urinary tract infection is an infection involving any part of the urinary system, most commonly the lower urinary tract (bladder and urethra - cystitis).",
        "symptoms": ["Strong, persistent urge to urinate", "Burning sensation or pain when urinating (dysuria)", "Passing frequent, small amounts of urine", "Cloudy, dark, or strong-smelling urine", "Pelvic pain in women"],
        "causes": ["Escherichia coli bacteria (responsible for ~80-90% of cases) originating from the gastrointestinal tract entering the urethra"],
        "prevention": ["Drink plenty of water to flush urinary pathways", "Wipe from front to back after using the toilet", "Urinate promptly after sexual intercourse", "Avoid irritating feminine sprays and douches"],
        "self_care": ["Complete prescribed antibiotic treatment course even if symptoms resolve early", "Increase fluid intake", "Heating pad on abdomen for pelvic discomfort", "Avoid caffeine, alcohol, and spicy foods that irritate the bladder"],
        "warning_signs": ["High fever, shaking chills, and pain in the flank or lower back (signs of acute pyelonephritis / kidney infection requiring prompt medical care)", "Nausea and vomiting"],
        "specialty": "Urology / Nephrology / Primary Care",
        "sources": [
            {"name": "CDC - Urinary Tract Infection", "url": "https://www.cdc.gov/antibiotic-use/uti.html"},
            {"name": "NHS UK - Urinary tract infections (UTIs)", "url": "https://www.nhs.uk/conditions/urinary-tract-infections-utis/"}
        ]
    },
    "Varicose veins": {
        "title": "Varicose Veins",
        "slug": "varicose-veins",
        "description": "Varicose veins are twisted, enlarged superficial veins, most commonly occurring in the legs and feet, caused by incompetent venous valves and venous hypertension.",
        "symptoms": ["Veins that are dark purple or blue and appear twisted and bulging", "Aching, heavy feeling in the legs", "Burning, throbbing, muscle cramping, and swelling in lower legs", "Worsened pain after prolonged sitting or standing", "Itching around affected veins"],
        "causes": ["Weak or damaged one-way vein valves allowing blood to pool backwards (venous reflux); prolonged standing, genetics, pregnancy, obesity"],
        "prevention": ["Exercise regularly to improve calf muscle pump function", "Avoid prolonged standing or sitting without leg movement breaks", "Maintain healthy weight"],
        "self_care": ["Wear medical-grade graduated compression stockings", "Elevate legs above the level of your heart for 15 minutes several times daily", "Avoid tight clothing around the waist or groin"],
        "warning_signs": ["Sudden painful swelling and redness in one leg (deep vein thrombosis - DVT)", "Open skin ulcers near the ankle", "Heavy bleeding from a ruptured varicose vein (elevate and apply firm pressure)"],
        "specialty": "Vascular Surgery / Phlebology",
        "sources": [
            {"name": "NHS UK - Varicose veins", "url": "https://www.nhs.uk/conditions/varicose-veins/"},
            {"name": "MedlinePlus - Varicose Veins", "url": "https://medlineplus.gov/varicoseveins.html"}
        ]
    },
    "hepatitis A": {
        "title": "Hepatitis A",
        "slug": "hepatitis-a",
        "description": "Hepatitis A is a highly contagious, short-term liver infection caused by the Hepatitis A virus, typically spread through ingestion of contaminated food or water.",
        "symptoms": ["Fatigue and sudden nausea/vomiting", "Abdominal pain or discomfort, especially in upper right side under ribs", "Loss of appetite", "Low-grade fever", "Dark urine and pale stools", "Jaundice (yellow skin/eyes)"],
        "causes": ["Hepatitis A virus (HAV) transmitted via the fecal-oral route when an uninfected person consumes contaminated food or water"],
        "prevention": ["Hepatitis A vaccination (two doses provide long-lasting immunity)", "Thorough handwashing with soap after using the toilet and before preparing food", "Avoid drinking untreated water or eating raw shellfish in areas with poor sanitation"],
        "self_care": ["Most people recover fully with no permanent liver damage: rest, hydration, and nutritious diet", "Avoid alcohol completely during recovery and for months afterwards to protect the liver"],
        "warning_signs": ["Severe persistent vomiting causing dehydration", "Extreme lethargy, confusion, or bleeding tendencies (acute liver failure - rare but critical)"],
        "specialty": "Infectious Disease / Gastroenterology",
        "sources": [
            {"name": "WHO - Hepatitis A", "url": "https://www.who.int/news-room/fact-sheets/detail/hepatitis-a"},
            {"name": "CDC - Hepatitis A Questions and Answers", "url": "https://www.cdc.gov/hepatitis/hav/afaq.htm"}
        ]
    }
}

class HealthDataService:
    @staticmethod
    def get_all_conditions():
        """Return a sorted list of all supported conditions."""
        return [
            {
                "model_key": key,
                "title": data["title"],
                "slug": data["slug"],
                "description": data["description"],
                "specialty": data["specialty"]
            }
            for key, data in sorted(CONDITIONS_DATA.items(), key=lambda x: x[1]["title"])
        ]

    @staticmethod
    def get_condition_by_key(model_key):
        """Retrieve condition by its exact model class key."""
        return CONDITIONS_DATA.get(model_key)

    @staticmethod
    def get_condition_by_slug(slug):
        """Retrieve condition by its URL slug."""
        for key, data in CONDITIONS_DATA.items():
            if data["slug"] == slug:
                # Attach the original model key
                res = dict(data)
                res["model_key"] = key
                return res
        return None

    @staticmethod
    def search_conditions(query):
        """Search conditions by query string matching title, description, or symptoms."""
        q = (query or "").lower().strip()
        if not q:
            return HealthDataService.get_all_conditions()
        
        matches = []
        for key, data in CONDITIONS_DATA.items():
            if (
                q in data["title"].lower()
                or q in data["description"].lower()
                or any(q in s.lower() for s in data["symptoms"])
                or q in data["specialty"].lower()
            ):
                matches.append({
                    "model_key": key,
                    "title": data["title"],
                    "slug": data["slug"],
                    "description": data["description"],
                    "specialty": data["specialty"]
                })
        return sorted(matches, key=lambda x: x["title"])

    @staticmethod
    def is_emergency_condition(disease_name):
        """Identify critical red-flag conditions requiring immediate emergency triage."""
        emergency_names = {
            "Heart attack",
            "Paralysis (brain hemorrhage)",
            "Hypoglycemia"
        }
        return disease_name in emergency_names

health_service = HealthDataService()
