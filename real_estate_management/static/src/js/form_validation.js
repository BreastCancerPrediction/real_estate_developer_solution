const submitButton = document.getElementById('sub_btn');
function validatePhoneNumber(phoneNumber) {
    if (typeof phoneNumber !== 'string') {
        return false;
    }
    const regex = /^[0-9]+$/;
    return regex.test(phoneNumber);
}

function validateName(name) {
    if (typeof name !== 'string') {
        return false;
    }
    // Updated regex to prevent leading spaces
    const regex = /^[A-Za-z]+[A-Za-z\s]*$/;
    return regex.test(name);
}

function setupPhoneValidation() {
    const phoneInput = document.querySelector('input[name="phone"]');

    if (phoneInput) {
        phoneInput.addEventListener('input', function() {
            const inputValue = this.value;

            if (!validatePhoneNumber(inputValue)) {
            console.log("this=====>",this)
                this.setCustomValidity("Phone number must contain only numbers.");
            } else {
                this.setCustomValidity("");
            }
            this.reportValidity();
        });
    } else {
        console.error("Phone input field not found.");
    }
}

function setupNameValidation() {
    const nameInput = document.querySelector('input[name="name"]');

    if (nameInput) {
        nameInput.addEventListener('input', function() {
            const inputValue = this.value;

            if (!validateName(inputValue)) {
                this.setCustomValidity("Name must start with a letter and contain only letters and spaces and no space at starting");
            } else {
                this.setCustomValidity("");
            }
            this.reportValidity();
        });
    } else {
        console.error("Name input field not found.");
    }
}

document.addEventListener('DOMContentLoaded', function() {
    setupPhoneValidation();
    setupNameValidation();
});

if (submitButton) {
    submitButton.addEventListener('click', function (event) {
        console.log("form submission starts");
        const phoneInput = document.querySelector('input[name="phone"]');
        const phoneNumber = phoneInput.value;
        const nameInput = document.querySelector('input[name="name"]');
        const nameValue = nameInput.value;

        let isValid = true;

        if (!validatePhoneNumber(phoneNumber)) {
            event.preventDefault();
            console.log("setCustomValidity====",this)
            phoneInput.setCustomValidity("Phone number must contain only numbers");
            phoneInput.reportValidity();
            console.log("Phone number validation failed");
            isValid = false;
        } else {
            phoneInput.setCustomValidity("");
            phoneInput.reportValidity();
        }

        if (!validateName(nameValue)) {
            event.preventDefault();
            nameInput.setCustomValidity("Name must start with a letter and contain only letters and spaces. and no space at starting");
            nameInput.reportValidity();
            console.log("Name validation failed");
            isValid = false;
        } else {
            nameInput.setCustomValidity("");
            nameInput.reportValidity();
        }

        if (isValid) {
            console.log("All validations passed");
        }
    });
}