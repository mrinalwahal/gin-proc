<template>
    <Header>
      <sui-menu secondary style="font-size:14px">
        <sui-menu-item><a href="/"><img src="../../../images/favicon.png" height="30" width="28" /></a></sui-menu-item>
      <sui-menu-item link href="/">Dashboard</sui-menu-item>
      <sui-menu-item link>FAQ</sui-menu-item>
      <sui-menu-item icon="help circle" link>Help</sui-menu-item>
      <sui-menu-item link href="https://github.com/G-Node/gin-proc">Contribute</sui-menu-item>
      <sui-menu-item link href="https://github.com/G-Node/gin-proc/issues/new" icon="bug">Report</sui-menu-item>
      <sui-menu-menu position="right">
         <sui-dropdown item icon="user outline" simple>
        <sui-dropdown-menu>
         <sui-dropdown-header>Signed-in as @{{this.$auth.user.username}}</sui-dropdown-header> 
         <sui-dropdown-divider />
          <sui-dropdown-item icon="power" v-on:click="this.$auth.logout">Logout</sui-dropdown-item>
        </sui-dropdown-menu>
      </sui-dropdown>

      </sui-menu-menu>
    </sui-menu>
    </Header>
</template>

<script>
export default {

}
</script>

<style>

</style>
