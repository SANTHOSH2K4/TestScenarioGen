const inputFile = document.getElementById('input-file');
const inputFileBtn = document.getElementById('input-file-btn');
const fileNameElement = document.getElementById('file-name');
const fileStatusContainer = document.getElementById('file-status');

const fileInput = document.getElementById('input-file');
const fileButton = document.getElementById('input-file-btn');
function createFormattedDiv(inputString) {
    // Helper function to clean and format the input string
    function cleanAndFormatString(str) {
        // Remove common unwanted notations
        str = str.replace(/###/g, ""); // Remove '###'
        str = str.replace(/--+/g, "—"); // Convert multiple dashes to em-dashes
        str = str.replace(/\s{2,}/g, " "); // Replace multiple spaces with a single space
        str = str.trim(); // Trim leading and trailing whitespace

        // Replace **text** with <strong>text</strong>
        str = str.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");

        // Replace `code` with <code>code</code>
        str = str.replace(/`(.+?)`/g, "<code>$1</code>");

        // Replace [text](link) with <a href="link">text</a>
        str = str.replace(/\[(.+?)\]\((.+?)\)/g, '<a href="$2">$1</a>');

        // Replace blockquote syntax with <blockquote>
        str = str.replace(/^>\s*(.+)/gm, "<blockquote>$1</blockquote>");

        // Ensure proper numbering of lists
        let listIndex = 0;
        str = str.replace(/^(\d+)\./gm, () => {
            listIndex++;
            return `${listIndex}.`;
        });

        // Handle bullet points (*)
        str = str.replace(/^\*\s?/gm, "<li>").replace(/<li>(.+)/g, "<li>$1</li>");

        // Wrap bullet points in <ul></ul>
        str = str.replace(/(<li>.+?<\/li>)/gs, "<ul>$1</ul>");

        // Split text into paragraphs by detecting double newlines
        const paragraphs = str.split(/\n{2,}/)
            .map(p => p.trim()) // Trim each paragraph
            .filter(p => p); // Remove empty paragraphs

        // Format paragraphs into HTML
        return paragraphs.map(p => `<p>${p.replace(/\n/g, "<br>")}</p>`).join("");
    }

    // Handle tables in the input string
    function convertTableToHTML(str) {
        const tableRegex = /\|(.+?)\|/g;
        const rows = str.split("\n").filter(line => line.startsWith("|")).map(line =>
            line.split("|").slice(1, -1).map(cell => cell.trim())
        );

        if (rows.length > 1) {
            const headers = rows.shift();
            const tableHTML = `
                <table border="1">
                    <thead>
                        <tr>${headers.map(header => `<th>${header}</th>`).join("")}</tr>
                    </thead>
                    <tbody>
                        ${rows.map(row => `<tr>${row.map(cell => `<td>${cell}</td>`).join("")}</tr>`).join("")}
                    </tbody>
                </table>`;
            // Remove table lines from the original string
            str = str.split("\n").filter(line => !line.startsWith("|")).join("\n");
            return str + tableHTML;
        }
        return str;
    }

    // Process and combine text formatting and table conversion
    inputString = convertTableToHTML(inputString);
    inputString = cleanAndFormatString(inputString);

    // Create a div and set its innerHTML
    const div = document.createElement("div");
    div.innerHTML = inputString;

    // Return the div element (Node) instead of a string
    return div;
}






function setActiveConversation(cid) {
    // Remove active class from all conversation buttons
    console.log("activating this conversation button",cid);
    const allButtons = document.querySelectorAll('#sidebar-list .convo-button');
    allButtons.forEach(button => {
        button.classList.remove('active-convo');
    });
    
    // Add active class to the button with the given cid
    const activeButton = document.querySelector(`#sidebar-list .convo-button[data-cid="${cid}"]`);
    if (activeButton) {
        activeButton.classList.add('active-convo');
        return true
    } else {
        return false
    }
}


// Trigger file input click on button click
fileButton.addEventListener('click', function () {
    fileInput.click();
});
inputFile.addEventListener('change', function() {
    const file = inputFile.files[0];
    
    if (file) {
        // Display the file name and the tick icon
        fileNameElement.textContent = file.name.length > 20 
    ? file.name.slice(0, 20) + "..." 
    : file.name;
        fileStatusContainer.style.position='absolute';
        fileStatusContainer.style.backgroundColor='white';
        fileNameElement.style.color='black';
        fileStatusContainer.style.display='block'
        fileStatusContainer.style.left='-600px'
        fileStatusContainer.style.top='4px'
        fileStatusContainer.style.padding='5px'
        fileStatusContainer.style.borderRadius='10px'
        document.getElementById(attach-bg).style.backgroundColor='black';
    } else {
        // Clear the file status if no file is selected
        fileNameElement.textContent = '';
        fileStatusContainer.style.display = 'none';
        document.getElementById(attach-bg).style.backgroundColor='white';
    }
});

document.addEventListener('DOMContentLoaded', function () {
    
    
    fetchConversations();

    async function fetchConversations() {
        const response = await fetch('/get_conversations/', {
            method: 'GET',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        });
    
        if (response.status === 403) {
            console.error('User not authenticated');
            window.location.href = '/ulogin/';
            return;
        }
    
        const data = await response.json();
        if (data && data.status === 'success') {
            const sidebarList = document.getElementById('sidebar-list');
            sidebarList.innerHTML = '';
            console.log(data);
    
            if (data.conversations.length > 0) {
                data.conversations.forEach(convo => {
                    const convoItem = document.createElement('div');
                    convoItem.classList.add('convo-item');
    
                    const button = document.createElement('button');
                    button.classList.add('convo-button');
                    button.dataset.cid = convo.cid;
                    button.textContent = convo.conversation_name;
                    button.addEventListener('click', function () {
                        fetchChats(convo.cid);
                    });
    
                    // const renameIcon = document.createElement('span');
                    // renameIcon.classList.add('rename-icon');
                    // renameIcon.innerHTML = '&#9998;'; // Pencil icon
                    // renameIcon.title = 'Rename';
                    // renameIcon.addEventListener('click', function (event) {
                    //     event.stopPropagation(); // Prevent triggering the button click
                    //     rename_convo(convo.cid);
                    // });
    
                    convoItem.appendChild(button);
                    // convoItem.appendChild(renameIcon);
                    sidebarList.appendChild(convoItem);
                });
    
                sidebarList.firstElementChild.querySelector("button").classList.add("active-convo");
            } else {
                const noConvoDiv = document.createElement('div');
                noConvoDiv.classList.add('no-conversations');
                noConvoDiv.textContent = 'No previous test scenarios generated';
                sidebarList.appendChild(noConvoDiv);
            }
        } else if (data) {
            console.error('Error fetching conversations:', data.message);
        }
    }
    
    

    const settingsIcon = document.getElementById('settings-icon');
    const configDropdown = document.getElementById('config-dropdown');
    const checkboxes = configDropdown.querySelectorAll('input[type="checkbox"]');

    settingsIcon.addEventListener('click', function () {

        configDropdown.classList.toggle('show');
    });


    const sidebarToggleBtn = document.getElementById('sidebar-toggle');
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('main-content');
    const collapsedIcon = document.querySelector('.collapsed-icon');
    const expandedIcon = document.querySelector('.expanded-icon');

    // Toggle sidebar visibility
    sidebarToggleBtn.addEventListener('click', function () {
        sidebar.classList.toggle('collapsed');
        mainContent.classList.toggle('expanded');

        if (sidebar.classList.contains('collapsed')) {
            collapsedIcon.style.display = 'none';
            expandedIcon.style.display = 'inline';
        } else {
            collapsedIcon.style.display = 'inline';
            expandedIcon.style.display = 'none';
        }
    });

    // Chat form submission and conversation handling (unchanged)
    const chatForm = document.getElementById('chat-form');
    const inputStringField = document.getElementById('input-string');
    const chatHistoryDiv = document.getElementById('chat-history');

    chatForm.addEventListener('submit', function (e) {
        e.preventDefault();
        
        const inputString = inputStringField.value;
        inputStringField.value = '';  // Clears the value of the input field
        inputStringField.focus();
        const file = inputFile.files[0];

    
        // Create FormData and append the necessary data
        const formData = new FormData();
        formData.append('input_string', inputString);
        if (file){
            formData.append('input_file', file);
            inputFile.value = '';  // Clear the file input
            fileNameElement.textContent = '';  // Clear file name display
            fileStatusContainer.style.display = 'none';  // Hide the status box
        }
    
        // Get the value of the hidden 'cid' input field and append it to FormData
        const encryptedCid = document.querySelector('[name="cid"]').value;
        formData.append('cid', encryptedCid);
    
        // Check if "Use Default" is selected
        const useDefault = document.getElementById('use_default').checked;
        formData.append('use_default', useDefault);  // Send the use_default status
    
        // If "Use Default" is not selected, append the selected configuration options
        if (!useDefault) {
            // Select the checkboxes or inputs for the configuration options
            const applicationTypes = ['application_type_web_app', 'application_type_mobile_app', 'application_type_api'];
            applicationTypes.forEach((appType) => {
                if (document.getElementById(appType) && document.getElementById(appType).checked) {
                    formData.append(appType, true);
                }
            });
    
            const testDesignTechniques = [
                'test_design_techniques_boundary_value_analysis',
                'test_design_techniques_equivalence_partitioning',
                'test_design_techniques_state_transition_testing',
                'test_design_techniques_decision_table_testing'
            ];
            testDesignTechniques.forEach((technique) => {
                if (document.getElementById(technique) && document.getElementById(technique).checked) {
                    formData.append(technique, true);
                }
            });
    
            const testCoverage = [
                'test_coverage_functional_testing',
                'test_coverage_nonfunctional_testing',
                'test_coverage_functional_testing_individual_field_testing',
                'test_coverage_nonfunctional_testing_performance_testing',
                'test_coverage_nonfunctional_testing_security_testing',
                'test_coverage_nonfunctional_testing_compatibility_testing',
                'test_coverage_nonfunctional_testing_network_based_testing',
                'test_coverage_nonfunctional_testing_interruption_testing'
            ];
            testCoverage.forEach((coverage) => {
                if (document.getElementById(coverage) && document.getElementById(coverage).checked) {
                    formData.append(coverage, true);
                }
            });
        }
        
        const newChat = document.createElement('div'); // Wrapper for a single chat message
        newChat.classList.add('chat-message'); // Add common chat message class
                
        if (inputString) {
            const userMessage = document.createElement('div');
            userMessage.classList.add('message', 'user-message'); // Add classes for user message
            userMessage.innerHTML = `
                <div class="message-content">
                    <strong>You:</strong> ${inputString}
                </div>`;
            newChat.appendChild(userMessage);
        }
        const outputMessage = document.createElement('div');
        outputMessage.classList.add('message', 'output-message');
        const message_content=document.createElement('div');
        message_content.classList.add('message-content');
        outputMessage.appendChild(message_content)
        newChat.appendChild(outputMessage);
        chatHistoryDiv.appendChild(newChat);
        showLoadingIcon();
        const instructElement = document.querySelector('.new-instruct');
                    const inputContainer = document.querySelector('.input-container');
                    const historyContainer = document.querySelector('.history-container');
                    if (instructElement) {
                        instructElement.style.display = 'none';
                    }
                
                    if (historyContainer) {
                        historyContainer.style.transition = 'top 0.5s ease-in-out'; // Smooth transition
                        historyContainer.style.position = 'relative';
                        historyContainer.style.top = '-300px'; // Place at the top
                        historyContainer.style.marginTop = '0px';
                        historyContainer.style.height = 'calc(100vh - 60px)'; // Adjust height to make space for input
                        historyContainer.style.overflowY = 'auto'; // Ensure scrolling if content overflows
                    }
                    
                    if (inputContainer) {
                        inputContainer.style.transition = 'transform 0.3s ease-in-out'; // Smooth transition
                        inputContainer.style.transform = 'translateY(35vh)'; // Initial positioning at 40% of the viewport height
                        inputContainer.style.marginBottom = '0px';
                        inputContainer.style.position = 'relative'; // Stick to the bottom
                        inputContainer.style.bottom = '0px'; // Position at the bottom of the viewport
                        inputContainer.style.width = '100%'; // Stretch to fit the width
                        inputContainer.style.zIndex = '10'; // Ensure it's above the chat container
                        
                        // Adjust the position when in fullscreen mode
                        if (window.innerHeight === screen.height) { // Check if fullscreen is active
                            inputContainer.style.transform = 'translateY(48vh)'; // 50% of the viewport height for fullscreen
                        }
                    }
        chatHistoryDiv.scrollTop = chatHistoryDiv.scrollHeight;


        // Now the formData contains all the necessary inputs, including the config options (based on "Use Default" or custom selection)
    
        fetch(`/add_chat/`, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => {
            return response.json();
        })
        .then(data => {
           
            if (data.status === 'success') {
                if (data.new_convo === 'false') {
                    
                    document.getElementById('hidden-cid').value = data.cid;
                    console.log(`New conversation created. CID updated to: ${data.cid}`);
                    const ad_cid=data.cid;
                    console.log("trying activing this conversation.................",ad_cid);
                    if(setActiveConversation(ad_cid) == false ){
                        
                        async function initializeConversations() {
                            await fetchConversations();  // Ensure fetchConversations is completed first
                        }
                        initializeConversations();  
                        }
                        

                } else {
                    console.log('Existing conversation updated.');
                }
                
                
                // Output message
                if (data.output) {
                    const lastOutputMessage = document.querySelector('.chat-message:last-child .output-message .message-content');
            
                    if (lastOutputMessage) {
                        // Remove the loading icon from the output message
                        const loadingIcon = lastOutputMessage.querySelector('.loading-icon');
                        if (loadingIcon) {
                            loadingIcon.remove();
                        }
                        const outputDiv = createFormattedDiv(data.output);
                        lastOutputMessage.innerHTML = ``;
                        lastOutputMessage.appendChild(outputDiv);
                        chatHistoryDiv.scrollTop = chatHistoryDiv.scrollHeight;
                        }
                    }
                // File link (if available)
                if (data.file_url) {
                    const fileMessage = document.createElement('div');
                    fileMessage.classList.add('message', 'file-message'); // Add a specific class for file messages
                    fileMessage.innerHTML = `
                    <div class="message-content">
                        <strong>Attached:</strong> <a href="${data.file_url}" target="_blank">${data.file_url.split('/').pop()}</a>
                    </div>`;
                    newChat.appendChild(fileMessage);
                }
                
                // Append the new chat message to the chat history
                chatHistoryDiv.appendChild(newChat);
                chatHistoryDiv.scrollTop = chatHistoryDiv.scrollHeight; 
            }
        });
        
    });
    
    function fetchChats(convoId) {
        setActiveConversation(convoId)
        inputStringField.value = '';  
        inputFile.value = '';
        fileNameElement.textContent = '';
        fileStatusContainer.style.display = 'none';
        fetch(`/get_chats/${convoId}/`)
            .then(response =>response.json())
            .then(data => {
                if (data.status === 'success') {
                    const instructElement = document.querySelector('.new-instruct');
                    const inputContainer = document.querySelector('.input-container');
                    const historyContainer = document.querySelector('.history-container');
                    // Hide the instruction element
                    if (instructElement) {
                        instructElement.style.display = 'none';
                    }
                
                    // Smoothly move the input container to the bottom
                    if (historyContainer) {
                        historyContainer.style.transition = 'top 0.5s ease-in-out'; // Smooth transition
                        historyContainer.style.position = 'relative';
                        historyContainer.style.top = '-300px'; // Place at the top
                        historyContainer.style.marginTop = '0px';
                        historyContainer.style.height = 'calc(100vh - 60px)'; // Adjust height to make space for input
                        historyContainer.style.overflowY = 'auto'; // Ensure scrolling if content overflows
                    }
                    
                    if (inputContainer) {
                        inputContainer.style.transition = 'transform 0.3s ease-in-out'; // Smooth transition
                        inputContainer.style.transform = 'translateY(35vh)'; // Initial positioning at 40% of the viewport height
                        inputContainer.style.marginBottom = '0px';
                        inputContainer.style.position = 'relative'; // Stick to the bottom
                        inputContainer.style.bottom = '0px'; // Position at the bottom of the viewport
                        inputContainer.style.width = '100%'; // Stretch to fit the width
                        inputContainer.style.zIndex = '10'; // Ensure it's above the chat container
                        
                        // Adjust the position when in fullscreen mode
                        if (window.innerHeight === screen.height) { // Check if fullscreen is active
                            inputContainer.style.transform = 'translateY(48vh)'; // 50% of the viewport height for fullscreen
                        }
                    }
                    
                    

                    document.getElementById('hidden-cid').value = data.cid;
                    console.log(data.cid)
                    chatHistoryDiv.innerHTML = ''; // Clear the chat history

                    data.chats.forEach(chat => {
                        const chatMessage = document.createElement('div'); // Wrapper for a single chat message
                        chatMessage.classList.add('chat-message'); // Add a common chat message class

                        // User input message
                        if (chat.input_string) {
                            const userMessage = document.createElement('div');
                            userMessage.classList.add('message', 'user-message'); // Add classes for user message
                            userMessage.innerHTML = `
                                <div class="message-content">
                                    <strong>You:</strong> ${chat.input_string}
                                </div>`;
                            chatMessage.appendChild(userMessage);
                        }

                        // Output message
                        if (chat.output_string) {
                            const outputMessage = document.createElement('div');
                            const outputDiv = createFormattedDiv(chat.output_string);
                            outputMessage.classList.add('message', 'output-message'); // Add classes for output message
                            outputMessage.appendChild(outputDiv);
                            chatMessage.appendChild(outputMessage);
                        }

                        // File link (if available)
                        if (chat.input_file_url) {
                            const fileMessage = document.createElement('div');
                            fileMessage.classList.add('message', 'file-message'); // Add a specific class for file messages
                            fileMessage.innerHTML = `
                            <div class="message-content">
                                <strong>Attached:</strong> <a href="${chat.input_file_url}" target="_blank">${chat.input_file_url.split('/').pop()}</a>
                            </div>`;
                            chatMessage.appendChild(fileMessage);
                        }

                        chatHistoryDiv.appendChild(chatMessage); // Append the chat message to the chat history
                        chatHistoryDiv.scrollTop = chatHistoryDiv.scrollHeight;  


                    });
                } else {
                    // Handle error fetching chats
                    console.error('Error fetching chats:', data.message);
                    const chatHistoryDiv = document.getElementById('chat-history');
                    chatHistoryDiv.innerHTML = '<p>No chats found for this conversation.</p>';
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
    }
    

    document.getElementById('use_default').addEventListener('change', function() {
        // Get all checkbox inputs inside the config dropdown
        const configCheckboxes = document.querySelectorAll('#config-dropdown input[type="checkbox"]:not(#use_default)');
    
        // If the toggle is checked (Use Default is selected)
        if (this.checked) {
            // Disable all checkboxes and make them look grayed out
            configCheckboxes.forEach(checkbox => {
                checkbox.disabled = true; // Disable the checkbox
                checkbox.parentElement.style.opacity = '0.5'; // Make them appear grayed out
            });
        } else {
            // Enable all checkboxes and remove the grayed-out effect
            configCheckboxes.forEach(checkbox => {
                checkbox.disabled = false; // Enable the checkbox
                checkbox.parentElement.style.opacity = '1'; // Remove the grayed-out effect
            });
        }
    });
    

});


document.getElementById("logout-icon").addEventListener("click", () => {
    const dropdown = document.getElementById("logout-dropdown");
    dropdown.style.display = dropdown.style.display === "block" ? "none" : "block";
});

document.getElementById("confirm-logout").addEventListener("click", () => {
    // Redirect to Django logout view
    window.location.href = "/logout/"; // Adjust URL based on your Django view
});

document.getElementById("cancel-logout").addEventListener("click", () => {
    document.getElementById("logout-dropdown").style.display = "none";
});
