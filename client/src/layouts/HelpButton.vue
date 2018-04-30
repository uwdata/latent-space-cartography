<template>
  <div class="d-inline-block">
    <!--Button-->
    <div class="bd-icon" v-b-modal.model-help>
      <i class="fa fa-fw fa-question-circle-o"></i>
    </div>

    <!--Modal-->
    <b-modal id="model-help" title="Latent Space Explorer" class="text-dark">
      <h5>Introduction</h5>
      <p>
        You are viewing the data of <b>latent spaces</b>, a compressed stage in
        generative machine learning models. This tool allows
        you to grasp the structure of the latent space, for instance assessing how
        logos cluster. Additionally, you can isolate a subset of logos and see how
        they relate.
      </p>

      <h5 class="mt-4">How to Use?</h5>
      <p>
        Each dot represents a logo, colored by its average image color.
        Its position is given by 2-dimensional PCA or t-SNE.
      </p>
      <ul>
        <li>Brush to see a group of logos.</li>
        <li>Click on a logo to see its details.</li>
        <li>Holding <b>SHIFT</b>, you can zoom and pan around.</li>
        <li>Add logos of your interests to the right panel, and you can perform PCA over just the set.</li>
      </ul>
    </b-modal>
  </div>
</template>

<script>
  export default {
    name: 'HelpButton'
  }
</script>

<style>
  .bd-icon {
    font-size: 1.5em;
    cursor: pointer;
  }
</style>
