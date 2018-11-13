# latent-space-cartography
Visual analysis tools for mapping and orienting latent spaces (reduced dimensionality vector spaces produced by unsupervised learning).

### I want to see how it works

We provide example datasets on three different data types / scenarios:

1. `emoji`: image generation. We scraped ~24,000 emoji images from the web, trained several Variational Auto-Encoders (VAEs) and obtained latent spaces capapble of hallucinating new emojis.
2. `tybalt`: scientific feature learning. The 100-dimensional latent space encodes gene expression in cancer patients, fit using a Variational Auto-Encoder by [Way & Green](https://github.com/greenelab/tybalt).
3. `glove_6b`: natural language processing. These spaces contain the top 10,000 words from pretrained 50-, 100-, 200-, and 300-dimensional [GloVe](https://nlp.stanford.edu/projects/glove/) word embeddings.

To start visualizing any one of the above datasets, follow these steps (using `emoji` as an example):

1. Clone the repository
2. Run these commands (only tested on macOS, might works on Linux)
```
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

```
cd deploy
python use_data.py tybalt
python server.py
```

### I want to use it on my own data
TODO

### I want to code

1. Clone the repository

2. Ask @yyyliu for data and a database dump

3. Useful commands
```
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
