<template>
  <div class="container">
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

<script>
  import axios from "axios"

  export default {
    data() {
      return {
        loginData: {
            username:null,
            password:null,
        },
        valid: true
      }
    },
    methods: {
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
    font-size: 42px;
    color: #526488;
    word-spacing: 5px;
    padding-bottom: 15px;
  }

  .links {
    padding-top: 15px;
  }

</style>
