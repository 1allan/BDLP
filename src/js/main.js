const menuButton = document.getElementById('index-button')
const indexMenu = document.getElementById('index-menu')
const teiWrapper = document.getElementById('tei-wrapper')
const header = document.querySelector('header') || null
let url = window.location.href.split('/')

if (header) {
	header.classList.add('active')
	
	//Toggle index menu on click
	document.addEventListener('click', ev => {
		if ([menuButton, ...menuButton.children ].includes(ev.target)) {
			indexMenu.classList.toggle('active')
			menuButton.classList.toggle('close')
		} else if (![indexMenu, ...indexMenu.children].includes(ev.target)) {
			indexMenu.classList.remove('active')
			menuButton.classList.remove('close')
		} 
	})

	//Toggle header on scroll
	let lastScrollTop = 0;
	document.addEventListener("scroll", () => {
		let st = window.pageYOffset || document.documentElement.scrollTop
		if (st > lastScrollTop && !indexMenu.classList.contains('active')){
			header.classList.remove('active')
		} else {
			header.classList.add('active')
		}
		lastScrollTop = st <= 0 ? 0 : st
	})
}

setTimeout(() => {
	document.querySelector('#device-alert').style.opacity = 0
}, 5500)

// Removes teibp.xsl generated index, so it appears only in the HTML version
document.getElementById('index').remove()

// Prevents page from FOUC
document.body.onload = () => {
	document.body.removeAttribute('class')
	let loadWall = document.getElementById('load-wall')
	loadWall.querySelector('.progress-bar span').style.width = '100%'
	loadWall.style.opacity = '0'
	setTimeout(() => {
		loadWall.style.display = 'none'
	}, 1000)
	
}