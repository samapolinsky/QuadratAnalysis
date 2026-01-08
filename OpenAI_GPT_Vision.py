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
    filename_without_extension = os.path.splitext(os.path.basename(image_local))[0] #for local image

    json_filename = f"{filename_without_extension}.json"
    json_data = json.loads(json_string)
    site_id = os.path.splitext(image_local)[0]

    append_quadrat_to_csv(json_data, site_id)


# path to image
image_local ="CS01_HIGH0_21JULY2022_red2" + "_cropped"
image_path = f"./Data/Cropped/{image_local}.jpg"

# Getting the Base64 string
base64_image = encode_image(image_path)

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
           "Given a photo of a vegetation quadrat:"
           "- Estimate percent cover by projected area of the image."
           "- Use the following classes: Spartina alterniflora (Smooth Cordgrass), Juncus roemerianus (Black Needle Rush), Bolboschoenus robustus (Salt Marsh Bulrush), Iva frutescens (Marsh Elder), Panicum virgatum (Switch Grass), Spartina patens (Salt Meadow Hay), Spartina cynosuroides (Big Cordgrass), Borrichia frutescens (Sea Oxeye), Salicornia spp. (Glasswort), Kosteletzkya virginica (Marsh Mallow), Hibiscus moscheutos (Marsh Hibiscus), Solidago sempervirens (Seaside Goldenrod), Distichlis spicata (Salt Grass), Limonium carolinianum (Sea Lavender), Symphyotrichum tenuifolium (Salt Marsh Aster), Atriplex patula (Marsh Orach), Phragmites australis (Phragmites or Reed Grass), Baccharis halimifolia (Groundsel Tree), Dead Organic Matter, Bare Ground, and the counts of oysters, mussels, crab burrows, and periwinkles."
           "- Spartina alterniflora and Spartina patens are usually the most common. They are sometimes found together, but usually not. Spartina alterniflora is green, thicker grass leaves. Spartina patens is thinner and lighter"
           "- For oysters, mussels, crab burrows, and periwinkles counts, they will only be visible atop bare ground or DOM. Give the counts of those."
           "- Percent cover must sum to 100"
           "- Ignore shadows and quadrat frame"
           "- Only count plants whose base is (or can be inferred to be) within the square quadrat"
           "- If uncertain, choose the closest reasonable estimate"
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
more_context = (
    "Expected species types:"
    "Bare ground vs. dead leaves: "
    "What to do if a plant whose root is not in the quadrat spans part of the quadrat"
    ""
)

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
                    "image_url": f"data:image/jpeg;base64,{base64_image}",
                },
            ],
        }
    ],
)

print(response.output_text)
process_response(response)