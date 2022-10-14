const allSideMenu = document.querySelectorAll('#sidebar .side-menu.top li a');
var selectedMeter = 'general';
allSideMenu.forEach(item=> {
	const li = item.parentElement;

	item.addEventListener('click', function () {
		allSideMenu.forEach(i=> {
			i.parentElement.classList.remove('active');
		})
		li.classList.add('active');
		meter.innerHTML = Burhan;
	})
});




// TOGGLE SIDEBAR
const menuBar = document.querySelector('#content nav .bx.bx-menu');
const sidebar = document.getElementById('sidebar');

menuBar.addEventListener('click', function () {
	sidebar.classList.toggle('hide');
})







const searchButton = document.querySelector('#content nav form .form-input button');
const searchButtonIcon = document.querySelector('#content nav form .form-input button .bx');
const searchForm = document.querySelector('#content nav form');

searchButton.addEventListener('click', function (e) {
	if(window.innerWidth < 576) {
		e.preventDefault();
		searchForm.classList.toggle('show');
		if(searchForm.classList.contains('show')) {
			searchButtonIcon.classList.replace('bx-search', 'bx-x');
		} else {
			searchButtonIcon.classList.replace('bx-x', 'bx-search');
		}
	}
})





if(window.innerWidth < 768) {
	sidebar.classList.add('hide');
} else if(window.innerWidth > 576) {
	searchButtonIcon.classList.replace('bx-x', 'bx-search');
	searchForm.classList.remove('show');
}


window.addEventListener('resize', function () {
	if(this.innerWidth > 576) {
		searchButtonIcon.classList.replace('bx-x', 'bx-search');
		searchForm.classList.remove('show');
	}
})



const switchMode = document.getElementById('switch-mode');

switchMode.addEventListener('change', function () {
	if(this.checked) {
		document.body.classList.add('dark');
	} else {
		document.body.classList.remove('dark');
	}
})

function getRandomColor() {
	var letters = '0123456789ABCDEF'.split('');
	var color = '#';
	for (var i = 0; i < 6; i++) {
		color += letters[Math.floor(Math.random() * 16)];
	}
	return color+'B3';
}

function selectedRow(){
                
	var index, table = document.getElementById("meterTable");
	for(var i = 1; i < table.rows.length; i++)
	{
		table.rows[i].onclick = function()
		{
			 // remove the background from the previous selected row
			if(typeof index !== "undefined"){
			   table.rows[index].classList.toggle("selected");
			}
			// get the selected row index
			index = this.rowIndex;
			// add class selected to the row
			this.classList.toggle("selected");
			if (index<=3){
				if (index==1){
					chartConfig.data.labels = x1;
					chartConfig.data.datasets[0].data = y1;
					var selectedMeter = 'PS-B-ELE-L03-EM001';
					meterName.innerHTML= 'PS-B-ELE-L03-EM001';
					meterDescription.innerHTML = 'PS-B-ELE-L03-EM001 EMS Lighting'
				} else if (index==2){
					chartConfig.data.labels = x1;
					chartConfig.data.datasets[0].data = y1;
					var selectedMeter = 'PS-B-ELE-L03-EM002';
					meterName.innerHTML= 'PS-B-ELE-L03-EM002';
					meterDescription.innerHTML = 'PS-B-ELE-L03-EM002 EMS Power'
				}
				else if (index==3){
					chartConfig.data.labels = x1;
					chartConfig.data.datasets[0].data = y1;
					var selectedMeter = 'PS-B-ELE-L03-EM003';
					meterName.innerHTML= 'PS-B-ELE-L03-EM003';
					meterDescription.innerHTML = 'PS-B-ELE-L03-EM003 EMS Lighting'
				}
				chartConfig.options.scales.y.beginAtZero = false;
				Chart1.update('active');
			} else {
				meterName.innerHTML='EMS';
				meterDescription.innerHTML = 'Total consuption of all meters';
				chartConfig.options.scales.y.beginAtZero = true;
				chartConfig.data.labels = xValues;
				chartConfig.data.datasets[0].data = yValues;
				Chart1.update('active');
			}
		 };
	}
	
}