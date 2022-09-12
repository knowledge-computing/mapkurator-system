
---

# Table of Contents
- [Dataset Card](#dataset-card)
  - [Dataset Description](#dataset-description)
    - [Dataset Download Link](#dataset-download-link)
    - [Dataset Languages](#dataset-languages)
  - [Dataset Structure](#dataset-structure)
    - [Data Fields](#data-fields)
- [Model Card](#model-card)
  - [Model Description](#model-description)
    - [Model Summary](#model-summary)
    - [Model Tags](#model-tags)
    - [Model Input and Output](#model-input-and-output)
- [Additional Information](#additional-information)
  - [Licensing Information](#licensing-information)
  - [Contributions](#contributions)    


# Dataset Card 

## Dataset Description

Map text recognized from the georeferenced Rumsey historical map collection.

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



# Model Card 

## Model Description

A **fully automatic** pipeline to process a large amount of scanned historical map images. **Outputs** include the recognized text labels, label bounding polygons, labels after post-OCR correction and geo-entity identifier in OSM database. 

### Model Summary

- **Orange boxes:** Modules in the pipeline
- **Blue boxes:** Inputs of the modules
- **Green boxes:** Outputs of the modules

<img width="1627" alt="image" src="https://user-images.githubusercontent.com/5383572/189727942-80ad63c6-6c2e-478a-9992-c0f1519a0549.png">


### Model Tags
- Text spotting
- Entity Linking
- Historical maps

# Additional Information

### Licensing Information

MIT License

### Contributions

Thanks to [@zekun-li](https://zekun-li.github.io/),[@Jina-Kim](https://github.com/Jina-Kim), [@MinNamgung](https://github.com/MinNamgung) and [@linyijun](https://github.com/linyijun) for adding this dataset and models