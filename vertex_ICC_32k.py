
from hcp_class_alignment import *
import sys
import numpy as np 
import nibabel as nib 
import pandas as pd
import matplotlib.pyplot as plt
from surfplot.plotting import Plot
from sklearn.neighbors import NearestNeighbors
from pingouin import intraclass_corr

subj=sys.argv[1]
subj_inst=hcp_subj(subj,4)

def gradDispersion(grads_ses1_aligned, grads_ses2_aligned, save = False, file_name = None):
    if grads_ses1_aligned != None:
        vd_subject_list_ses1 = []
        for subject_grads in grads_ses1_aligned:
            vertex_coords = subject_grads.T
            vertex_nbrs = NearestNeighbors(n_neighbors=500, algorithm='brute').fit(vertex_coords)
            distances, indices = vertex_nbrs.kneighbors(vertex_coords)
            mean_distances = distances.mean(axis = 1)
            vd_subject_list_ses1.append(mean_distances)
        vd_ses1 = np.asarray(vd_subject_list_ses1)
    else:
        pass

    if grads_ses2_aligned != None:
        vd_subject_list_ses2 = []
        for subject_grads in grads_ses2_aligned:
            vertex_coords = subject_grads.T
            vertex_nbrs = NearestNeighbors(n_neighbors=500, algorithm='brute').fit(vertex_coords)
            distances, indices = vertex_nbrs.kneighbors(vertex_coords)
            mean_distances = distances.mean(axis = 1)
            vd_subject_list_ses2.append(mean_distances)
        vd_ses2 = np.asarray(vd_subject_list_ses2)
    else:
        pass
    vd_list = [vd_ses1, vd_ses2]
    if save == True:
        vd_array = np.stack((vd_list))
        np.save(arr = vd_array, file = file_name + ".npy")
    return vd_list

def make_measure_df(measure_array, measure_name, subjects, session):
    measure_df = pd.DataFrame(measure_array[0], columns = [measure_name])
    measure_df["Subject"] = subjects[0]
    measure_df["Session"] = session
    measure_df["Vertex"] = np.arange(len(measure_df[0]))
    for subject, array in zip(subjects[1:], measure_df):
        df = pd.DataFrame(array, columns = ["Dispersion"])
        df["Subject"] = subject
        df["Session"] = 2
        df["Vertex"] = np.arange(len(array))
        measure_df = pd.concat([measure_df, df])
        
def vertexICC(measure_df, ICC_type = "ICC2"):
    vertices = np.arange(len(measure_df[0]))
    vertex_wise_ICC = []
    for vertex in vertices:
        data = measure_df[measure_df["Vertex"] == vertex]
        ICC = intraclass_corr(data, targets = "Subject", raters = "Session", ratings = "Dispersion")
        ICC["Vertex"] = vertex
        vertex_wise_ICC.append(ICC[ICC["Type"] == ICC_type])
    vertex_wise_ICC = pd.concat(vertex_wise_ICC)
    return vertex_wise_ICC