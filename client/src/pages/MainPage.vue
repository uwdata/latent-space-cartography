<template>
  <div class="row">
    <div class="col-7">
      <div class="landing-left d-flex flex-column justify-content-between">
        <div>
          <!--Title-->
          <div class="landing-title mb-3">
            <span class="first">L</span>atent
            Space Cartography
          </div>
          <div class="ml-3 mb-5 landing-subtitle">
            Visual analysis of vector space embeddings
          </div>

          <!--Buttons-->
          <div class="ml-3 landing-button-group">
            <router-link to="/analogy" tag="a" class="btn btn-lg btn-danger">
              <i class="fa fa-magic mr-2"></i>
              Demo
            </router-link>
            <a class="btn btn-lg btn-secondary text-light" href="mailto:yliu0@uw.edu">
              <i class="fa fa-question mr-2"></i>
              Contact Us
            </a>
          </div>
        </div>

        <!--Footer-->
        <div class="mb-2">
          <hr>
          <div class="m-3">
            <a href="http://idl.cs.washington.edu/" target="_blank">
              <img src="build/idl-logo.png" alt="Interactive Data Lab" class="landing-idl"/>
            </a>
            <span class="text-muted ml-3">Interactive Data Lab, University of Washington</span>
          </div>
        </div>
      </div>
    </div>
    <div class="col-5">
      <div class="text-muted landing-right">
        <p>
          Latent spaces, vector spaces produced by machine learning algorithms, can learn important semantic features of the data.
        </p>
        <p>
          These meaningful structures are buried in the multi-dimensional space.
          How do we explore the space to discover and verify these relationships?
        </p>
        <p>
          You may ask ...
        </p>
        <p>
          How do input data distribute in the space? Do they form meaningful clusters?
        </p>
        <p>
          What are the neighboring points of my favorite sample?
        </p>
        <p>
          Here is a subset of interesting samples. What are the relationships among them?
        </p>
        <p>
          What are the key differences between two conceptual groups?
        </p>
        <p class="d-none">
          Can I find analogies similar to "King - Man - Woman = Queen"?
        </p>
        <p>...</p>
        <p>
          Our visual analysis tool let you explore the answers interactively.
          Hit the demo button to start!
        </p>
        <p v-if="dataset==='tybalt'">
          Dataset: a latent space of gene expression data in cancer patients,
          fit using a Variational Auto-Encoder by
          <a href="https://github.com/greenelab/tybalt" target="_blank">Way & Greene</a>
        </p>
        <p v-else-if="dataset==='glove_6b'">
          Dataset: pre-trained
          <a href="https://nlp.stanford.edu/projects/glove/" target="_blank">GloVe</a> word embeddings.
        </p>
        <p v-else-if="dataset==='emoji'">
          Dataset: latent spaces of emoji images, fit via convolutional Variational Autoencoders.
          The 24,000 input images were crawled from
          <a href="https://emojipedia.org/" target="_blank">Emojipedia</a>.
        </p>
        <p v-else>Dataset: {{dataset}}</p>
      </div>
    </div>
  </div>
</template>

<script>
  import {CONFIG} from '../controllers/config'

  export default {
    name: 'MainPage',
    data() {
      return {
        dataset: CONFIG.dataset,
        menus: [
          {link: '/tsne', name: 't-SNE'},
          {link: '/splom', name: 'PCA - Scatter Plots Matrix'},
          {link: '/analogy', name: 'Analogy'},
          {link: '/pca', name: 'PCA - 2 Dimensions'},
          {link: '/scatter_canvas', name: 'Scatter Plot in Canvas'},
          {link: '/scatter_svg', name: 'Scatter Plot in SVG'}
        ]
      }
    }
  }
</script>

<style>
  .landing-title {
    font-size: 3em;
    font-weight: 300;
  }

  .landing-title .first {
    font-size: 5em !important;
    line-height: 1px;
  }

  .landing-subtitle {
    font-size: 1.5em;
  }

  .landing-button-group a{
    border-radius: 2rem !important;
    margin-right: 1em;
  }

  .landing-left {
    padding-left: 120px;
    padding-top: 200px;
    height: 100vh;
  }

  .landing-right {
    padding-top: 110px;
    padding-right: 120px;
    height: calc(100vh - 6rem);
    overflow-y: auto;
  }

  .landing-idl {
    max-height: 32px;
  }
</style>
