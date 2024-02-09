
## About mapKurator System

**[New]**: Our documentation website for mapKurator system is up! [https://knowledge-computing.github.io/mapkurator-doc/](https://knowledge-computing.github.io/mapkurator-doc/#/)

[mapKurator](https://dl.acm.org/doi/abs/10.1145/3589132.3625579) is a fully automatic pipeline developed by the [**Knowledge Computing Lab**](https://knowledge-computing.github.io/) at the **University of Minnesota** to process a large number of scanned historical map images. Outputs include the recognized text labels, label bounding polygons, labels after post-OCR correction, and a geo-entity identifier from OpenStreetMap. 

### mapKurator textspotter repository
Please refer to this link to check all the spotter models in mapKurator : [Spotter-v2](https://github.com/knowledge-computing/mapkurator-spotter), [PALETTE](https://github.com/knowledge-computing/mapkurator-palette)

---------

## Data Card - Derived Dataset Processed by mapKurator System 

Map text recognized from the [Rumsey historical map collection](https://www.davidrumsey.com/) with 57K georeferenced maps. 

### Dataset Download Link

Contact Zekun (li002666@umn.edu) or Yijun (lin00786@umn.edu) for the data.

### Dataset Languages

English

### Language Creators:

Machine-generated

## Dataset Structure

### Data Fields

<img src="https://user-images.githubusercontent.com/5383572/188784909-10cd04fd-4b61-4205-a563-33d20f9026db.png" width="700">

### Output File Name

Output GeoJSON file is named after the external ID of original map image.

<img src="https://user-images.githubusercontent.com/5383572/188785367-446690fd-76fc-47db-b2ae-a1fac4fc61d6.png" width="700">

### Citation
```
@inproceedings{kim2023mapkurator,
  title={The mapKurator System: A Complete Pipeline for Extracting and Linking Text from Historical Maps},
  author={Kim, Jina and Li, Zekun and Lin, Yijun and Namgung, Min and Jang, Leeje and Chiang, Yao-Yi},
  booktitle={Proceedings of the 31st ACM International Conference on Advances in Geographic Information Systems},
  pages={1--4},
  year={2023}
}
```

### Licensing Information

CC BY-NC 2.0

