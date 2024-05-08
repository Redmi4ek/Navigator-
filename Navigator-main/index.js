const sendMoneyBtn = document.querySelector('.continue_btn'),
getAmount = document.getElementById('get_amount'),
transactionName = document.querySelector('.transaction-name'),
sendTo = document.getElementById('send_to'),
sendAmount = document.getElementById('send_amount'),
current_balance_div = document.getElementById('current_balance'),
recentActionsDiv = document.querySelector('.transactions');

// TRANSFER MONEY BTN
function transferMoney() {
    const send_to = document.getElementById('send_to').value; 
    const send_amount = parseFloat(document.getElementById('send_amount').value);
    const send_from = document.getElementById('send_from').value; 

    const formData = {
        amount: send_amount,
        sender_id: send_from,
        receiver_id: send_to  
    };

    fetch('http://localhost:1111/moneytransfercommand/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
    })
    .then(response => response.json())
    .then(data => {
        console.log('Money transfer successful:', data);
        // Добавьте здесь код для отображения сообщения об успешном переводе
    })
    .catch(error => {
        console.error('An error occurred during money transfer:', error);
        // Добавьте здесь код для отображения сообщения об ошибке
    });
}



function depositMoney() {
    const amount = parseFloat(document.getElementById('get_amount').value);
    const account_id = parseInt(document.getElementById('account').value); 

    const formData = {
        amount: amount,
        account_id: account_id
    };

    fetch('http://localhost:1111/moneydepositcommand/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
    })
    .then(response => response.json())
    .then(data => {
        console.log('Money deposit successful:', data);
        // Add code here to display a success message
    })
    .catch(error => {
        console.error('An error occurred during money deposit:', error);
        // Add code here to display an error message
    });
}

function registerAccount() {
    const account_name = document.getElementById('account_name').value;
    const account_email = document.getElementById('account_email').value;
    const password_hash = document.getElementById('password_hash').value;

    const formData = {
        account_name: account_name,
        account_email: account_email,
        password_hash: password_hash
    };

    fetch('http://localhost:1111/accountcreatecommand/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
    })
    .then(response => response.json())
    .then(data => {
        console.log('Account creation successful:', data);
        // Сохраняем user_id в глобальной переменной
        window.user_id = data.user_id;
        // Перенаправляем пользователя на index.html
        window.location.href = 'index.html';
    })
    .catch(error => {
        console.error('An error occurred during account creation:', error);
        // Добавьте здесь код для отображения сообщения об ошибке
    });
}