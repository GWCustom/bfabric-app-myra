import pandas as pd
import bfabric
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

B = bfabric.Bfabric()

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

def get_dataset(order_number):

    bc1s = []
    bc2s = []
    ids = []
    names = []
    tubeids = []

    res, all_res = B.read_object(endpoint="sample", obj={"containerid":str(order_number)}, page=1), []

    print(res)

    next_page = 2
    while res is not None and len(res):
        all_res += res
        try:
            res = B.read_object(endpoint="sample", obj={"containerid":str(order_number)}, page=next_page)
        except:
            break
        next_page += 1

    samples = all_res
    # for i in range(19999999999999999999999999999999999999999999999):
    #     samples = B.read_object(endpoint="sample", obj={"containerid":str(order_number)}, page=str(i))
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

        res = B.save_object(endpoint="sample", obj=objs)
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
            run = Bfab.read_object(endpoint="run", obj={"id":str(OR[order])})
        except:
            run = []
        for i in run:
            print(i)
        try:
            runsamples = [str(elt._id) for elt in run[0].sample]
        except:
            continue
        # print("\n\n\nRUN SAMPLES\n\n\n")
        # print(runsamples)
        all_samples = []
        new_samples = []
        next_page = 0

        while len(runsamples) // 99 >= next_page:
            # print(order)
            samples = Bfab.read_object(endpoint="sample", obj={"id":runsamples[99*next_page:min(99*next_page+99, len(runsamples))],"includeruns":True,"type":"Library on Run - Illumina"})
            # samples = B.read_object(endpoint="sample", obj={"id":runsamples[99*next_page:min(99*next_page+99, len(runsamples))],"type":"Library on Run - Illumina","containerid":str(order)})
            if type(samples) != type(None):
                new_samples += samples
                next_page += 1
            else:
                break
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

        df = pd.DataFrame({"tubeID":tubeids, "reads":read_counts})

        print(df)

        for i in list(df['reads']):
            if int(i) != 0:
                # corr.append(round(float(pooling_volume)*s.median([float(j) for j in list(df['reads'])])/int(i), 3))
                corr.append(round(float(pooling_volume)*s.median([float(j) for j in list(df['reads'])])/int(i), 3))
            else:
                corr.append(0)
        df['correction_factor'] = corr

        df = df.merge(tmp, how="inner", on="tubeID")

        dfs.append(df)
    df2 = pd.concat(dfs)
    df = pd.DataFrame({"Well":df2['groupNum'],
                       "PlatePosition":df2['gridPosition'],
                       "ID":df2['sampleID'],
                       "tube_ID":df2['tubeID'],
                       "volume_to_pool":df2['correction_factor']})

    srtd = sortPlate()
    normalize_sort = [srtd[elt] for elt in list(df['PlatePosition'])]
    df['srt'] = normalize_sort
    df = df.sort_values(by = 'srt', ascending=True)
    df = df.drop(columns=['srt'])

    return df


def get_plate_details(plate_id, pool_volume, wrapper):

    df = pd.DataFrame()
    B = wrapper

    parent = [] ####
    sampleID = [] ####
    container = [] ###
    containerType = [] ####
    containerNames = [] ####
    iSeq = []
    inputAmount = [] ####
    inputVolume = [] ####
    library_molarity = [] ####
    target_molarity = [] ####
    target_volume = [] ####
    volume_to_pool = [] ####
    gridPosition = [] ####
    group = [] ####
    tubeID = [] ####
    inConc = []

    # Get plate object from bfabric

    if True:
        res = B.read_object(endpoint='plate', obj={'id':str(plate_id)})
        print(res)
        plate = res[0]
        plate_name = str(res[0].name)
    else:
        pass #TODO Add error handling

    # Populate Dataframe

    if res[0].type != "Illumina Library":
        pass #TODO Add error handling

    IDS = []
    librarypassed = []

    for x in range(len(res[0].sample)):  #for all samples on plate
        IDS.append(res[0].sample[x]._id)
        print("Querying details of sample " +str(res[0].sample[x]._id) + " (position "+str(res[0].sample[x]._gridposition)+ ") from plate "+str(res[0].name))

        try:
            gridPosition.append(res[0].sample[x]._gridposition)  # get sample plate position
        except:
            gridPosition.append("NA")

        try:
            volume_to_pool.append(pool_volume)  # get sample plate position
        except:
            volume_to_pool.append("NA")

    res2 = B.read_object(endpoint='sample', obj={'id':IDS})

    for bf_sample in res2:

        try:
            sampleID.append(bf_sample._id) # get sample id
        except:
            sampleID.append("NA")

        try:
            target_volume.append(bf_sample.volumetarget)
        except:
            target_volume.append("NA")

        try:
            target_molarity.append(bf_sample.molaritytarget)
        except:
            target_molarity.append("NA")

        try:
            library_molarity.append(bf_sample.molarity)
        except:
            library_molarity.append("NA")

        try:
            inputAmount.append(float(bf_sample.amountinput))
        except:
            inputAmount.append("NA")

        try:
            inputVolume.append(float(bf_sample.volumeinput))
        except:
            inputVolume.append("NA")

        try:
            parent.append(bf_sample.parent[0]._id)
        except:
            parent.append("NA")

        try:
            container.append(bf_sample.container._id)
        except:
            container.append("NA")

        try:
            containerType.append(bf_sample.container._classname)
        except:
            containerType.append("NA")

        try:
            tubeID.append(bf_sample.tubeid)
        except:
            tubeID.append("NA")

        try:
            inConc.append(bf_sample.concentrationinputqc)
        except:
            inConc.append("NA")

        try:
            librarypassed.append(bf_sample.qcpassed)
        except:
            librarypassed.append("NA")

        if containerType[-1] != "NA" and container[-1] != "NA":
            containerNames.append(str(bf_sample.container._classname) + '_' + str(bf_sample.container._id))
            group.append(str(bf_sample.container._classname) + '_' + str(bf_sample.container._id))

    containerNames = list(set(containerNames))
    containerDict = {containerNames[i]:i+1 for i in range(len(containerNames))}

    df_orig = pd.DataFrame({'sampleID':IDS,
        'volumeToPool':volume_to_pool,
        'gridPosition':gridPosition})

    df['groupNum']=[containerDict[elt] for elt in group]
    df['parent']=parent
    df['sampleID']=sampleID
    df['container']=container
    df['containerType']=containerType
    df['inputAmount']=inputAmount
    df['inputVolume']=inputVolume
    df['libraryMolarity']=library_molarity
    df['targetMolarity']=target_molarity
    df['targetVolume']=target_volume
    df['group']=group
    df['tubeID']=tubeID
    df['inConc']=inConc
    df['libraryPassed']=librarypassed

    df = df.merge(df_orig, how="inner", on="sampleID")

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
        # print(tmp)
        try:    
            run = Bfab.read_object(endpoint="run", obj={"id":str(OR[order])})
        except:
            run = []
        for i in run:
            print(i)
        try:
            runsamples = [str(elt._id) for elt in run[0].sample]
        except:
            continue
        # print("\n\n\nRUN SAMPLES\n\n\n")
        # print(runsamples)
        all_samples = []
        new_samples = []
        next_page = 0

        while len(runsamples) // 99 >= next_page:
            # print(order)
            samples = Bfab.read_object(endpoint="sample", obj={"id":runsamples[99*next_page:min(99*next_page+99, len(runsamples))],"includeruns":True,"type":"Library on Run - Illumina"})
            # samples = B.read_object(endpoint="sample", obj={"id":runsamples[99*next_page:min(99*next_page+99, len(runsamples))],"type":"Library on Run - Illumina","containerid":str(order)})
            if type(samples) != type(None):
                new_samples += samples
                next_page += 1
            else:
                break
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

        df = pd.DataFrame({"tubeID":tubeids, "reads":read_counts})

        print(df)

        for i in list(df['reads']):
            if int(i) != 0:
                # corr.append(round(float(pooling_volume)*s.median([float(j) for j in list(df['reads'])])/int(i), 3))
                corr.append(round(float(pooling_volume)*s.median([float(j) for j in list(df['reads'])])/int(i), 3))
            else:
                corr.append(0)
        df['correction_factor'] = corr

        df = df.merge(tmp, how="inner", on="tubeID")

        dfs.append(df)

    if dfs:
        df2 = pd.concat(dfs)
        df = pd.DataFrame({"Well":df2['groupNum'],
                       "PlatePosition":df2['gridPosition'],
                       "ID":df2['sampleID'],
                       "tube_ID":df2['tubeID'],
                       "volume_to_pool":df2['correction_factor']})

        srtd = sortPlate()
        normalize_sort = [srtd[elt] for elt in list(df['PlatePosition'])]
        df['srt'] = normalize_sort
        df = df.sort_values(by = 'srt', ascending=True)
        df = df.drop(columns=['srt'])
    else:
        df = pd.DataFrame({
            "Well":[],
            "PlatePosition":[],
            "ID":[],
            "tube_ID":[],
            "volume_to_pool":[]
        })

    return df