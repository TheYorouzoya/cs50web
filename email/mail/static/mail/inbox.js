document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => {
    history.pushState({'mailbox': 'inbox'}, '', '#inbox');
    load_mailbox('inbox');
  });
  document.querySelector('#sent').addEventListener('click', () => {
    history.pushState({'mailbox': 'sent'}, '', '#sent');
    load_mailbox('sent')
  });
  document.querySelector('#archived').addEventListener('click', () => {
    history.pushState({'mailbox': 'archive'}, '', '#archive');
    load_mailbox('archive')
  });
  document.querySelector('#compose').addEventListener('click', () => {
    history.pushState({'mailbox': 'compose'}, '', '#compose');
    compose_email();
  });

  // If a history state exists, load the specific mailbox
  if (history.state !== null) {
    if (history.state.id) {
      load_email(history.state.id);
    } else if (history.state.mailbox === 'compose') {
      compose_email();
    } else {
      load_mailbox(history.state.mailbox);
    }
  }  else {
    // Load the inbox by default
    load_mailbox('inbox');
  }

  // If popstate is fired, i.e., user clicks back/forward button on the browser
  window.addEventListener('popstate', function (event) {
    // If a previous state exists
    if (event.state) {
      // If state is an email
      if (event.state.id) {
        load_email(event.state.id);
      } else if (event.state.mailbox === 'compose') {
        // If state was compose page
        compose_email();
      } else {
        // Load mailbox in state
        load_mailbox(event.state.mailbox);
      }
    } else {
      // Load inbox if no previous state exists
      load_mailbox('inbox');
    }
  });

  document.querySelector('#compose-form').onsubmit = function () {
    
    // Send POST request with the email contents
    fetch('/emails', {
      method: 'POST',
      body: JSON.stringify({
        recipients: document.querySelector('#compose-recipients').value,
        subject: document.querySelector('#compose-subject').value,
        body: document.querySelector('#compose-body').value
      })
    })

    .then(response => {
      return response.json();
    })
    .then(data => {
      if (data.error) {
        // If form is invalid
        display_error(data.error);
      } else { 
        // Email sent successfully
        // Push history state
        history.pushState({ 'mailbox': 'inbox' }, '', '#inbox');
        // Load sent mailbox
        load_mailbox('sent');
        // Display success message
        display_success(data.message);
      }
    })

    .catch(error => {
      console.log(error);
    });
    return false;
  }

});

function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#message').style.display = 'none';
  document.querySelector('#email').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';

}

function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#message').style.display = 'none';
  document.querySelector('#email').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3 id="mailbox-heading">${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;


  fetch(`emails/${mailbox}`)

  .then(response => response.json())
  .then(data => {
    // For each email in response
    data.forEach(email => {
      // Initialize email div
      const email_container = document.createElement('div');
      email_container.classList.add('email', email.read);
      email_container.dataset.id = email.id;
      let fields = ["sender", "subject", "timestamp"];

      // Populate fields as separate divs and add to container
      fields.forEach(field => {
        let div = document.createElement('div');
        div.classList.add(field);
        div.textContent = email[field];
        email_container.append(div);
      })

      // Add on click listener
      email_container.addEventListener('click', function () {
        // Push history state
        history.pushState({'id': this.dataset.id}, '', `#${mailbox}?id=${this.dataset.id}`);

        // Set read status to true
        if (email.read === false) {
          fetch(`emails/${this.dataset.id}`, {
            method: 'PUT',
            body: JSON.stringify({
              read: true
            })
          })
        }

        // Load the email
        load_email(this.dataset.id, mailbox);
      });

      // Append the email to container
      document.querySelector('#emails-view').append(email_container);
      
    })
  })
  .catch(error => {
    console.log(error);
  });
}

function load_email(id, mailbox) {

  // Show the email and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#message').style.display = 'none';
  document.querySelector('#email').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';
  
  // Clear the view
  document.querySelector('#email').innerHTML = '';

  // Fetch the email from the database
  fetch(`emails/${id}`)

  .then(response => response.json())
  .then(data => {
    if (data.error) {
      // If there's an error, display it
      display_error(data.error);
    } else {
      // Initialize mail container
      const mail_container = document.createElement('div');
      mail_container.setAttribute('id', 'mail');

      // Initialize email fields
      let fields = ["subject", "sender", "recipients", "timestamp"];
      
      // For each email field
      fields.forEach(field => {
        // Create div, add class, add data
        let div = document.createElement('div');
        div.classList.add(field);
        if (field === "sender") {
          div.innerHTML = `<b>From:</b> ${data[field]}`;
        } else if (field === "recipients") {
          div.innerHTML = `<b>To:</b> ${data[field]}`;
        } else {
          div.textContent = data[field];
        }
        mail_container.append(div);
      })

      // For reply and archive buttons
      // Exempt the sent mailbox
      if (mailbox !== 'sent') {
        // Initialize archive button
        const archive_button = document.createElement('button');
        // If mail isn't archived, add Archive button
        if (!data.archived) {
          archive_button.classList.add('btn', 'btn-outline-success');
          archive_button.textContent = "Add To Archive";
        } else {
          // Add Remove button
          archive_button.classList.add('btn', 'btn-outline-secondary');
          archive_button.textContent = "Remove from Archive";
        }

        // Add click listener to archive button
        archive_button.addEventListener('click', function () {
          // Push history state
          history.pushState({ 'id': id }, '', `#${mailbox}/?id=${id}`);

          // Update archive status in database
          fetch(`emails/${id}`, {
            method: 'PUT',
            body: JSON.stringify({
              archived: !data.archived
            })
          })
            .then(response => {
              // Load mailbox once request is processed
              load_mailbox('inbox');
            })

        });

        // Initialize reply button
        const reply_button = document.createElement('button');
        reply_button.classList.add('btn', 'btn-outline-info');
        reply_button.textContent = "Reply";

        reply_button.addEventListener('click', function () {
          // Push history state
          history.pushState({ 'id': id }, '', `#${mailbox}/?id=${id}`);

          // Render reply view
          reply_view(data);
        });

        // Append archive and reply buttons
        const button_container = document.createElement('div');
        button_container.classList.add('btn-container');

        button_container.append(reply_button);
        button_container.append(archive_button);
        mail_container.append(button_container);
      }

      const ruler = document.createElement('hr');
      mail_container.append(ruler);

      // Initialize email's body container
      const body_container = document.createElement('div');
      body_container.classList.add('body');
      body_container.textContent = data["body"];

      mail_container.append(body_container);
      document.querySelector('#email').append(mail_container);
    }
  })
}

function reply_view(email) {
  // Hide other views and show compose form
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#message').style.display = 'none';
  document.querySelector('#email').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out compose fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';

  document.querySelector('#compose-recipients').value = email.sender;
  // Regex to text the "Re: " prefix in subject
  let header = /^Re: /;
  if (header.test(email.subject)) {
    document.querySelector('#compose-subject').value = email.subject;
  } else {
    document.querySelector('#compose-subject').value = "Re: " + email.subject;
  }
  document.querySelector('#compose-body').value = `On ${email.timestamp}, ${email.sender} wrote: ` + email.body;

}

function display_error(error) {
  document.querySelector('#message').innerHTML = '';
  const element = document.createElement('div');
  element.classList.add('alert', 'alert-danger');
  element.setAttribute('role', 'alert');
  element.textContent = error;
  document.querySelector('#message').append(element);
  document.querySelector('#message').style.display = 'block';
}

function display_success(message) {
  document.querySelector('#message').innerHTML = '';
  const element = document.createElement('div');
  element.classList.add('alert', 'alert-success');
  element.setAttribute('role', 'alert');
  element.textContent = message;
  document.querySelector('#message').append(element);
  document.querySelector('#message').style.display = 'block';
}
