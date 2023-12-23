

$('#datepicker').datepicker({
    format: 'd MM yyyy',
    autoclose: true,
    todayHighlight: true,
    language: 'en-GB',
    startDate: '-0d',
});


function checkDateValidity() {
    console.log('checking date validity')
    const dateInput = document.querySelector('#datepicker')
    const date = dateInput.value
    const parts = date.split(' ');

    const year = parseInt(parts[2]);
    const monthString = parts[1];
    const day = parseInt(parts[0]);

    const monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
    const month = monthNames.indexOf(monthString);

    const dateObj = new Date(year, month, day);

    const today = new Date()
    console.log(dateObj)
    console.log(today)
    if (dateObj < today) {
        console.log('date is in the past')

        const existingNowDiv = document.querySelector('#now')
        if (existingNowDiv) {
            return
        }
        const dropdownContent = document.getElementById('time-dropdown-content');
        const nowDiv = document.createElement('div')
        nowDiv.className = 'time-option'
        nowDiv.id = 'now'
        nowDiv.textContent = 'Now'
        nowDiv.onclick = () => selectTimeOption('Now');
        dropdownContent.appendChild(nowDiv);
    } else {
        const dropdownContent = document.getElementById('time-dropdown-content');
        const nowDiv = document.querySelector('#now')
        dropdownContent.removeChild(nowDiv)
        const selectedTime = document.getElementById('selected-time')
        selectedTime.textContent = ''
    }
    console.log(date)
}


function convertTextToDate(text){
    const parts = text.split(' ');

    const year = parseInt(parts[2]);
    const monthString = parts[1];
    const day = parseInt(parts[0]);
    console.log(year)
    console.log(monthString)
    console.log(day)

    const monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
     "November", "December"];
    const month = monthNames.indexOf(monthString);
    console.log('month is ',month)

    const dateObj = new Date(year, month, day);
    return dateObj
}

function convertDateToText(dateString){
    const dateObj = new Date(dateString)
    const year = dateObj.getFullYear()
    const month = dateObj.getMonth()
    const day = dateObj.getDate()
    
    const monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", 
    "October","November", "December"];
    const monthString = monthNames[month];
    console.log('date string is', dateString)
    console.log(year)
    console.log('month is ',month)
    console.log(monthString)
    console.log(day)

    const date = day + ' ' + monthString + ' ' + year
    return date
}