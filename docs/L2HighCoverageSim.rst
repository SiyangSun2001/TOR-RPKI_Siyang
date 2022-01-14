Level 2 Simulator with High ROA and ROV Coverage
=================================================

This directory has the same basic functionality as sim_roa_rov_L2. But we assume a higher percentage of ROA and ROV coverage to simulate
the new guard selection algorithm's performance if ROA and ROV coverage were to increase in the future. 

We assume all partial ROA enforcing AS will fully cover their IP space to mimic an increased ROA coverage in the future. 
So if a client is in one of the AS that appears in the .csv file for ROA coverage, then that client is considered covered by ROA.

We assumed that all Tier 1 AS will enforce ROV in all of their IP space. So we added all Tier 1 AS' ASN to the current set of AS
that enforces ROV. 

Use sim_roa_rov_highCoverage/distributeUser.py: user_specified_client2() function to generate client with high ROA, ROV coverage. 

The main difference are in the util.py and the helper function to make these changes are in modifyConsensus.py.

.. toctree::
   :maxdepth: 4

   modifyConsensus
