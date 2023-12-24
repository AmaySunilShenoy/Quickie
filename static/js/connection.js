
const alertDiv = document.querySelector('.alert-div')

function hideAlert(){
    const alertDiv = document.querySelector('.alert-div')
    alertDiv.style.display = 'none'
}

if(alertDiv){
    setTimeout(hideAlert, 2000)
}

  

function handleSubmit(event) {
    event.preventDefault();
    const formData = new FormData(document.querySelector('form'))
    if (formData.get('password') !== '') {
        fetch('/login', {
            method: 'POST',
            body: formData
        }).then(response => response.json()).then(data => {
            if (data.user) {
                // USER AUTH SUCCESS
                console.log("USER AUTH SUCCESS, sending to otp")
                window.location.href = '/otp';
            } else {
                //  USER AUTH FAILS
                console.log("USER AUTH FAILS")
                const passwordInput = document.querySelector('#password')
                const incorrectPassword = document.querySelector('.incorrect-password')
                passwordInput.value = ''
                passwordInput.style.border = '2px solid red'
                incorrectPassword.style.display = 'block'
            }
        })
    } else {
        fetch('/check', {
            method: 'POST',
            body: formData
        }).then(response => response.json()).then(data => {
            console.log(data.user)
            if (data.user) {
                // USER EXISTS
                const createHeader = document.querySelector('.create-header')
                const loginHeader = document.querySelector('.login-header')
                const passwordInput = document.querySelector('#password')

                if (window.innerWidth < 508) {
                    loginHeader.style.animation = 'moveRight 1.3s forwards'
                    createHeader.style.animation = 'moveLeftFade 1.3s forwards'
                } else {
                    loginHeader.style.animation = 'jumpAndLeft 1.3s forwards'
                    createHeader.style.animation = 'moveLeftFade 1.3s forwards 0.63s'
                }
                passwordInput.type = 'password'
                setTimeout(() => {
                    passwordInput.style.height = '40px'
                    passwordInput.style.padding = '25px'

                }, 800)
            } else {
                // USER DOESNT EXIST, USER CREATION
                const createHeader = document.querySelector('.create-header')
                const loginHeader = document.querySelector('.login-header')
                const orHeader = document.querySelector('.or-header')
                const passwordInput = document.querySelector('#password')

                if (window.innerWidth < 508) {
                    loginHeader.style.animation = 'moveLeftFade 1.3s forwards'
                    createHeader.style.animation = 'moveRight 1.3s forwards'
                } else {
                    loginHeader.style.animation = 'moveRightFade 0.8s forwards 0.63s'
                    createHeader.style.animation = 'jumpAndRight 1.3s forwards'
                    orHeader.style.animation = 'moveRightFade 1.3s forwards 0.63s'
                }
                passwordInput.type = 'password'
                setTimeout(() => {
                    passwordInput.style.height = '0px'
                    passwordInput.style.padding = '0px'
                }, 800)
                setTimeout(() => {
                    localStorage.setItem('email', formData.get('email'))
                    window.location.href = '/signup'
                }, 1000)
            }
        })
    }

}