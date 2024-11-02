# OneSOC
OneSoc is a project aimed at building a unified installation script to deploy a Security Operations Center (SOC) in one go, "one shot" style.

## Project Overview

The goal of this project is to create a single installation script that provides flexibility in deploying a SOC. You can either deploy **Wazuh** on a single server or distribute its components (manager, indexer, dashboard) across multiple machines. The script handles the interconnection between components automatically or via a provided configuration file.
The SOC also includes **Suricata** (integrated through SELKS), and the script manages its integration with Wazuh as well.

### Key Features:
- **Flexible Deployment**: Deploy Wazuh as an all-in-one solution on a single machine, or distribute its components across multiple servers.
- **Automated Interconnection**: The script automatically configures communication between Wazuh components or reads from a configuration file.
- **Suricata Integration**: Includes Suricata (via SELKS) and automates its connection to Wazuh for improved network monitoring.
- **Customization & Optimization**: After the installation, the script includes a phase to customize and enhance Wazuh’s parameters and features.
- **Agent Deployment**: Wazuh agents are automatically propagated across the network, with the goal of zero-touch client configuration.

## Components
The following components are deployed by OneSoc:
- **Wazuh**: Open-source security monitoring platform.
  - **Manager**: Manages alerts, security data, and agents.
  - **Indexer**: Stores logs and events for analysis.
  - **Dashboard**: Visualizes security data through a web interface.
- **Suricata**: High-performance network IDS/IPS, integrated through SELKS.

## Requirements 

you need python3.10 or better with pip installed 
  
## Installation

1. Just run:
   ```bash
   git clone https://github.com/flouksac/OneSoc.git && cd OneSoc && sudo python3 OneSOC.py
   ````
2. Enjoy !
