// this file contains the javascript used to request the map to the backend and display it on the page
let report_placeholder = document.createElement('option');
report_placeholder.text = "Reporte";
report_placeholder.defaultSelected = true;

let year_placeholder = document.createElement('option');
year_placeholder.text = "Año";
year_placeholder.defaultSelected = true;

let report_select = document.getElementById('report');
let year_select = document.getElementById('year');

// fill report list when province is selected
document.getElementById('province').addEventListener('change', function() {
    let province = document.getElementById('province').value;

    year_select.disabled = true;
    year_select.innerHTML = "";
    year_select.appendChild(year_placeholder);
    
    // make a request to the backend
    fetch(`/map_index_reports/${province}/`)
    .then(response => response.json())
    .then(data => {
        // clear the options
        report_select.innerHTML = "";
        report_select.append(report_placeholder);
    
        // add the options
        data.reports.forEach(report => {
            let option = document.createElement('option');
            option.value = report;
            option.text = report;
            report_select.appendChild(option);
        });

        report_select.disabled = false;
    });
});

// fill year list when report is selected
document.getElementById('report').addEventListener('change', function() {
    let province = document.getElementById('province').value;
    let report = document.getElementById('report').value;

    // make a request to the backend
    fetch(`/map_index_years/${province}/${report}/`)
    .then(response => response.json())
    .then(data => {
        // clear the options
        year_select.innerHTML = "";
        year_select.append(year_placeholder);
    
        // add the options
        data.years.forEach(year => {
            let option = document.createElement('option');
            option.value = year;
            option.text = year;
            year_select.appendChild(option);
        });

        year_select.disabled = false;
    });
});

// request map when submit button is clicked
document.getElementById('submit').addEventListener('click', function() {
    // get the values of the inputs
    let province = document.getElementById('province').value;
    let report = document.getElementById('report').value;
    let year = document.getElementById('year').value;

    if(province == "null") {
        // warn user and return
        alert("Please select a province");
        return;
    }

    if(report == "null") {
        // warn user and return
        alert("Please select a report type");
        return;
    }

    if(year == "null") {
        // warn user and return
        alert("Please select a year");
        return;
    }

    // make a request to the backend
    fetch(`/map/${province}/${report}/${year}/`)
    .then(response => response.text())
    .then(data => {
        let map = document.getElementById('map');
        map.innerHTML = data;
    });
});