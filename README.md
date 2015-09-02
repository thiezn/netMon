# netMon
A Distributed Network Monitoring Solution using locally deployed nodes. 

Nodes running on low-cost hardware (e.g. rasberry pi's) or docker containers running various network probes providing insight into the health of the network.

Main features are:
- Full mesh node network providing
  - latency between nodes
  - network path between nodes
  - detecting routing and latency changes between the nodes
  - extensible through addon modules
  - HTTP/HTTPS probes
  - DNS probes
  - bandwidth probes
- Central control plane
  - collecting node performance data
  - distributing probe configuration
  - network/node overview
  - reports with fancy pants graphs
  - node health status
  - web based interface
- RESTful API
