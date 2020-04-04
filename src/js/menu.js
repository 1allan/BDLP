const navButton = document.getElementById('index-button')
const navMenu = document.getElementById('side-nav')
const teiWrapper = document.getElementById('tei_wrapper')
const header = document.querySelector('header')
let menuIsActive = false

//Get depth of a element in the document tree
function getElementDepth(el, root, offset=0) {
	let depth = 0
	while (el.parentElement !== root) {
		el = el.parentElement
		depth++
	}
	return depth - offset
}

//Generate indexes
document.querySelectorAll('#tei_wrapper head').forEach(el => {
	let elementDepth = getElementDepth(el, teiWrapper, 3)
	let a = document.createElement('a')
	
	a.innerHTML = el.innerText
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
	navMenu.appendChild(a)
})

//Toggle index menu on click
document.addEventListener('click', ev => {
	if ([navButton, ...navButton.children].includes(ev.target)) {
		if (menuIsActive) {
			navMenu.style.right = '-310px'
			menuIsActive = false
			
		} else {
			navMenu.style.right = '0px'
			menuIsActive = true
		}
	} else if (![navMenu, ...navMenu.children].includes(ev.target)) {
		navMenu.style.right = '-310px'
		menuIsActive = false
	}
})

//Toggle header on scroll
let lastScrollTop = 0;
document.addEventListener("scroll", () => {
   let st = window.pageYOffset || document.documentElement.scrollTop
   if (st > lastScrollTop && !menuIsActive){
   		header.style.top = '-200px'
   } else {
   		header.style.top = '0'
   }
   lastScrollTop = st <= 0 ? 0 : st
}, false)