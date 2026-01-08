import base64
import csv
import json
import os

import cv2
import numpy as np
from openai import OpenAI

client = OpenAI()

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


def encode_image_from_array(img, ext=".jpg"):
    success, buffer = cv2.imencode(ext, img)
    if not success:
        raise RuntimeError("Image encoding failed")
    return base64.b64encode(buffer).decode("utf-8")

def append_quadrat_to_csv(json_data, site_id, csv_path="quadrat_data.csv"):
    file_exists = os.path.exists(csv_path)

    row = {"site": site_id}
    row_to_ret = {"site": site_id}

    for species in SPECIES:
        pct_key = f"{species}_pct"
        conf_key = f"{species}_conf"

        if species in json_data:
            row[pct_key] = json_data[species]["percent cover"]
            row[conf_key] = json_data[species]["confidence"]
            row_to_ret[pct_key] = json_data[species]["percent cover"]
            row_to_ret[conf_key] = json_data[species]["confidence"]
        else:
            row[pct_key] = 0
            row[conf_key] = 0

    for other_species in OTHER_SPECIES:
        count_key = f"{other_species}_ct"
        conf_key = f"{other_species}_conf"

        if other_species in json_data:
            row[count_key] = json_data[other_species]["count"]
            row[conf_key] = json_data[other_species]["confidence"]
            row_to_ret[count_key] = json_data[other_species]["count"]
            row_to_ret[conf_key] = json_data[other_species]["confidence"]
        else:
            row[count_key] = 0
            row[conf_key] = 0


    row["Total_Confidence"] = json_data.get("Total Confidence", "")
    row["Notes"] = json_data.get("notes", "")
    row_to_ret["Total_Confidence"] = json_data.get("Total Confidence", "")
    row_to_ret["Notes"] = json_data.get("notes", "")

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

    return_list = []
    for species in SPECIES:
        pct_key = f"{species}_pct"
        conf_key = f"{species}_conf"
        if row_to_ret[pct_key] != 0:
            return_list.append(f"{species}: {row_to_ret[pct_key]}%, Confidence: {row_to_ret[conf_key]}")

    for other_species in OTHER_SPECIES:
        ct_key = f"{other_species}_ct"
        conf_key = f"{other_species}_conf"
        if row_to_ret[ct_key] != 0:
            return_list.append(f"{other_species}: {row_to_ret[ct_key]}, Confidence: {row_to_ret[conf_key]}")

    return_list.append(f"Total Confidence: {row_to_ret["Total_Confidence"]}")
    return_list.append(f"Notes: {row_to_ret["Notes"]}")

    return {
        "row_data": row_to_ret,   # raw data
        "display_list": return_list  # easy to render on frontend
    }

def process_response(response, site_id):
    if not response.output_text:
        raise RuntimeError("Model returned no text output")

    json_string = response.output_text.strip()
    json_string = json_string.replace("```json", "").replace("```", "").strip()

    json_data = json.loads(json_string)

    return append_quadrat_to_csv(json_data, site_id)

def get_images_from_crop(cropped_bytes, context_bytes, site_id):
    cropped_img = cv2.imdecode(
        np.frombuffer(cropped_bytes, np.uint8),
        cv2.IMREAD_COLOR
    )
    context_img = cv2.imdecode(
        np.frombuffer(context_bytes, np.uint8),
        cv2.IMREAD_COLOR
    )

    crop_base64 = encode_image_from_array(cropped_img)
    context_base64 = encode_image_from_array(context_img)

    response = client.responses.create(
        model="gpt-5-mini",
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": context
                    },
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{crop_base64}"
                    },
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{context_base64}"
                    }
                ],
            }
        ],
    )

    return process_response(response, site_id)