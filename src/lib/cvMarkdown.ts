/**
 * Single source of truth for the machine-readable CV.
 *
 * Rendered as:
 *   - /cv.md                      (standalone markdown, agent-friendly)
 *   - /llms-full.txt              (embedded CV section)
 *   - linked from /llms.txt
 *
 * Keep in sync with src/pages/cv.astro. Structure is deliberately flat and
 * unambiguous so an LLM can parse it without guessing: every role is a
 * heading with explicit `Organization | Location | Dates` metadata.
 */

const EN = `
## About Me

Even though my company is still moving through legacy workflow, I have already adapted Agentic Workflows, implemented LangChain and N8N deployments, and run agents to manage our ticketing system and RAG over my Confluence and email knowledge for semantic search.

My experience spans a wide range of network specialties — from IP backbone hosting converged IMS/mobile backhaul (Egypt Telecom), enterprise service provider VPN/MPLS routing and tunneling for global sites (Orange Business Services), cloud backend on OpenStack-based public cloud in Europe (Flexible Engine / Huawei CloudStack), to my previous role in customer-end enterprise networks managing Wifi, firewalls and VPNs across datacenter and office sites (Hyundai Autoever Europe GmbH). I have now moved to the OpenStack deployment, managing the data center and virtual OpenStack layers.

In addition, working in a very process-oriented environment at Orange Business Services taught me how to establish process and apply best practices — from change management and project implementation to documentation of daily work.

## Work Experience

### 1. Senior Private Cloud Engineer (Networks)
- **Organization:** Hyundai Autoever Europe GmbH
- **Location:** Frankfurt am Main, Germany
- **Dates:** 01/06/2026 — Current
- **Type:** Full-time

I work with an Arista data center hosting an OpenStack vanilla deployment, managing the network between the data center, underlay/overlay on Arista switches, and the OpenStack Neutron layer. It's an operational role in which I develop scripts, automation, and AI-driven automations for optimizing day-to-day operations.

**Vendors:** Arista, Palo Alto, OpenStack, Rancher, Grafana, Zabbix

### 2. Network Systems Engineer
- **Organization:** Hyundai Autoever GmbH
- **Location:** Offenbach, Germany
- **Dates:** 07/2023 — 06/2026
- **Type:** Full-time

Implementation and management of datacenter and enterprise infrastructure, including managing multiple customers with multiple infrastructure needs, also acting as project manager for new implementations.

**Technologies involved:** Cisco ISE (2.x & 3.x), Cisco Nexus (legacy & 9K), Cisco WLC (9800 & 5500), Cisco IOS-based devices (legacy and Catalyst 9k), Cisco ASA & Palo Alto firewalls (filtering, SSL & IPSec), Cisco DNA Center.

### 3. Cloud as Systems Engineer
- **Organization:** G42 Cloud
- **Location:** Abu Dhabi, United Arab Emirates
- **Dates:** 03/2023 — 06/2023
- **Type:** Full-time

Maintained Huawei Cloud Stack (OpenStack-based) cloud, mainly managing the Neutron infrastructure — continuing the same track from Ericsson and Orange Business Services.

### 4. Cloud Operations and Automation Engineer — Network Domain
- **Organization:** Ericsson
- **Location:** Cairo, Egypt
- **Dates:** 11/2022
- **Type:** Full-time

Joined Ericsson as an operations engineer, with main responsibility for automating tedious bug checks that customers may face and automating fix application with minimal customer intervention, using mainly Python and Bash scripting.

### 5. Public Cloud Operations Engineer — Network Domain
- **Organization:** Orange Business Services
- **Location:** Cairo, Egypt
- **Dates:** 08/2021 — 10/2022
- **Type:** Full-time

Worked on both the physical and virtual parts of the cloud DC infrastructure, as follows:

- Working on the physical DCs hosting all cloud services, adhering to current CLOS design standards and using APIs to configure and control network nodes (routers, switches, firewalls).
- Management and optimization of network capacity and peering with the Orange backbone for both MPLS and internet traffic.
- Exposure to multiple security appliances such as VPN gateways, Anti-DDoS and WAF — essential to any internet-facing solution, especially for hosting compliant and critical tenants.
- For the first time in my career, I worked on the most upcoming technologies — OpenStack virtual networks and highly efficient virtual network appliances for security and load balancing.
- Worked with both legacy VLANs and new VXLAN virtual private networks, with multiple interworked encapsulation criteria.
- From managing both physical and virtual networks, I worked on DC routing/switching alongside troubleshooting virtual networks, as traffic passes through security appliances and physical/virtual switches — so network operations extended even through the Linux machines.
- New DC technologies gave me the opportunity to migrate from SSH-based scripting to NetConf / REST API-based calls that are much more reliable and efficient.
- New to Terraform, but very experienced using Python for API interactions; also completed multiple large self-initiated projects (see the Projects section).

### 6. IP Core Planning Senior Engineer
- **Organization:** TE Data (Telecom Egypt) / WE
- **Location:** Cairo, Egypt
- **Dates:** 06/2019 — 07/2021
- **Type:** Full-time

- Responsible for utilizing Python scripting for reporting on the whole backbone network and performing automated pre- and post-checks across an area while migrating critical devices.
- Implementation of backbone-hosted services and backhaul services for fixed, mobile, and broadband services using L3/L2 VPNs.
- Migration and implementation of backbone devices (P-PE-RR-BNG) from multiple vendors (Cisco, Juniper, Nokia, etc.).
- Software upgrades across multiple vendor devices.
- Deep understanding of BGP, MPLS & OSPF as the underlay for all hosted services.
- Due to the converged nature of the network, worked with mobile, fixed, and broadband backbones such as IMS, EPC, BNGs, and a suite of devices — also establishing connectivity toward multiple security devices (Palo Alto, Cisco ASA, Juniper SRX).

### 7. VPN Implementation Engineer Level 3
- **Organization:** Orange Business Services
- **Location:** Cairo, Egypt
- **Dates:** 06/2018 — 06/2019
- **Type:** Full-time

- Worked on an international, vast network — gaining knowledge of how to manage enormous-scale networks.
- Supported customers across huge geographical areas and multiple languages; every enterprise worked with was global, enabling management of networks across multiple Autonomous Systems.
- Due to Orange Business Services' global reach, worked with multiple physical technologies, some phasing out — such as ATM and Frame Relay.
- Management of customer HUB sites with multiple unique network setups.

### 8. Incident Management Specialist (1st Line Engineer)
- **Organization:** Orange Business Services
- **Location:** Cairo, Egypt
- **Dates:** 10/2016 — 06/2018
- **Type:** Full-time

- Midway through the role, shifted to optimization technologies and devices such as Riverbed and Ipanema, gaining deep knowledge of TCP/IP operation.
- Developed skills in managing customers from across the world and handling customer frustration during service instability.
- Basic troubleshooting skills on PE-CE, LAN, and wireless technologies.

## Language Skills

- English — C2
- German — A2 (improving)

## Skills

**Networking:** IP Routing (BGP, MP-BGP, MPLS, OSPF), Switching; Cisco ISE 2.6 & 3.1; Cisco WLC (9800 & 5500); Cisco Catalyst / Nexus 9k; Palo Alto 10.x & 11.x Firewalls / GlobalProtect VPN; Cisco ASA Firewalls & SSL VPN; Juniper MX, PTX Backbone Routers; Juniper SRX Firewalls; NOKIA Routers — ADSL Termination; Cisco ASR 9k Backbone Routers — full OSPF converged Egypt backbone.

**Cloud & Virtualization:** OpenStack Neutron (Orange Flexible Engine, Huawei Cloud Stack); Huawei Cloud Stack — Networks / Neutron; Linux Administration.

**Automation & AI:** LangChain, N8N, Pi, MCP — agentic code workflows; Terraform (Orange Flexible Engine); Python (automation of network + OpenStack); Python Flask + HTML / CSS / Bootstrap (self-taught).

**Monitoring & Tools:** Docker, Grafana, Telegraf, InfluxDB (self-taught); SolarWinds NPM, NTA Administration.

## Education and Training

### Bachelor's Degree, Computer Engineering
- **Institution:** Arabische Akademie für Wissenschaften, Technologie und Seeverkehr (AASTMT)
- **Location:** Cairo, Egypt
- **Dates:** 06/2008 — 11/2013
- **Website:** http://www.aast.edu/en/index.php/
- **Address:** P.O. Box 2033, Elhorria, El Moshir Ismail St. (behind Sheraton Bldg.), 2033, Cairo, Egypt
- **Field of study:** Engineering, manufacturing and construction
- **Final grade:** 3.56 / A
- **Anabin Institutionstyp:** Universität privat staatlich anerkannt
- **Anabin Status:** H+

## Driving Licence

- Category B — German licence
- Issued 18/02/2025

## Projects

### Blog
amroelhusseini.vercel.app — https://amroelhusseini.vercel.app

### MCP Servers
During my current role I have developed a number of automation tools using AI, including several private and publicly hosted MCP servers on GitHub for managing systems such as Palo Alto, Cisco, Outlook, and ServiceNow — mostly private but applicable to public deployments too. I built these MCP server skills to run automations, especially through N8N.

### Physical Network Auditing
At both TE Data and Orange, I wrote a multithreaded Python script to audit network configuration against standard templates. It was the first time I used the Python multiprocessing library to log into hundreds of devices in parallel — shortening a 4-hour audit to just 2 minutes.

### Web Application for Network Inventory
Using Flask, Redis and SQLite, I built a web application to store chassis inventories across the TE Data backbone, queryable for Excel and web reports. This saved significant time for hardware planning decisions. To solve slow queries under concurrent use, I introduced Redis to cache commonly produced reports.

### Network Topology Plotter
Combining JavaScript/Jinja2 with Python scripting, I created automated, up-to-date network topologies by parsing and generating JavaScript (GoJS) and SVG high-level diagrams, plus automated XLS low-level diagrams — used at both Orange and TE Data.
https://github.com/amrelhusseiny/drawio_network_plot

### Backbone Internet Traffic Path
As part of my backbone work at TE Data, I built a script to plot the internet traffic path for each region, generated automatically by parsing backbone routing tables and factoring in BGP and OSPF data to determine and trace the path.
`;

const DE = `
## Über mich

Auch wenn mein Unternehmen noch traditionelle Workflows verwendet, habe ich bereits Agentic Workflows adaptiert, LangChain- und N8N-Deployments implementiert und Agenten betrieben, die unser Ticketingsystem verwalten und RAG über mein Confluence- und E-Mail-Wissen für semantische Suche ausführen.

Meine Erfahrung umfasst ein breites Spektrum an Netzwerk-Spezialgebieten — vom IP-Backbone mit konvergiertem IMS-/Mobile-Backhaul (Egypt Telecom), über Enterprise-Service-Provider-VPN-/MPLS-Routing und -Tunneling für globale Standorte (Orange Business Services) und Cloud-Backend auf OpenStack-basierter Public Cloud in Europa (Flexible Engine / Huawei CloudStack), bis hin zu meiner vorherigen Rolle in unternehmensseitigen Enterprise-Netzwerken mit Verwaltung von WLAN, Firewalls und VPNs über Rechenzentren und Bürostandorte hinweg (Hyundai Autoever Europe GmbH). Nun bin ich zum OpenStack-Deployment gewechselt und verwalte die Datacenter- und virtuellen OpenStack-Ebenen.

Darüber hinaus hat mir die Arbeit in einem sehr prozessorientierten Umfeld bei Orange Business Services gezeigt, wie man Prozesse etabliert und Best Practices anwendet — vom Change-Management über die Projektimplementierung bis zur Dokumentation der täglichen Arbeit.

## Berufserfahrung

### 1. Senior Private Cloud Engineer (Netzwerke)
- **Unternehmen:** Hyundai Autoever Europe GmbH
- **Standort:** Frankfurt am Main, Deutschland
- **Zeitraum:** 01.06.2026 — heute
- **Anstellungsart:** Vollzeit

Ich arbeite mit einem Arista-Datacenter, das ein OpenStack-Vanilla-Deployment hostet, und verwalte das Netzwerk zwischen dem Datacenter, dem Underlay/Overlay auf Arista-Switches und der OpenStack-Neutron-Schicht. Es ist eine operative Rolle, in der ich Skripte, Automatisierungen und KI-gestützte Automatisierungen zur Optimierung des Tagesgeschäfts entwickle.

**Hersteller:** Arista, Palo Alto, OpenStack, Rancher, Grafana, Zabbix

### 2. Netzwerk-Systemingenieur
- **Unternehmen:** Hyundai Autoever GmbH
- **Standort:** Offenbach, Deutschland
- **Zeitraum:** 07/2023 — 06/2026
- **Anstellungsart:** Vollzeit

Implementierung und Verwaltung von Datacenter- und Enterprise-Infrastruktur, einschließlich der Betreuung mehrerer Kunden mit unterschiedlichen Infrastrukturanforderungen sowie Tätigkeit als Projektmanager für neue Implementierungen.

**Eingesetzte Technologien:** Cisco ISE (2.x & 3.x), Cisco Nexus (Legacy & 9K), Cisco WLC (9800 & 5500), Cisco IOS-basierte Geräte (Legacy und Catalyst 9k), Cisco ASA- & Palo-Alto-Firewalls (Filterung, SSL & IPSec), Cisco DNA Center.

### 3. Cloud als Systems Engineer
- **Unternehmen:** G42 Cloud
- **Standort:** Abu Dhabi, Vereinigte Arabische Emirate
- **Zeitraum:** 03/2023 — 06/2023
- **Anstellungsart:** Vollzeit

Betreuung der Huawei Cloud Stack Cloud (OpenStack-basiert), hauptsächlich Verwaltung der Neutron-Infrastruktur — Fortsetzung des gleichen Wegs wie bei Ericsson und Orange Business Services.

### 4. Cloud-Betriebs- und Automatisierungsingenieur — Netzwerkbereich
- **Unternehmen:** Ericsson
- **Standort:** Kairo, Ägypten
- **Zeitraum:** 11/2022
- **Anstellungsart:** Vollzeit

Einstieg bei Ericsson als Operations Engineer mit Hauptverantwortung für die Automatisierung lästiger Bug-Prüfungen, mit denen Kunden konfrontiert sein können, und für die automatisierte Anwendung von Fixes mit minimalem Kundenaufwand — hauptsächlich mit Python- und Bash-Scripting.

### 5. Public-Cloud-Betriebsingenieur — Netzwerkbereich
- **Unternehmen:** Orange Business Services
- **Standort:** Kairo, Ägypten
- **Zeitraum:** 08/2021 — 10/2022
- **Anstellungsart:** Vollzeit

Arbeit an beiden Teilen der Cloud-DC-Infrastruktur, physisch und virtuell:

- Arbeit an den physischen DCs, die alle Cloud-Dienste hosten, nach aktuellen CLOS-Design-Standards und unter Einsatz von APIs zur Konfiguration und Steuerung von Netzwerkknoten (Router, Switches, Firewalls).
- Verwaltung und Optimierung der Netzwerkkapazität und des Peerings mit dem Orange-Backbone für MPLS- und Internet-Traffic.
- Erfahrung mit verschiedenen Security-Appliances wie VPN-Gateways, Anti-DDoS und WAF — essenziell für jede internetorientierte Lösung, insbesondere für das Hosting regulierungskonformer und kritischer Mandanten.
- Erstmals in meiner Karriere arbeitete ich mit den modernsten Technologien — OpenStack-virtuelle Netzwerke und hocheffiziente virtuelle Netzwerk-Appliances für Security und Load Balancing.
- Arbeit mit klassischen VLANs und neuen VXLAN-VPN, mit mehreren aufeinander abgestimmten Kapselungskriterien.
- Aus der Verwaltung physischer und virtueller Netzwerke heraus arbeitete ich am DC-Routing/-Switching und am Troubleshooting virtueller Netzwerke, da der Verkehr Security-Appliances sowie physische/virtuelle Switches durchläuft — die Netzwerkbetriebs-Perspektive erstreckte sich bis hin zu den Linux-Maschinen.
- Neue DC-Technologien gaben mir die Möglichkeit, von SSH-basiertem Scripting auf NetConf-/REST-API-basierte Aufrufe zu migrieren, die deutlich zuverlässiger und effizienter sind.
- Neu mit Terraform, aber sehr erfahren im Einsatz von Python für API-Interaktionen; zudem mehrere große, selbst initiierte Projekte abgeschlossen (siehe Abschnitt Projekte).

### 6. Senior-Ingenieur für IP-Core-Planung
- **Unternehmen:** TE Data (Telecom Egypt) / WE
- **Standort:** Kairo, Ägypten
- **Zeitraum:** 06/2019 — 07/2021
- **Anstellungsart:** Vollzeit

- Verantwortlich für den Einsatz von Python-Scripting für das Reporting des gesamten Backbone-Netzwerks und für automatisierte Pre- und Post-Checks über ein Gebiet hinweg bei der Migration kritischer Geräte.
- Implementierung von Backbone-gehosteten Diensten und Backhaul-Diensten für Festnetz-, Mobilfunk- und Breitbanddienste mittels L3/L2-VPNs.
- Migration und Implementierung von Backbone-Geräten (P-PE-RR-BNG) mehrerer Hersteller (Cisco, Juniper, Nokia usw.).
- Software-Upgrades geräteübergreifend bei mehreren Herstellern.
- Tiefes Verständnis von BGP, MPLS & OSPF als Underlay für alle gehosteten Dienste.
- Aufgrund der konvergierten Natur des Netzwerks Arbeit mit Mobile-, Festnetz- und Breitband-Backbones wie IMS, EPC und BNGs sowie einer ganzen Reihe von Geräten — inklusive Anbindung verschiedener Security-Geräte (Palo Alto, Cisco ASA, Juniper SRX).

### 7. VPN-Implementierungsingenieur Level 3
- **Unternehmen:** Orange Business Services
- **Standort:** Kairo, Ägypten
- **Zeitraum:** 06/2018 — 06/2019
- **Anstellungsart:** Vollzeit

- Arbeit an einem internationalen, gewaltigen Netzwerk — Wissen über die Verwaltung von Netzen enormer Größenordnung.
- Unterstützung von Kunden über riesige geografische Gebiete und mehrere Sprachen hinweg; jedes betreute Unternehmen war global, was die Verwaltung von Netzwerken über mehrere Autonomous Systems ermöglichte.
- Aufgrund der globalen Reichweite von Orange Business Services Arbeit mit mehreren physischen Technologien, teils in der Ausphasung — etwa ATM und Frame Relay.
- Verwaltung von Kunden-HUB-Standorten mit mehreren einzigartigen Netzwerk-Setups.

### 8. Incident-Management-Spezialist (1st-Line-Engineer)
- **Unternehmen:** Orange Business Services
- **Standort:** Kairo, Ägypten
- **Zeitraum:** 10/2016 — 06/2018
- **Anstellungsart:** Vollzeit

- Mitte der Tätigkeit Wechsel zu Optimierungstechnologien und -geräten wie Riverbed und Ipanema, mit tiefem Wissen über das Verhalten von TCP/IP.
- Aufbau von Kompetenzen in der Betreuung von Kunden aus aller Welt und im Umgang mit Kundenfrust bei Dienstinstabilität.
- Grundlegende Troubleshooting-Kenntnisse zu PE-CE-, LAN- und Wireless-Technologien.

## Sprachkenntnisse

- Englisch — C2
- Deutsch — A2 (in Verbesserung)

## Fähigkeiten

**Networking:** IP-Routing (BGP, MP-BGP, MPLS, OSPF), Switching; Cisco ISE 2.6 & 3.1; Cisco WLC (9800 & 5500); Cisco Catalyst / Nexus 9k; Palo Alto 10.x- & 11.x-Firewalls / GlobalProtect-VPN; Cisco ASA Firewalls & SSL-VPN; Juniper MX-, PTX-Backbone-Router; Juniper SRX Firewalls; NOKIA Router — ADSL-Terminierung; Cisco ASR 9k Backbone-Router — voll konvergierter OSPF-Backbone Ägyptens.

**Cloud & Virtualisierung:** OpenStack Neutron (Orange Flexible Engine, Huawei Cloud Stack); Huawei Cloud Stack — Netzwerke / Neutron; Linux-Administration.

**Automatisierung & KI:** LangChain, N8N, Pi, MCP — agentische Code-Workflows; Terraform (Orange Flexible Engine); Python (Automatisierung von Netzwerk + OpenStack); Python Flask + HTML / CSS / Bootstrap (autodidaktisch).

**Monitoring & Werkzeuge:** Docker, Grafana, Telegraf, InfluxDB (autodidaktisch); SolarWinds NPM-, NTA-Administration.

## Ausbildung und Weiterbildung

### Bachelorabschluss, Computer Engineering
- **Institution:** Arabische Akademie für Wissenschaften, Technologie und Seeverkehr (AASTMT)
- **Standort:** Kairo, Ägypten
- **Zeitraum:** 06/2008 — 11/2013
- **Website:** http://www.aast.edu/en/index.php/
- **Adresse:** P.O. Box 2033, Elhorria, El Moshir Ismail St. (hinter Sheraton Building), 2033, Kairo, Ägypten
- **Studienfach:** Ingenieurwesen, Fertigung und Bau
- **Abschlussnote:** 3,56 / A
- **Anabin Institutionstyp:** Universität privat staatlich anerkannt
- **Anabin Status:** H+

## Führerschein

- Klasse B — deutscher Führerschein
- Ausgestellt am 18.02.2025

## Projekte

### Blog
amroelhusseini.vercel.app — https://amroelhusseini.vercel.app

### MCP-Server
In meiner aktuellen Rolle habe ich eine Reihe von Automatisierungstools mit KI entwickelt, darunter mehrere private und öffentlich gehostete MCP-Server auf GitHub zur Verwaltung von Systemen wie Palo Alto, Cisco, Outlook und ServiceNow — überwiegend privat, aber auch für öffentliche Deployments geeignet. Ich habe diese MCP-Server-Skills aufgebaut, um Automatisierungen auszuführen, insbesondere über N8N.

### Auditing physischer Netzwerke
Bei TE Data und Orange schrieb ich ein multithreaded Python-Skript, um Netzwerkkonfigurationen gegen Standard-Templates zu prüfen. Es war das erste Mal, dass ich die Python-Multiprocessing-Bibliothek nutzte, um mich parallel in Hunderte von Geräten einzuloggen — verkürzte ein 4-Stunden-Audit auf nur 2 Minuten.

### Webanwendung für Netzwerkinventar
Mit Flask, Redis und SQLite baute ich eine Webanwendung zur Speicherung von Chassis-Inventaren im TE-Data-Backbone, abfragbar für Excel- und Web-Reports. Das sparte erhebliche Zeit bei Hardware-Planungsentscheidungen. Um langsame Abfragen bei gleichzeitiger Nutzung zu lösen, führte ich Redis ein, um häufig erzeugte Reports zu cachen.

### Netzwerk-Topologie-Plotter
Durch die Kombination von JavaScript/Jinja2 mit Python-Scripting erstellte ich automatisierte, aktuelle Netzwerktopologien durch Parsen und Generieren von JavaScript-(GoJS)- und SVG-Übersichtsdiagrammen sowie automatisierten XLS-Detaildiagrammen — eingesetzt bei Orange und TE Data.
https://github.com/amrelhusseiny/drawio_network_plot

### Internet-Traffic-Pfade im Backbone
Im Rahmen meiner Backbone-Arbeit bei TE Data baute ich ein Skript, das den Internet-Traffic-Pfad je Region darstellt — automatisch generiert durch Parsen der Backbone-Routing-Tabellen unter Einbeziehung von BGP- und OSPF-Daten zur Bestimmung und Nachverfolgung des Pfades.
`;

/** Full machine-readable CV, English followed by German. */
export const cvMarkdown = `# Curriculum Vitae — Amro ElHusseini

> Machine-readable CV. Plain Markdown, no HTML. Safe to paste into an LLM,
> fetch from a bot, or attach to an application. This file is the canonical
> text version of https://amroelhusseini.vercel.app/cv/

## Identity

- **Name:** Amro ElHusseini
- **Current title:** Senior Private Cloud Engineer (Networks)
- **Current employer:** Hyundai Autoever Europe GmbH
- **Location:** Konstanzer Str. 40, 60386 Frankfurt am Main, Germany
- **Phone / WhatsApp:** +49 152 2517 6681
- **Email:** amroashram@hotmail.com
- **Website:** https://amroelhusseini.vercel.app
- **LinkedIn:** https://www.linkedin.com/in/amro-elhusseini-2a330456/
- **GitHub:** https://github.com/amrelhusseiny
- **Date of birth:** 1991-12-01
- **Nationality:** Egyptian
- **Residence permit:** Niederlassungserlaubnis (YZ7M3MK5V), Germany
- **Work permit:** Germany
- **Driving licence:** Category B, German, issued 2025-02-18
- **Last updated:** ${new Date().toISOString().slice(0, 10)}

---

# English
${EN.trim()}

---

# Deutsch
${DE.trim()}
`;

/** JSON-LD schema.org payload mirroring the visible CV. */
export const cvJsonLd = {
  "@context": "https://schema.org",
  "@type": "Person",
  name: "Amro ElHusseini",
  jobTitle: "Senior Private Cloud Engineer (Networks)",
  url: "https://amroelhusseini.vercel.app/cv/",
  email: "mailto:amroashram@hotmail.com",
  telephone: "+49 152 2517 6681",
  birthDate: "1991-12-01",
  nationality: { "@type": "Country", name: "Egypt" },
  address: {
    "@type": "PostalAddress",
    streetAddress: "Konstanzer Str. 40",
    postalCode: "60386",
    addressLocality: "Frankfurt am Main",
    addressCountry: "DE",
  },
  worksFor: { "@type": "Organization", name: "Hyundai Autoever Europe GmbH" },
  alumniOf: {
    "@type": "EducationalOrganization",
    name: "Arabische Akademie für Wissenschaften, Technologie und Seeverkehr (AASTMT)",
  },
  knowsLanguage: ["English (C2)", "German (A2)"],
  hasOccupation: {
    "@type": "Occupation",
    name: "Senior Private Cloud Engineer (Networks)",
    skills: [
      "IP Routing (BGP, MP-BGP, MPLS, OSPF), Switching",
      "Cisco ISE 2.6 & 3.1",
      "Cisco WLC (9800 & 5500)",
      "Cisco Catalyst / Nexus 9k",
      "Palo Alto 10.x & 11.x Firewalls / GlobalProtect VPN",
      "Cisco ASA Firewalls & SSL VPN",
      "Juniper MX, PTX Backbone Routers",
      "Juniper SRX Firewalls",
      "NOKIA Routers — ADSL Termination",
      "Cisco ASR 9k Backbone Routers — full OSPF converged Egypt backbone",
      "OpenStack Neutron (Orange Flexible Engine, Huawei Cloud Stack)",
      "Huawei Cloud Stack — Networks / Neutron",
      "Linux Administration",
      "LangChain, N8N, Pi, MCP — agentic code workflows",
      "Terraform (Orange Flexible Engine)",
      "Python (automation of network + OpenStack)",
      "Python Flask + HTML / CSS / Bootstrap (self-taught)",
      "Docker, Grafana, Telegraf, InfluxDB (self-taught)",
      "SolarWinds NPM, NTA Administration",
    ],
  },
  subjectOf: { "@type": "WebPage", url: "https://amroelhusseini.vercel.app/cv.md" },
};