import os
import glob

import warnings
warnings.simplefilter("ignore")

from tqdm import tqdm
import numpy as np
import librosa
import resemblyzer
import sklearn
from sklearn.mixture import GaussianMixture
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

import matplotlib.pyplot as plt


if __name__ == "__main__":

    root = 'datasets/alcaim'
    #root = 'datasets/vctk/vctk_train'
    out_dir = 'dataset_analysis/alcaim'
    os.makedirs(out_dir, exist_ok=True)
    encoder = resemblyzer.VoiceEncoder()

    tries = 20

    emb_dict = {}
    emb_means = {}
    clusters = {}

    spks = sorted([d for d in os.listdir(root) if os.path.isdir(os.path.join(root, d))])

    for spk in tqdm(spks):
        embeddings = []
        silhouette_scores = []
        filenames = sorted(glob.glob(os.path.join(root, spk, '*.wav')))
        for signal_fn in filenames:
            signal, sr = librosa.load(signal_fn, sr=16000)
            signal = resemblyzer.preprocess_wav(signal, source_sr=sr)
            embeddings.append(encoder.embed_utterance(signal))

        embeddings = np.stack(embeddings)
        emb_dict[spk] = embeddings


        train_scores = []
        val_scores = []
        for k in range(1, 6):
            train_scores_itt = []
            val_scores_itt = []
            for _ in range(tries):
                train, val = sklearn.model_selection.train_test_split(embeddings, test_size=0.2)
                model = GaussianMixture(n_components=k).fit(train)
                train_scores_itt.append(model.score(train))
                val_scores_itt.append(model.score(val))

                #clusters = model.fit_predict(embeddings)
                #score = sklearn.metrics.silhouette_score(embeddings, clusters)
                #silhouette_scores.append(score)
            train_scores.append(np.mean(train_scores_itt))
            val_scores.append(np.mean(val_scores_itt))

            print(f'{spk}: k={k} train={train_scores[-1]} val={val_scores[-1]}')
            
            clusters = GaussianMixture(n_components=k, n_init=10).fit_predict(embeddings)
            pca = PCA(n_components=2).fit(embeddings)
            reduced = pca.transform(embeddings)
            cmap = plt.cm.rainbow(np.linspace(0, 1, k))
            colors = np.stack([cmap[cl] for cl in clusters])
            
            fig, ax = plt.subplots()
            ax.set_title(f'{spk}, {k} clusters, explained var = {sum(pca.explained_variance_ratio_):.2f}')
            plt.scatter(reduced[:, 0], reduced[:, 1], c=colors)
            plt.savefig(os.path.join(out_dir, f'emb_scatter-{spk}-{k}_comps.png'))
            
            with open(os.path.join(out_dir, f'clusters-{spk}-{k}.txt'), 'w') as cluster_file:
                cluster_file.writelines(f'{fn}:{cl}\n' for fn, cl in zip(filenames, clusters))

        with open(os.path.join(out_dir, 'clusters_results.txt'), 'a') as result_file:
            result_file.write(f'{spk}:\n')
            result_file.write('  train scores=' + ' '.join(f'{s:.2f}' for s in train_scores)+'\n')
            result_file.write('  val scores=' + ' '.join(f'{s:.2f}' for s in val_scores)+'\n')
            result_file.write(f'best k={np.argmax(val_scores)+1}\n')
