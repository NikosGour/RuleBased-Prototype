"""
Copyright © 2024 Nikos Gournakis
All rights reserved
"""

import json5
import uvicorn

from utils import *

# @formatter:off
# TODO: Add more items
intervention_library = {"Twitter_Post_About_Quiting_Smoking": {"beh": ["cease_smoking"], "stg": [1,2,3], "opr": "max"},
                        "Youtube_Video_About_Quiting_Smoking": {"beh": ["cease_smoking"], "stg": [2,3], "opr": "max"},
                        "News_Article_About_Diet_And_Exercise": {"beh": ["improve_diet_quality", "increase_physical_activity"], "stg": [2, 3], "opr": "min"},
                        "Facebook_Post_About_Getting_Better_Sleep": {"beh": ["improve_sleep_quality"], "stg": [4,5], "opr": "max"},
                        "Instagram_Reel_About_Reducing_Alcohol_Intake": {"beh": ["reduce_alcohol_consumption"], "stg": [2,3,4], "opr": "max"},
                        "TikTok_About_Reducing_Alcohol_Intake": {"beh": ["reduce_alcohol_consumption"], "stg": [5], "opr": "max"},
                        "Youtube_Short_About_Quiting_Smoking": {"beh": ["cease_smoking"], "stg": [1,2], "opr": "max"},
                        "Youtube_Video_About_Improving_Life_Quality": {"beh": ["cease_smoking","reduce_alcohol_consumption","improve_diet_quality","increase_physical_activity","improve_sleep_quality"], "stg": [1,2,3], "opr": "min"},}
# @formatter:on

def get_recommendations(user_profile) -> dict:
    # with open("example_patient.json", "r") as read_file:
    #     user_profile = json5.load(read_file)
    user_profile = infer_integrated_data_layer(user_profile)
    with open("example_patient_integrated.json", "w") as write_file:
        json5.dump(user_profile, write_file, indent=4, quote_keys=True)
    user_profile = infer_aggregated_data_layer(user_profile)
    with open("example_patient_aggregated.json", "w") as write_file:
        json5.dump(user_profile, write_file, indent=4, quote_keys=True)
    user_profile = {k: [min_max_transform(v[0], 1, 5), v[1]]
                    for k, v in user_profile.items()}
    sim_needs = sim_need(user_profile, intervention_library)
    sim_stages = sim_stage(user_profile, intervention_library)
    sim_totals = sim_total(sim_needs, sim_stages)
    # print(f"Similarity Needs: {sim_needs}")
    # print("-" * 50)
    # print(f"Similarity Stages: {sim_stages}")
    # print("-" * 50)
    # print(f"Similarity Totals: {sim_totals}")
    # print("-" * 50)

    sim_totals_filtered = {k: v for k, v in sim_totals.items() if v >= 0.5}
    # print(f"Similarity Totals Filtered (if value >= 0.5): {sim_totals_filtered}")
    # print("-" * 50)

    sim_total_ordered = dict(sorted(sim_totals_filtered.items(), key=lambda x: x[1], reverse=True))
    # print(f"Similarity Totals Filtered and Ordered: {sim_total_ordered}")
    return sim_total_ordered


# with open("example_patient.json", "r") as read_file:
#     user_profile = json5.load(read_file)
#
#     user_profile = infer_integrated_data_layer(user_profile)
#     with open("example_patient_integrated.json", "w") as write_file:
#         json5.dump(user_profile, write_file, indent=4, quote_keys=True)
#     print(json5.dumps(user_profile, indent=4, quote_keys=True))

from fastapi import FastAPI, Request

app = FastAPI()


@app.post("/")
async def root(item: Request):
    user_profile = await item.json()
    print(f"User Profile: {user_profile}")
    # Integrated Data Layer
    user_profile = infer_integrated_data_layer(user_profile)
    with open("example_patient_integrated.json", "w") as write_file:
        json5.dump(user_profile, write_file, indent=4, quote_keys=True)
    print(f"Integrated Data Layer: {user_profile}")
    # Aggregated Data Layer
    user_profile = infer_aggregated_data_layer(user_profile)
    with open("example_patient_aggregated.json", "w") as write_file:
        json5.dump(user_profile, write_file, indent=4, quote_keys=True)
    print(f"Aggregated Data Layer: {user_profile}")
    # TTM stages
    user_profile = add_ttm_stages(user_profile)
    with open("example_patient_ttm.json", "w") as write_file:
        json5.dump(user_profile, write_file, indent=4, quote_keys=True)
    print(f"TTM Stages: {user_profile}")
    # Similarity Needs
    user_profile = {k: {"str": min_max_transform(v["str"], 1, 5), "stg": v["stg"]}
                    for k, v in user_profile.items()}
    sim_needs = sim_need(user_profile, intervention_library)
    sim_stages = sim_stage(user_profile, intervention_library)
    sim_totals = sim_total(sim_needs, sim_stages)
    sim_totals_filtered = {k: v for k, v in sim_totals.items() if v >= 0.5}
    sim_total_ordered = dict(sorted(sim_totals_filtered.items(), key=lambda x: x[1], reverse=True))
    return sim_total_ordered


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)