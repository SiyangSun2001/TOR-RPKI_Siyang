import pickle
with open("/home/siyang/research/tor-rpki/processed/2021-10-01-19-processed.pickle", "rb") as f:
    rs = pickle.load(f)
    for r in rs:
        print(r.or_addresses)