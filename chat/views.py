from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.http import HttpResponseBadRequest
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .models import User, Conversation, Chat
from cryptography.fernet import Fernet
import random
from django.core.exceptions import ObjectDoesNotExist

def landing_page(request):
    return render(request, 'landing_page.html')

def get_started(request):
    uid = request.session.get('uid')
    if(uid):
        return redirect('home')  
    else:
        return render(request, 'logreg.html',{'pg':'login'})

def logout_view(request):
    if request.session.get('uid'):
        request.session.flush()
    return redirect('login')

def load_key():
    with open("secret.key", "rb") as key_file:
        key = key_file.read()
    return key

def encrypt_string(plain_text):
    key = load_key()  # Ensure the key is generated and saved beforehand
    fernet = Fernet(key)
    encrypted = fernet.encrypt(plain_text.encode())
    return encrypted.decode()

def decrypt_string(encrypted_text):
    key = load_key()  # Ensure the key is the same used for encryption
    fernet = Fernet(key)
    decrypted = fernet.decrypt(encrypted_text.encode())
    return decrypted.decode()

def generate_otp():
    return str(random.randint(100000, 999999))

def send_email(to_email_id, subject, message):
    try:
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER, 
            [to_email_id], 
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def otp_verify(request):
    if request.method == 'POST':
        try:
            # Extract data from POST request
            encrypted_email = request.POST.get('em')
            encrypted_name = request.POST.get('nm')
            encrypted_password = request.POST.get('ps')
            encrypted_otp = request.POST.get('o')
            input_otp = request.POST.get('otp')  # This might be a number

            # Convert input_otp to a string to ensure consistent comparison
            input_otp = str(input_otp)

            # Decrypt the hidden fields
            email = decrypt_string(encrypted_email)
            name = decrypt_string(encrypted_name)
            password = decrypt_string(encrypted_password)
            stored_otp = decrypt_string(encrypted_otp)

            # Validate decrypted data
            if not all([email, name, password, stored_otp]):
                return HttpResponseBadRequest("Decryption failed or invalid data.")

            # Verify the OTP
            if input_otp == stored_otp:
                # OTP matches, proceed to success page or further logic
                User.objects.create(name=name, email=email, password=password)
                return render(request, 'logreg.html', {'pg': 'login','pg_alert':'', 'pg_alert_green': 'Successfully Registered, Please login to continue'})
            else:
                # OTP mismatch
                return render(request, 'logreg.html', {'pg': 'otp_verify','pg_alert_green':'', 'pg_alert': 'Invalid OTP.','em':encrypted_email,'nm':encrypted_name,'ps':encrypted_password,'o':encrypted_otp})
        except Exception as e:
            # Handle unexpected errors
            return HttpResponseBadRequest("An error occurred: " + str(e))
    else:
        return render(request,'logreg.html',{'pg':'login'})

# Registration view
def register(request):
    if request.method == 'POST':
        name = request.POST['nm_reg']
        email = request.POST['em_reg']
        password = request.POST['pw_reg']

        # Check if the email is already in use
        if User.objects.filter(email=email).exists():
            return render(request,'logreg.html',{'reg_alert':'Entered Email is already registered','pg':'reg'})
        else:
            email_encrypted=encrypt_string(email)
            name_encrypted=encrypt_string(name)
            password_encrypted=encrypt_string(password)
            otp=generate_otp()
            otp_encrypted=encrypt_string(otp)
            subject = "Email Verification for QST Test Scenarios Generator"
            message = f"Your OTP for email verification is: {otp}"
            if send_email(email, subject, message):
                print("Email sent successfully!",subject,message)
                return render(request,'logreg.html',{'pg':'otp_verify','em':email_encrypted,'nm':name_encrypted,'ps':password_encrypted,'o':otp_encrypted})
            else:
                return render(request, 'logreg.html',{'pg':'reg','reg_alert':'error sending OTP to this email, please Retry!'})
    return render(request, 'logreg.html',{'pg':'reg'})


# Login view
def ulogin(request):
    if request.method == 'POST':
        email = request.POST['em_log']
        password = request.POST['pw_log']
        print(email)
        # Check if the user exists
        user = User.objects.filter(email=email).first()
        print(user)
        if user:
            if user.password == password:
                print("db password, ",user.password,"input pass",password,"inside this if!")
                request.session['uid'] = user.uid
                return redirect('home')  
            else:
                return render(request, 'logreg.html',{'pg':'login','pwalert':'Incorrect Password'})
        else:
            return render(request, 'logreg.html',{'pg':'login','alert':'Please Register your Email ID'})

    return render(request, 'logreg.html',{'pg':'login'})

def pass_reset_otp(request):
    if request.method == 'POST':
        try:
            # Extract data from POST request
            encrypted_email = request.POST.get('em')
            encrypted_otp = request.POST.get('o')
            input_otp = request.POST.get('otp') 

            input_otp = str(input_otp)

            email = decrypt_string(encrypted_email)
            stored_otp = decrypt_string(encrypted_otp)

            if not all([email, stored_otp]):
                return HttpResponseBadRequest("Decryption failed or invalid data.")

            if input_otp == stored_otp:
                return render(request, 'forgot_pass.html', {'pg': 'reg','pg_alert_green':'', 'pg_alert': '','em':encrypted_email})
        except Exception as e:
            # Handle unexpected errors
            return HttpResponseBadRequest("An error occurred: " + str(e))
    return render(request,'forgot_pass.html',{'pg':'login'})

def pass_reset(request):
    if request.method == 'POST':
        encrypted_email = request.POST.get('em')
        email=decrypt_string(encrypted_email)
        pass1 = request.POST.get('pass1')
        pass2 = request.POST.get('pass2')
        if(pass1==pass2):
            User.objects.filter(email=email).update(password=pass1)
            return render(request,'logreg.html',{'pg':'login','pg_alert':'','pg_alert_green':'Password Reset was Successful!'})
            
        else:
            return render(request,'forgot_pass.html',{'pg':'reg','pg_alert_green':'','pg_alert':'Passwords didnt match!','em':encrypted_email})


    else:   
        return render(request,'forgot_pass.html',{'pg':'login'})

def pass_reset_req(request):
    if request.method == 'POST':
        email = request.POST['em']
        if User.objects.filter(email=email).exists():
            email_encrypted=encrypt_string(email)
            otp=generate_otp()
            otp_encrypted=encrypt_string(otp)
            subject = "Password Reset Request for QST Test Scenarios Generator"
            message = f"Your OTP for password reset is: {otp}"
            if send_email(email, subject, message):
                print("Email sent successfully!",subject,message)
                return render(request,'forgot_pass.html',{'pg':'otp_verify','em':email_encrypted,'o':otp_encrypted})
            else:
                return render(request,'forgot_pass.html',{'pg':'login','pg_alert_green':'','pg_alert':'Error Sending email, please try again!'})
        else:
            return render(request,'forgot_pass.html',{'pg':'login','alert':'Entered Email is not registered!'})
           
    else:    
        return render(request,'forgot_pass.html',{'pg':'login'})
    
def home(request):
    # Safely check if 'uid' exists in session
    uid = request.session.get('uid')
    print(uid)
    if uid:
        conversations = Conversation.objects.filter(uid=uid).order_by('-datetime')
        encrypted_cid = encrypt_string('-0')
        return render(request, 'app_page.html', {
            'is_new': 'true',
            'encrypted_cid': encrypted_cid
        })
    else:
        # Redirect to login if 'uid' is missing
        return redirect('login')
    
def get_conversations(request):
    """Return the list of conversations as JSON."""
    if 'uid' not in request.session:
        return JsonResponse({"status": "error", "message": "User not authenticated"}, status=403)

    user_uid = request.session['uid']  # Get the UID from the session
    conversations = Conversation.objects.filter(uid=user_uid).order_by('-datetime')  # Order by most recent

    data = [
        {"cid": encrypt_string(str(convo.cid)),'conversation_name':convo.conversation_name, "datetime": convo.datetime.strftime("%Y-%m-%d %H:%M:%S")}
        for convo in conversations
    ]

    return JsonResponse({"status": "success", "conversations": data,'recent':conversations[0].cid})

def get_chat_history(cid):
    """
    Retrieves and formats the chat history for a specific conversation ID.

    Args:
        cid (int): The conversation ID for which to retrieve the chat history.

    Returns:
        str: A formatted string containing the chat history sorted by timestamp.
    """
    try:
        # Query the Chat model for the specified conversation ID, sorted by timestamp
        cid = int(cid)
        print("inside try of get_chat_ history1 id,",cid)
        chat_history = Chat.objects.filter(cid=cid).order_by('timestamp')
        print("inside try of get_chat_history:")
        # Format the output as "user: input_string, response: output_string"
        formatted_history = []
        for chat in chat_history:
            formatted_history.append(f"user: {chat.input_string}, response: {chat.output_string}")
        print("".join(formatted_history))
        # Join all entries into a single string separated by newline
        return "\n".join(formatted_history)
    except Chat.DoesNotExist:
        return False

def add_chat(request):
    if 'uid' not in request.session:
        return JsonResponse({'status': 'error', 'message': 'User not authenticated'}, status=403)

    print("inside add_chat")
    try:
        # Default Configuration
        default_config = {
            'application_type': {
                'description': 'Type of application',
                'options': {
                    'web app': False,
                    'mobile app': True,
                    'api': False,
                }
            },
            'test_design_techniques': {
                'description': 'Test Design Techniques',
                'test_methodologies': {
                    'boundary_value_analysis': True,
                    'equivalence_partitioning': True,
                    'state_transition_testing': True,
                    'decision_table_testing': True,
                }
            },
            'testing_coverage': {
                'description': 'Required testing coverage',
                'test_coverage_needed': {
                    'functional_testing': True,
                    'nonfunctional_testing': True,
                },
                'test_coverage_options': {
                    'functional_testing': {
                        'description': 'Functional testing coverage options',
                        'individual_field_testing': True,
                    },
                    'nonfunctional_testing': {
                        'description': 'Non-functional testing coverage options',
                        'performance_testing': True,
                        'security_testing': False,
                        'compatibility_testing': True,
                        'network_based_testing': True,
                        'interruption_testing': True,
                    }
                }
            }
        }

        # Check if "Use Default" is selected
        use_default = request.POST.get('use_default', 'false') == 'true'

        # If "Use Default" is selected, apply the default configuration
        if use_default:
            config_data = default_config.copy()
        else:
            # Otherwise, start with the default config and update based on user input
            config_data = default_config.copy()

            # Check and update application_type options based on user input
            config_data['application_type']['options']['web app'] = 'application_type_web_app' in request.POST
            config_data['application_type']['options']['mobile app'] = 'application_type_mobile_app' in request.POST
            config_data['application_type']['options']['api'] = 'application_type_api' in request.POST

            # Check and update test_design_techniques options based on user input
            config_data['test_design_techniques']['test_methodologies']['boundary_value_analysis'] = 'test_design_techniques_boundary_value_analysis' in request.POST
            config_data['test_design_techniques']['test_methodologies']['equivalence_partitioning'] = 'test_design_techniques_equivalence_partitioning' in request.POST
            config_data['test_design_techniques']['test_methodologies']['state_transition_testing'] = 'test_design_techniques_state_transition_testing' in request.POST
            config_data['test_design_techniques']['test_methodologies']['decision_table_testing'] = 'test_design_techniques_decision_table_testing' in request.POST

            # Check and update testing_coverage_needed based on user input
            config_data['testing_coverage']['test_coverage_needed']['functional_testing'] = 'test_coverage_functional_testing' in request.POST
            config_data['testing_coverage']['test_coverage_needed']['nonfunctional_testing'] = 'test_coverage_nonfunctional_testing' in request.POST

            # Check and update functional testing options based on user input
            config_data['testing_coverage']['test_coverage_options']['functional_testing']['individual_field_testing'] = 'test_coverage_functional_testing_individual_field_testing' in request.POST

            # Check and update non-functional testing options based on user input
            config_data['testing_coverage']['test_coverage_options']['nonfunctional_testing']['performance_testing'] = 'test_coverage_nonfunctional_testing_performance_testing' in request.POST
            config_data['testing_coverage']['test_coverage_options']['nonfunctional_testing']['security_testing'] = 'test_coverage_nonfunctional_testing_security_testing' in request.POST
            config_data['testing_coverage']['test_coverage_options']['nonfunctional_testing']['compatibility_testing'] = 'test_coverage_nonfunctional_testing_compatibility_testing' in request.POST
            config_data['testing_coverage']['test_coverage_options']['nonfunctional_testing']['network_based_testing'] = 'test_coverage_nonfunctional_testing_network_based_testing' in request.POST
            config_data['testing_coverage']['test_coverage_options']['nonfunctional_testing']['interruption_testing'] = 'test_coverage_nonfunctional_testing_interruption_testing' in request.POST

        input_string = request.POST.get('input_string')
        encrypted_cid = request.POST.get('cid')
        input_file = request.FILES.get('input_file')
        print("input_string, enc_cid", input_string, encrypted_cid)

        # Decrypt the conversation ID (checking if encrypted_cid is valid)
        dec_cid = decrypt_string(str(encrypted_cid))
        print("input_string, dec_cid", input_string, dec_cid)


        print(input_string)
        # Check if the 'uid' exists in the session and fetch the corresponding User object
        try:
            user = User.objects.get(uid=request.session['uid'])
        except ObjectDoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User not found'}, status=404)

        if dec_cid != '-0':
            print('IT SHOULD BE HERE', dec_cid)
            print('this ! -0 condition cid', dec_cid)
            # Fetch the existing conversation
            conversation = Conversation.objects.get(cid=int(dec_cid))
            print("!=-0 conversation", conversation.cid)
            try:
                conv_id = Conversation.objects.get(cid=conversation.cid)
            except ObjectDoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'User not found'}, status=404)
            history=get_chat_history(dec_cid)
            chat = Chat(cid=conv_id, input_string=input_string)
            if history:
                print("inside history block checking error")
                input_string = f"{history}\nthe above is history of the current chat, now give response to: {input_string}"
                print("\n\n\n",input_string,"\n\n")
        else:
            # Create a new conversation if `dec_cid == '-0'`
            print('this -0 condition cid 1', dec_cid)
            conversation_name=generate_conversation_name(input_string)
            conversation = Conversation(uid=user,conversation_name=conversation_name)
            print("really new conversation created!")
            conversation.save()
            try:
                conv_id = Conversation.objects.get(cid=conversation.cid)
            except ObjectDoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'User not found'}, status=404)
            if conversation.cid:
                print('this -0 condition cid 2, and conversation obj', dec_cid, conversation.cid)
                chat = Chat(cid=conv_id, input_string=input_string)
                print('this -0 condition cid 3', dec_cid)

        
        if input_file:
            chat.input_file = input_file  # Save the uploaded file
        chat.save()

        # Generate output (mock method for output generation)
        output_string = generate_output(input_string, input_file, config_data)
        chat.output_string = output_string
        chat.config = config_data
        chat.save()
        print("current conversation cid", conversation.cid)
        new_cid = encrypt_string(str(conversation.cid))
        print("new cid, this is what frontend says keep updated", encrypted_cid)
        if dec_cid!='-0':
            return JsonResponse({
                'status': 'success',
                'new_convo': 'false',
                'cid': encrypted_cid,
                'output': output_string,
                'file_url':chat.get_input_file_url(),
            })
        elif(dec_cid=='-0'):
            return JsonResponse({
                'status': 'success',
                'new_convo': 'false',
                'cid': new_cid,
                'output': output_string,
                'file_url':chat.get_input_file_url(),
            })

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)





def get_chats(request, convo_id):
    # Check if the user is authenticated (if uid is set in the session)
    if 'uid' not in request.session:
        return redirect('ulogin')  # Redirect to login if not authenticated
    dec_id=decrypt_string(convo_id)
    # Check if the conversation exists for the logged-in user
    conversation = Conversation.objects.filter(cid=int(dec_id), uid=request.session['uid']).first()

    if not conversation:
        return JsonResponse({'status': 'error', 'message': 'Conversation not found or you do not have access.'})

    # Fetch all chats related to the conversation
    chats = Chat.objects.filter(cid=int(dec_id)).order_by('timestamp')
    
    chat_data = []
    for chat in chats:
        chat_info = {
            'input_string': chat.input_string,
            'output_string': chat.output_string,
            'input_file_url': chat.get_input_file_url(),
        }
        chat_data.append(chat_info)
    print(chat_data)
    return JsonResponse({'status': 'success', 'chats': chat_data,'cid':convo_id})

def new_convo(request):
    encrypted_cid = encrypt_string('-0')
    response_data = {
        'encrypted_string': encrypted_cid,
        'new_convo': 'true', 
    }
    return JsonResponse(response_data)



import os
import json
from PyPDF2 import PdfReader
from pdf2image import convert_from_path
from pytesseract import image_to_string
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from langchain_community.llms import Ollama
from langchain.docstore.document import Document
from tempfile import NamedTemporaryFile

llm = Ollama(model="llama3.2:latest")

# Function to extract text from a PDF file
def get_pdf_text(pdf_file):
    text = ""
    try:
        with NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            temp_pdf.write(pdf_file.read())
            temp_pdf_path = temp_pdf.name
            pdf_reader = PdfReader(temp_pdf_path)
            for page in pdf_reader.pages:
                extracted_text = page.extract_text()
                if extracted_text.strip():
                    text += extracted_text
                else:
                    text += extract_text_with_ocr(temp_pdf_path)
            os.remove(temp_pdf_path)  # Clean up the temporary file
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return text

# Function to perform OCR on a PDF file
def extract_text_with_ocr(pdf_path):
    try:
        images = convert_from_path(pdf_path)
        text = ""
        for image in images:
            text += image_to_string(image)
        return text
    except Exception as e:
        print(f"Error with OCR: {e}")
        return ""

# Function to parse a JSON configuration string
def parse_json_config(json_string):
    try:
        config = json.loads(json_string)
        return config
    except Exception as e:
        print(f"Error parsing JSON: {e}")
        return {}

# Function to set up the conversational chain
def get_conversational_chain():
    prompt_template = """
    Generate as much as test cases with maximum Test coverage by Including Product Coverage, Requirement Coverage, Risk Coverage, Boundary Value Coverage based on the provided Product Requirement Document (PRD).

IMPORTANT NOTE : "I need you to generate full test coverage, not even neglecting a single workflow or functionality. Cover all the aspects widely. Don't worry about the token used."

Decompose the task into sequential sub-tasks, each building upon the previous, to ensure thorough and systematic test case generation.

Steps:

1. Analyze Requirements: [ only for your understanding ] 
   - Review the PRD to identify and generate test cases in:
     - Input Variations: Valid and invalid inputs for flows with test data.
     - User Acceptance
     - Functional Test Cases: Evaluate individual fields, workflows, and state transitions as specified in the PRD. Apply testing techniques like decision tables and equivalence partitioning where applicable.
     - Boundary Conditions: Limits such as extremely long usernames or passwords.
     - Positive Scenarios: Ensure successful operations.
     - Edge Cases: Scenarios like empty inputs and prefilled fields.
     - Negative Scenarios: Cases like SQL injection attempts.
     - Positive Scenarios: Successful operations, e.g., user registration.
     - Input Variations: Include both valid and invalid inputs with appropriate test data.
     - Test Category: Specify as Functional or Non-Functional (e.g., Non-Functional: Performance).
     - Non-Functional Testing: Performance, security, compatibility, usability.
     - User Behavior and Data Integrity testing.
     - Compatibility: Test across different devices, browsers, and operating systems.
     - Test Data : Include example test data if necessary


---
Example Output:

| Test Case ID | Test Case Summary                         | Description                                                                                   | Test Category               | Priority |
|--------------|-------------------------------------------|-----------------------------------------------------------------------------------------------|-----------------------------|----------|
| TC001        | Validate Username with Valid Data         | As a customer, verify that the username field accepts valid inputs without errors. Test Data: 'ValidUser123'. | Functional: Data Validation | High     |
| TC002        | Validate Username with Invalid Characters | As a customer, ensure that the username field rejects inputs with invalid characters. Test Data: '!nv@l!dUs3r#'. | Functional: Data Validation | Medium   |
| TC003        | Test System Response to SQL Injection     | As a customer, confirm that the system is protected against SQL injection attempts in inputs. Test Data: "'; DROP TABLE users;--". | Non-Functional: Security    | Critical |
| TC004        | Assess Performance Under Load             | As a customer, evaluate system performance when multiple users register simultaneously. Test Data: N/A. | Non-Functional: Performance | High     |
| TC005        | Check Compatibility on Multiple Browsers  | As a customer, verify that the registration page functions correctly across different browsers. Test Data: N/A. | Non-Functional: Compatibility | Medium   |
---
    ...
    Here is my product requirement document data: {context}
    {question}
    generate test scenarios accordingly
    """
    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"]
    )
    return load_qa_chain(llm=llm, chain_type="stuff", prompt=prompt)

# Function to generate test scenarios using the chain
def generate_test_scenarios(prd_text, config):
    context = prd_text
    #question = f"Using the following configuration: {config}, generate test scenarios."
    question=''
    document = Document(page_content=context, metadata={"source": "PRD data"})
    chain = get_conversational_chain()
    response = chain({"input_documents": [document], "question": question}, return_only_outputs=True)
    return response.get('output_text', "No response generated.")

# Function to save the output to a file
def save_output(output, file_name="test_scenarios.txt"):
    try:
        with open(file_name, "w") as file:
            file.write(output)
        print(f"Test scenarios saved to {file_name}")
    except Exception as e:
        print(f"Error saving output: {e}")

def generate_output(input_string, input_file, config_data):
    # Use the input_string if provided
    if input_string.strip():
        prd_text = input_string
    elif input_file:  # Fall back to extracting text from the file
        try:
            prd_text = get_pdf_text(input_file)
            prd_text+=input_string
        except Exception as e:
            return f"Error extracting text from the file: {e}"
    else:
        return "No valid PRD input provided (neither string nor file)."

    # Ensure the PRD text is not empty
    if not prd_text.strip():
        return "No text extracted from the input source."

    # Parse the JSON configuration
    config = config_data
   

    # Generate test scenarios using the chain
    response = generate_test_scenarios(prd_text, config)
    return response

def generate_conversation_name(prompt_string):
    try:
        # Send the prompt directly to the LLM
        st='Generate a title best suit the following can be a summary, concise title but it shouldnt have more that 3 words! no matter what the input is it may be simple hello (title should be greeings rlt) or a complex theory or maths or scienc or computer or coding whatever the input is just generate a title about the following input within 3 words, dont exceed more than that'
        response = llm(st+prompt_string)
        return response
    except Exception as e:
        return f"Error generating response: {e}"