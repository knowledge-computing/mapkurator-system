
## About mapKurator System

**[New]**: Our documentation website for mapKurator system is up! [https://knowledge-computing.github.io/mapkurator-doc/](https://knowledge-computing.github.io/mapkurator-doc/#/)

mapKurator is a fully automatic pipeline developed by the [**Knowledge Computing Lab**](https://knowledge-computing.github.io/) at the **University of Minnesota** to process a large number of scanned historical map images. Outputs include the recognized text labels, label bounding polygons, labels after post-OCR correction, and a geo-entity identifier from OpenStreetMap.

### mapKurator textspotter repository
Please refer to this link to check all the spotter models in mapKurator : [https://github.com/knowledge-computing/mapkurator-spotter](https://github.com/knowledge-computing/mapkurator-spotter)

---------

## Data Card - Derived Dataset Processed by mapKurator System 

Map text recognized from the [Rumsey historical map collection](https://www.davidrumsey.com/) with 57K georeferenced maps. 

### Dataset Download Link

- **Original Map Images:**  https://www.davidrumsey.com/
- **Processed Output:** https://s3.msi.umn.edu/rumsey_output/geojson_testr_syn_54119.zip

### Dataset Languages

English

### Language Creators:

Machine-generated

## Dataset Structure

### Data Fields

<img src="https://user-images.githubusercontent.com/5383572/188784909-10cd04fd-4b61-4205-a563-33d20f9026db.png" width="700">

### Output File Name

Output geojson file is named after the external ID of origina map image.

<img src="https://user-images.githubusercontent.com/5383572/188785367-446690fd-76fc-47db-b2ae-a1fac4fc61d6.png" width="700">

### Licensing Information

CC BY-NC 2.0

