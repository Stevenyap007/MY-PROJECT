var err;
var username, email, gender, address;

function check_alphanumeric(name){
    for(let i=0; i < name.length ; i++){
        if(!(
            (name.charAt(i) >= '0' && name.charAt(i) <='9') || 
            (name.charAt(i) >= 'a' && name.charAt(i) <='z') || 
            (name.charAt(i) >= 'A' && name.charAt(i) <='Z')
        )){
            return false;
        }
    }
    return true;
}

function validate_username(){
    username = document.getElementById("input_username").value;
    if(username.length < 6){
        err.innerHTML = "Please enter your Fullname"
        return false;
    }

    if(check_alphanumeric(username) == false){
        err.innerHTML = "Username must be alphanumeric"
        return false;
    }
    return true;
   
}

function check_email(email){
    for(let i = 0; i< email.length ; i++){
        if(email.charAt(i) == '@') return true;
    }
    return false;
}

function validate_email(){
    email=document.getElementById("input_email").value;
    if(email.length < 1){
        err.innerHTML = "Email must not be empty";
        return false;
    }

    if( ! email.endsWith(".com")){
        err.innerHTML = "Email must ends with .com!"
        return false;
    }

    if( ! check_email(email)){
        err.innerHTML = "Email invalid"
        return false
    }
    return true
}

function validate_gender(){
    gender = document.getElementById("input_gender").value
    // console.log(gender)
    if(gender == ""){
        err.innerHTML = "Please select a gender"
        return false;
    }
    return true;
}

function validate_address(){
    address = document.getElementById("input_address").value;

    if(! address.includes("Street")){
        err.innerHTML = "Address must have word \"Street\""
        return false
    }
    return true
}

function validate_agree(){
    var agree = document.getElementById("input_agree").checked
    if(!agree){
        err.innerHTML = "you must agree with our terms and condition"
        return false
    }
    return true
}

function on_submit(){
    err= document.getElementById("error");

    if(validate_username() == false){
        return
    }
    else if(validate_email() == false) {
        return
    }
    else if(validate_gender() == false){
        return
    }
    else if(validate_address() == false){
        return
    }
    else if(validate_agree() == false){
        return
    }
    else{
        err.innerHTML = ""

        var formConfirm = 
        "Username: "+ username + "\n" +
        "Email: "+ email + "\n" +
        "Gender: "+ gender + "\n" +
        "Address: "+ address + "\n" 

        if(confirm(formConfirm)){
            alert("PLEASE ENJOY YOUR MEMBERSHIP")
            setInterval('refresh()', 500);
        }else{
            alert("You cancelled your membership registration")
            setInterval('refresh()', 500);
        }
    }
}

function on_reset(){
    err.innerHTML = "";
}