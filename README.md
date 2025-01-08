# OneSOC

Deploy a SOC in one go, "one shot" style.

> **⚠️ OneSOC is at a very early stage of development. Expect incomplete functionality and potential bugs. ⚠️**
---
## Project Overview

The goal of this project is to create a unified framework installation program that provides flexibility in deploying all components of a SOC (Security Operations Center).

Our focus is to build a SOC entirely on open-source tools, offering a powerful, transparent,
free, and customizable solution for individuals and organizations of all sizes.

---

## How OneSOC Works

### The Five Main Actions

The script is designed to be user-friendly and versatile, with five main actions:

- **Info**: Displays information about a component on your system (e.g., version, location).
- **Health-Check**: Verifies the health and configuration of components.
- **Install**: Installs one or more SOC components.
- **Configure**: Configures components to work together, applies custom settings, adds detection rules...
- **Repair**: Repairs components that are malfunctioning.

Currently, the focus is on **Info**, **Install**, and **Configure**, with plans to expand to include **Uninstall**, **Update**, and more.

### Philosophy

We aim to minimize deployment time by automating as much as possible with a short command. During the first run, OneSOC installs:

On the first run :
- we install the correct version of python,
- create a virtual environment, 
- install all the python dependencies, 
- run OneSOC in interactive mode. 

Some components, like IDS, may require system-level changes (e.g., network configuration). 
While we strive for minimal impact, keep in mind that some components can change your system comportment. 
So don't forget to look at the documentation of the components you want to install.

This project is also cross-platform, so you can use it on Windows, Linux, and MacOS but you won't be able to deploy all components on all OS.
Because of that we will provide a list of compatible components for each OS automatically.
Even if this project is cross-platform, the business part of the SOC is thought for Linux systems.

**_Why not rely only on containers?_**
>Because we want to be able to deploy any component on the more systems as possible, and we don't want to be limited by the container technology.
but when it's feasible we will use containers or have both options.

### Technologies

The script is written in Python because it is a versatile language that is easy to read and write, cross-platform, 
and will allow us to keep the codebase clean, short, and maintainable.
---
## Run OneSOC

### ⚠️ Disclaimer ⚠️

> First of all, because it's all about security, **We highly recommend reviewing the script before running it**, 
a SOC is a critical component of your infrastructure and you should know what you are doing.
Onesoc is open-source so you can check the code and see what it does. 

**We can not be responsible for any damage caused by the script.**

### Requirements 

To run the script, you MUST run the script as an administrator or with sudo privileges.

### Recommended Installation

We recommend that you run the script on a fresh installation of your system, (except for the client agents).

**Server installation**:

The easiest way to deploy a SOC is to use github to clone the repository and run the shell script that will install onesoc dependencies and the script itself.
It can be done with the following command for the first install:

```bash
git clone https://github.com/flouksac/OneSoc.git && chmod +x ./OneSoc/run_linux.sh && sudo ./OneSoc/run_linux.sh 
```

If you prefer to run the script directly with python, you should have :
- downloaded the repository or cloned it
- be in the same path that contains the onesoc directory
- have python3.10 or higher installed
- create a virtual environment and activate it
- install from the binary of python in the virtual environment the requirements.txt file with pip
- run the script with python

After installing the dependencies, this can be done with the following commands:
```
git clone https://github.com/flouksac/OneSoc.git
python3.12 -m venv onesoc_venv
source onesoc_venv/bin/activate
pip install -r onesoc/requirements.txt
sudo python onesoc/src/main.py -h
```

**Agent installation**:

Because Python isn't installed by default on all systems, we recommend you using the shell script on macos and linux agents and the powershell script on windows agents.
Git won't be installed on the agents, so you can download the repository as a zip file and extract it on the agent.
then you can run the script with the following commands:

On Linux
```bash
chmod +x ./OneSoc/run_linux.sh && sudo ./OneSoc/run_linux.sh 
```

On MacOS
```bash
chmod +x ./OneSoc/run_macos.sh && sudo ./OneSoc/run_macos.sh 
```

On Windows, in powershell as admin
```powershell
. .\OneSoc\run_windows.ps1 
```

### Usage
To use the script, you just have to run it and follow the instructions given by the interactive command line interface.
Also you can use the script in a non-interactive mode by providing the options as arguments thanks to flags. 

if you are not sure about which mode to use, keep in mind that interactive mode is the default mode and the easiest to use,
The flag mode is more for automation and scripting to don't have to request user input at all.

If you have already installed some components, the script will try to detect them and use them if needed.

Because you may encounter some bugs, we recommend you to use the interactive mode for now and add the -v flag to have more information about what the script is doing.
the higher the verbosity value is, the more information you will have (0-4).

---

## SOC Core Architecture

Our concept is to deploy a SOC build around **Wazuh** as a core component.

Wazuh is the best open-source XDR (Extended Detection and Response) and SIEM (Security Information and Event Management) solution in our opinion.
We chose it because of its scalability, effectiveness, configurability, large community, and connectivity with other tools.

You can either deploy **Wazuh** on a single server or distribute its components (manager, indexer, dashboard) 
across multiple machines.
The script handles the interconnection between components via a provided configuration file or manual input.

Because we believe that network monitoring is essential for a SOC, 
we decided to integrate an IDS (Intrusion Detection System) into it.
So we chose **SELKS** as our IDS solution, which is a Suricata container with an ELK stack.
By design we configure wazuh to work with SELKS to improve network monitoring.

### Key Features:
- **Flexible Deployment**: Deploy Wazuh as an all-in-one solution on a single machine, 
  or distribute its components across multiple servers.
- **Automated Interconnection**: The script automatically configures communication between Wazuh components or 
  reads from a configuration file.
- **Suricata Integration**: Includes Suricata (via SELKS) and 
  automates its connection to Wazuh for improved network monitoring.
- **Customization & Optimization**: After the installation, 
  the script includes a phase to customize and enhance Wazuh’s parameters and features.
- **Agent Deployment**: Wazuh agents are automatically propagated across the network, 
  with the goal of zero-touch client configuration.

### Components
Our first focus is deploying theses following components:

SIEM:
- **Wazuh**: Open-source security monitoring platform.
  - **Indexer**: Stores logs and events for analysis.
  - **Manager**: Manages alerts, security data, and agents.
  - **Dashboard**: Visualizes security data through a web interface.

IDS:
- **SELKS**: Suricata-IDS container with ELK stack.
  - **Suricata**: Open-source IDS/IPS engine.
  - **Elasticsearch**: Distributed, RESTful search and analytics engine.
  - **Logstash**: Server-side data processing pipeline.
  - **Kibana**: Data visualization dashboard for Elasticsearch.
  - **Arkime**: Full packet capture and network forensic analysis tool.

In the futur we will add more components like:
- **DFIR-IRIS**: Ticketing system for incident response team.
- **Keepass**: Password manager for storing secrets
- **MISP**: Threat intelligence platform for sharing indicators of compromise.
- **Shuffle**: SOAR platform for security automation and orchestration.
- **greenbone**: Vulnerability scanner for detecting security issues.
- **snort**: Network intrusion detection system.
- **cyberchef**: Web app for decoding, encoding, and analyzing data.

We may also thinks (much much later) about components like:
- **atomic-red-team**: Automated testing for security controls.
- **caldera**: Automated adversary emulation system.
- **Infection Monkey**: Breach and attack simulation tool.
- **nmap**: Network discovery and security auditing tool.
- **velociraptor**: Endpoint visibility and collection tool.
- **CISO assistant**: Security policy and compliance management tool.
- **opencti**: Threat intelligence platform for sharing indicators of compromise.
- **dfir-orc**: Incident response and digital forensics tool.
- **The honeynet project**: Some of their tools for honey pots and threat intelligence.
  - **T-POT**: All-in-one honeypot platform.
  - **GreadyBear**: 
  - **Buffalogs**: Impossible time travel logins
  - **intelOwl**: Cyber threat intelligence unified platform.
  - **honeyscanner**: Honey pot security scanner.
  - **conpot**: ICS/SCADA honeypot.
- **Lynis**: Security auditing tool for Unix-based systems.




