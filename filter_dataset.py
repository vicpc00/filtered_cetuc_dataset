import os
import shutil

def main():
    dataset_folder = '/home/victor.costa/data/alcaim'
    out_folder = '../cetuc-filtered'
    cluster_select_file = "alcaim_clusters/cluster-format.txt"
    cluster_folder = "alcaim_clusters/clusters"
    
    clusters = {}
    with open(cluster_select_file, "r") as select_f:
        for line in select_f.readline():
            spk, cluster_number, cluster_id, _ = line.split(':')
            clusters[spk] = set()
            with open(f"clusters-{spk}-{cluster_number}.txt", "r") as cluster_f:
                for l in cluster_f.readlines():
                    fn, cl = l.split(':')
                    if cl == cluster_id:
                        clusters[spk].add(os.path.basename(fn))
                        
    os.makedirs(dataset_out, exist_ok=True)
    
    for spk in os.listdir(dataset_folder):
        in_folder = os.path.join(dataset_folder, spk)
        out_folder = os.path.join(out_folder, spk)
        if not os.path.isdir(in_folder):
            continue
        os.path.makedirs(out_folder, exist_ok=True)
        for fn in os.listdir(in_folder):
            if os.path.splitext(fn)[1] != '.wav' or fn not in clusters[spk]:
                continue
            shitil.copy2(os.path.join(in_folder, fn), os.path.join(out_folder, fn))
                
    
    
if __name__ == "__main__":
    main()



