<template>
  <div class="container">
    <b-col>
          <h1 class="title">gin-proc</h1>
          <p class="subtitle">Workflow automation for GIN</p>
          <b-list-group>
  <b-list-group-item class="d-flex justify-content-between align-items-center">
    Total Jobs
    <b-badge variant="primary" pill>14</b-badge>
  </b-list-group-item>

  <b-list-group-item class="d-flex justify-content-between align-items-center">
    Workflow Inputs: {{workflowFiles}}
    <b-badge variant="primary" pill>2</b-badge>
  </b-list-group-item>

  <b-list-group-item active class="d-flex justify-content-between align-items-center">
    Backpushing: {{backpushFiles}}
  </b-list-group-item>
</b-list-group>
    </b-col>
    <b-col>
    <div>
      <b-alert v-show="repos.length == 0" show variant="danger">No repos found</b-alert>
      <b-form @submit="onSubmit" @reset="onReset" @submit.stop.prevent>
      <b-form-group
        id="input-group-1"
        label="Workflow File:"
        label-for="input-1"
        description="We'll never share your data with anyone else."
      >
        <b-form-input
          id="input-1"
          v-for="x in workflowCounter" :key="x"
          v-model="workflowFiles[x]"
          type="text"
          required
          placeholder="Enter your workflow file"
        ></b-form-input>
    <b-input-group-append>
      <b-button variant="info" v-on:click="addWorkflowFile">Add File</b-button>
    </b-input-group-append>
      </b-form-group>

      <b-form-group id="input-group-2" label="Files to Annex" label-for="input-2">
        <b-form-input
          id="input-2"
          v-for="x in anexxFilesCounter" :key="x"
          v-model="annexFiles[x]"
          required
          placeholder="Enter file to annex"
        ></b-form-input>
    <b-input-group-append>
      <b-button variant="info" v-on:click="addBackpushFile">Add File</b-button>
    </b-input-group-append>
      </b-form-group>

      <b-form-group id="input-group-2" label="Backpush Files" label-for="input-2">
        <b-form-input
          id="input-2"
          v-for="x in backpushCounter" :key="x"
          v-model="backpushFiles[x]"
          required
          placeholder="Enter your backpush file"
        ></b-form-input>
    <b-input-group-append>
      <b-button variant="info" v-on:click="addBackpushFile">Add File</b-button>
    </b-input-group-append>
      </b-form-group>

      <b-form-group id="input-group-3" label="Repository:" label-for="input-3">
        <b-form-select
          id="input-3"
          v-model="form.repo"
          :options="repos"
          required
        ></b-form-select>
      </b-form-group>

      
          <b-input-group>
    <b-input-group-text slot="prepend">Commit Message</b-input-group-text>
    <b-form-input v-model="form.commitMessage" />
  </b-input-group>
      <b-form-group id="input-group-4" label="Notifications:" label-for="input-4">
        <b-form-checkbox-group v-model="form.notifications" id="checkboxes-4">
          <b-form-checkbox value="slack">Slack Notifs</b-form-checkbox>
          <b-form-checkbox value="email">Email Notifs</b-form-checkbox>
        </b-form-checkbox-group>
      </b-form-group>
      <b-button type="submit" :variant="action.variant" :disabled="!action.btn_state">
    <b-spinner v-if="action.active" small />
    {{action.text}}
  </b-button>
      <b-button type="reset" variant="danger">Start Over</b-button>
    </b-form>
      <div class="mt-3">
    <b-button-group>
      <b-button v-b-toggle.result variant="outline-dark">Logs</b-button>
      <b-button v-b-toggle.debug variant="outline-dark" v-b-popover.hover="'Click to read debug data'" title="Realtime Inputs">Debug</b-button>
    </b-button-group>
  </div>
    <b-collapse id="result" class="mt-2">
    <b-card class="mt-3" header="Execution Logs">
      <pre class="m-0">{{ execution_status }}</pre>
    </b-card>
    </b-collapse>
    <br>
    <b-collapse id="debug" class="mt-2">
    <b-card class="mt-3" header="Debugging: Realtime Inputs">
      <pre class="m-0">{{ form }}</pre>
    </b-card>
    </b-collapse>
    </div>
    </b-col>
  </div>
</template>

<script>
import axios from "axios"
var API = "http://127.0.0.1:8000"

export default {

  async asyncData ({params}) {
    let repos = await axios.get(API + '/repos')
    return { repos: repos.data }
    },
  data() {
    return {
      form: {
        repo: null,
        notifications: [],
        commitMessage: null,
      },
      backpushFiles: {},
      workflowFiles: {},
      workflowCounter: 1,
      backpushCounter: 1,
      annexFiles: {},
      anexxFilesCounter: 1,
      execution_status: "Waiting for your workflow",
      action: {
        text: 'Submit',
        btn_state: true,
        active: false,
        variant: 'primary',
      }
    }
  },
  methods: {
    addWorkflowFile() {
      this.workflowCounter += 1
    },
    addBackpushFile() {
      this.backpushCounter += 1
    },
    onReset() {
      this.form = {
      workflowFiles: null,
        backpushFiles: null,
        annexFiles: null,
        repo: null,
        notifications: [],
        commitMessage: null,
      },
      this.action = {
        text: 'Submit',
        btn_state: true,
        active: false,
        variant: 'primary',
      },
      this.execution_status = "Waiting for your workflow"
      },
    onSubmit() {
     axios({
            method: "post",
            url: API + "/execute",
            data: {
        repo: this.form.repo,
        notifications: [],
        workflowFiles: this.workflowFiles,
        backpushFiles: this.backpushFiles,
        annexFiles: this.annexFiles,
        commitMessage: this.commitMessage,
            }
          })
          .then(
            this.action.text = "Processing", this.action.active = true, this.action.btn_state = false,
            this.execution_status = this.execution_status + "\nDesigning workflow...",
            )
          .then((response) => {
            if (response.status == 500) {
              this.execution_status = this.execution_status + "\nFailed. Execution aborted.",
              this.action.text = "Failed", this.action.active = false, this.action.btn_state = true, this.action.variant = 'danger'
              }
            else if (response.status == 200) {
              this.execution_status = this.execution_status + "\n" +response.data,
              this.action.text = "Access Drone", this.action.active = false, this.action.btn_state = true, this.action.variant = 'info'
              }
            })
    },
    }
}
</script>

<style>
.container {
  margin: 0 auto;
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  text-align: center;
}

.title {
  font-family: 'Quicksand', 'Source Sans Pro', -apple-system, BlinkMacSystemFont,
    'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  display: block;
  font-weight: 300;
  font-size: 100px;
  color: #35495e;
  letter-spacing: 1px;
}

.subtitle {
  font-weight: 300;
  font-size: 32px;
  color: #526488;
  word-spacing: 5px;
  padding-bottom: 15px;
}

.links {
  padding-top: 15px;
}
</style>
