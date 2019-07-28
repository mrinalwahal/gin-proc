<template>
  <div class="container">
<<<<<<< HEAD
    <sui-grid>
      <sui-grid-column :width="8" textAlign="left">
        <p class="title">gin-proc</p>
        <p class="subtitle">Workflow automation for GIN</p>
      </sui-grid-column>
      <sui-grid-column :width="8" verticalAlign="middle">
        <sui-form equalWidth @submit="login" @submit.stop.prevent>
            <sui-form-field>
              <sui-input v-model="loginData.username" type="text" placeholder="Elon Musk" icon="user" />
            </sui-form-field>
            <sui-form-field>
              <sui-input v-model="loginData.password" type="password"
                placeholder="I'm_the_greatest_inventor_of_all_time" icon="key" />
            </sui-form-field>
          <sui-form-field>
            <sui-label style="font-family: Menlo, Consolas, DejaVu Sans Mono, monospace;">Use your GIN credentials only.
            </sui-label>
          </sui-form-field>
          <br>
          <sui-button type="submit" animated color="black" basic fluid size="small">
            <sui-button-content visible>Login</sui-button-content>
            <sui-button-content hidden>
              <sui-icon name="right arrow" />
            </sui-button-content>
          </sui-button>
        </sui-form>
      </sui-grid-column>
    </sui-grid>
</div></template>
=======
    <div>
      <b-form inline @submit="login" @submit.stop.prevent>
        <label id="inline-form-input-name" class="sr-only">Username</label>
        <b-input id="inline-form-input-name" class="mb-2 mr-sm-2 mb-sm-0" v-model="loginData.username" placeholder="Jane Doe" />

        <label class="sr-only" for="inline-form-input-username">Password</label>
        <b-input-group class="mb-2 mr-sm-2 mb-sm-0">
          <b-input id="inline-form-input-username" type="password" v-model="loginData.password" placeholder="Password"></b-input>
        </b-input-group>

        <b-button variant="outline-success" type="submit">Login</b-button>
      </b-form>
          <b-form-text v-if="valid" >
      Use your GIN credentials to login.
    </b-form-text>
          <b-form-text v-else style="color:red !important">
      Invalid credentials
    </b-form-text>
    </div>
  </div>
</template>
>>>>>>> 2e79cf169fdc3345ce863ac2426f531b4d28c04c

<script>
  import axios from "axios"

  export default {
<<<<<<< HEAD
    layout: 'login',
    data() {
      return {
        loginData: {
          username: null,
          password: null,
=======
    data() {
      return {
        loginData: {
            username:null,
            password:null,
>>>>>>> 2e79cf169fdc3345ce863ac2426f531b4d28c04c
        },
        valid: true
      }
    },
    methods: {
<<<<<<< HEAD
      login() {
        this.$auth.loginWith('local', {
          data: {
            username: this.loginData.username,
            password: this.loginData.password
          }
        })
      }
=======
      login()
{          axios({
            method: "post",
            url: "http://127.0.0.1:8000/login",
            data: this.loginData
          }).then((response) => {
            if (response.status == 200) {this.$router.push({path: '/'})}
            else this.valid = false
          })
          .catch(this.valid = false)
}
>>>>>>> 2e79cf169fdc3345ce863ac2426f531b4d28c04c
    }
  }

</script>

<style>
  .container {
    margin: 0 auto;
<<<<<<< HEAD
    min-height: 80vh;
=======
    min-height: 100vh;
>>>>>>> 2e79cf169fdc3345ce863ac2426f531b4d28c04c
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
<<<<<<< HEAD
    font-size: 80px;
    color: black;
=======
    font-size: 100px;
    color: #35495e;
>>>>>>> 2e79cf169fdc3345ce863ac2426f531b4d28c04c
    letter-spacing: 1px;
  }

  .subtitle {
    font-weight: 300;
<<<<<<< HEAD
    font-size: 30px;
    color: slategray;
=======
    font-size: 42px;
    color: #526488;
>>>>>>> 2e79cf169fdc3345ce863ac2426f531b4d28c04c
    word-spacing: 5px;
    padding-bottom: 15px;
  }

  .links {
    padding-top: 15px;
  }

</style>
