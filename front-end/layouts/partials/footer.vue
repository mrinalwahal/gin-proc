<template>
    <Footer>
        <br><br>
        <div style="text-align:center">
            <sui-list horizontal>
                <sui-list-item v-for="item in items" :key="item.name">
                <a :href="item.url">{{item.name}}</a>
                </sui-list-item>
            </sui-list>
    <p class="tagline">Coded with &hearts; at INCF</p>
  </div>
        <br>
    </Footer>
</template>

<script>
export default {

    data() {
        return {
            items: [
                {'name': '© G-Node, 2016-2019', 'url': 'http://www.g-node.org/'},
                {'name': 'About', 'url': 'https://gin.g-node.org/G-Node/Info/wiki/about'},
                {'name': 'Imprint', 'url': 'https://gin.g-node.org/G-Node/Info/wiki/imprint'},
                {'name': 'Contact', 'url': 'https://gin.g-node.org/G-Node/Info/wiki/contact'},
                {'name': 'Terms of Use', 'url': 'https://gin.g-node.org/G-Node/Info/wiki/Terms+of+Use'},
                {'name': 'Datenschutz', 'url': 'https://gin.g-node.org/G-Node/Info/wiki/Datenschutz'},
                ]
        }
    }

}
</script>

<style>
.tagline {
    font-family: Menlo, Consolas, DejaVu Sans Mono, monospace;
    font-size: 12px;
}
</style>
