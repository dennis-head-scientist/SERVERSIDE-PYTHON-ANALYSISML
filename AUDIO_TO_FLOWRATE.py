# %%
import os

# import tensorflow as tf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import librosa
from pyAudioAnalysis import ShortTermFeatures
import tensorflow as tf
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler, RobustScaler

# Run setup.py to install the required packages
# os.system("python setup.py") # CLEANUP

# Path: AUDIO_TO_FLOWRATE.py
# This file takes in a .wav file and outputs a flowrate csv file


# Load an audio file
def GiveMeData(path_to_audio, path_to_csv):
    audioFile = path_to_audio
    x, Fs = librosa.load(audioFile, sr=None)
    superFlow_df = pd.read_csv(path_to_csv, error_bad_lines=False)
    voidedVolume = superFlow_df[" Vmic"].to_numpy()
    voidedVolume_diff = np.diff(voidedVolume[::2])
    Q = superFlow_df[" Qura"].to_numpy()[::2]
    F, f_names = ShortTermFeatures.feature_extraction(x, Fs, 8820, 8820, deltas=False)
    length_F = F.shape[1]
    Q_trim = Q[0:length_F]
    voidedVolume_diff_trim = voidedVolume_diff[0:length_F]
    F_transposed = np.transpose(F)
    print(F_transposed.shape)
    Q_column = np.reshape(Q_trim, (length_F, 1))
    V_column = np.reshape(voidedVolume_diff_trim, (length_F, 1))
    print(Q_column.shape)
    print(V_column.shape)
    return F_transposed, f_names, Q_column, V_column


F1, f_names_1, Q1, V1 = GiveMeData("sghfebt2sf1w.wav", "sf1post.CSV")
F2, f_names_2, Q2, V2 = GiveMeData("sghfebt2sf1wr2.wav", "sf1post.CSV")  # test
F3, f_names_3, Q3, V3 = GiveMeData("sghfebt2sf2w.wav", "sf2post.CSV")
F4, f_names_4, Q4, V4 = GiveMeData("sghfebt2sf2wr2.wav", "sf2post.CSV")
# %%
# V_stack F1, F3, F4
F = np.vstack((F1, F3, F2))
Q = np.vstack((Q1, Q3, Q2))
V = np.vstack((V1, V3, V2))
print(F.shape)
print(Q.shape)
print(V.shape)

Test_F = F4
Test_Q = Q4
Test_V = V4

# %%

regQ = MLPRegressor(
    solver="adam",
    activation="logistic",
    max_iter=500,
    alpha=1e-5,  # 1e-6,
    verbose=True,
    hidden_layer_sizes=(10, 10, 10),
    tol=0.0000000001,
    random_state=100,
)

scaler = StandardScaler()  # subtracting mean / sd
## transform - train
scaler.fit(F)
F = scaler.transform(F)
Test_F = scaler.transform(Test_F)
regQ.fit(F, Q)

regV = MLPRegressor(
    solver="adam",
    activation="logistic",
    max_iter=500,
    alpha=1e-5,  # 1e-6,
    verbose=True,
    hidden_layer_sizes=(10, 10, 10),
    tol=0.0000000001,
    random_state=100,
)


regV.fit(F, V)
# %%
y_hat = regQ.predict(Test_F)
plt.plot(Test_Q, label="Actual")
plt.plot(y_hat, "--", alpha=1, label="Predicted", linewidth=0.4)
plt.legend()
plt.figure(2)
y_hat_V = regV.predict(Test_F)
plt.plot(Test_V, label="Actual")
plt.plot(y_hat_V, "--", alpha=1, label="Predicted", linewidth=0.4)
plt.legend()

# %%
TotalVolume = np.cumsum(Test_V)
TotalVolume_hat = np.cumsum(y_hat_V)
plt.figure(3)
plt.plot(TotalVolume, label="Actual")
plt.plot(TotalVolume_hat, "--", alpha=1, label="Predicted", linewidth=1)
plt.legend()

# %%


def GetQ(array):
    outputArray = np.array([])
    for i in range(len(array) - 5):
        # look at next 10 samples
        current_array = array[i : i + 4]
        current_Q = np.sum(current_array)
        outputArray = np.append(outputArray, current_Q)
        # get every 10 number from array
    outputArray = outputArray[::5]

    return outputArray


Test_V_Q = GetQ(Test_V)
y_hat_V_Q = GetQ(y_hat_V)

plt.figure(4)
plt.plot(Test_V_Q, label="Actual")
plt.plot(y_hat_V_Q, "--", alpha=1, label="Predicted", linewidth=1)
plt.legend()

# %%
