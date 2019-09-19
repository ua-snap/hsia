## HSIA
#### Prepare raw NSIDC_0051 Monthly Sea Ice Concentration Grids for Ingest to the [Historical Sea Ice Atlas](http://seaiceatlas.snap.uaf.edu/)

![hsia](https://github.com/ua-snap/hsia/blob/master/hsia-splash.png)

- The data used for this is distributed from: https://catalog.data.gov/dataset/sea-ice-concentrations-from-nimbus-7-smmr-and-dmsp-ssm-i-ssmis-passive-microwave-data-v001/resource/88927a8a-eeb2-4510-8f08-a4b9cd6bff16

- Step-by-step instructions on getting this tool up and running is located [here](https://github.com/ua-snap/hsia/blob/master/how_to_run.md) which links to the `how_to_run.md` file in the root of this repository.

- See `example.py` for a quick look at how to run the application. Basic use is to change the year(s) and output_path
in that script and point to the `.bin` files downloaded from the NSIDC-0051. **requires a NASA EarthData Login for access to the files.**

- See the [`run2018_hsia.py`](https://github.com/ua-snap/hsia/blob/master/run2018_hsia.py) file for the way we post-processed for the 2018 data update.
