#  © 2018 - 2021 Schneider Electric Industries SAS. All rights reserved.

import json
import xml.etree.ElementTree as ET

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import gridspec
from scipy.io import loadmat

import efoc
import time


# Script used to create the microapp call example
xml_file = "data/microapp/config_microapp.xml"
efoc_instance = efoc.api.create_energy_manager(xml_file)

profiles = loadmat("data/microapp/load_pv_microapp.mat")
t_step = efoc_instance.control_params.sample_period
n_samples = efoc_instance.control_params.nbr_time_step
current_date_time = pd.Timestamp("2018-4-1 00:00:00")
initial_threshold = 0

measures_time_index = pd.date_range(start=current_date_time, freq=str(int(t_step / 60)) + "min", periods=1)
measures = pd.DataFrame(index=measures_time_index, columns=[])
measures["energy_hub_battery_soc"] = 0
# measures['dcm_contract_power'] = initial_threshold

measures["contract_offpeak_threshold"] = 0
measures["contract_midpeak_threshold"] = 0
measures["contract_onpeak_threshold"] = 0
threshold = 220
measures["contract_non_coincidental_threshold"] = threshold

forecasts_time_index = pd.date_range(start=current_date_time, freq=str(int(t_step / 60)) + "min", periods=n_samples)
forecasts = pd.DataFrame(index=forecasts_time_index, columns=[])
forecasts["energy_hub_building_power"] = profiles["loadProfile2"]
forecasts["energy_hub_pv_power"] = -0.75 * profiles["pvProfile2"]

forecasts["energy_hub_pv_power"] = forecasts["energy_hub_pv_power"].shift(-8, freq=str(int(t_step / 60)) + "min")
forecasts["energy_hub_pv_power"] = forecasts["energy_hub_pv_power"].fillna(0)

forecasts["contract_tou_buy"] = [0.02] * 5 * 4 + [0.025] * 8 * 4 + [0.030] * 2 * 4 + [0.025] * 6 * 4 + [0.02] * 3 * 4
forecasts["contract_tou_sell"] = [0] * n_samples
start = time.time()
setpoints, solver_info = efoc.api.solve_control_problem(
    current_date_time=current_date_time, measures=measures, forecasts=forecasts, energymanager=efoc_instance
)
end =time.time()
flag_plot = True
if flag_plot:
    plt.figure()
    gs = gridspec.GridSpec(4, 1, height_ratios=[2, 1, 1, 1])

    axs_a_0 = plt.subplot(gs[0])
    axs_a_0.plot(setpoints["energy_hub_elec_ext_power"], label="grid")
    axs_a_0.plot(forecasts["energy_hub_building_power"], label="building")
    axs_a_0.plot(setpoints["energy_hub_pv_power_produced"], label="pv")
    axs_a_0.plot(setpoints["energy_hub_battery_power"], label="battery")
    axs_a_0.axhline(y=threshold, color="red", linestyle="--")
    axs_a_0.axhline(y=0, color="grey", linestyle="--")
    axs_a_0.legend(bbox_to_anchor=(1.01, 1), loc=2, borderaxespad=0)
    axs_a_0.grid()

    axs_a_4 = plt.subplot(gs[3], sharex=axs_a_0)
    axs_a_4.plot(
        forecasts["energy_hub_building_power"] + setpoints["energy_hub_pv_power_produced"], label="building+pv"
    )
    axs_a_4.axhline(y=0, color="grey", linestyle="--")
    axs_a_4.axhline(y=threshold, color="red", linestyle="--")
    axs_a_4.legend(bbox_to_anchor=(1.01, 1), loc=2, borderaxespad=0)
    axs_a_4.grid()

    axs_a_1 = plt.subplot(gs[1], sharex=axs_a_0)
    axs_a_1.plot(setpoints["energy_hub_battery_soc"], label="soc")
    axs_a_1.legend(bbox_to_anchor=(1.01, 1), loc=2, borderaxespad=0)
    axs_a_1.grid()

    axs_a_2 = plt.subplot(gs[2], sharex=axs_a_0)
    axs_a_2.plot(
        setpoints.index,
        [
            efoc_instance.contracts["contract"].control_model.tou_price_buy[i].value * (3600 / t_step)
            for i in range(n_samples)
        ],
        label="buy_price",
    )
    axs_a_2.legend(bbox_to_anchor=(1.01, 1), loc=2, borderaxespad=0)
    axs_a_2.grid()

    plt.show()

# Web service
flag_json = False
if flag_json:
    forecasts["datetime"] = forecasts.index.strftime("%Y-%m-%dT%H:%M:%S")
    forecasts["energy_hub_pv_power"] *= -1
    forecasts = str(forecasts.to_dict(orient="records"))

    measures["datetime"] = measures.index.strftime("%Y-%m-%dT%H:%M:%S")
    measures = str(measures.to_dict(orient="records"))

    tree = ET.parse(xml_file)
    root = tree.getroot()
    xml = ET.tostring(root, encoding="unicode")
    xml = xml.replace("\n", "").replace("\t", "")

    web_service_input = {
        "GlobalParameters": {},
        "Inputs": {
            "config": [{"xml_file_header": xml}],
            "forecast": [{"forecast_header": forecasts}],
            "measure": [{"measure_header": measures}],
        },
    }

    with open("data/microapp/efoc_microapp.json", "w") as fp:
        json.dump(web_service_input, fp)


print("---------"+str(end-start)+" seconds of execution by Intel Core i7-10850 ----------")
res=(end-start)*259.2
print("    - Estimated number of operation is "+str(res)+" Gflop")