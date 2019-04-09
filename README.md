# Latent Space Cartography

Latent Space Cartography (LSC) is a visual analysis tool for mapping and comparing meaningful "semantic" dimensions in latent spaces. This repository contains the source code of LSC and includes three example case studies.

## Citation
If you are interested in this work, please see our research [paper](https://yangliu.life/build/misc/lsc.pdf) and consider citing our work:

```
@article{liu2019-lsc,
 title = {Latent space cartography: Visual analysis of vector space embeddings},
 author = {Yang Liu AND Eunice Jun AND Qisheng Li AND Jeffrey Heer},
 journal = {Computer Graphics Forum (Proc. EuroVis)},
 year = {2019}
}
```

## Demo

You might run LSC on your machine (we only support MacOS at the moment) using one of the three example datasets: `emoji` for image generation, `tybalt` for scientific feature learning, and `glove_6b` for natural language processing.
Here are the steps for running the demo:

1. Clone this repository

2. Run the following commands in your console:
```bash
cd deploy

# replace "tybalt" with the dataset of your choice
./start.sh tybalt
```

3. After the server starts, navigate to http://localhost:5000/#/ in your browser. We strongly recommend using Chrome!

Below are descriptions on the example datasets:

1. `emoji`: image generation. We scraped ~24,000 emoji images from the web, trained several Variational Auto-Encoders (VAEs) and obtained latent spaces capable of hallucinating new emojis. (Warning: this dataset is 3.3 GB in size so it will take a while to download.)
2. `tybalt`: scientific feature learning. The 100-dimensional latent space encodes gene expression in cancer patients, fit using a Variational Auto-Encoder by [Way & Green](https://github.com/greenelab/tybalt).
3. `glove_6b`: natural language processing. These spaces contain the top 10,000 words from pretrained 50-, 100-, 200-, and 300-dimensional [GloVe](https://nlp.stanford.edu/projects/glove/) word embeddings.


## Using LSC on Your Own data
You might also use LSC to explore your own data.
You'll need to supply three components: (1) your data, (2) a server-side config and (3) a client-side config.

### Data

Your data folder holds all the data: latent space coordinates, precomputed t-SNE results, images, etc.

#### Folder Structure
After picking a convenient name for your dataset, create a folder `<project_root>/deploy/data/<dataset>`. Under this directory, you will need to provide the following sub-directories. The first two are required, while the rest are dependent on data types:

- `latent`: contains the latent spaces. Each file is in HDF5 format. It contains a dataset named `latent`, which is an n*m array where n is the number of samples, and m is the number of latent dimensions. The file name should be `latent<dim>.h5`, where dim is the latent dimension.

- `tsne`: contains precomputed t-SNE coordinates. Each file is in HDF5 format. It contains a dataset named `tsne`, which is an n*2 array, where n is the number of samples.

- `umap`: contains precomputed UMAP results. This is optional, because the tool will compute UMAP on the fly if it does not find existing results.

- `images`: if your data type is "image", put all your images here. The image file name should correspond to the index in the input tensor you used to train the model, for example `0.png` is the first row in the input.

- `models`: if your model is generative, put your models here so the tool can reconstruct output. However, you'll probably also need to modify the source code to load your model ...

- `raw.h5`: HDF5 file of the input array (namely, the input to your unsupervised model). This is only required if your data is arbitrary vector, because we will use it to visualize each input sample.

#### Metadata
In addition, you will need to specify some metadata associated with each sample. For example, if each sample is a word, you may want to display which word it is and its frequency count. Such information will then be displayed in the tool, e.g. when the user clicks on a point.

The metadata file is a CSV file. These two fields are required:
- `i` maps back to the row index in the input matrix.
- `name` is the name of this sample. For example, it is the word if your sample is a word. It can be the patient ID if your sample is the gene profile of a patient.

You are free to provide other metadata columns, but remember to specify the schema in config files.

Place the meta file as `<project_root>/deploy/data/<dataset>/meta.csv`. The installation script `use_data.py` will look into this location to import metadata into the appropriate database table.

### Server-side Config

Server-side config tells the tool where to look for your data, as well as other customized behavior to your data type. 

Create a file with the name `config_<dataset>.py` under the `<project_root>/model` folder. Below is an example:

```python
# name of the dataset
# it must be consistent with your data folder name and config file names
dset = 'emoji'

# data type, can be one of ['image', 'text', 'other']
# image: input and output are images (e.g. convolutional VAEs and GANs)
# text: input are words (e.g. word embeddings)
# other: input and output are arbitrary vectors
data_type = 'image'

# (required for "image" type) image specifications
img_rows, img_cols, img_chns = 64, 64, 4
img_mode = 'RGBA'

# train/test split
# [0, train_split) samples are used in training, the rest in testing
train_split = 19500

# distance metrics, can be one of ['l2', 'cosine']
# l2: Euclidean distance
# cosine: Cosine distance
metric = 'l2'

# (required for "other" type) the file name of the input
fn_raw = 'emoji.h5'
# (required for "other" type) the dataset key in the hdf5 file, only used for "other" data type
key_raw = 'emoji' 

# all available latent dimensions
dims = [4, 8, 16, 32, 64, 128]

# database table schema
# meta table schema (order is important)
schema_meta = 'i, name, mean_color, category, platform, version, codepoints, shortcode'
# header table schema
schema_header = None
```

### Client-side Config

Client-side config is a JSON file that customizes the UI. We will provide a default config that you can further build on. After you run the command to add your dataset (in the next subsection), the config will appear as `<project_root>/deploy/configs/config_<dataset>.json`.

Below is an example configuration file. Remove the comments if you copy-paste the following into your JSON file. For the optional items, they usually create a new UI element. Omit the item entirely if you do not need its corresponding functionality.

```javascript
{
  // only samples before train_split will be visualized
  // you can use this to limit the number of samples displayed
  "train_split": 13500,

  // which latent space to display initially
  "initial_dim": 32,

  // which projection method to use initially
  "initial_projection": "t-SNE",

  // database schema
  "schema": {
    // types of each field, can be one of ['categorical', 'numeric']
    "type": {
        "category": "categorical",
        "platform": "categorical",
        "version": "categorical"
        // and more ...
    }
  },
  "rendering": {
    // which field in the meta is used to color the dots in the scatter plot
    // set this to null if you do not want the color channel to encode anything
    "dot_color": "mean_color",

    // the image file extension, only useful for image data type
    "ext": "png"
  },

  // related to the search UI
  "search": {
    // (optional) if true, show a simple search bar in the right panel
    "simple": false,

    // (optional) if true, show a search icon in the bottom toolbar
    // on click, it will open a panel with more advanced search functions
    "advanced": true,

    // which fields to search
    // it becomes a dropdown menu in the advanced search panel
    "by": ["name", "codepoints", "shortcode"],

    // (optional) filter search results by this field
    "filter": "platform"
  },
  
  // (optional) show a filter icon in the bottom toolbar
  "filter": {
    // the fields that can be filtered
    "fields": ["platform", "category", "version"]
  },

  // (optional) display a UI for changing what field is used to color dots
  "color_by": ["platform", "category", "mean_color"],

  // (optional) allow users to customize what field is used as the Y-axis
  // note: "y" refers to the original Y-axis, for example the 1st PC in PCA plot
  "y_axis": ["y", "platform", "category"]
}
```

### Finally ...

Run the following script to add your dataset. It will check necessary files, create database tables, perform precomputation, etc.

```bash
cd deploy
source lsc/bin/activate # if it returns error, run "./start.sh dataset" once
python use_data.py --add <dataset>
```

You can then run `./start.sh <dataset>` to start the server.

## Developer

If you would like to develop LSC further, you might begin by:

1. Clone the repository

2. Useful commands
```bash
cd client

# install dependencies
npm install

# transpile client-side code
npm run dev

# create a virtual environment for the project
pip install virtualenv
virtualenv lsc
source lsc/bin/activate

# install dependencies for the server
pip install -r requirements.txt

# download data
# change <dataset> to be one of [iamge, tybalt, glove_6b]
python use_data.py <dataset> --download

# start the server
python server.py

# switch between datasets
python use_data.py <dataset>

# remove a dataset (warning: danger)
python use_data.py <dataset> --remove

# deploy
npm run deploy
```

3. Navigate to http://localhost:5000/#/ in your browser 
