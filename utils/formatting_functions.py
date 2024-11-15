import pandas as pd
import statistics as s
import plotly.graph_objects as go
import numpy as np
from datetime import datetime as dt
from datetime import timedelta as td
import datetime
import statistics
import os
import pickle as pkl

## TODO Rewrite all of this: This is very old code, some of it is inefficient

def RC(barcode):
    if str(barcode).lower().startswith("si"):
        return barcode
    if type(barcode) != type(0.123325):
        BC = str(barcode).lower()[::-1].strip()

        associations = {"a":"T",
                        "t":"A",
                        "c":"G",
                        "g":"C"}
        newstring = ""

        for character in BC:
            try:
                newstring += associations[character]
            except:
                continue
        return newstring
    else:
        return barcode

def RS(barcode):
    if str(barcode).lower().startswith("si"):
        return barcode
    if type(barcode) != type(0.1233237435612354347451235):
        BC = str(barcode).lower()[::-1].strip()
        associations = {"a":"A",
                        "t":"T",
                        "c":"C",
                        "g":"G"}
        newstring = ""
        for character in BC:
            try:
                newstring += associations[character]
            except:
                continue
        return newstring
    else:
        return barcode

def gre(order_number, B):

    bc1s = []
    bc2s = []
    ids = []
    names = []
    tubeids = []

    results = B.read(endpoint="sample", obj={"containerid": str(order_number)}, max_results=None)
    samples = results.get_first_n_results(None)    

    # for i in range(19999999999999999999999999999999999999999999999):
    #     samples = B.read(endpoint="sample", obj={"containerid":str(order_number)}, page=str(i))
    #     if type(samples) != type(None):
    #         all_samples += samples
    #     else:
    #         break

    # samples = all_samples

    for sample in samples:
        # if sample.type == "Library - Illumina" or sample.type == "User Library in Pool":
        if sample.type == "Library on Run - Illumina":
            ids.append(sample._id)

            try:
                tubeids.append(sample.tubeid)
            except:
                tubeids.append(None)
            try:
                names.append(sample.name)
            except:
                names.append(None)
            try:
                bc1s.append(sample.multiplexiddmx)
            except:
                bc1s.append(None)
            try:
                bc2s.append(sample.multiplexid2dmx)
            except:
                bc2s.append(None)
        else:
            continue

    final = pd.DataFrame({
        "Sample ID":ids,
        "Tube ID":tubeids,
        "Name":names,
        "Barcode 1":bc1s,
        "Barcode 2":bc2s
    })
    final = final.sort_values(by=['Sample ID'], ascending=True)
    # print(final)

    return final

def update_bfabric(df):

    print("STARTING")

    errors = []
    ress = []
    ids = list(df['Sample ID'])

    print(ids)
    bc1 = [str(i) if type(i) != type(0.1) else "" for i in list(df['Barcode 1'])]
    bc2 = [str(i) if type(i) != type(0.1) else "" for i in list(df['Barcode 2'])]
    # Remove Whitespace #
    bc1 = [''.join(sentence.split()) for sentence in bc1]
    # print(bc1)
    bc2 = [''.join(sentence.split()) for sentence in bc2]
    # print(bc2) 
    n_itr = (len(ids) // 100) + 1

    print(n_itr)

    # for i in range(len(ids)):
    for itr in range(n_itr):
        # print("ITR: " + str(itr) + " of " + str(n_itr))
        objs = []
        for i in range(100):
            if i+itr*100 >= len(ids):
                break            
            objs.append(
                {
                 "id":str(ids[i+itr*100]),
                 "multiplexiddmx":str(bc1[i+itr*100]),
                 "multiplexid2dmx":str(bc2[i+itr*100])
                }
            )
            
            # objs.append({"id":str(ids[i+itr*100]),"barcode1dmx":str(bc1[i+itr*100]),"barcode2dmx":str(bc2[i+itr*100])})

        res = B.save(endpoint="sample", obj=objs)
        # print(res)
        # res = B.save_object(endpoint="sample", obj={"id":"0","barcode1dmx":str(bc1[i]),"barcode2dmx":str(bc2[i])})
        # ress.append(res)
        ress += res
        if "errorreport" in str(res[0]):
            print("Recieved Error Report from Bfabric")
            errors.append(str(ids[i]))

    return (ress, errors)

def sortPlate():

    letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    numbers = [i + 1 for i in range(12)]
    order = []
    for i in range(len(numbers)):
        for j in range(len(letters)):
            position = str(letters[j]) + str(numbers[i])
            order.append(position)
    orderings = {order[i]:i+1 for i in range(96)}

    return orderings

def RePool(data, OR, pooling_volume, Bfab):
    data['container'] = [str(elt) for elt in list(data['container'])]
    df = data[data['container'].isin(list(OR.keys()))]
    dfs = []
    for order in OR:
        tmp = data[data['container'] == order]
        # print(tmp)
        try:
            run = Bfab.read(endpoint="run", obj={"id": str(OR[order])}, max_results=None)
        except:
            run = []
        for i in run:
            print(i)
        try:
            runsamples = [str(elt._id) for elt in run[0].sample]
        except:
            continue
        # Fetch all samples in one call using max_results=None
        try:
            results = Bfab.read(
                endpoint="sample",
                obj={
                    "id": runsamples,
                    "includeruns": True,
                    "type": "Library on Run - Illumina",
                },
                max_results=None,
            )
            new_samples = results.get_first_n_results(None)
        except:
            new_samples = []

        all_samples = []
        for samp in new_samples:
            if int(samp.container._id) == int(order):
                all_samples.append(samp)
            else:
                continue

        tubeids = []
        read_counts = []
        corr = []

        for sample in all_samples:
            try:
                read_counts.append(sample.readcount)
            except:
                read_counts.append(0)
            try:
                tubeids.append(sample.tubeid)
            except:
                tubeids.append("None")

        df = pd.DataFrame({"tubeID": tubeids, "reads": read_counts})

        print(df)

        for i in list(df['reads']):
            if int(i) != 0:
                corr.append(
                    round(
                        float(pooling_volume)
                        * s.median([float(j) for j in list(df['reads'])])
                        / int(i),
                        3,
                    )
                )
            else:
                corr.append(0)
        df['correction_factor'] = corr

        df = df.merge(tmp, how="inner", on="tubeID")

        dfs.append(df)
    df2 = pd.concat(dfs)
    df = pd.DataFrame(
        {
            "Well": df2['groupNum'],
            "PlatePosition": df2['gridPosition'],
            "ID": df2['sampleID'],
            "tube_ID": df2['tubeID'],
            "volume_to_pool": df2['correction_factor'],
        }
    )

    srtd = sortPlate()
    normalize_sort = [srtd[elt] for elt in list(df['PlatePosition'])]
    df['srt'] = normalize_sort
    df = df.sort_values(by='srt', ascending=True)
    df = df.drop(columns=['srt'])

    return df


def get_plate_details(plate_id, pool_volume, wrapper):
    df = pd.DataFrame()
    B = wrapper

    parent, sampleID, container, containerType, containerNames = [], [], [], [], []
    inputAmount, inputVolume, library_molarity, target_molarity, target_volume = [], [], [], [], []
    volume_to_pool, gridPosition, group, tubeID, inConc = [], [], [], [], []
    librarypassed = []

    # Get plate object from bfabric
    res = B.read(endpoint='plate', obj={'id': str(plate_id)}, max_results=None)
    print("Plate Data:", res[0])  # Debug output to verify the response
    plate = res[0]

    # Check plate type
    if plate.get('type') != "Illumina Library":
        pass

    IDS = [sample["id"] for sample in plate.get("sample", [])]
    gridPosition = [sample.get('_gridposition', "NA") for sample in plate.get("sample", [])]
    volume_to_pool = [pool_volume] * len(IDS)  # Pool volume for each sample

    res2 = B.read(endpoint='sample', obj={'id': IDS}, max_results=None)
    print("Detailed Sample Data:", res2)  # Debug output for detailed data

    for bf_sample in res2:
        sampleID.append(bf_sample.get("id", "NA"))
        target_volume.append(bf_sample.get("volumetarget", "NA"))
        target_molarity.append(bf_sample.get("molaritytarget", "NA"))
        library_molarity.append(bf_sample.get("molarity", "NA"))
        
        inputAmount.append(float(bf_sample.get("amountinput", "NA")) if bf_sample.get("amountinput") else "NA")
        inputVolume.append(float(bf_sample.get("volumeinput", "NA")) if bf_sample.get("volumeinput") else "NA")
        
        parent_data = bf_sample.get("parent", [{}])
        parent.append(parent_data[0].get("_id", "NA"))
        
        container_data = bf_sample.get("container", {})
        container.append(container_data.get("id", "NA"))
        containerType.append(container_data.get("classname", "NA"))
        
        tubeID.append(bf_sample.get("tubeid", "NA"))
        inConc.append(bf_sample.get("concentrationinputqc", "NA"))
        librarypassed.append(bf_sample.get("qcpassed", "NA"))

        # Formulate container names and group information
        if containerType[-1] != "NA" and container[-1] != "NA":
            containerNames.append(f"{containerType[-1]}_{container[-1]}")
            group.append(f"{containerType[-1]}_{container[-1]}")
        else:
            group.append("NA")

    # Remove duplicates from containerNames for unique naming
    containerNames = list(set(containerNames))
    containerDict = {containerNames[i]: i + 1 for i in range(len(containerNames))}

    # Create DataFrames for original and detailed sample data
    df_orig = pd.DataFrame({
        'sampleID': IDS,
        'volumeToPool': volume_to_pool,
        'gridPosition': gridPosition
    })

    df = pd.DataFrame({
        'sampleID': sampleID,
        'parent': parent,
        'container': container,
        'containerType': containerType,
        'inputAmount': inputAmount,
        'inputVolume': inputVolume,
        'libraryMolarity': library_molarity,
        'targetMolarity': target_molarity,
        'targetVolume': target_volume,
        'group': group,
        'tubeID': tubeID,
        'inConc': inConc,
        'libraryPassed': librarypassed,
        'groupNum': [containerDict.get(elt, "NA") for elt in group]
    })

    # Merge the original data with detailed sample data
    df = df.merge(df_orig, how="inner", on="sampleID")

    print("Final DataFrame with Plate and Sample Details:")
    print(df)

    return df


def Normalize(md):

    srtd = sortPlate()
    normalize = pd.DataFrame({
        'Well':md['gridPosition'],
        'Source name':md['tubeID'],
        'Concentration [nM]':md['libraryMolarity'],
        'Norm. Molarity [nM]':md['targetMolarity'],
        'Volume [ul]':md['targetVolume'],
        'Group':md['group']})
    normalize_sort = [srtd[elt] for elt in list(normalize['Well'])]
    normalize['srt'] = normalize_sort
    normalize = normalize.sort_values(by = 'srt', ascending=True)
    normalize = normalize.drop(columns=['srt'])

    return normalize


def iNormalize(md):

    in_norm = []
    srtd = sortPlate()
    input_normalize = pd.DataFrame({
        'Well':md['gridPosition'],
        'Source name':md['tubeID'],
        'Input QC Conc. [ng/ul]':md['inConc']})

    for i, j in zip(list(md['inputAmount']), list(md['inputVolume'])):
        try:
            in_norm.append(i / j)
        except:
            in_norm.append("ERROR")
    input_normalize['Norm. Conc. [ng/ul]'] = in_norm
    input_normalize['Input Volume [ul]'] = md['inputVolume']
    input_normalize['Group'] = md['group']
    in_normalize_sort = [srtd[elt] for elt in list(input_normalize['Well'])]
    input_normalize['srt'] = in_normalize_sort
    input_normalize = input_normalize.sort_values(by = 'srt', ascending=True)
    input_normalize = input_normalize.drop(columns=['srt'])

    return input_normalize

def Pool(md):

    pool = pd.DataFrame()
    srtd = sortPlate()

    pool['Well']=md['groupNum']
    pool['Sources']=md['tubeID']
    pool['Concentration']=['' for i in range(len(list(md['tubeID'])))]
    pool['Volume']=md['volumeToPool']
    pool['PlatePosition'] = md['gridPosition']

    pool = pool.loc[(pool["Sources"] != "FGCZ_control_RNA_v3")]
    pool = pool.loc[(pool["Sources"] != "FGCZ_control_DNA_v2")]
    pool = pool.loc[(pool["Sources"] != "FGCZ_control_DNA_Nextera")]
    pool = pool.loc[(pool["Sources"] != "FGCZ_control_RNA_SS2")]
    pool = pool.loc[(pool["Sources"] != "FGCZ_control_negative")]

    pool_sort = [srtd[elt] for elt in list(pool['PlatePosition'])]
    pool['srt'] = pool_sort
    pool = pool.sort_values(by = 'srt', ascending=True)
    pool = pool.drop(columns=['srt'])

    return pool

def RePool(data, OR, pooling_volume, Bfab):

    print("-------------------")
    print("DATA")
    print(data)
    print("-------------------")
    print("OR")
    print(OR)
    print("-------------------")
    print("POOLING VOLUME")
    print(pooling_volume)
    print("-------------------")
    print("BFAB")
    print(Bfab)
    print("-------------------")

    data['container'] = [str(elt) for elt in list(data['container'])]
    df = data[data['container'].isin(list(OR.keys()))]
    dfs = []
    for order in OR:
        tmp = data[data['container'] == order]

        try:    
            run = Bfab.read(endpoint="run", obj={"id": str(OR[order])}, max_results=None)
            print(f"Run data for order {order}:", run[0])  # Shows run data for debugging
        except Exception as e:
            print(f"Error in reading run for order {order}: {e}")
            run = []
        
        if run and 'sample' in run[0]:
            try:
                runsamples = [str(sample['id']) for sample in run[0]['sample']]
                print(f"Sample IDs for run in order {order}:", runsamples)
            except KeyError:
                print("Error: 'id' not found in some samples within run.")
                continue
        else:
            print(f"No 'sample' field found or 'sample' is empty in run for order {order}. Full run data:", run)
            continue

        all_samples = []
        new_samples = []
        next_page = 0

        while len(runsamples) // 99 >= next_page:
            samples = Bfab.read(
                endpoint="sample",
                obj={
                    "id": runsamples[99 * next_page : min(99 * next_page + 99, len(runsamples))],
                    "includeruns": True,
                    "type": "Library on Run - Illumina"
                },
                max_results=None
            )
            if samples:
                new_samples.extend(samples)
                next_page += 1
            else:
                break

        for samp in new_samples:
            container_info = samp.get("container", {})
            container_id = str(container_info.get("id", ""))
            container_classname = container_info.get("classname", "")
            
            # Debugging output to confirm container ID and classname for each sample
            # print("Sample container info:", container_info)

            # Check if container matches order and classname is "order"
            if container_id == str(order) and container_classname == "order":
                all_samples.append(samp)

        #print("Filtered samples for order", order, ":", all_samples)


        tubeids = []
        read_counts = []
        corr = []

        for sample in all_samples:
            read_counts.append(sample.get("readcount", 0))
            tubeids.append(sample.get("tubeid", "None"))

        df = pd.DataFrame({"tubeID": tubeids, "reads": read_counts})
        print("df", df)

        for i in df['reads']:
            if int(i) != 0:
                correction = round(float(pooling_volume) * s.median([float(j) for j in df['reads']]) / int(i), 3)
                corr.append(correction)
            else:
                corr.append(0)
        
        df['correction_factor'] = corr
        df = df.merge(tmp, how="inner", on="tubeID")
        dfs.append(df)

    if dfs:
        df2 = pd.concat(dfs)
        df = pd.DataFrame({
            "Well": df2['groupNum'],
            "PlatePosition": df2['gridPosition'],
            "ID": df2['sampleID'],
            "tube_ID": df2['tubeID'],
            "volume_to_pool": df2['correction_factor']
        })

        srtd = sortPlate()
        normalize_sort = [srtd[elt] for elt in df['PlatePosition']]
        df['srt'] = normalize_sort
        df = df.sort_values(by='srt', ascending=True).drop(columns=['srt'])
    else:
        df = pd.DataFrame({
            "Well": [],
            "PlatePosition": [],
            "ID": [],
            "tube_ID": [],
            "volume_to_pool": []
        })

    return df