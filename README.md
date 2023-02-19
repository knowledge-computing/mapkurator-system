
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

### Model Details
- **ImageCropping** module divides huge map images (>10K pixels) to smaller image patches (1K pixels) so that TextSpotter could process.

- **PatchTextSpotter** uses a state-of-the-art network architecture [TESTR](https://github.com/mlpc-ucsd/TESTR) for detecting and recognizing text labels on image patches. Due to the lack of annotated samples for training, we create a set of synthetic maps to mimic the text styles (e.g., font, spacing, orientation) in the real historical maps. We place the location names from OpenStreetMap on a map by considering the shape of the location geometry and merge the text with various background styles extracted from the Rumsey collection maps. We train the model with these unlimited synthetic maps and apply the model to the historical maps.

- **PatchtoMapMerging** is the module to merge the patch-level spotting results into map-level. Output polygons can be loaded in QGIS for visualization, and they should be aligned with the *ungeorefernced* map image. **Note:** QGIS is **not able to show JP2 file** directly. JP2 should be converted to JPEG before loading in QGIS. 

- **GeocoordinateConverter** converts the text label bounding polygons from image coordinates system to geocoordinates system. Note: polygons in both coordinate systems are saved in the output. 

- **PostOCR** helps to verify the output and correct misspelled words from PatchTextSpotter using the OpenStreetMap dictionary. PostOCR module finds words' candidates using [fuzzy query function](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-fuzzy-query.html) from elasticsearch, which contains the place name attribute from the Openstreetmap dictionary. Once PostOCR module identifies words' candidates, the module picks one candidate by the word popularity from the dictionary.

- **EntityLinker** links each map text to the candidate geo-entities in the OpenStreetMap. The entity linking retrieves the candidates that satisfy two criteria: 1) the recognized text from the text spotter contains the geo-entities' name 2) the geocoordinates of detected bounding polygons intersect with the geo-entities' geometry. (Geo-coordinates are obtained from GeocoordConverter)


### How To Use
All the modules can be launched from `run.py`. All the outputs will be saved in the `expt_name` subfolder in `output_folder` specified in the input arguments. 

```
usage: run.py [-h] [--map_kurator_system_dir MAP_KURATOR_SYSTEM_DIR] [--text_spotting_model_dir TEXT_SPOTTING_MODEL_DIR]
              [--sample_map_csv_path SAMPLE_MAP_CSV_PATH] [--output_folder OUTPUT_FOLDER] [--expt_name EXPT_NAME] [--module_get_dimension]
              [--module_gen_geotiff] [--module_cropping] [--module_text_spotting] [--module_img_geojson] [--module_geocoord_geojson] [--module_entity_linking]
              [--module_post_ocr] [--spotter_model {abcnet,testr}] [--spotter_config SPOTTER_CONFIG] [--spotter_expt_name SPOTTER_EXPT_NAME] [--print_command]

optional arguments:
  -h, --help            show this help message and exit
  --map_kurator_system_dir MAP_KURATOR_SYSTEM_DIR
  --text_spotting_model_dir TEXT_SPOTTING_MODEL_DIR
  --sample_map_csv_path SAMPLE_MAP_CSV_PATH
  --output_folder OUTPUT_FOLDER
  --expt_name EXPT_NAME
  --module_get_dimension
  --module_gen_geotiff
  --module_cropping
  --module_text_spotting
  --module_img_geojson
  --module_geocoord_geojson
  --module_entity_linking
  --module_post_ocr
  --spotter_model {abcnet,testr}
                        Select text spotting model option from ["abcnet","testr"]
  --spotter_config SPOTTER_CONFIG
                        Path to the config file for text spotting model
  --spotter_expt_name SPOTTER_EXPT_NAME
                        Name of spotter experiment, if empty using config file name
  --print_command
  ```

### Model Tags
- Text spotting
- Entity Linking
- Historical maps


# Additional Information

### Licensing Information

MIT License

### Contribution and Acknowledgement

Thanks to [@zekun-li](https://zekun-li.github.io/),[@Jina-Kim](https://github.com/Jina-Kim), [@MinNamgung](https://github.com/MinNamgung) and [@linyijun](https://github.com/linyijun) for adding this dataset and models. 

Thanks to [TESTR](https://github.com/mlpc-ucsd/TESTR) for an open-source text spotting model. 
