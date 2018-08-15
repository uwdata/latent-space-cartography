<template>
  <div class="d-inline-block">
    <!--Button-->
    <div class="bd-icon" v-b-modal.model-help>
      <i class="fa fa-fw fa-question-circle-o"></i>
    </div>

    <!--Modal-->
    <b-modal id="model-help" title="Latent Space Explorer" class="text-dark">
      <!--Help information for image data-->
      <div class="bd-group" v-if="data_type === 'image'">
        <h5>Introduction</h5>
        <p>
          You are viewing the data of <b>latent spaces</b>, a compressed stage in
          generative machine learning models. This tool allows
          you to grasp the structure of the latent space, for instance assessing how
          data points cluster. Additionally, you can define <b>attribute vectors</b>
          and perform vector arithmetic.
        </p>
        <p class="text-center text-muted">
          <b>Man - Woman + Queen = King</b>
        </p>
        <p>
          This is a classic attribute vector example in NLP.
          Can you discover similar relationships in the dataset?
        </p>

        <h5 class="mt-4">How to Use?</h5>
        <p>
          Each dot represents a data point, colored by its average image color.
          Its position is given by 2-dimensional PCA or t-SNE.
        </p>
        <ul>
          <li>Brush to inspect cluster structure.</li>
          <li>Search to find a specific data point.</li>
          <li>Add similar items to a group and perform PCA over just the subset, to see how they relate within a group.</li>
          <li>Define a vector between two groups and apply the analogy to any data point.</li>
        </ul>
      </div>

      <!--Help information for other data-->
      <div class="bd-group" v-if="data_type === 'other'">
        <h5>Introduction</h5>
        <p>
          You are viewing the data of <b>latent spaces</b>, a compressed stage in
          unsupervised machine learning models. This tool allows
          you to grasp the structure of the latent space, for instance assessing how
          data points cluster. Additionally, you can define <b>attribute vectors</b>
          to deduce the difference between two groups.
        </p>

        <h5 class="mt-4">How to Use?</h5>
        <p>
          Each dot represents a data point.
          Its position is given by 2-dimensional PCA or t-SNE.
        </p>
        <ul>
          <li>Brush to inspect cluster structure.</li>
          <li>Search to find a specific data point.</li>
          <li>Add conceptually relevant items to a group.</li>
          <li>Define a vector between two groups to understand their differences.</li>
        </ul>

        <h5 class="mt-4">Advance Features</h5>
        <p>Interested in how a subset of data points relate to each other?
        Add them to a group, and hit "isolate".</p>
        <p>Already have a list of data points you want to investigate? Try "upload".</p>
      </div>
    </b-modal>
  </div>
</template>

<script>
  import {CONFIG} from '../controllers/config'

  export default {
    name: 'HelpButton',
    data () {
      return {
        data_type: CONFIG.data_type
      }
    }
  }
</script>

<style>
  .bd-icon {
    font-size: 1.5em;
    cursor: pointer;
  }
</style>
