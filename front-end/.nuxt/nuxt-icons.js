export default async function (ctx, inject) {
  const moduleOptions = {"accessibleIcons":true,"iconProperty":"$icon","icons":{"64":"\u002F_nuxt\u002Ficons\u002Ficon_64.8TduH9Br4bb.png","120":"\u002F_nuxt\u002Ficons\u002Ficon_120.8TduH9Br4bb.png","144":"\u002F_nuxt\u002Ficons\u002Ficon_144.8TduH9Br4bb.png","152":"\u002F_nuxt\u002Ficons\u002Ficon_152.8TduH9Br4bb.png","192":"\u002F_nuxt\u002Ficons\u002Ficon_192.8TduH9Br4bb.png","384":"\u002F_nuxt\u002Ficons\u002Ficon_384.8TduH9Br4bb.png","512":"\u002F_nuxt\u002Ficons\u002Ficon_512.8TduH9Br4bb.png"}}
  inject(moduleOptions.iconProperty.replace('$', ''), retrieveIcons(moduleOptions.icons))
}

const retrieveIcons = icons => size => icons[size] || ''
