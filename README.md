ApertuRisers SARMaps


SARMaps is an advanced environmental monitoring tool that leverages synthetic aperture radar (SAR) data from the Sentinel satellite constellation to quantify and evaluate long-term ecological damage with newfound insight and comprehensibility.
Traditional optical satellite imagery is limited by light capture and atmospheric conditions in ways that SAR is not. SAR also covers more than just reflected radar rays, capturing backscatter and phase prints, making it a much more powerful tool than ordinary satellite radar. SARMaps We translates these complex radar signatures into understandable, actionable data for regulatory groups, local communities, and environmental researchers.
SAR Applications
SAR Parameter
Ecological Insight
Backscatter Intensity (σ0)
Measures surface roughness and moisture. Used to detect flooded areas, soil exposure, and overall biomass loss.
Polarization (e.g., VV, VH)
Differentiates scattering mechanisms. Used to distinguish between volume scattering (healthy tree canopy) and double-bounce scattering (oil-contaminated trees/soil).
Coherence/Interferometry
Tracks minute structural changes in vegetation over time. Essential for identifying subtle degradation before visible canopy death.

Focus Area: Ecuadorian Oil Spills and SAR Analysis
Oil Spills in Ecuador
The Ecuadorian Amazon, a globally critical biodiversity hotspot, is continually threatened by spills from aging oil infrastructure, including the Trans-Ecuadorian Oil Pipeline System and the Heavy Crude Oil Pipeline. These spills introduce toxic crude oil into delicate biospheres, causing long-term damage to fragile wetlands, rivers, and the rainforest canopy. From a humanitarian perspective, a history of oil spills have led to poisoned environments, animals, and extreme health risks for people (especially indigenous peoples). Major oil spills also lead to substantial economic lapses in certain areas.
SARMaps Role
Immediate Spill Mapping (Water): SAR detects oil spills on river surfaces instantly in the correct polarization. Crude oil on water dampens capillary waves, causing an extreme drop in radar backscatter, which appears as a dark, easily identifiable patch against the surrounding water. This provides near real-time data crucial for emergency response.
Tracking Chronic Canopy Damage (Land): In the dense Amazon, oil spills often contaminate the soil and the base of trees. Polarimetry is key here: a healthy rainforest exhibits high volume scattering (from the dense canopy structure). When oil coats the vegetation or saturates the soil, it dramatically alters the dielectric properties and structure. The SAR signature changes to emphasize double-bounce scattering (signal hits the trunk/ground and then the canopy/trunk). SARMaps tracks changes in polarimetric ratios to precisely map the extent of oil-related dieback and soil exposure, which often precedes visible changes in optical imagery.
Risk Area Identification: By running a Time Series Analysis near pipelines, oil rigs and certain oil pits, SARMaps can identify chronic degradation that might otherwise have easily gone unnoticed—such as early vegetation stress or persistent soil moisture anomalies—that signal infrastructure segments as high-risk areas before the impact gets worse.
Future Plans
Mapping Software Integration: The final output is designed to be a simple, georeferenced layer (e.g., GeoTIFF, vector Shapefile) representing a "Damage Severity Index" or a "High-Risk Zone." This data can be directly ingested into common platforms like ArcGIS and QGIS used by government and conservation agencies.
Cloud-Native Processing: By leveraging cloud-based platforms (like Google Earth Engine or Amazon Web Services) for data processing, SAR-Guard is highly scalable. The methodology can be replicated across any region on Earth with SAR coverage (e.g., South-East Asia, the Arctic) to monitor a variety of ecological threats, including illegal logging, mining impacts, and wetland changes.
Open Data Policy: Our use of free and publicly available SAR data (e.g., Copernicus, Sentinel-1) ensures that the monitoring system remains cost-effective and accessible to stakeholders regardless of budget, promoting greater transparency and accountability.
A core design principle of SARMaps is the focus on scalability and integration. SARMaps focused on integration existing technologies into one central ecosystem, much like NASA's FIRMs for fire detection or CEMS for general disasters, which truly embody the spirit of this project. SARMaps has great potential for impact, especially in low-development, low-infrastructure environments. This potential for impact is precisely why SARMaps expansion and integration into existing mapping and emergency software is an essential next step to mitigating environmental lapses like in Ecuador and the world.
