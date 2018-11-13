# latent-space-cartography
Visual analysis tools for mapping and orienting latent spaces (reduced dimensionality vector spaces produced by unsupervised learning).

## I want to see how it works

We provide example datasets on three different data types / scenarios:

1. `emoji`: image generation. We scraped ~24,000 emoji images from the web, trained several Variational Auto-Encoders (VAEs) and obtained latent spaces capapble of hallucinating new emojis.
2. `tybalt`: scientific feature learning. The 100-dimensional latent space encodes gene expression in cancer patients, fit using a Variational Auto-Encoder by [Way & Green](https://github.com/greenelab/tybalt).
3. `glove_6b`: natural language processing. These spaces contain the top 10,000 words from pretrained 50-, 100-, 200-, and 300-dimensional [GloVe](https://nlp.stanford.edu/projects/glove/) word embeddings.

To start visualizing any one of the above datasets, follow these steps (using `tybalt` as an example):

1. Clone the repository
2. Run these commands (only tested on macOS, might work on Linux)
```bash
cd deploy

# install dependencies
pip install virtualenv
virtualenv lsc_env
source lsc_env/bin/activate
pip install -r requirements.txt

# download data
python use_data.py tybalt --download

# start the server
python server.py
```
4. Navigate to http://localhost:5000/#/ in your browser

The above commands are necessary only for first time setup. After that, you can view a downloaded dataset by the following stpes (again using `tybalt` as an example):

```bash
cd deploy
python use_data.py tybalt
source lsc_env/bin/activate
python server.py
```

## I have my own data
You'll need to supply three componenets: (1) your data, (2) server side config and (3) client side config.

### Data
TODO: folder structure

TODO: meta data, and database

### Server Side Config

Create a file with the name `config_<dataset>.py` under the `<project_root>/model` folder. Then run `python use_data.py <dataset>` to switch to this dataset.

Below is an example configuration file:

```python
# name of the dataset
# it must be consistent with your data folder name and config file names
dset = 'emoji'

# data type, can be one of ['image', 'text', 'other']
# image: input and output are images (e.g. convolutional VAEs and GANs)
# text: input are words (e.g. word embeddings)
# other: input and output are arbitrary vectors
data_type = 'image'

# image specifications (only valid for image data type)
img_rows, img_cols, img_chns = 64, 64, 4
img_mode = 'RGBA'

# train/test split
# [0, train_split) samples are used in training, the rest in testing
train_split = 19500

# distance metrics, can be one of ['l2', 'cosine']
# l2: Euclidean distance
# cosine: Cosine distance
metric = 'l2'

# the file name containing the input
fn_raw = 'emoji.h5'
# the dataset key in hdf5 file
key_raw = 'emoji' 

# all available latent dimensions
dims = [4, 8, 16, 32, 64, 128]

# database table schema
# meta table schema (order is important)
schema_meta = 'i, name, mean_color, category, platform, version, codepoints, shortcode'
# header table schema, only used for "other" data type
schema_header = None
```

### Client Side Config

Create a file with the name `config_<dataset>.json` in `<project_root>/deploy/configs/` folder. The file name needs to be consistent with your data folder name and the server config python file name.

Below is an example configuration file. Remove the comments if you copy-paste the following into your json file. For the optional items, they usually create a new UI element. Omit the item entirely if you do not need its corresponding functionality.

```javascript
{
  // name of the dataset
  // it must be consistent with your data folder name and config file names
  "dataset": "emoji",

  // data type, can be one of ['image', 'text', 'other']
  "data_type": "image",

  // only samples before train_split will be visualized
  "train_split": 13500,

  // which latent space to display initially
  "initial_dim": 32,

  // which projection method to use initially
  "initial_projection": "t-SNE",

  // all the available latent dimensions
  "dims": [4, 8, 16, 32, 64, 128],

  // database schema
  "schema": {
    // types of each field, can be one of ['categorical', 'numeric']
    "type": {
        "category": "categorical",
        "platform": "categorical",
        "version": "categorical"
        // and more ...
    },

    // meta table schema
    "meta": ["i","name", "mean_color", "category", "platform", "version", "codepoints", "shortcode"]
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

## I want to code

1. Clone the repository

2. Ask @yyyliu for data and a database dump

3. Useful commands
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

# start the server
npm run start

# deploy
npm run deploy
```

4. Navigate to http://localhost:5000/#/ in your browser 
