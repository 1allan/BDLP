window.onload = () => {
const navButton = document.getElementById('index-button')
const navMenu = document.getElementById('side-nav')
const teiWrapper = document.getElementById('tei_wrapper')
const fontebd = document.getElementById('fontebd')
const header = document.querySelector('header')

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
	a.setAttribute('href', '#' + el.id)
	navMenu.appendChild(a)
})

//Toggle index menu on click
document.addEventListener('click', ev => {
	if ([...navButton.children].includes(ev.target)) {
		navMenu.style.right = '0px'
	} else {
		navMenu.style.right = '-310px'
	}
})

//Toggle header on scroll
let lastScrollTop = 0;
document.addEventListener("scroll", () => {
   let st = window.pageYOffset || document.documentElement.scrollTop
   if (st > lastScrollTop){
   		header.style.top = '-200px'
   } else {
   		header.style.top = '0'
   }
   lastScrollTop = st <= 0 ? 0 : st
}, false)}