# netMon
##A Distributed Network Monitoring Solution using locally deployed nodes. 

Nodes running on low-cost hardware (e.g. raspberry pi's) or docker containers running various network probes providing insight into the health of the network.

##Key Features
- Local perspective of networks and applications
- Extensive and customisable reporting
- Level of access and visibility easily segmented (admins, region admins, managers, etc.)
- Clear overview of environment, able to scale from small to med-large organizations
- Quick and easy deployable nodes, plug-and-play

##Advantages of locally deployed nodes opposed to a central monitoring server
A local node is able to look at the environment from its own perspective. Traditionally monitoring servers are deployed in main datacentre’s. The health of the environment is only seen from this location. This makes it hard to determine performance or access issues due to routing, quality of service or access restrictions from the perspective of your users.

- Network performance seen from branch site
- Network route changes seen from branch site
- Access control seen from branch site
- HTTP en SSH proxy servers running on node to allow administrator to see the environment from the branch perspective through his own eyes.

##Probing Capabilities
The node network interfaces can be configured as a trunk. This will allow you to hook into the distribution layer of a site and be able to run probes from various vlans.
Probe      |Description                       
-----------
ICMP       |
http(s)    |
Traceroute |
MTR        |(traceroute/ping probe)
TCP        |
UDP        |
SNMP       |
MTU        |
Bandwidth  |
TCP Dump   |Not technically a probe but well..

##Main features
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

## High Level Overview (Or rather my wishlist)
remote deployed nodes die probes kunnen uitsturen
- Centrale reporting server waar nodes zich registreren
  - HA reporting server
  - Verschillende (HA) reporting servers/groepen per regio
- Listeners voor inkomende gegevensstromen
  - SNMP trap listener
  - Syslog listener
  - Probe result listener
  - Listeners zijn losstaande daemons
  - elke listener schrijft zijn data weg in key/value DB zodat we gemakkelijk nieuwe type probes weg kunnen schrijven
- Probe results storage
  - Key/Value storage zodat we gemakkelijk nieuwe probes data kunnen wegschrijven zonder veel logica te moeten aanpassen in de applicatie
- (REST/JSON) API voor Probe results te pakken
- Web frontend voor probe resultaten/reports
- Probe scheduler, wanneer, hoelang en hoevaak moeten we proben?
- Autoregister new probes to control server
- Autodiscover network topology?
- Autodiscover server infrastructure?
- Web frontend voor management van probes
- CLI commands om nodes te configureren
- Configuratie files allemaal plain text/JSON maken zodat je gemakkelijk kan automatiseren
- probe configuration management (ansible,puppet, chef, jinja2?)
- Probe definities via jinja2/json zodat je custom tcp/udp/http/snmp/dns/firewall probes kunt scrhijven
- promotion/demotion of nodes into supernodes?
- Simple HTTP/HTTPS proxy on nodes to be able to see what a website looks like from that locations perspective
- Service monitor - Houd de status van de verschillende componenten in de gaten. kan daemons starten, stoppen, herstarten,etc.  houd ook recourses in de gaten en kan zien als een daemon veel CPU en Memory gebruikt
- SNMP responder service. Geeft healthstatus terug van de nodes
- logging info/debug msgs
- Authenticatie model
  - user/role based
  - authentication database on superposed or all nodes?
  - Roles and users can be associated with AD groups
  - Roles and users can be associated with TACACS groups
  - Roles can be assigned access/views to specific nodes, specific regions or all regions. Also should be able to give insight into reports on this level for example for managers. This should be easy to set up. I miss this with all our network mgmt systems
- Een soort git/software repository waar remote nodes de laatste versie kunnen ophalen van de software.
