// document.addEventListener('DOMContentLoaded', function () {
//     // 모달 요소 가져오기
//     const reservationModal = document.getElementById('reservationModal');
//     // 추가 버튼 가져오기
//     const addButton = document.getElementById('addButton');
//     // 주소 입력 폼의 부모 요소 가져오기
//     const formGroup = document.querySelector('.form-group');

//     // 추가 버튼 클릭 시 이벤트 처리
//     addButton.addEventListener('click', function () {
//         // 새로운 주소 입력 필드 생성
//         const newAddressInput = document.createElement('input');
//         newAddressInput.type = 'text';
//         newAddressInput.name = 'address';
//         newAddressInput.placeholder = '주소를 입력하세요';
//         newAddressInput.classList.add('form-control');
//         newAddressInput.required = true;

//         // 주소 입력 폼에 새로운 입력 필드 추가
//         formGroup.appendChild(newAddressInput);
//     });
// });

// document.addEventListener('DOMContentLoaded', function () {
//     const addAddressButton = document.getElementById('addAddressButton');
//     const addressInputs = document.getElementById('addressInputs');

//     addAddressButton.addEventListener('click', function () {
//         const newAddressInput = document.createElement('input');
//         newAddressInput.type = 'text';
//         newAddressInput.name = 'address[]';
//         newAddressInput.placeholder = '주소';
//         addressInputs.appendChild(newAddressInput);
//     });
// });
let count = 1;
document.addEventListener('DOMContentLoaded', function () {
    const addAddressButton = document.getElementById('addAddressButton');
    const addressInputs = document.getElementById('addressInputs');

    addAddressButton.addEventListener('click', function () {
        count++;
        const addressGroup = document.createElement('div');
        addressGroup.classList.add('address-group');

        const newAddressInput = document.createElement('input');
        newAddressInput.type = 'text';
        newAddressInput.name = 'address' + count;
        newAddressInput.placeholder = '주소';
        newAddressInput.classList.add('form-control');
        newAddressInput.required = true;

        const newPeopleInput = document.createElement('input');
        newPeopleInput.type = 'number';
        newPeopleInput.name = 'people' + count;
        newPeopleInput.placeholder = '인원 수';
        newPeopleInput.classList.add('form-control');
        newPeopleInput.min = '1';
        newPeopleInput.required = true;

        addressGroup.appendChild(newAddressInput);
        addressGroup.appendChild(newPeopleInput);
        addressInputs.appendChild(addressGroup);
    });
});