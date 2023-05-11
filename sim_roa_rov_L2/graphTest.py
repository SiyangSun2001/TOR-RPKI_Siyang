from util import *

algo = "matching"
p_roa_rov = [0.014041666666666675,0.01600000000000001]
p_total_rov = [0.037666666666666675, 0.04408333333333334]

d1 = datetime(2022, 9, 13, 0)
d2 = datetime(2022, 10, 13, 0)
h = [d1, d2]
x = [0,1]
# print("length of h:", len(h))
plt.xlabel('Time by the hour')
plt.ylabel('Percent of Client that has ROA and ROV matching')
plt.title(algo + ': Tor Percent of Client with ROA and ROV matching 1000 Clients')
plt.plot(x,p_roa_rov,marker = 'o', label = "Matching Algorithm")
plt.plot(x, p_total_rov, marker = '.', label = "Upper Bound")
plt.xticks(x, h)
plt.legend()
plt.savefig(algo + 'Test2023.png')
print("finished grahing")