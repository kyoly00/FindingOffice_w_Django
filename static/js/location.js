document.addEventListener('DOMContentLoaded', function() {
    var addAddressButton = document.getElementById('addAddressButton');
    var addressInputs = document.getElementById('addressInputs');

    addAddressButton.addEventListener('click', function() {
        var addressGroup = document.createElement('div');
        addressGroup.classList.add('address-group');

        var addressInput = document.createElement('input');
        addressInput.type = 'text';
        addressInput.name = 'address[]';
        addressInput.placeholder = '주소';
        addressInput.classList.add('form-control');
        addressInput.required = true;

        var peopleInput = document.createElement('input');
        peopleInput.type = 'number';
        peopleInput.name = 'people[]';
        peopleInput.placeholder = '인원 수';
        peopleInput.classList.add('form-control');
        peopleInput.min = 1;
        peopleInput.required = true;

        addressGroup.appendChild(addressInput);
        addressGroup.appendChild(peopleInput);

        addressInputs.appendChild(addressGroup);
    });
});
