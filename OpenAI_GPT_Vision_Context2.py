import base64
import csv
import json
import os
from openai import OpenAI

client = OpenAI()

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def process_response(response):
    json_string = response.output_text
    json_string = json_string.replace("```json\n", "").replace("\n```", "")
    json_data = json.loads(json_string)

    #filename_without_extension = os.path.splitext(os.path.basename(urlparse(base64_img).path))[0] #for URL image
    filename_without_extension = os.path.splitext(os.path.basename(context_image_local))[0] #for local image

    json_filename = f"{filename_without_extension}.json"

    json_data = json.loads(json_string)

    site_id = os.path.splitext(context_image_local)[0]

    append_quadrat_to_csv(json_data, site_id + '2')


# path to image
image = "CS01_HIGH0_21JULY2022_red2"
crop_image_local = image + "_cropped"
crop_image_path = f"./Data/Cropped/{crop_image_local}.jpg"

context_image_local = image + "_context"
context_image_path = f"./Data/Context/{context_image_local}.jpg"

# Getting the Base64 string
crop_base64_image = encode_image(crop_image_path)
context_base64_image = encode_image(context_image_path)

SPECIES = [
    "Spartina alterniflora (Smooth Cordgrass)",
    "Juncus roemerianus (Black Needle Rush)",
    "Bolboschoenus robustus (Salt Marsh Bulrush)",
    "Iva frutescens (Marsh Elder)",
    "Panicum virgatum (Switch Grass)",
    "Spartina patens (Salt Meadow Hay)",
    "Spartina cynosuroides (Big Cordgrass)",
    "Borrichia frutescens (Sea Oxeye)",
    "Salicornia spp. (Glasswort)",
    "Kosteletzkya virginica (Marsh Mallow)",
    "Hibiscus moscheutos (Marsh Hibiscus)",
    "Solidago sempervirens (Seaside Goldenrod)",
    "Distichlis spicata (Salt Grass)",
    "Limonium carolinianum (Sea Lavender)",
    "Symphyotrichum tenuifolium (Salt Marsh Aster)",
    "Atriplex patula (Marsh Orach)",
    "Phragmites australis (Phragmites or Reed Grass)",
    "Baccharis halimifolia (Groundsel Tree)",
    "Dead Organic Matter",
    "Bare Ground",
]

OTHER_SPECIES = [
    "Oysters",
    "Mussels",
    "Crab Burrows",
    "Periwinkles",
]

def append_quadrat_to_csv(json_data, site_id, csv_path="quadrat_data.csv"):
    file_exists = os.path.exists(csv_path)

    row = {"site": site_id}

    for species in SPECIES:
        pct_key = f"{species}_pct"
        conf_key = f"{species}_conf"

        if species in json_data:
            row[pct_key] = json_data[species]["percent cover"]
            row[conf_key] = json_data[species]["confidence"]
        else:
            row[pct_key] = 0
            row[conf_key] = 0

    for other_species in OTHER_SPECIES:
        count_key = f"{other_species}_ct"
        conf_key = f"{other_species}_conf"

        if other_species in json_data:
            row[count_key] = json_data[other_species]["count"]
            row[conf_key] = json_data[other_species]["confidence"]
        else:
            row[count_key] = 0
            row[conf_key] = 0


    row["Total_Confidence"] = json_data.get("Total Confidence", "")
    row["Notes"] = json_data.get("notes", "")

    fieldnames = ["site"]
    for species in SPECIES:
        fieldnames.append(f"{species}_pct")
        fieldnames.append(f"{species}_conf")
    for other_species in OTHER_SPECIES:
        fieldnames.append(f"{other_species}_ct")
        fieldnames.append(f"{other_species}_conf")
    fieldnames += ["Total_Confidence", "Notes"]

    with open(csv_path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        writer.writerow(row)


context = ("You are an ecology field assistant trained in quadrat-based land cover estimation on coastal lands in Southeastern Virginia."
           "You are given TWO images of the same quadrat:"
           "1) A cropped image containing ONLY the area inside the quadrat."
           "2) A context image of the full scene with the quadrat outlined in red."
           ""
           "Task:"
           "- First, determine which species are present INSIDE the quadrat using both images for identification."
           "- Then, estimate percent cover by projected area using ONLY the cropped image."
           ""
           "Rules:"
           "- ONLY pixels within the cropped image may be used to estimate percent cover."
           "- The context image may ONLY be used to help identify species types."
           "- Percent cover must sum to exactly 100."
           "- Ignore shadows and the quadrat frame."
           "- Only count plants whose base is (or can reasonably be inferred to be) inside the quadrat."
           "- For oysters, mussels, crab burrows, and periwinkles, provide COUNTS (not percent cover). These will only appear on bare ground or dead organic matter."
           "- If uncertain, choose the closest reasonable estimate."
           ""
           "Spartina alterniflora has thicker, darker green blades and usually forms denser, upright stands. Spartina patens has finer, lighter-colored, and often wiry/matted blades."
           "Spartina alterniflora and Spartina patens may co-occur in the same site but typically one dominates if present."
           ""
           "Return ONLY valid JSON in this schema:"
           "{"
           "Spartina alterniflora (Smooth Cordgrass): {percent cover, confidence}"
           "Juncus roemerianus (Black Needle Rush): {percent cover, confidence}"
           "Bolboschoenus robustus (Salt Marsh Bulrush): {percent cover, confidence}"
           "Iva frutescens (Marsh Elder): {percent cover, confidence}"
           "Panicum virgatum (Switch Grass): {percent cover, confidence}"
           "Spartina patens (Salt Meadow Hay): {percent cover, confidence}"
           "Spartina cynosuroides (Big Cordgrass): {percent cover, confidence}"
           "Borrichia frutescens (Sea Oxeye): {percent cover, confidence}"
           "Salicornia spp. (Glasswort): {percent cover, confidence}"
           "Kosteletzkya virginica (Marsh Mallow): {percent cover, confidence}"
           "Hibiscus moscheutos (Marsh Hibiscus): {percent cover, confidence}"
           "Solidago sempervirens (Seaside Goldenrod): {percent cover, confidence}"
           "Distichlis spicata (Salt Grass): {percent cover, confidence}"
           "Limonium carolinianum (Sea Lavender): {percent cover, confidence}"
           "Symphyotrichum tenuifolium (Salt Marsh Aster): {percent cover, confidence}"
           "Atriplex patula (Marsh Orach): {percent cover, confidence}"
           "Phragmites australis (Phragmites or Reed Grass): {percent cover, confidence}"
           "Baccharis halimifolia (Groundsel Tree): {percent cover, confidence}"
           "Dead Organic Matter: {percent cover, confidence}"
           "Bare Ground: {percent cover, confidence}"
           "Oysters: {count, confidence}"
           "Mussels: {count, confidence}"
           "Crab Burrows: {count, confidence}"
           "Periwinkles: {count, confidence}"
           "Total Confidence: percent"
           "notes: short explanation"
           "}")

response = client.responses.create(
    model="gpt-5-mini",
    input=[
        {
            "role": "user",
            "content": [
                { "type": "input_text",
                  "text": context },
                {
                    "type": "input_image",
                    "image_url": f"data:image/jpeg;base64,{crop_base64_image}",
                },
                {
                    "type": "input_image",
                    "image_url": f"data:image/jpeg;base64,{context_base64_image}",
                }
            ],
        }
    ],
)

print(response.output_text)
process_response(response)