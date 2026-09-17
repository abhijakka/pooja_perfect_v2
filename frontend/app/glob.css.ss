:root {
	--blush: #f7d5df;
	--blush-light: #fff7f8;
	--rose: #d5537d;
	--rose-dark: #8f3658;
	--deep: #4a2734;
	--muted: #756b70;
	--gold: #c8943d;
	--green: #4c8b65;
	--border: #eadde2;
	--shadow: 0 14px 38px rgba(74, 39, 52, .1);
	--shadow-soft: 0 8px 24px rgba(74, 39, 52, .07);
}

* { box-sizing: border-box; }
html { scroll-behavior: smooth; background: #fffdfb; }
body {
	margin: 0;
	color: #2e282c;
	background: radial-gradient(circle at 0 0, rgba(246, 207, 220, .24), transparent 23%), radial-gradient(circle at 100% 12%, rgba(243, 226, 191, .16), transparent 19%), #fffdfb;
	font-family: Georgia, serif;
	-webkit-font-smoothing: antialiased;
	overflow-x: hidden;
}
button, input, select { font: inherit; }
button { border: 0; cursor: pointer; }
a { color: inherit; text-decoration: none; }
.icon { width: 1em; height: 1em; display: block; fill: none; stroke: currentColor; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }
.search-suggestions { position: absolute; top: calc(100% + 9px); left: 0; right: 0; z-index: 9000; overflow: hidden; background: #fff; border: 1px solid var(--border); border-radius: 16px; box-shadow: 0 18px 48px rgba(74,39,52,.16); }
.search-suggestions__head { display: flex; align-items: center; justify-content: space-between; gap: 10px; padding: 10px 13px; background: #fffafb; border-bottom: 1px solid var(--border); font: 9px Arial, sans-serif; }
.search-suggestion { width: 100%; display: flex; align-items: center; gap: 10px; padding: 9px 11px; background: #fff; border-bottom: 1px solid #f3eaed; text-align: left; }
.search-suggestion:last-child { border-bottom: 0; }
.search-suggestion:hover { background: #fff4f7; }
.search-suggestion-image { width: 49px; height: 49px; flex: 0 0 49px; overflow: hidden; background: linear-gradient(145deg,#fff3f6,#f5ded8); border-radius: 11px; }
.search-suggestion-image img { width: 100%; height: 100%; display: block; object-fit: cover; }
.search-suggestion-info { min-width: 0; flex: 1; }
.search-suggestion-name { display: block; overflow: hidden; color: var(--deep); font: 800 10px/1.3 Arial, sans-serif; white-space: nowrap; text-overflow: ellipsis; }
.search-suggestion-meta { display: flex; align-items: center; gap: 6px; margin-top: 4px; overflow: hidden; color: var(--muted); font: 7.5px Arial, sans-serif; white-space: nowrap; }
.search-suggestion-price { color: var(--rose-dark); }
.search-view-button { flex: 0 0 auto; padding: 7px 10px; color: var(--rose-dark); background: #fff3f6; border: 1px solid #edd6df; border-radius: 9px; font: 900 7.5px Arial, sans-serif; }

@keyframes pp-logo { from { opacity: 0; transform: translateY(15px) scale(.95); } to { opacity: 1; transform: translateY(0) scale(1); } }
@keyframes pp-float { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-6px); } }
@keyframes pp-text { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
@keyframes pp-progress { 0% { transform: translateX(-130%); } 50% { transform: translateX(120%); } 100% { transform: translateX(300%); } }
.pp-loader { position: fixed; inset: 0; z-index: 99999; display: flex; align-items: center; justify-content: center; background: radial-gradient(circle at 50% 40%, #fff 0, #fff7f9 40%, #f7d5df 100%); }
.pp-loader-content { width: 90%; max-width: 360px; text-align: center; }
.pp-loader-logo { color: var(--deep); font-size: 43px; font-weight: 700; letter-spacing: -1.5px; animation: pp-logo .8s ease both; }
.pp-loader-logo span { color: var(--rose); }
.pp-loader-symbol { position: relative; width: 82px; height: 82px; display: flex; align-items: center; justify-content: center; margin: 28px auto 0; color: var(--gold); background: radial-gradient(circle, #fff 0, #fff5f7 50%, #f7d5df 100%); border-radius: 50%; box-shadow: 0 12px 35px rgba(74,39,52,.12); animation: pp-float 2s ease-in-out infinite; }
.pp-loader-ring { position: absolute; width: 104px; height: 104px; border: 2px solid transparent; border-top-color: var(--rose); border-right-color: var(--gold); border-radius: 50%; animation: spin 1s linear infinite; }
.pp-loader-symbol > span { position: relative; z-index: 1; font: 38px Arial, sans-serif; }
.pp-loader-text { margin-top: 28px; color: #6a3a4d; font: 700 11px Arial, sans-serif; letter-spacing: 1.4px; text-transform: uppercase; animation: pp-text .8s .2s ease both; }
.pp-loader-track { width: 155px; height: 3px; overflow: hidden; margin: 16px auto 0; background: rgba(213,83,125,.14); border-radius: 999px; }
.pp-loader-track span { display: block; width: 45%; height: 100%; background: linear-gradient(90deg, var(--gold), var(--rose), var(--gold)); border-radius: 999px; animation: pp-progress 1.2s ease-in-out infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

.top-bar { padding: 9px 15px; color: #fff; background: linear-gradient(90deg, #432430, #5a3043 45%, #432430); text-align: center; font: 600 11px Arial, sans-serif; }
.navbar { position: sticky; top: 0; z-index: 1000; min-height: 74px; display: flex; align-items: center; gap: 22px; padding: 12px clamp(16px, 4vw, 60px); background: rgba(255, 255, 255, .94); border-bottom: 1px solid var(--border); box-shadow: 0 4px 24px rgba(72, 39, 53, .035); backdrop-filter: blur(15px); }
.logo { white-space: nowrap; color: var(--deep); font-size: 27px; font-weight: 700; }
.logo span { color: var(--rose); }
.search-box { position: relative; flex: 1; max-width: 680px; margin: auto; }
.search-box input { width: 100%; height: 46px; padding: 0 52px 0 18px; color: #2e282c; background: #fffafc; border: 1px solid var(--border); border-radius: 25px; outline: 0; }
.search-box input:focus { border-color: #df99b1; box-shadow: 0 0 0 4px rgba(214, 83, 125, .08); }
.search-button { position: absolute; top: 5px; right: 5px; width: 36px; height: 36px; display: grid; place-items: center; color: var(--deep); background: linear-gradient(145deg, #f7d5df, #efbdcb); border-radius: 50%; }
.nav-actions { display: flex; gap: 7px; }
.icon-button { position: relative; width: 42px; height: 42px; display: grid; place-items: center; color: #5a3042; background: #fff7f9; border: 1px solid rgba(234, 223, 227, .82); border-radius: 50%; box-shadow: var(--shadow-soft); }
.icon-button:hover { background: var(--blush); transform: translateY(-1px); }
.badge, .mobile-bottom-nav-badge { position: absolute; min-width: 17px; height: 17px; display: grid; place-items: center; padding: 0 4px; color: #fff; background: var(--rose); border-radius: 20px; font: 700 9px Arial, sans-serif; }
.badge { top: -2px; right: -1px; }
.category-nav { position: sticky; top: 74px; z-index: 999; display: flex; gap: 0; padding: 0 48px; overflow-x: auto; white-space: nowrap; background: rgba(255, 255, 255, .96); border-bottom: 1px solid var(--border); scrollbar-width: none; }
.category-nav::-webkit-scrollbar { display: none; }
.category-nav a { position: relative; flex: 0 0 auto; min-height: 48px; display: inline-flex; align-items: center; padding: 0 18px; color: #5e5258; font: 500 13px Arial, sans-serif; }
.category-nav a:hover { color: var(--rose-dark); }
.category-nav a::after { content: ""; position: absolute; right: 18px; bottom: 4px; left: 18px; height: 2px; background: var(--rose); transform: scaleX(0); transition: transform .2s ease; }
.category-nav a:hover::after { transform: scaleX(1); }

.hero, .section { width: min(1400px, calc(100% - 44px)); margin: 24px auto 58px; }
.hero-card { min-height: 440px; display: grid; grid-template-columns: 1.05fr .95fr; overflow: hidden; background: linear-gradient(125deg, #fff5f7, #f8dae2 52%, #f4e5d1); border: 1px solid rgba(255, 255, 255, .8); border-radius: 32px; box-shadow: 0 24px 70px rgba(72, 39, 53, .13); }
.hero-content { align-self: center; padding: 70px clamp(30px, 6vw, 90px); }
.eyebrow, .subscription-eyebrow { color: #c94770; font: 800 12px Arial, sans-serif; letter-spacing: 2px; text-transform: uppercase; }
.hero h1 { max-width: 650px; margin: 14px 0; color: var(--deep); font-size: clamp(40px, 5vw, 72px); line-height: 1.02; }
.hero p { max-width: 540px; color: #665a60; font: 15px/1.7 Arial, sans-serif; }
.primary-button { margin-top: 22px; padding: 14px 24px; color: #fff; background: linear-gradient(135deg, #492633, #62394b); border-radius: 28px; box-shadow: 0 10px 24px rgba(72, 39, 53, .16); }
.hero-art { min-height: 440px; display: grid; place-items: center; overflow: hidden; background: radial-gradient(circle at 50% 38%, rgba(255,255,255,.82) 0 21%, transparent 43%), linear-gradient(145deg, #f5dfe4, #f3e2c3); }
.hero-product-photo { width: min(88%, 580px); height: 380px; display: block; object-fit: cover; border-radius: 26px; box-shadow: 0 22px 42px rgba(77, 41, 56, .16); }
.section-header { display: flex; justify-content: space-between; align-items: end; margin-bottom: 22px; }
.section-title { color: var(--deep); font-size: 30px; }
.section-link { color: var(--rose); font: 700 13px Arial, sans-serif; }
.category-grid { display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 13px; }
.category-card, .product-card, .trust-card, .plan { position: relative; overflow: hidden; background: linear-gradient(180deg, #fff, #fffafa); border: 1px solid var(--border); box-shadow: var(--shadow-soft); }
.category-card { padding: 22px 10px; text-align: center; border-radius: 20px; }
.category-card:hover, .product-card:hover, .plan:hover { transform: translateY(-5px); box-shadow: var(--shadow); }
.category-icon { width: 60px; height: 60px; display: grid; place-items: center; margin: auto; color: var(--gold); background: linear-gradient(145deg, #fff1f4, #faead9); border-radius: 19px; }
.category-icon .icon { width: 30px; height: 30px; }
.category-card strong { display: block; margin-top: 12px; font: 650 13px Arial, sans-serif; }
.category-card small { display: block; margin-top: 4px; color: var(--muted); font: 11px Arial, sans-serif; }
.toolbar { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 18px; }
.filter-btn { padding: 9px 14px; color: var(--deep); background: #fff; border: 1px solid var(--border); border-radius: 20px; font: 12px Arial, sans-serif; }
.filter-btn.active, .filter-btn:hover { background: #fae5eb; border-color: #efc4d2; }
.product-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 17px; }
.product-card { padding: 10px; border-radius: 23px; transition: transform .22s ease, box-shadow .22s ease; }
.product-image { position: relative; height: 235px; overflow: hidden; display: grid; place-items: center; background: linear-gradient(145deg, #fff1f4, #f3e4cf); border-radius: 18px; }
.product-photo { width: 100%; height: 100%; object-fit: cover; transition: transform .45s ease; }
.product-card:hover .product-photo { transform: scale(1.045); }
.wishlist-button { position: absolute; top: 12px; right: 12px; z-index: 2; width: 36px; height: 36px; display: grid; place-items: center; color: var(--rose); background: rgba(255,255,255,.97); border: 1px solid var(--border); border-radius: 50%; box-shadow: 0 6px 14px rgba(72,39,53,.09); }
.wishlist-button.active { background: #fff0f4; color: var(--rose-dark); }
.product-view-button { position: absolute; right: 10px; bottom: 10px; left: 10px; padding: 8px; color: var(--deep); background: rgba(255,255,255,.9); border-radius: 9px; text-align: center; opacity: 0; font: 700 10px Arial, sans-serif; transition: opacity .2s ease; }
.product-card:hover .product-view-button { opacity: 1; }
.product-info { padding: 4px 5px 2px; font-family: Arial, sans-serif; }
.product-title { margin: 10px 0 0; color: var(--deep); font-size: 15px; }
.rating { margin-top: 7px; color: #bd873f; font-size: 11px; letter-spacing: 1px; }
.rating span { color: var(--muted); letter-spacing: 0; }
.price { margin-top: 8px; color: var(--deep); font-size: 17px; font-weight: 800; }
.old-price { margin-left: 5px; color: #a69a9f; font-size: 11px; font-weight: 400; }
.add-cart, .checkout { width: 100%; margin-top: 11px; padding: 11px; color: #fff; background: linear-gradient(145deg, #4a2734, #6a3a4d); border-radius: 13px; font-weight: 700; }

.subscription { width: min(1400px, calc(100% - 44px)); margin: 70px auto; padding: 65px clamp(15px, 4vw, 50px) 70px; overflow: hidden; background: linear-gradient(135deg, #fff0f4, #f8dbe4 48%, #fff9f1); border: 1px solid rgba(255,255,255,.8); border-radius: 36px; box-shadow: 0 24px 70px rgba(74,39,52,.12); }
.subscription h2 { margin: 9px 0 0; color: var(--deep); font-size: clamp(32px, 4vw, 48px); }
.subscription h2 span { color: var(--rose); }
.subscription-intro { max-width: 680px; margin-top: 10px; color: var(--muted); font: 13px/1.7 Arial, sans-serif; }
.pack-box { margin-bottom: 25px; padding: 18px; background: rgba(255,255,255,.76); border: 1px solid rgba(255,255,255,.94); border-radius: 20px; }
.pack-title, .paygo-title { margin-bottom: 13px; color: var(--deep); font: 900 11px Arial, sans-serif; }
.pack-grid, .plans { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 12px; }
.pack-item { display: flex; align-items: center; gap: 9px; min-height: 64px; padding: 9px; background: rgba(255,255,255,.93); border: 1px solid var(--border); border-radius: 13px; font-family: Arial, sans-serif; }
.pack-emoji { width: 36px; height: 36px; display: grid; place-items: center; flex-shrink: 0; background: #fff; border-radius: 10px; }
.pack-item strong, .pack-item small { display: block; }.pack-item strong { font-size: 10px; }.pack-item small { margin-top: 3px; color: var(--muted); font-size: 9px; }
.plan { min-height: 385px; display: flex; flex-direction: column; padding: 21px 18px 18px; border-radius: 22px; font-family: Arial, sans-serif; transition: transform .22s ease, box-shadow .22s ease; }
.plan.featured { border: 2px solid var(--rose); background: linear-gradient(180deg,#fff0f4,#fff 68%); }
.popular { position: absolute; top: -12px; left: 50%; padding: 6px 12px; color: #fff; background: linear-gradient(135deg,var(--rose),var(--rose-dark)); border-radius: 30px; transform: translateX(-50%); white-space: nowrap; font-size: 8px; font-weight: 900; }
.plan-top, .selected-plan, .delivery-time-head, .selected-products-head, .total-row { display: flex; align-items: center; justify-content: space-between; gap: 10px; }
.plan-icon, .modal-icon { width: 43px; height: 43px; display: grid; place-items: center; color: var(--gold); background: linear-gradient(145deg,#fff1f4,#f2e0c5); border-radius: 13px; }
.plan h3 { margin: 16px 0 0; color: var(--deep); font-size: 17px; }.plan-desc { min-height: 58px; margin-top: 7px; color: var(--muted); font-size: 10px; line-height: 1.65; }.included { margin-top: 14px; padding: 9px 10px; color: var(--deep); background: #fff4f3; border-radius: 11px; font-size: 9px; font-weight: 800; }.included span { color: #4f8d68; }.features { margin: 11px 0; padding: 0; list-style: none; color: #75686f; font-size: 9px; line-height: 1.8; }.features li::before { content: "✓"; display: inline-grid; width: 14px; height: 14px; place-items: center; margin-right: 6px; color: var(--rose); background: #fbe8ee; border-radius: 50%; }.plan-button { width: 100%; min-height: 43px; margin-top: auto; color: var(--deep); background: #fff; border: 1px solid #e6dce0; border-radius: 11px; font-size: 10px; font-weight: 900; }.plan-button.primary { color: #fff; background: linear-gradient(135deg,#482634,#62394b); }.subscription-note { margin: 20px 0 0; color: #998d93; text-align: center; font: 9px Arial, sans-serif; }
.offer-banner { display: grid; grid-template-columns: 1fr auto; gap: 20px; align-items: center; padding: 28px 32px; color: #fff; background: linear-gradient(135deg,#472531,#62394b); border-radius: 24px; }.offer-banner h2 { margin: 0; font-size: 28px; }.offer-banner p { margin: 7px 0 0; color: #ead9df; font: 13px Arial, sans-serif; }.offer-code { padding: 10px 15px; border: 1px dashed #db9eb3; border-radius: 12px; font: 12px Arial, sans-serif; }
.trust-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 15px; }.trust-card { padding: 21px; border-radius: 19px; }.trust-icon { color: var(--gold); }.trust-card strong, .trust-card span { display: block; font-family: Arial, sans-serif; }.trust-card strong { margin-top: 9px; color: var(--deep); font-size: 14px; }.trust-card span { margin-top: 4px; color: var(--muted); font-size: 12px; line-height: 1.5; }
.footer { margin-top: 75px; padding: 50px clamp(22px,5vw,70px); color: #f9edf1; background: linear-gradient(145deg,#3f222f,#573044); }.footer-grid { max-width: 1400px; margin: auto; display: grid; grid-template-columns: 2fr 1fr 1fr 1fr; gap: 40px; }.footer h3 { margin: 0 0 14px; }.footer p, .footer a { display: block; margin: 0 0 7px; color: #d9c8cf; font: 12px/1.7 Arial, sans-serif; }.copyright { max-width: 1400px; margin: 35px auto 0; padding-top: 18px; border-top: 1px solid rgba(255,255,255,.1); color: #bfaeb5; font: 11px Arial, sans-serif; }
.toast { position: fixed; left: 50%; bottom: 90px; z-index: 8000; padding: 12px 19px; color: #fff; background: linear-gradient(135deg,#482634,#62394b); border-radius: 30px; transform: translate(-50%,20px); opacity: 0; pointer-events: none; transition: .25s; font: 13px Arial, sans-serif; }.toast.show { transform: translate(-50%,0); opacity: 1; }
.cart-overlay { position: fixed; inset: 0; z-index: 3000; background: rgba(40,20,30,.3); }.cart { position: fixed; top: 0; right: 0; z-index: 3001; width: min(410px, 94vw); height: 100vh; padding: 22px; background: #fff; box-shadow: -20px 0 60px rgba(51,27,38,.15); }.cart-head { display: flex; align-items: center; justify-content: space-between; padding-bottom: 18px; border-bottom: 1px solid var(--border); }.cart-head h2 { color: var(--deep); }.close-cart, .modal-close, .remove { width: 35px; height: 35px; color: var(--deep); background: var(--blush-light); border-radius: 50%; }.cart-items { padding: 20px 0; }.empty { padding: 70px 15px; color: var(--muted); text-align: center; font: 14px Arial, sans-serif; }.cart-item { position: relative; margin-bottom: 10px; padding: 14px; background: #fffafa; border: 1px solid var(--border); border-radius: 15px; font-family: Arial, sans-serif; }.cart-item strong { display: block; padding-right: 25px; color: var(--deep); font-size: 12px; }.cart-item-price { margin-top: 5px; color: var(--rose-dark); font-size: 13px; font-weight: 900; }.remove { position: absolute; top: 8px; right: 8px; width: 27px; height: 27px; color: #aa7a89; background: #fff; }
.modal-overlay { position: fixed; inset: 0; z-index: 5000; display: flex; align-items: center; justify-content: center; padding: 18px; background: rgba(49,27,37,.46); }.modal { position: relative; width: min(720px, 100%); max-height: 94vh; overflow-y: auto; padding: 30px; background: linear-gradient(145deg,#fffafb,#fff2f5); border-radius: 28px; box-shadow: 0 30px 90px rgba(45,24,34,.25); }.modal-close { position: absolute; top: 15px; right: 15px; }.modal-label { display: block; margin-top: 15px; color: var(--rose); font: 900 9px Arial, sans-serif; letter-spacing: 2px; }.modal h2 { margin: 6px 0 0; color: var(--deep); font-size: 29px; }.modal-subtitle, .paygo-help { color: var(--muted); font: 12px/1.6 Arial, sans-serif; }.paygo-box, .selected-products-section, .selected-plan, .delivery-time-section { margin-top: 20px; padding: 15px; background: rgba(255,255,255,.84); border: 1px solid rgba(213,83,125,.13); border-radius: 17px; }.paygo-search { display: flex; align-items: center; height: 46px; padding: 0 10px; gap: 8px; background: #fff; border: 1px solid var(--border); border-radius: 13px; }.paygo-search input { flex: 1; border: 0; outline: 0; }.paygo-search button { color: var(--rose); background: #fff0f4; border-radius: 50%; }.paygo-product-results, .paygo-plans { display: grid; grid-template-columns: repeat(2, minmax(0,1fr)); gap: 8px; margin-top: 10px; }.paygo-product-card, .selected-paygo-item { display: flex; align-items: center; gap: 9px; padding: 8px; background: #fff; border: 1px solid var(--border); border-radius: 14px; font: 10px Arial, sans-serif; }.paygo-product-card img, .paygo-product-image { width: 58px; height: 58px; flex-shrink: 0; object-fit: cover; border-radius: 11px; }.paygo-product-info { min-width: 0; flex: 1; }.paygo-product-info strong, .paygo-product-info small, .paygo-product-info b { display: block; margin-top: 3px; }.paygo-product-info strong { overflow: hidden; white-space: nowrap; text-overflow: ellipsis; color: var(--deep); }.paygo-product-info small { color: var(--muted); font-size: 8px; }.paygo-product-info b { color: var(--rose-dark); }.paygo-add { width: 30px; height: 30px; color: #fff; background: var(--deep); border-radius: 9px; }.selected-paygo-products { display: grid; gap: 7px; }.selected-paygo-info { min-width: 0; flex: 1; }.selected-paygo-info strong, .selected-paygo-info small { display: block; }.selected-paygo-info small { margin-top: 3px; color: var(--rose-dark); }.quantity-control { display: flex; align-items: center; gap: 4px; }.quantity-control button { width: 24px; height: 24px; color: var(--rose); background: #fff0f4; border-radius: 7px; }.no-products { padding: 18px 8px; color: var(--muted); text-align: center; font: 9px Arial, sans-serif; }.clear-products { padding: 6px 9px; color: var(--rose); background: #fff; border-radius: 9px; font-size: 8px; }.paygo-plan-title { margin-top: 20px; }.paygo-option { padding: 12px; color: var(--deep); background: #fff; border: 1px solid var(--border); border-radius: 13px; text-align: left; }.paygo-option.active { border: 2px solid var(--rose); background: #fff0f4; }.paygo-option strong, .paygo-option small { display: block; }.paygo-option small { margin-top: 4px; color: var(--muted); font-size: 8px; }.selected-plan { margin-top: 20px; }.selected-plan small { color: #9b8d93; font-size: 8px; }.selected-plan strong { display: block; margin-top: 4px; color: var(--deep); font-size: 13px; }.selected-plan b { color: var(--rose-dark); font-size: 20px; }.date-section { margin-top: 20px; font: 11px Arial, sans-serif; }.date-fields { display: grid; gap: 9px; margin-top: 9px; }.date-input, .weekday-select { width: 100%; height: 38px; padding: 0 10px; background: #fff; border: 1px solid var(--border); border-radius: 10px; }.date-preview, .selected-delivery-time { min-height: 42px; display: flex; flex-wrap: wrap; gap: 6px; align-items: center; margin-top: 10px; padding: 9px 11px; color: #9b8d93; background: #fff8f4; border-radius: 12px; font-size: 9px; }.date-chip { padding: 5px 8px; color: var(--rose-dark); background: #fbe6ec; border-radius: 8px; }.delivery-time-help { color: var(--muted); font: 9px/1.5 Arial, sans-serif; }.delivery-time-required { padding: 4px 7px; color: var(--rose); background: #fff0f4; border-radius: 20px; font: 900 7px Arial, sans-serif; }.delivery-time-options { display: grid; grid-template-columns: repeat(2, minmax(0,1fr)); gap: 8px; }.delivery-time-option { display: grid; grid-template-columns: 35px minmax(0,1fr); grid-template-rows: auto auto; gap: 2px 8px; min-height: 58px; padding: 9px; color: var(--deep); background: #fff; border: 1px solid var(--border); border-radius: 13px; text-align: left; }.delivery-time-option.active { border: 2px solid var(--rose); background: #fff0f4; }.delivery-time-icon { grid-row: 1 / 3; width: 35px; height: 35px; display: grid; place-items: center; background: #fff7f9; border-radius: 10px; }.delivery-time-option strong, .delivery-time-option small { grid-column: 2; }.delivery-time-option small { color: var(--muted); font-size: 8px; }.confirm { min-height: 48px; margin-top: 15px; }.confirm:disabled { opacity: .45; cursor: not-allowed; }
.mobile-bottom-nav { display: none; }
.plans { padding-top: 14px; }
.plan { overflow: visible; }
.popular { z-index: 2; top: -8px; padding: 5px 10px; font-size: 7px; }
.footer{margin-bottom: 0px;}

@media (max-width: 950px) { .navbar { flex-wrap: wrap; gap: 10px; }.search-box { order: 3; flex-basis: 100%; max-width: none; }.hero-card { grid-template-columns: 1fr; }.hero-art { min-height: 230px; }.hero-product-photo { width: 84%; height: 260px; }.category-grid { grid-template-columns: repeat(3, minmax(0,1fr)); }.product-grid { grid-template-columns: repeat(2, minmax(0,1fr)); }.trust-grid { grid-template-columns: repeat(2, minmax(0,1fr)); }.footer-grid { grid-template-columns: repeat(2, minmax(0,1fr)); }.plans, .pack-grid { grid-template-columns: repeat(3, minmax(0,1fr)); } }
@media (max-width: 700px) { body { padding-bottom:0px; }.hero, .section { width: calc(100% - 20px); margin-top: 34px; margin-bottom: 34px; }.navbar { padding: 9px 12px; }.logo { font-size: 21px; }.icon-button { width: 38px; height: 38px; }.category-nav { top: 102px; padding: 0 36px; }.category-nav a { min-height: 43px; padding: 0 13px; font-size: 10px; }.hero-card { border-radius: 22px; }.hero-content { padding: 32px 20px; }.hero h1 { font-size: clamp(32px, 10vw, 42px); }.hero p { font-size: 12px; }.hero-art { min-height: 155px; }.hero-product-photo { width: 84%; height: 155px; }.section-title { font-size: 23px; }.category-card { padding: 13px 4px; border-radius: 14px; }.category-icon { width: 44px; height: 44px; border-radius: 12px; }.category-card strong { font-size: 9px; }.category-card small { font-size: 7px; }.product-grid { gap: 8px; }.product-card { padding: 7px; border-radius: 17px; }.product-image { height: 155px; border-radius: 13px; }.product-title { font-size: 11px; }.price { font-size: 14px; }.add-cart { padding: 9px 7px; font-size: 8px; }.subscription { width: calc(100% - 20px); margin: 34px 10px; padding: 34px 12px 38px; border-radius: 25px; }.subscription h2 { font-size: clamp(28px, 8vw, 38px); }.pack-grid { grid-template-columns: repeat(2, minmax(0,1fr)); }.plans { grid-template-columns: 1fr; }.plan { min-height: 0; }.offer-banner { grid-template-columns: 1fr; padding: 20px; }.trust-grid { gap: 8px; }.trust-card { padding: 15px; }.footer { padding: 40px 20px 80px; }.mobile-bottom-nav { position: fixed; left: 8px; right: 8px; bottom: 8px; z-index: 9999; height: 62px; display: grid; grid-template-columns: repeat(5, minmax(0,1fr)); gap: 2px; padding: 5px; background: rgba(255,255,255,.98); border: 1px solid rgba(213,83,125,.17); border-radius: 23px; box-shadow: 0 10px 28px rgba(72,39,53,.15); }.mobile-bottom-nav-item { min-width: 0; min-height: 50px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 3px; color: #796e73; border-radius: 16px; font: 800 7.5px Arial, sans-serif; }.mobile-bottom-nav-item.active { color: var(--deep); background: var(--blush); }.mobile-bottom-nav-icon-wrap { position: relative; width: 23px; height: 23px; display: grid; place-items: center; }.mobile-bottom-nav-badge { top: -3px; right: -5px; min-width: 15px; height: 15px; border: 2px solid var(--blush-light); font-size: 7px; }.modal-overlay { padding: 10px; }.modal { max-height: calc(100dvh - 20px); padding: 20px 14px; }.paygo-product-results, .delivery-time-options { grid-template-columns: 1fr; }.paygo-plans { grid-template-columns: 1fr; } }
@media (prefers-reduced-motion: reduce) { *, *::before, *::after { scroll-behavior: auto !important; transition-duration: .01ms !important; animation-duration: .01ms !important; } }

#subscriptionModal #confirmSubscription.confirm {
	display: block;
	width: 100%;
	min-height: 48px;
	margin-top: 15px;
	padding: 13px;
	margin-bottom:50px;
	color: #fff;
	background: linear-gradient(135deg, #482634, #62394b) !important;
	border: 0;
	border-radius: 14px;
	box-shadow: 0 8px 20px rgba(74, 39, 52, .14);
	font: 900 11px Arial, sans-serif;
	opacity: 1;
}

#subscriptionModal #confirmSubscription.confirm:disabled {
	color: #fff;
	background: linear-gradient(135deg, #482634, #62394b) !important;
	opacity: .45;
	cursor: not-allowed;
}

#subscriptionModal .modal-close {
	position: absolute;
	top: 15px;
	right: 15px;
	z-index: 10;
	width: 36px;
	height: 36px;
	display: grid;
	place-items: center;
	padding: 0;
	color: var(--deep);
	background: #fff !important;
	border: 1px solid var(--border);
	border-radius: 50%;
	box-shadow: 0 6px 14px rgba(72, 39, 53, .1);
	font: 400 22px/1 Arial, sans-serif;
	cursor: pointer;
}

#subscriptionModal .modal-close:hover {
	color: var(--rose-dark);
	background: #fff0f4 !important;
}

.product-page { max-width: 1400px; margin: auto; padding: 20px 22px 70px; }
.product-main { display: grid; grid-template-columns: minmax(0, 1.05fr) minmax(420px, .95fr); gap: 55px; align-items: start; }
.gallery { position: sticky; top: 105px; }.gallery-layout { display: grid; grid-template-columns: 82px minmax(0, 1fr); gap: 14px; }.thumbnails { display: flex; flex-direction: column; gap: 10px; }.thumbnail { width: 76px; height: 76px; display: grid; place-items: center; color: var(--gold); background: linear-gradient(145deg, #fff4f7, #f4ddd7); border: 1px solid var(--border); border-radius: 15px; }.thumbnail:hover, .thumbnail.active { border-color: var(--rose); box-shadow: 0 0 0 2px rgba(184, 92, 120, .12); }.thumbnail .icon { width: 40px; height: 40px; }
.main-image { position: relative; min-height: 570px; display: grid; place-items: center; overflow: hidden; background: radial-gradient(circle at 50% 45%, rgba(255,255,255,.85), transparent 35%), linear-gradient(145deg, #fff1f5, #f4d9d4); border-radius: 28px; }.detail-product-photo { width: 84%; height: 78%; object-fit: contain; filter: drop-shadow(0 22px 25px rgba(77,41,56,.14)); transition: transform .25s ease; }.main-image:hover .detail-product-photo { transform: scale(1.04); }.zoom-label { position: absolute; right: 18px; bottom: 18px; display: inline-flex; align-items: center; gap: 5px; padding: 8px 12px; color: var(--muted); background: rgba(255,255,255,.8); border-radius: 20px; font: 11px Arial, sans-serif; }.zoom-label .icon { width: 13px; height: 13px; }.gallery-wishlist { position: absolute; top: 18px; right: 18px; z-index: 1; width: 44px; height: 44px; display: grid; place-items: center; color: var(--rose); background: #fff; border-radius: 50%; box-shadow: var(--shadow-soft); }.gallery-wishlist.active { background: var(--blush); }.gallery-wishlist.active .icon { fill: currentColor; }
.product-detail-info { padding-top: 4px; }.product-brand { color: var(--rose); font: 800 12px Arial, sans-serif; letter-spacing: 1.8px; text-transform: uppercase; }.product-detail-info .product-title { margin-top: 10px; color: var(--deep); font: 700 clamp(28px, 3.5vw, 44px)/1.12 Georgia, serif; }.product-subtitle { margin-top: 10px; color: var(--muted); font: 14px/1.6 Arial, sans-serif; }.rating-row { display: flex; align-items: center; gap: 12px; margin-top: 16px; flex-wrap: wrap; }.rating-pill { display: inline-flex; align-items: center; gap: 5px; padding: 6px 10px; color: #936725; background: #fff0d7; border-radius: 8px; font: 800 12px Arial, sans-serif; }.review-link { color: var(--rose); font: 12px Arial, sans-serif; }.divider { height: 1px; margin: 20px 0; background: var(--border); }.price-block { padding: 17px 0; }.current-price { color: var(--deep); font: 800 31px Arial, sans-serif; }.tax-note { margin-top: 5px; color: var(--muted); font: 11px Arial, sans-serif; }.product-detail-info .mrp { color: #999; font-size: 14px; }.product-detail-info .discount { color: #4c8b65; font-size: 13px; font-weight: 800; }
.offer-title { margin-bottom: 10px; color: var(--deep); font: 800 14px Arial, sans-serif; }.offer-list { display: grid; gap: 9px; }.offer-card { display: flex; align-items: flex-start; gap: 10px; padding: 12px 14px; background: #fff7f9; border: 1px solid #f1dce3; border-radius: 13px; }.offer-icon { width: 27px; height: 27px; flex: none; display: grid; place-items: center; color: var(--rose); background: var(--blush); border-radius: 50%; }.offer-icon .icon { width: 14px; height: 14px; }.offer-card strong, .offer-card span { display: block; }.offer-card strong { color: var(--deep); font: 700 12px Arial, sans-serif; }.offer-card span { margin-top: 3px; color: var(--muted); font: 11px/1.4 Arial, sans-serif; }
.delivery-box { padding: 17px; background: #fff; border: 1px solid var(--border); border-radius: 16px; }.delivery-head { display: flex; align-items: center; gap: 8px; color: var(--deep); font: 800 13px Arial, sans-serif; }.delivery-head .icon { width: 19px; height: 19px; color: var(--gold); }.pincode-row { display: flex; gap: 8px; margin-top: 12px; }.pincode-row input { flex: 1; height: 42px; padding: 0 12px; border: 1px solid var(--border); border-radius: 10px; outline: 0; font-size: 13px; }.check-btn { padding: 0 17px; color: #fff; background: var(--deep); border-radius: 10px; font-size: 12px; font-weight: 700; }.delivery-result { min-height: 16px; margin-top: 9px; color: #4c8b65; font: 11px Arial, sans-serif; }.delivery-error { color: var(--rose); }
.buy-row { display: grid; grid-template-columns: 120px 1fr 1fr; gap: 10px; margin-top: 18px; }.quantity { height: 50px; display: flex; align-items: center; justify-content: space-between; background: #fff; border: 1px solid var(--border); border-radius: 13px; }.quantity button { width: 38px; height: 100%; color: var(--deep); background: none; font-size: 19px; }.quantity span { font: 800 14px Arial, sans-serif; }.cart-button, .buy-button { height: 50px; border-radius: 13px; font-weight: 800; }.cart-button { color: #fff; background: linear-gradient(145deg, #4a2734, #6a3a4d); }.buy-button { color: #fff; background: linear-gradient(135deg, #d5537d, #a8335c); box-shadow: 0 8px 18px rgba(77,41,56,.14); }.product-trust { display: grid; grid-template-columns: repeat(3, 1fr); gap: 9px; margin-top: 18px; }.product-trust-card { min-height: 80px; display: flex; align-items: center; gap: 9px; padding: 12px; background: var(--blush-light); border-radius: 14px; }.product-trust-card .icon { width: 21px; height: 21px; flex: none; color: var(--gold); }.product-trust-card strong, .product-trust-card span { display: block; }.product-trust-card strong { color: var(--deep); font: 700 11px Arial, sans-serif; }.product-trust-card span { margin-top: 3px; color: var(--muted); font: 9px/1.4 Arial, sans-serif; }
.details-section, .reviews-section, .related { margin-top: 55px; padding-top: 35px; border-top: 1px solid var(--border); }.details-grid { display: grid; grid-template-columns: 1.3fr .7fr; gap: 55px; }.details-title { margin-bottom: 17px; color: var(--deep); font: 700 28px Georgia, serif; }.details-copy { color: #665b61; font: 14px/1.85 Arial, sans-serif; }.highlights { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-top: 22px; }.highlight { padding: 15px; background: #fff; border: 1px solid var(--border); border-radius: 14px; }.highlight strong, .highlight span { display: block; }.highlight strong { color: var(--deep); font: 700 12px Arial, sans-serif; }.highlight span { margin-top: 5px; color: var(--muted); font: 11px/1.5 Arial, sans-serif; }.spec-box { overflow: hidden; background: #fff; border: 1px solid var(--border); border-radius: 18px; }.spec-row { display: grid; grid-template-columns: 1fr 1fr; border-bottom: 1px solid var(--border); }.spec-row:last-child { border-bottom: 0; }.spec-row div { padding: 13px 15px; font: 12px Arial, sans-serif; }.spec-row div:first-child { color: var(--muted); background: #fff8fa; }.spec-row div:last-child { color: var(--deep); font-weight: 650; }
.reviews-summary { display: grid; grid-template-columns: 180px 1fr; gap: 30px; align-items: center; margin-top: 20px; padding: 25px; background: #fff4f7; border-radius: 20px; }.average-rating { text-align: center; }.average-rating strong { display: block; color: var(--deep); font: 800 48px Arial, sans-serif; }.average-rating .stars, .review-stars { color: #b47c30; letter-spacing: 2px; font-size: 14px; }.average-rating span { display: block; margin-top: 5px; color: var(--muted); font: 11px Arial, sans-serif; }.rating-bars { display: grid; gap: 8px; }.rating-bar { display: grid; grid-template-columns: 35px 1fr 40px; align-items: center; gap: 8px; color: var(--muted); font: 10px Arial, sans-serif; }.bar { height: 6px; overflow: hidden; background: #eadfe3; border-radius: 20px; }.bar-fill { height: 100%; background: var(--gold); border-radius: 20px; }.review-list { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; margin-top: 20px; }.review-card { padding: 20px; background: #fff; border: 1px solid var(--border); border-radius: 18px; }.reviewer { display: flex; align-items: center; gap: 10px; }.avatar { width: 37px; height: 37px; display: grid; place-items: center; color: var(--rose-dark); background: var(--blush); border-radius: 50%; font: 800 12px Arial, sans-serif; }.reviewer strong, .reviewer .verified { display: block; }.reviewer strong { color: var(--deep); font: 700 12px Arial, sans-serif; }.verified { margin-top: 2px; color: #4c8b65; font: 9px Arial, sans-serif; }.review-stars { margin-top: 12px; font-size: 11px; }.review-card p { margin-top: 10px; color: #6b6066; font: 12px/1.65 Arial, sans-serif; }
.related-product-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 15px; margin-top: 20px; }.related-product-grid .product-card { padding: 9px; background: #fff; border: 1px solid var(--border); border-radius: 19px; }.related-product-grid .product-image { height: 190px; }.related-product-grid .product-info { padding: 4px 4px 2px; }.related-product-grid .product-name { min-height: 36px; margin: 5px 0 0; color: var(--deep); font: 650 14px/1.35 Arial, sans-serif; }.related-product-grid .product-price { display: flex; align-items: baseline; gap: 6px; margin-top: 7px; }.related-product-grid .current { color: var(--deep); font-size: 16px; font-weight: 800; }
@media (max-width: 1000px) { .product-main { grid-template-columns: 1fr; gap: 30px; }.gallery { position: relative; top: auto; }.main-image { min-height: 480px; }.details-grid { grid-template-columns: 1fr; }.review-list { grid-template-columns: repeat(2, 1fr); }.related-product-grid { grid-template-columns: repeat(3, 1fr); } }
@media (max-width: 650px) { .product-page { padding: 15px 12px 50px; }.gallery-layout { grid-template-columns: 58px minmax(0, 1fr); }.thumbnails { gap: 7px; }.thumbnail { width: 54px; height: 54px; border-radius: 11px; }.thumbnail .icon { width: 28px; height: 28px; }.main-image { min-height: 380px; border-radius: 21px; }.product-detail-info .product-title { font-size: 31px; }.current-price { font-size: 27px; }.buy-row { grid-template-columns: 105px 1fr; }.buy-button, .cart-button { grid-column: 2; }.product-trust, .highlights, .reviews-summary { grid-template-columns: 1fr; }.review-list { grid-template-columns: 1fr; }.related-product-grid { grid-template-columns: repeat(2, 1fr); gap: 10px; }.related-product-grid .product-image { height: 150px; }.related-product-grid .product-name { font-size: 12px; }.related-product-grid .current { font-size: 14px; } }
@media (max-width: 400px) { .gallery-layout { grid-template-columns: 1fr; }.thumbnails { order: 2; flex-direction: row; overflow-x: auto; }.thumbnail { flex: none; }.main-image { order: 1; }.buy-row { grid-template-columns: 1fr 1fr; }.quantity { grid-column: 1 / -1; }.buy-button, .cart-button { grid-column: auto; } }

.cart-page { max-width: 1400px; margin: auto; padding: 20px 22px 70px; }.cart-page-heading { display: flex; align-items: end; justify-content: space-between; gap: 20px; padding: 20px 0 30px; }.cart-page-heading h1 { margin-top: 7px; color: var(--deep); font: 700 clamp(32px, 4vw, 50px) Georgia, serif; }.cart-page-heading p { margin-top: 8px; color: var(--muted); font: 13px Arial, sans-serif; }.continue-shopping, .cart-primary-link { display: inline-flex; align-items: center; justify-content: center; min-height: 42px; padding: 0 16px; color: #fff; background: var(--deep); border-radius: 11px; font: 700 12px Arial, sans-serif; }.cart-layout { display: grid; grid-template-columns: minmax(0, 1.4fr) minmax(300px, .6fr); gap: 25px; align-items: start; }.cart-list, .cart-summary { padding: 22px; background: #fff; border: 1px solid var(--border); border-radius: 20px; }.cart-section-heading { display: flex; align-items: center; justify-content: space-between; padding-bottom: 15px; border-bottom: 1px solid var(--border); }.cart-section-heading h2, .cart-summary h2 { color: var(--deep); font: 700 20px Georgia, serif; }.cart-section-heading span { color: var(--muted); font: 11px Arial, sans-serif; }.cart-page-item { display: grid; grid-template-columns: 92px minmax(0, 1fr) auto auto; gap: 16px; align-items: center; padding: 18px 0; border-bottom: 1px solid var(--border); }.cart-page-item:last-child { border-bottom: 0; padding-bottom: 0; }.cart-page-item img { width: 92px; height: 92px; object-fit: cover; background: #fff3f5; border-radius: 13px; }.cart-page-item-info { min-width: 0; }.cart-page-item-info h3 { color: var(--deep); font: 700 14px/1.35 Arial, sans-serif; }.cart-page-item-info span { display: block; margin-top: 6px; color: var(--muted); font: 11px Arial, sans-serif; }.cart-page-item-info strong { display: block; margin-top: 12px; color: var(--deep); font: 800 15px Arial, sans-serif; }.cart-page-quantity { display: flex; align-items: center; height: 38px; border: 1px solid var(--border); border-radius: 10px; }.cart-page-quantity button { width: 32px; height: 100%; color: var(--deep); background: none; font-size: 17px; }.cart-page-quantity span { min-width: 25px; text-align: center; font: 700 12px Arial, sans-serif; }.cart-page-remove { color: var(--rose); background: none; font: 700 11px Arial, sans-serif; }.cart-summary { position: sticky; top: 105px; }.summary-row, .summary-total { display: flex; justify-content: space-between; gap: 12px; color: var(--muted); font: 12px Arial, sans-serif; }.summary-row { padding: 14px 0 0; }.summary-row strong { color: var(--deep); font-weight: 700; text-align: right; }.summary-total { margin-top: 18px; padding-top: 18px; color: var(--deep); border-top: 1px solid var(--border); font-size: 15px; font-weight: 800; }.cart-summary > .checkout { display: flex; align-items: center; justify-content: center; min-height: 46px; margin-top: 18px; }.cart-delivery-box { margin-top: 25px; padding-top: 20px; border-top: 1px solid var(--border); }.cart-delivery-box > strong { color: var(--deep); font: 700 12px Arial, sans-serif; }.cart-empty-state { padding: 75px 20px; text-align: center; background: #fff; border: 1px solid var(--border); border-radius: 20px; }.cart-empty-mark { width: 60px; height: 60px; display: grid; place-items: center; margin: auto; color: var(--rose); background: var(--blush-light); border-radius: 50%; font-size: 28px; }.cart-empty-state h2 { margin-top: 18px; color: var(--deep); font: 700 24px Georgia, serif; }.cart-empty-state p { margin: 8px 0 20px; color: var(--muted); font: 13px Arial, sans-serif; }
@media (max-width: 800px) { .cart-page-heading { align-items: flex-start; flex-direction: column; }.cart-layout { grid-template-columns: 1fr; }.cart-summary { position: static; }.cart-page-item { grid-template-columns: 72px minmax(0, 1fr) auto; gap: 12px; }.cart-page-item img { width: 72px; height: 72px; }.cart-page-remove { grid-column: 2 / -1; justify-self: start; }.cart-page-quantity { grid-column: 3; grid-row: 1; } }
@media (max-width: 480px) { .cart-page { padding: 15px 12px 50px; }.cart-list, .cart-summary { padding: 16px; border-radius: 16px; }.cart-page-item { grid-template-columns: 60px minmax(0, 1fr); }.cart-page-item img { width: 60px; height: 60px; }.cart-page-quantity { grid-column: 2; grid-row: auto; justify-self: start; }.cart-page-remove { grid-column: 2; }.continue-shopping { width: 100%; } }

.weekday-select {
	appearance: none;
	-webkit-appearance: none;
	min-height: 42px;
	padding: 0 38px 0 13px !important;
	color: var(--deep) !important;
	background-color: #fff !important;
	background-image: linear-gradient(45deg, transparent 50%, var(--rose) 50%), linear-gradient(135deg, var(--rose) 50%, transparent 50%);
	background-position: calc(100% - 17px) 18px, calc(100% - 12px) 18px;
	background-repeat: no-repeat;
	background-size: 5px 5px, 5px 5px;
	border: 1px solid var(--border) !important;
	border-radius: 11px !important;
	font: 700 12px Arial, sans-serif;
	cursor: pointer;
}

.weekday-select:hover {
	border-color: #d99aac !important;
}

.weekday-select:focus {
	border-color: var(--rose) !important;
	box-shadow: 0 0 0 3px rgba(213, 83, 125, .1);
	outline: 0;
}

/* Exact cart conversion: shared header/footer remain component-owned. */
.cart-exact-page { width: 100%; max-width: 1200px; padding: 30px 20px 80px; }
.cart-exact-page .breadcrumb { max-width: none; margin: 0 0 20px; padding: 0; font-size: 10px; }
.cart-exact-page .cart-header { display: flex; align-items: flex-end; justify-content: space-between; gap: 20px; margin-bottom: 18px; }
.cart-exact-page .cart-title { color: var(--deep); font: 700 29px Georgia, serif; }
.cart-exact-page .cart-subtitle { margin-top: 5px; color: var(--muted); font: 9px Arial, sans-serif; }
.cart-exact-page .continue-shopping { display: inline-flex; align-items: center; gap: 6px; min-height: 0; padding: 0; color: var(--rose); background: none; border-radius: 0; font: 800 9px Arial, sans-serif; }
.cart-exact-page .continue-shopping .icon { width: 13px; height: 13px; }
.delivery-progress { margin-bottom: 20px; padding: 13px 15px; background: #fff; border: 1px solid var(--border); border-radius: 12px; box-shadow: var(--shadow-soft); }
.delivery-progress-top { display: flex; align-items: center; justify-content: space-between; gap: 10px; margin-bottom: 8px; font: 8px Arial, sans-serif; }.delivery-progress-top strong { color: var(--green); }.delivery-progress-top span { color: var(--muted); }.progress-track { height: 5px; overflow: hidden; background: #eee4e7; border-radius: 10px; }.progress-fill { height: 100%; background: linear-gradient(90deg, var(--rose), #e9a0b5); border-radius: 10px; transition: width .4s; }
.cart-exact-page .cart-grid { display: grid; grid-template-columns: minmax(0, 1fr) 350px; gap: 20px; align-items: start; }.cart-exact-page .cart-card, .cart-exact-page .summary { overflow: hidden; padding: 0; background: #fff; border: 1px solid var(--border); border-radius: 18px; box-shadow: var(--shadow-soft); }.cart-exact-page .cart-card-header { display: flex; align-items: center; justify-content: space-between; padding: 17px 19px; border-bottom: 1px solid var(--border); }.cart-exact-page .cart-card-header h2, .cart-exact-page .summary h2 { color: var(--deep); font: 700 14px Arial, sans-serif; }.cart-exact-page .select-all { color: var(--rose); background: none; font: 800 8px Arial, sans-serif; }
.cart-exact-page .cart-items { padding: 0 19px; }.cart-exact-page .cart-item { display: grid; grid-template-columns: 100px minmax(0, 1fr) auto; gap: 15px; align-items: center; padding: 17px 0; border-bottom: 1px solid var(--border); }.cart-exact-page .cart-item:last-child { border-bottom: 0; }.cart-exact-page .product-image { position: relative; width: 100px; height: 100px; overflow: hidden; display: grid; place-items: center; padding: 0; background: linear-gradient(145deg, #fff0f3, #f5dfd9); border-radius: 13px; }.cart-exact-page .product-image img { width: 100%; height: 100%; object-fit: cover; }.discount-badge { position: absolute; top: 7px; left: 7px; z-index: 1; padding: 4px 6px; color: #fff; background: var(--rose); border-radius: 6px; font: 800 7px Arial, sans-serif; }.cart-exact-page .product-info { min-width: 0; }.cart-exact-page .product-category { color: var(--rose); font: 800 8px Arial, sans-serif; letter-spacing: .5px; text-transform: uppercase; }.cart-exact-page .product-name { margin-top: 5px; color: var(--deep); font: 800 12px/1.4 Arial, sans-serif; }.cart-exact-page .product-description { margin-top: 4px; color: var(--muted); font: 8px/1.5 Arial, sans-serif; }.product-meta { display: flex; align-items: center; flex-wrap: wrap; gap: 7px; margin-top: 8px; }.meta-pill { padding: 4px 6px; color: var(--muted); background: var(--blush-light); border-radius: 5px; font: 700 7px Arial, sans-serif; }.price-row { display: flex; align-items: center; flex-wrap: wrap; gap: 7px; margin-top: 8px; }.cart-exact-page .current-price { color: var(--deep); font: 900 13px Arial, sans-serif; }.old-price { color: #aaa; font: 9px Arial, sans-serif; text-decoration: line-through; }.save-price { color: var(--green); font: 800 8px Arial, sans-serif; }.item-actions { display: flex; align-items: center; flex-wrap: wrap; gap: 7px; margin-top: 11px; }.item-action { display: inline-flex; align-items: center; gap: 4px; padding: 7px 9px; color: var(--deep); background: var(--blush-light); border-radius: 7px; font: 800 7px Arial, sans-serif; }.item-action .icon { width: 11px; height: 11px; }.item-action.delete { color: #b9505c; background: #fff0f2; }
.cart-exact-page .item-right { display: flex; flex-direction: column; align-items: flex-end; gap: 14px; }.cart-exact-page .quantity { height: 32px; display: flex; align-items: center; overflow: hidden; background: #fff; border: 1px solid var(--border); border-radius: 8px; }.cart-exact-page .quantity button { width: 31px; height: 31px; display: grid; place-items: center; color: var(--deep); background: var(--blush-light); }.cart-exact-page .quantity button .icon { width: 13px; height: 13px; }.cart-exact-page .quantity span { min-width: 32px; color: var(--deep); text-align: center; font: 900 9px Arial, sans-serif; }.cart-exact-page .item-total { color: var(--deep); font: 900 13px Arial, sans-serif; white-space: nowrap; }
.cart-exact-page .summary { position: sticky; top: 96px; padding: 20px; overflow: visible; }.cart-exact-page .summary h2 { padding-bottom: 14px; border-bottom: 1px solid var(--border); font-size: 15px; }.coupon { margin: 16px 0; padding: 12px; background: var(--blush-light); border-radius: 11px; }.coupon-title { display: flex; align-items: center; gap: 6px; color: var(--deep); font: 800 9px Arial, sans-serif; }.coupon-title .icon { width: 13px; height: 13px; color: var(--rose); }.coupon-row { display: flex; gap: 6px; margin-top: 8px; }.coupon-row input { min-width: 0; flex: 1; height: 34px; padding: 0 9px; background: #fff; border: 1px solid var(--border); border-radius: 7px; outline: 0; font-size: 9px; }.coupon-button { height: 34px; padding: 0 11px; color: #fff; background: var(--deep); border-radius: 7px; font-size: 8px; font-weight: 800; }.coupon-message { min-height: 11px; margin-top: 6px; color: var(--green); font: 700 8px Arial, sans-serif; }.coupon-error { color: #b9505c; }.summary-rows { padding-bottom: 12px; border-bottom: 1px solid var(--border); }.cart-exact-page .summary-row { display: flex; align-items: center; justify-content: space-between; gap: 10px; padding: 7px 0; color: var(--muted); font: 9px Arial, sans-serif; }.cart-exact-page .summary-row strong { color: var(--deep); }.cart-exact-page .summary-row.discount strong { color: var(--green); }.cart-exact-page .summary-row.delivery strong { color: var(--green); }.cart-exact-page .total-row { display: flex; align-items: flex-end; justify-content: space-between; gap: 15px; padding: 15px 0; border: 0; }.cart-exact-page .total-row span { color: var(--deep); font: 800 11px Arial, sans-serif; }.cart-exact-page .total-row strong { color: var(--deep); font: 900 21px Arial, sans-serif; }.checkout-button { width: 100%; min-height: 46px; display: flex; align-items: center; justify-content: center; gap: 8px; color: #fff; background: var(--deep); border-radius: 10px; box-shadow: 0 8px 20px rgba(77,41,56,.14); font: 900 10px Arial, sans-serif; }.checkout-button .icon { width: 15px; height: 15px; }.secure-note { display: flex; align-items: center; justify-content: center; gap: 6px; margin-top: 11px; color: var(--muted); text-align: center; font: 7px Arial, sans-serif; }.secure-note .icon { width: 12px; height: 12px; color: var(--green); }.payment-methods { display: flex; align-items: center; justify-content: center; flex-wrap: wrap; gap: 5px; margin-top: 11px; }.payment { padding: 4px 6px; color: var(--muted); background: #fff; border: 1px solid var(--border); border-radius: 5px; font: 800 6px Arial, sans-serif; }.benefits { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-top: 13px; padding-top: 13px; border-top: 1px solid var(--border); }.benefit { text-align: center; }.benefit-icon { width: 29px; height: 29px; display: grid; place-items: center; margin: auto; color: var(--rose); background: var(--blush-light); border-radius: 8px; }.benefit-icon .icon { width: 14px; height: 14px; }.benefit span { display: block; margin-top: 5px; color: var(--muted); font: 6px/1.3 Arial, sans-serif; }
.cart-exact-page .empty-cart { display: block; padding: 65px 25px; text-align: center; }.cart-exact-page .empty-icon { width: 75px; height: 75px; display: grid; place-items: center; margin: 0 auto 15px; color: var(--rose); background: var(--blush-light); border-radius: 50%; }.cart-exact-page .empty-icon .icon { width: 34px; height: 34px; }.cart-exact-page .empty-cart h2 { color: var(--deep); font: 700 21px Georgia, serif; }.cart-exact-page .empty-cart p { max-width: 350px; margin: 7px auto 17px; color: var(--muted); font: 9px/1.6 Arial, sans-serif; }.shop-button { display: inline-flex; align-items: center; justify-content: center; padding: 10px 17px; color: #fff; background: var(--deep); border-radius: 9px; font: 800 9px Arial, sans-serif; }
.recommendations { margin-top: 25px; }.recommendations h2 { margin-bottom: 12px; color: var(--deep); font: 700 20px Georgia, serif; }.recommend-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 10px; }.recommend-card { overflow: hidden; background: #fff; border: 1px solid var(--border); border-radius: 14px; transition: .2s; }.recommend-card:hover { transform: translateY(-2px); box-shadow: var(--shadow); }.recommend-image { height: 125px; display: grid; place-items: center; overflow: hidden; background: linear-gradient(145deg, #fff0f3, #f5dfd9); }.recommend-image img { width: 100%; height: 100%; object-fit: cover; }.recommend-info { padding: 11px; }.recommend-info small { color: var(--rose); font: 800 7px Arial, sans-serif; }.recommend-info strong { display: block; margin-top: 4px; color: var(--deep); font: 900 9px/1.4 Arial, sans-serif; }.recommend-price { margin-top: 6px; color: var(--deep); font: 900 10px Arial, sans-serif; }
@media (max-width: 1000px) { .cart-exact-page .cart-grid { grid-template-columns: minmax(0, 1fr) 310px; }.recommend-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); } }
@media (max-width: 800px) { .cart-exact-page .cart-grid { grid-template-columns: 1fr; }.cart-exact-page .summary { position: static; }.recommend-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); } }
@media (max-width: 650px) { .cart-exact-page { padding: 22px 12px 100px; }.cart-exact-page .cart-header { align-items: flex-start; flex-direction: column; }.cart-exact-page .cart-title { font-size: 25px; }.cart-exact-page .cart-item { grid-template-columns: 82px minmax(0, 1fr); gap: 12px; align-items: start; }.cart-exact-page .product-image { width: 82px; height: 82px; }.cart-exact-page .item-right { grid-column: 2; flex-direction: row; align-items: center; justify-content: space-between; width: 100%; }.cart-exact-page .cart-items { padding: 0 13px; }.cart-exact-page .cart-card-header { padding: 15px 13px; }.recommend-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }.recommend-image { height: 110px; } }
@media (max-width: 420px) { .cart-exact-page .cart-item { grid-template-columns: 70px minmax(0, 1fr); }.cart-exact-page .product-image { width: 70px; height: 70px; }.cart-exact-page .product-name { font-size: 10px; }.cart-exact-page .current-price { font-size: 11px; }.cart-exact-page .item-action { padding: 6px 7px; }.benefits { gap: 4px; } }

.weekday-picker {
	position: relative;
	width: 100%;
}

.weekday-select {
	position: relative;
	width: 100%;
	min-height: 42px;
	padding: 0 38px 0 13px !important;
	color: var(--deep) !important;
	background-color: #fff !important;
	background-image: linear-gradient(45deg, transparent 50%, var(--rose) 50%), linear-gradient(135deg, var(--rose) 50%, transparent 50%);
	background-position: calc(100% - 17px) 18px, calc(100% - 12px) 18px;
	background-repeat: no-repeat;
	background-size: 5px 5px, 5px 5px;
	border: 1px solid var(--border) !important;
	border-radius: 11px !important;
	font: 700 12px Arial, sans-serif;
	text-align: left;
	cursor: pointer;
}

.weekday-select.open {
	border-color: var(--rose) !important;
	border-radius: 11px 11px 0 0 !important;
	box-shadow: 0 0 0 3px rgba(213, 83, 125, .1);
}

.weekday-options {
	position: absolute;
	top: 100%;
	right: 0;
	left: 0;
	z-index: 20;
	overflow: hidden;
	padding: 4px;
	background: #fff;
	border: 1px solid var(--rose);
	border-top: 0;
	border-radius: 0 0 11px 11px;
	box-shadow: 0 12px 24px rgba(74, 39, 52, .15);
}

.weekday-option {
	width: 100%;
	min-height: 34px;
	padding: 8px 10px;
	color: var(--deep);
	background: #fff;
	border-radius: 7px;
	text-align: left;
	font: 600 11px Arial, sans-serif;
}

.weekday-option:hover,
.weekday-option.selected {
	color: var(--rose-dark);
	background: #fff0f4;
}

.weekday-select option {
	padding: 10px;
	color: var(--deep);
	background: #fff;
}

.date-picker { position: relative; width: 100%; }
.date-picker-trigger { width: 100%; min-height: 42px; padding: 0 13px; color: var(--deep); background: #fff; border: 1px solid var(--border); border-radius: 11px; text-align: left; font: 700 12px Arial, sans-serif; }
.date-picker-trigger::after { content: ""; float: right; width: 7px; height: 7px; margin-top: 3px; border-right: 2px solid var(--rose); border-bottom: 2px solid var(--rose); transform: rotate(45deg); }
.date-picker-trigger.open { border-color: var(--rose); border-radius: 11px 11px 0 0; box-shadow: 0 0 0 3px rgba(213,83,125,.1); }
.date-picker-popover { position: absolute; top: 100%; left: 0; right: 0; z-index: 30; padding: 12px; background: #fff; border: 1px solid var(--rose); border-top: 0; border-radius: 0 0 13px 13px; box-shadow: 0 14px 28px rgba(74,39,52,.16); }
.date-picker-header { display: flex; align-items: center; justify-content: space-between; color: var(--deep); font: 700 12px Arial, sans-serif; }
.date-picker-header > div { display: flex; gap: 5px; }
.date-picker-header button, .date-picker-footer button { min-width: 30px; min-height: 28px; color: var(--rose); background: #fff4f7; border-radius: 7px; font: 700 11px Arial, sans-serif; }
.date-picker-weekdays, .date-picker-days { display: grid; grid-template-columns: repeat(7, minmax(0, 1fr)); gap: 4px; margin-top: 12px; text-align: center; }
.date-picker-weekdays { color: var(--muted); font: 700 9px Arial, sans-serif; }
.date-picker-day, .date-picker-empty { min-height: 30px; }
.date-picker-day { color: var(--deep); background: #fff; border-radius: 7px; font: 600 10px Arial, sans-serif; }
.date-picker-day:hover:not(:disabled), .date-picker-day.selected { color: #fff; background: var(--rose); }
.date-picker-day:disabled { color: #c8bec2; background: #fffafa; cursor: not-allowed; }
.date-picker-footer { display: flex; justify-content: space-between; margin-top: 12px; padding-top: 10px; border-top: 1px solid var(--border); }

/* Final mobile cascade: keep the compact layout stable after all legacy overrides. */
@media (max-width: 700px) {
	body { padding-bottom: 0px !important; }
	.navbar { min-height: 0 !important; display: flex !important; flex-wrap: wrap !important; align-items: center !important; gap: 8px !important; padding: 9px 12px !important; }
	.navbar > .logo { flex: 0 0 auto !important; }
	.navbar > .search-box { order: 3 !important; flex: 0 0 100% !important; width: 100% !important; margin: 0 !important; }
	.navbar > .nav-actions { flex: 0 0 auto !important; margin-left: auto !important; }
	.category-nav { top: 102px !important; min-height: 43px !important; padding: 0 36px !important; gap: 0 !important; }
	.category-nav a { min-height: 43px !important; padding: 0 13px !important; font-size: 10px !important; }
	.hero, .section { width: calc(100% - 20px) !important; max-width: calc(100% - 20px) !important; padding: 0 !important; margin: 34px 10px !important; }
	.hero-card { grid-template-columns: 1fr !important; border-radius: 22px !important; }
	.hero-content { padding: 32px 20px !important; }
	.hero-art { min-height: 155px !important; }
	.hero-product-photo { width: 84% !important; height: 155px !important; }
	.category-grid, .product-grid { grid-template-columns: repeat(2, minmax(0, 1fr)) !important; gap: 8px !important; }
	.category-grid { grid-template-columns: repeat(3, minmax(0, 1fr)) !important; }
	.product-image { height: 155px !important; }
	.subscription { width: calc(100% - 20px) !important; max-width: calc(100% - 20px) !important; margin: 34px 10px !important; padding: 34px 12px 38px !important; }
	.pack-grid { grid-template-columns: repeat(2, minmax(0, 1fr)) !important; }
	.plans { grid-template-columns: 1fr !important; }
	.modal-overlay { padding: 10px !important; }
	.modal { width: 100% !important; max-width: 100% !important; max-height: calc(100dvh - 20px) !important; padding: 20px 14px !important; }
	.mobile-bottom-nav { left: 8px !important; right: 8px !important; bottom: 8px !important; width: auto !important; height: 62px !important; min-height: 62px !important; max-height: 62px !important; padding: 5px !important; display: grid !important; grid-template-columns: repeat(5, minmax(0, 1fr)) !important; }
	.mobile-bottom-nav-item { min-height: 50px !important; max-height: 50px !important; padding: 4px 2px !important; }
	.footer { padding-bottom: 80px !important; }
}

@media (max-width: 390px) {
	body { padding-bottom: 0px !important; }
	.mobile-bottom-nav { left: 5px !important; right: 5px !important; bottom: 5px !important; height: 60px !important; min-height: 60px !important; max-height: 60px !important; }
	.mobile-bottom-nav-item { min-height: 48px !important; max-height: 48px !important; }
}

@media (max-width: 700px) {
	body { padding-bottom: 0px !important; }
	.mobile-bottom-nav {
		display: grid !important;
		align-items: stretch !important;
		overflow: visible !important;
	}

	.mobile-bottom-nav-item {
		display: flex !important;
		flex-direction: column !important;
		align-items: center !important;
		justify-content: center !important;
		gap: 5px !important;
		height: 50px !important;
		min-height: 50px !important;
		max-height: 50px !important;
		line-height: 1 !important;
		text-align: center !important;
	}

	.mobile-bottom-nav-icon-wrap {
		width: 24px !important;
		height: 24px !important;
		min-width: 24px !important;
		min-height: 24px !important;
		display: flex !important;
		align-items: center !important;
		justify-content: center !important;
		flex: 0 0 24px !important;
	}

	.mobile-bottom-nav-icon-wrap .icon {
		width: 20px !important;
		height: 20px !important;
		min-width: 20px !important;
		min-height: 20px !important;
	}

	.mobile-bottom-nav-label {
		display: block !important;
		width: 100% !important;
		height: 10px !important;
		overflow: hidden !important;
		color: currentColor !important;
		font: 800 9px/10px Arial, sans-serif !important;
		text-align: center !important;
		white-space: nowrap !important;
	}
}

@media (max-width: 390px) {
	.mobile-bottom-nav-item {
		height: 48px !important;
		min-height: 48px !important;
		max-height: 48px !important;
		gap: 3px !important;
	}

	.mobile-bottom-nav-label {
		font-size: 8px !important;
	}
}

.delivery-time-option:disabled {
	opacity: .42 !important;
	color: #b7aeb2 !important;
	background: #fff !important;
	border-color: #eee7e9 !important;
	box-shadow: none !important;
	filter: grayscale(.15) !important;
	transform: none !important;
}

.delivery-time-option:disabled .delivery-time-icon {
	color: #c9c1c4 !important;
	background: #fffafb !important;
}

.delivery-time-option:disabled strong,
.delivery-time-option:disabled small {
	color: #b7aeb2 !important;
}

.delivery-time-option:disabled:hover {
	border-color: #eee7e9 !important;
	transform: none !important;
}

.paygo-product-card.selected {
	border-color: #e3a5b8 !important;
	box-shadow: 0 6px 16px rgba(213, 83, 125, .08) !important;
}

.paygo-add.selected {
	color: #fff !important;
	background: linear-gradient(135deg, #482634, #62394b) !important;
	font-size: 18px;
	font-weight: 900;
}

.delivery-time-option {
	position: relative !important;
}

.delivery-time-check {
	position: absolute !important;
	top: 7px !important;
	right: 7px !important;
	width: 19px !important;
	height: 19px !important;
	display: none !important;
	place-items: center !important;
	border-radius: 50% !important;
	color: #fff !important;
	background: var(--rose) !important;
	font: 900 12px/1 Arial, sans-serif !important;
	z-index: 2 !important;
}

.delivery-time-option.active .delivery-time-check {
	display: grid !important;
}

.delivery-time-option:disabled .delivery-time-check {
	display: none !important;
}

.date-picker-trigger,
.weekday-select {
	position: relative !important;
	padding-right: 42px !important;
}

.date-selection-check {
	position: absolute !important;
	top: 50% !important;
	right: 10px !important;
	width: 19px !important;
	height: 19px !important;
	display: grid !important;
	place-items: center !important;
	border-radius: 50% !important;
	color: #fff !important;
	background: var(--rose) !important;
	font: 900 12px/1 Arial, sans-serif !important;
	transform: translateY(-50%);
}

.paygo-option {
	position: relative !important;
	text-align: left !important;
}

.paygo-check {
	position: absolute !important;
	top: 9px !important;
	right: 9px !important;
	width: 19px !important;
	height: 19px !important;
	display: none !important;
	place-items: center !important;
	border-radius: 50% !important;
	color: #fff !important;
	background: var(--rose) !important;
	font: 900 12px/1 Arial, sans-serif !important;
	z-index: 2 !important;
}

.paygo-option.active .paygo-check {
	display: grid !important;
}

.selected-products-head > strong {
	font-size: 13px !important;
}

.selected-products-head > strong small {
	font-size: 10px !important;
}

.selected-products-head .clear-products {
	font-size: 10px !important;
}

.selected-paygo-info strong {
	font-size: 12px !important;
}

.selected-paygo-info small {
	font-size: 10px !important;
}

.products-page { max-width: 1400px; margin: auto; padding: 20px 22px 70px; }
.breadcrumb { max-width: 1400px; margin: auto; padding: 20px 22px 5px; color: var(--muted); font: 12px Arial, sans-serif; }
.breadcrumb a { color: var(--rose); }.breadcrumb span { margin: 0 7px; }
.page-heading { display: flex; justify-content: space-between; align-items: end; gap: 20px; padding: 20px 0 25px; }
.heading-eyebrow { color: var(--rose); font: 800 11px Arial, sans-serif; letter-spacing: 2px; text-transform: uppercase; }
.page-heading h1 { margin: 7px 0 0; color: var(--deep); font: 700 clamp(32px, 4vw, 50px) Georgia, serif; }
.page-heading p { margin: 8px 0 0; color: var(--muted); font: 13px Arial, sans-serif; }
.shop-layout { display: grid; grid-template-columns: 245px minmax(0, 1fr); gap: 25px; }
.filters { align-self: start; position: sticky; top: 105px; padding: 20px; background: #fff; border: 1px solid var(--border); border-radius: 20px; }
.filter-header, .shop-toolbar, .toolbar-right { display: flex; align-items: center; }.filter-header { justify-content: space-between; padding-bottom: 15px; border-bottom: 1px solid var(--border); }.filter-header strong, .filter-section h3 { color: var(--deep); }.filter-header strong { font: 700 15px Arial, sans-serif; }.clear-filter { color: var(--rose); background: none; font: 11px Arial, sans-serif; }
.filter-section { padding: 18px 0; border-bottom: 1px solid var(--border); }.filter-section:last-child { border-bottom: 0; }.filter-section h3 { margin: 0 0 12px; font: 700 12px Arial, sans-serif; }.filter-option { display: flex; align-items: center; gap: 9px; margin: 9px 0; color: var(--muted); font: 12px Arial, sans-serif; cursor: pointer; }.filter-option input { accent-color: var(--rose); }
.price-inputs { display: grid; grid-template-columns: 1fr 1fr; gap: 7px; }.price-inputs input { width: 100%; height: 35px; padding: 0 9px; border: 1px solid var(--border); border-radius: 8px; outline: 0; font-size: 11px; }.apply-price { width: 100%; height: 35px; margin-top: 8px; color: #fff; background: var(--deep); border-radius: 8px; font-size: 11px; font-weight: 700; }
.shop-toolbar { justify-content: space-between; gap: 12px; margin-bottom: 17px; }.results { color: var(--muted); font: 12px Arial, sans-serif; }.toolbar-right { gap: 8px; }.mobile-filter { display: none; align-items: center; gap: 6px; padding: 9px 13px; color: var(--deep); background: var(--blush-light); border-radius: 20px; font-size: 11px; font-weight: 700; }.mobile-filter .icon { width: 14px; }.sort-select { height: 38px; padding: 0 30px 0 12px; color: var(--deep); background: #fff; border: 1px solid var(--border); border-radius: 10px; outline: 0; font-size: 11px; }
.products-page .product-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 17px; }.products-page .product-card { padding: 9px; background: #fff; border: 1px solid var(--border); border-radius: 21px; transition: transform .25s, box-shadow .25s; }.products-page .product-card:hover { transform: translateY(-5px); box-shadow: var(--shadow); }.products-page .product-image { position: relative; height: 235px; overflow: hidden; display: grid; place-items: center; background: linear-gradient(145deg, #fff1f4, #f2e3cf); border-radius: 16px; }.products-page .product-photo { width: 100%; height: 100%; object-fit: cover; }.products-page .product-badge { position: absolute; top: 10px; left: 10px; z-index: 1; padding: 5px 8px; color: #fff; background: var(--rose); border-radius: 8px; font: 800 9px Arial, sans-serif; }.products-page .wishlist-button { top: 10px; right: 10px; }.products-page .product-info { padding: 4px 4px 2px; }.products-page .product-category { margin-top: 8px; color: var(--rose); font: 700 9px Arial, sans-serif; letter-spacing: .7px; text-transform: uppercase; }.products-page .product-title { min-height: 36px; margin: 5px 0 0; color: var(--deep); font: 650 14px/1.35 Arial, sans-serif; }.products-page .price { display: flex; align-items: baseline; gap: 6px; }.products-page .discount { color: #4c8b65; font-size: 10px; font-weight: 800; }.card-actions { display: grid; grid-template-columns: 1fr 40px; gap: 7px; margin-top: 10px; }.products-page .quick-view { height: 38px; display: grid; place-items: center; color: #fff; background: var(--deep); border-radius: 10px; }.quick-view .icon { width: 16px; height: 16px; }.empty-products { padding: 55px 15px; color: var(--muted); text-align: center; font: 13px Arial, sans-serif; }
.pagination { display: flex; justify-content: center; align-items: center; gap: 7px; margin-top: 35px; }.page-btn { width: 36px; height: 36px; display: grid; place-items: center; color: var(--deep); background: #fff; border: 1px solid var(--border); border-radius: 10px; font-size: 11px; }.page-btn.active, .page-btn:hover { color: #fff; background: var(--deep); border-color: var(--deep); }
.products-page .trust-banner { margin-top: 60px; display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; padding: 25px; background: var(--blush-light); border-radius: 23px; }.products-page .trust-item { display: flex; align-items: center; gap: 11px; }.products-page .trust-item .icon { width: 24px; height: 24px; color: var(--gold); }.products-page .trust-item strong, .products-page .trust-item span { display: block; }.products-page .trust-item strong { color: var(--deep); font: 700 11px Arial, sans-serif; }.products-page .trust-item span { margin-top: 3px; color: var(--muted); font: 9px Arial, sans-serif; }
.product-quick-modal { text-align: left; }.product-quick-modal .modal-icon { width: 100%; height: 230px; }.product-quick-modal .modal-icon img { width: 100%; height: 100%; object-fit: contain; border-radius: 13px; }

@media (max-width: 1100px) { .products-page .product-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }.shop-layout { grid-template-columns: 215px minmax(0, 1fr); }.products-page .trust-banner { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 850px) { .shop-layout { grid-template-columns: 1fr; }.filters { display: none; position: fixed; top: 0; left: 0; z-index: 3500; width: min(320px, 90vw); height: 100vh; overflow: auto; border-radius: 0; }.filters.mobile-open { display: block; }.mobile-filter { display: inline-flex; } }
@media (max-width: 600px) { .breadcrumb { padding: 16px 14px 5px; }.products-page { padding: 15px 12px 50px; }.page-heading { align-items: flex-start; flex-direction: column; }.shop-toolbar { align-items: flex-start; flex-direction: column; }.toolbar-right { width: 100%; justify-content: space-between; }.sort-select { flex: 1; }.products-page .product-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }.products-page .product-image { height: 180px; }.products-page .product-title { font-size: 12px; }.products-page .price { font-size: 14px; }.products-page .card-actions { grid-template-columns: 1fr; }.products-page .quick-view { display: none; }.products-page .trust-banner { grid-template-columns: 1fr; } }