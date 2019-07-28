<template>
<<<<<<< HEAD
<div>
  <sui-container>

      <sui-message header="Heads Up!" style="text-align:left">
        <sui-list bulleted>
          <sui-list-item>Don't separate files by commas. Use the `+` button to add a new file.</sui-list-item>
          <sui-list-item>Write file paths from your project's root. Use nested notation "<span class="log">subfolder/file</span>" if required.</sui-list-item>
          <sui-list-item>Go home and thank INCF for making your life easier!</sui-list-item>
        </sui-list>
      </sui-message>

      <sui-divider />

      <transition>
     <sui-message
     v-if="action.complete"
      color="info"
      content="Check your Drone service for updates."
      dismissable
      @dismiss="dismissCompletionMessage"
      />
      </transition>
      <!--
      <sui-progress
      v-if="action.progress > 100"
      state="success"
      :percent="action.progress"
      size="small"
    />
    -->
      <sui-message
      v-if="repos.length == 0"
      color="red"
      header="We have a problem!"
      content="You don't seem to have any repositories."
      />

        <sui-form @submit.stop.prevent @submit="onSubmit" @reset="onReset">
          <sui-grid>
            <sui-grid-row>
          <sui-grid-column :width="8" textAlign="left">
            <sui-form-field>
              <label>
                <i class="icon file alternate outline" />
                Workflow files *
                <a style="float:right; color:black" data-inverted='' data-tooltip="Files will be executed in the same order you add them in.">
                  <i class="icon help circle" /> </a>
                <i class="icon plus" style="float:right" v-on:click="workflowCounter += 1" />
                <i class="icon minus" style="float:right" v-if="workflowCounter > 1" v-on:click="workflowCounter -= 1" /></label>
              <sui-input v-for="x in workflowCounter" :key="x" v-model="workflowFiles[x]" required />
            </sui-form-field>
            <sui-form-field>
              <label>
                <i class="icon file alternate outline" />
                Annex files
                <a style="float:right; color:black" data-inverted='' data-tooltip="If no files are mentioned, then all required files will be annexed."><i class="icon help circle" /> </a>
                <i class="icon plus" style="float:right" v-on:click="annexCounter += 1" />
                <i class="icon minus" style="float:right" v-if="annexCounter > 1" v-on:click="annexCounter -= 1" />
                </label>
              <sui-input v-for="x in annexCounter" :key="x" v-model="annexFiles[x]"></sui-input>
            </sui-form-field>
            <sui-form-field>
              <label>
                <i class="icon file alternate outline" />
                Backpush files
                <a style="float:right; color:black" data-inverted='' data-tooltip="These are the output files which will be pushed to a separate gin-proc branch in your repo."><i class="icon help circle" /> </a>
                <i class="icon plus" style="float:right" v-on:click="backpushCounter += 1" />
                <i class="icon minus" style="float:right" v-if="backpushCounter > 1" v-on:click="backpushCounter -= 1" /></label>
              <sui-input v-for="x in backpushCounter" :key="x" v-model="backpushFiles[x]"></sui-input>
            </sui-form-field>
            </sui-grid-column>
          <sui-grid-column :width="8" textAlign="left">
            <sui-form-field>
              <label><i class="icon folder outline" />Repository</label>
              <sui-dropdown placeholder="Choose One" selection :options="repos" v-model="form.repo" />
            </sui-form-field>
            <sui-form-field>
              <label><i class="icon paper plane outline" />Commit Message</label>
              <sui-input v-model="form.commitMessage" />
            </sui-form-field>
            <sui-form-field>
              <label><i class="icon bell outline" />Notifications</label>
              <sui-checkbox
              v-for="notification in form.notifications" 
              :key="notification.name"
              toggle 
              v-model="notification.value"> <sui-icon :name="notification.icon" /> {{notification.name}} &emsp;</sui-checkbox>
            </sui-form-field>
            </sui-grid-column>
            </sui-grid-row>
            <sui-grid-row>
              <sui-grid-column :width="8" textAlign="left">
                <i class="icon cog blue loading" v-if="action.active" />
          <sui-button type="submit" size="small" compact="true" color="green" :disabled="action.active">Submit</sui-button>
          <sui-button type="reset" size="small" compact="true" basic="true" color="red">Reset</sui-button>
          </sui-grid-column>
              <sui-grid-column :width="8" textAlign="right">
          <span is=sui-button size="small" compact="true" basic="true" icon="archive" v-on:click="logs = !logs">Logs</span>
          <span is=sui-button size="small" compact="true" basic="true" icon="code" v-on:click="debug = !debug">Debug</span>
          <span is=sui-button size="small" compact="true" basic="true" icon="user secret" v-on:click="dev = !dev">Dev</span>
          </sui-grid-column>
          </sui-grid-row>
            <sui-grid-row>
              <sui-grid-column :width="16" textAlign="left">
                <sui-divider />

                <sui-segment inverted v-show="logs">
            <p class="log" v-for="log in  execution_status" :key="log">{{log}}</p>
                </sui-segment>
                <sui-segment inverted v-show="debug">
            <div class="log">
            <p>Form: {{ form }}</p>
            <p>Workflow Files: {{ workflowFiles }}</p>
            <p>Backpush Files: {{ backpushFiles }}</p>
            <p>Annex Files: {{ annexFiles }}</p>
            </div>
                </sui-segment>
                <sui-segment inverted v-show="dev">
            <p class="log">
              Logged In: {{this.$auth.loggedIn}} <br>
              Username: {{this.$auth.user.username}} <br>
              Token: {{$nuxt.$auth.getToken('local')}}
            </p>
                </sui-segment>
          </sui-grid-column>
          </sui-grid-row>
          </sui-grid>
        </sui-form>


  </sui-container>
=======
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

      <b-form-group 
      id="input-group-2" 
      label="Files to Annex" 
      label-for="input-2"
      description="No annex inputs will simply get all the annex files."
      >
        <b-form-input
          id="input-2"
          v-for="x in anexxFilesCounter" :key="x"
          v-model="annexFiles[x]"
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
>>>>>>> 2e79cf169fdc3345ce863ac2426f531b4d28c04c
  </div>
</template>

<script>
<<<<<<< HEAD
  import axios from "axios"
  var API = "http://127.0.0.1:8000"

  export default {

    async asyncData({
      params
    }) {
      let repos = await axios.get(API + '/repos')
      return {
        repos: repos.data
      }
    },
    data() {
      return {
        form: {
          repo: null,
          notifications: [{
            'name': 'Slack',
            'value': false,
            'icon': 'slack hash'
          }, {
            'name': 'Email',
            'value': false,
            'icon': 'envelope outline'
          }],
          commitMessage: 'gin-proc is awesome',
        },
        backpushFiles: {},
        workflowFiles: {},
        workflowCounter: 1,
        backpushCounter: 1,
        annexFiles: {},
        annexCounter: 1,
        logs: false,
        debug: false,
        dev: false,
        execution_status: ["Waiting for your workflow."],
        action: {
          text: 'Submit',
          btn_state: true,
          active: false,
          variant: 'primary',
          progress: 0,
          complete: false,
        }
      }
    },
    methods: {
      dismissCompletionMessage() {
        this.action.complete = !this.action.complete
      },
      onReset() {
        this.form = {
            repo: null,
            notifications: [{
            'name': 'Slack',
            'value': false
          }, {
            'name': 'Email',
            'value': false
          }],
            commitMessage: 'gin-proc is awesome',
          },
          this.workflowFiles = {},
          this.backpushFiles = {},
          this.annexFiles = {},
        this.workflowCounter = 1,
        this.backpushCounter = 1,
        this.annexCounter = 1,
          this.action = {
            text: 'Submit',
            btn_state: true,
            active: false,
            variant: 'primary',
            progress: 0
          },
          this.execution_status = ["Waiting for your workflow"]
      },
      onSubmit() {
        this.action.progress += 10,
        axios({
            method: "post",
            url: API + "/execute",
            data: {
              repo: this.form.repo,
              notifications: this.form.notifications,
              workflowFiles: this.workflowFiles,
              backpushFiles: this.backpushFiles,
              annexFiles: this.annexFiles,
              commitMessage: this.form.commitMessage,
            }
          })
          .then(
            this.action.text = "Processing", this.action.active = true, this.action.btn_state = false, this.action
            .progress += 50,
            this.execution_status.push("Designing workflow..."),
          )
          .then((response) => {
            if (response.status == 500) {
              this.execution_status.push("Failed. Execution aborted."),
                this.action.text = "Failed", this.action.active = false, this.action.btn_state = true, this.action
                .variant = 'danger'
            } else if (response.status == 200) {
              this.execution_status.push(response.data),
                this.action.text = "Access Drone", this.action.active = false, this
                .action.variant = 'info', this.action.progress = 100,
                this.action.complete = true
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

  .log {
    font-family: Menlo, Consolas, DejaVu Sans Mono, monospace;
    font-size: 12px;
  }
=======
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
        commitMessage: 'gin-proc is awesome',
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
      workflowFiles: {},
        backpushFiles: {},
        annexFiles: {},
        repo: null,
        notifications: [],
        commitMessage: 'gin-proc is awesome',
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
        notifications: this.form.notifications,
        workflowFiles: this.workflowFiles,
        backpushFiles: this.backpushFiles,
        annexFiles: this.annexFiles,
        commitMessage: this.form.commitMessage,
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
>>>>>>> 2e79cf169fdc3345ce863ac2426f531b4d28c04c
</style>
