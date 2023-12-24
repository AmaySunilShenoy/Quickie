

$('#datepicker').datepicker({
    format: 'd MM yyyy',
    autoclose: true,
    todayHighlight: true,
    language: 'en-GB',
    startDate: '-0d',
});

function roundUpToNearestTenMinutes(date) {
    const newDate = new Date(date);
    const minutes = newDate.getMinutes();
    const remainder = minutes % 10;
    if (remainder !== 0) {
        newDate.setMinutes(minutes + (10 - remainder));
    }
    return newDate;
}


function populateTimeDropdown(state) {
    const dropdownContent = document.getElementById('time-dropdown-content');

    // Set start and end times (adjust as needed)
    let startTime;
    if (state === 'today') {
        const currentTime = new Date();
        startTime = roundUpToNearestTenMinutes(currentTime);
    } else if (state === 'future') {
        startTime = new Date();
        startTime.setHours(0, 0, 0, 0); // 00:00:00
    }

    const endTime = new Date();
    endTime.setHours(23, 50, 0, 0); // 23:50:00

    const nowDiv = document.createElement('div')
    nowDiv.className = 'time-option'
    nowDiv.id = 'now'
    nowDiv.textContent = 'Now'
    nowDiv.onclick = () => selectTimeOption('Now');
    dropdownContent.appendChild(nowDiv);


    // Loop through times and add options to dropdown content
    for (let time = new Date(startTime); time <= endTime; time.setMinutes(time.getMinutes() + 10)) {
        const option = document.createElement('div');
        option.className = 'time-option';
        option.textContent = time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        option.onclick = () => selectTimeOption(option.textContent);
        dropdownContent.appendChild(option);
    }
}


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
        console.log('date is in the past or today')
        const dropdownContent = document.getElementById('time-dropdown-content');

        const existingNowDiv = document.querySelector('#now')
        if (existingNowDiv) {
            return
        }
        dropdownContent.innerHTML = ''
        populateTimeDropdown('today');
    } else {
        console.log('date is in the future')
        const dropdownContent = document.getElementById('time-dropdown-content');
        dropdownContent.innerHTML = ''
        populateTimeDropdown('future');
        const nowDiv = document.querySelector('#now')
        if (nowDiv) {
            dropdownContent.removeChild(nowDiv)
        }
        const selectedTime = document.getElementById('selected-time')
        selectedTime.textContent = ''
    }
    console.log(date)
}


function convertTextToDate(text) {
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
    console.log('month is ', month)

    const dateObj = new Date(year, month, day);
    return dateObj
}

function convertDateToText(dateString) {
    const dateObj = new Date(dateString)
    const year = dateObj.getFullYear()
    const month = dateObj.getMonth()
    const day = dateObj.getDate()

    const monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September",
        "October", "November", "December"];
    const monthString = monthNames[month];
    console.log('date string is', dateString)
    console.log(year)
    console.log('month is ', month)
    console.log(monthString)
    console.log(day)

    const date = day + ' ' + monthString + ' ' + year
    return date
}