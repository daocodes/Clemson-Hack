# 🌍 ApertuRisers SARMaps  
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-blue)
![Platform](https://img.shields.io/badge/Platform-Cloud--Native-orange)
![Data Source](https://img.shields.io/badge/Data-Sentinel--1%20SAR-blueviolet)
![Region](https://img.shields.io/badge/Focus-Ecuadorian%20Amazon-green)

---

## 🧩 Overview

**SARMaps** (developed by *ApertuRisers*) is an advanced **environmental monitoring platform** that leverages **Synthetic Aperture Radar (SAR)** data from the **Sentinel satellite constellation** to quantify and visualize **long-term ecological damage** with unprecedented accuracy and clarity.

Traditional optical satellite imagery is often limited by weather, cloud cover, and daylight conditions.  
**SAR**, however, operates independently of these constraints — capturing **backscatter intensity**, **polarization**, and **interferometric phase** data that reveal surface changes invisible to optical sensors.

SARMaps translates these **complex radar signatures** into **intuitive, actionable data** for:
- 🌱 Environmental researchers  
- 🧑‍💼 Government & regulatory agencies  
- 🧭 Local and indigenous communities  

---

## 🛰️ SAR Applications and Parameters

| **SAR Parameter** | **Measured Property** | **Ecological Insight** |
|--------------------|------------------------|------------------------|
| **Backscatter Intensity (σ₀)** | Surface roughness, moisture, and dielectric constant | Detects **flooded regions**, **soil exposure**, and **biomass loss** |
| **Polarization (VV, VH)** | Scattering mechanism (surface, volume, or double-bounce) | Differentiates between **healthy canopies (volume scattering)** vs. **oil-contaminated vegetation/soil (double-bounce)** |
| **Coherence / Interferometry (InSAR)** | Phase stability over time | Identifies **structural changes** in vegetation and land surfaces before visible degradation occurs |

---

## 🌎 Focus Area: Ecuadorian Oil Spills and SAR Analysis

### 🛢️ Oil Spills in Ecuador
The **Ecuadorian Amazon** — one of the most biodiverse ecosystems on Earth — faces continual threats from oil spills due to aging infrastructure like the:
- *Trans-Ecuadorian Oil Pipeline System (SOTE)*  
- *Heavy Crude Oil Pipeline (OCP Ecuador)*  

**Impact Statistics:**
- 🧾 *Over 1,000 oil spill incidents* reported since 1972  
- 💧 *More than 500,000 barrels of crude oil* released into Amazonian waterways  
- 👥 *Hundreds of indigenous communities* exposed to toxic contamination  
- 🐍 *Severe declines in aquatic biodiversity* and long-term soil toxicity

Oil spills cause:
- Destruction of wetlands and river ecosystems  
- Chronic vegetation loss and canopy stress  
- Public health crises (especially among indigenous peoples)  
- Long-term economic degradation of affected areas  

---

## 🧠 SARMaps Role and Capabilities

### ⚡ 1. Immediate Spill Mapping (Water)
SAR detects oil films on river surfaces **within hours** of an incident.  
- Oil dampens **capillary waves**, sharply reducing backscatter intensity.  
- These areas appear as **dark patches** in VV/VH polarization imagery.  
- Enables **real-time emergency response** and resource deployment.

### 🌳 2. Tracking Chronic Canopy Damage (Land)
In dense rainforest regions, optical imagery often fails to reveal sub-canopy contamination.  
SARMaps uses **polarimetry** to:
- Track changes in **volume vs. double-bounce scattering** ratios  
- Identify oil-coated vegetation and soil absorption zones  
- Map **vegetation dieback** and **soil exposure** months before visible canopy loss  

### ⚠️ 3. Risk Area Identification (Predictive Monitoring)
Using **time-series SAR analysis**, SARMaps highlights high-risk zones along:
- Pipelines  
- Storage pits  
- Oil rigs  

By detecting **persistent moisture anomalies**, **reduced coherence**, or **progressive backscatter decline**, the system can flag **infrastructure sections likely to fail**, allowing **preventive maintenance and policy intervention**.

---

## 📊 Analytical Workflow

```mermaid
graph LR
    A[Sentinel-1 SAR Data] --> B[Preprocessing & Speckle Filtering]
    B --> C[Polarimetric Decomposition]
    C --> D[Change Detection & Time-Series Analysis]
    D --> E[Damage Severity Index Mapping]
    E --> F[Integration into ArcGIS/QGIS Platforms]
