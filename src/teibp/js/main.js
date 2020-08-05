const menuButton = document.getElementById('index-button')
const indexMenu = document.getElementById('index-menu')
const teiWrapper = document.getElementById('tei-wrapper')
const header = document.querySelector('header') || null
let url = window.location.href.split('/')


//Get element depth in the document tree
function getElementDepth(el, root, offset=0) {
	let depth = 0
	while (el.parentElement !== root) {
		el = el.parentElement
		depth++
	}
	return depth - offset
}

if (header) {
	header.classList.add('active')
	
	//Generate indexes
	document.querySelectorAll('#tei-wrapper head, span.head').forEach(el => {
		let elementDepth = getElementDepth(el, teiWrapper, 3)
		let a = document.createElement('a')
		let clone = el.cloneNode(true)
		
		clone.querySelectorAll('*').forEach(child => child.remove())
		
		a.innerHTML = clone.textContent
		a.setAttribute('data-depth', elementDepth)
		a.addEventListener('click', ev => {
			let href = location.href
			if (href.includes('#')) {
				window.location = href.slice(0, href.indexOf('#') + 1) + el.id
			} else {
				window.location = href + '#' + el.id
			}
			scrollBy(0, -80)
		})
		indexMenu.appendChild(a)
	})

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

// Removes teibp.xsl generated index, so it appears only in the HTML version
document.getElementById('index').remove()

// Prevents page from FOUC
document.body.onload = () => document.body.removeAttribute('class')