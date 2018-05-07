### How to Train a New Model

1. Create a configuration file like `config_logo.py`. Before running each python file below,
modify the import statement to point to my current config.
2. Run `train.py` to train a variational autoencoder. I may want to set epochs to 1 for sanity check.
3. Run `read.py` to store latent dimensions.
4. Run `tsne.py` to pre-compute t-SNE.
5. Copy everything in the data folder to my local machine.
6. Run `util/create_symlink.sh` to generate symbolic links from client data folder to data.
7. Modify the hardcoded dataset flag in client and server code:
    - Set the value of `dset` in `server.py`.
    - Create a config object in `config.js` in the client code.
