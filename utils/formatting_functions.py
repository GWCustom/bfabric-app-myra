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