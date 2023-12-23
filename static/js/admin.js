function handleSelection(element,content) {
    const routeContent = document.querySelector('.route-content')
    const logContent = document.querySelector('.log-content')

    if(content == 'routes'){
        routeContent.style.display = 'grid'
        logContent.style.display = 'none'
    }else{
        routeContent.style.display = 'none'
        logContent.style.display = 'block'
    }
    const trackers = document.querySelectorAll('.tracker')
    trackers.forEach(tracker => {
        tracker.classList.remove('selected-option')
    })
    element.classList.add('selected-option')
}


function handleApprove(id) {
    const confirm = window.confirm('Are you sure you want to approve this driver?')
    if(!confirm){
        return;
    }
    console.log('approve', id)
    fetch(`/admin/approve/${id}`, {
            method: 'POST',
        }).then(response => response.json()).then(result => {
            console.log(result)
            if(result.status == 'success'){
                window.location.href = '/admin/drivers';
            }
        });
}

function handleReject(id) {
    const confirm = window.confirm('Are you sure you want to reject this driver?')
    if(!confirm){
        return;
    }
    
    console.log('reject', id)
    fetch(`/admin/reject/${id}`, {
            method: 'POST',
        }).then(response => response.json()).then(result => {
            console.log(result)
            if(result.status == 'success'){
                window.location.href = '/admin/drivers';
            }
        });
}