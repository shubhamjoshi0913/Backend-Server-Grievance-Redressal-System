from dataclasses import Field
from http.client import responses
from logging import raiseExceptions

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pyexpat.errors import messages

from firebase_config import db  # Firebase config
from typing import Optional
import hashlib
from mailAPi import send_email
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins. Change this to specific origins for production.
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Hash password using SHA-256 (for basic security)
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# User model for signup
class StudentSignupUser(BaseModel):
    name: str
    email: str
    roll_no:str
    gender:str
    course:str
    contact_number:str
    password: str
    batch:str
    user_type:str

class FacultySignupUser(BaseModel):
    name: str
    email: str
    gender:str
    password: str
    user_type:str
    designation:str
    department:str
    contact_number:str



# User model for login
class LoginUser(BaseModel):
    email: str
    password: str
    userType:str


class GrievanceModel(BaseModel):
    title:str
    description:str
    name:str
    user_ref:str
    type:str
    date:str

class approveUser(BaseModel):
    user_id:str
    user_type:str
    approved:bool

class replyModel(BaseModel):
    reply:str
    date:str
    ack_number:str

class OTPUser(BaseModel):
    content:str
    email:str
    subject:str

class EmailUpdateRequest(BaseModel):
    oldEmail: str
    newEmail: str

class PasswordRequest(BaseModel):
    password: str  


class PasswordUserRequest(BaseModel):
    password: str
    user_id:str
    user_type:str


class UpdateProfileRequest(BaseModel):
    user_id: str
    name: str
    email: str
    contact_number: str
    user_type: str


@app.put("/api/update-profile")
async def update_profile(request: UpdateProfileRequest):
    user_id = request.user_id
    user_type = request.user_type  # Use `user_type` to identify the collection

    try:
        # Fetch the user document from the corresponding collection
        user_doc_ref = db.collection(user_type).document(user_id)
        user_doc = user_doc_ref.get()

        if not user_doc.exists:
            raise HTTPException(status_code=404, detail="User not found")

        # Update user information in Firestore
        user_doc_ref.update(
            {
                "name": request.name,
                "email": request.email,
                "contact_number": request.contact_number,
            }
        )
        return {"message": "Profile updated successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update profile: {str(e)}")

@app.post("/api/change-user-password/")
async def change_password(request: PasswordUserRequest):
    # Reference the specific document in Firestore
    password=request.password
    user_id=request.user_id
    user_type=request.user_type
    doc_ref = db.collection(user_type).document(user_id)
    
    # Fetch the document data
    user_data = doc_ref.get()
    if not user_data.exists:
        return {"error": "Admin document not found"}  # Handle case where document does not exist
    
    # Convert document data to a dictionary
    user_dict = user_data.to_dict()
    
    # Update the password field
    user_dict["password"] = password
    
    # Save the updated data back to Firestore
    doc_ref.set(user_dict)
    
    return {"message": "Password has been changed successfully"}


@app.post("/api/change-password/")
async def change_password(request: PasswordRequest):
    # Reference the specific document in Firestore
    password=request.password
    doc_ref = db.collection('admin').document('YMOdhYQVS6q79oCUZNEE')
    
    # Fetch the document data
    user_data = doc_ref.get()
    if not user_data.exists:
        return {"error": "Admin document not found"}  # Handle case where document does not exist
    
    # Convert document data to a dictionary
    user_dict = user_data.to_dict()
    
    # Update the password field
    user_dict["password"] = password
    
    # Save the updated data back to Firestore
    doc_ref.set(user_dict)
    
    return {"message": "Password has been changed successfully"}

    
@app.post("/api/change-email/")
async def change_email(request: EmailUpdateRequest):
    old_email = request.oldEmail
    new_email = request.newEmail
    print(request)
    # Reference the specific document in Firestore
    doc_ref = db.collection('admin').document('YMOdhYQVS6q79oCUZNEE')
    
    # Fetch the document data
    user_data = doc_ref.get()
    if not user_data.exists:
        return {"error": "Admin document not found"}  # Handle case where document does not exist
    
    # Convert document data to a dictionary
    user_dict = user_data.to_dict()
    
    # Update the email field
    user_dict["email"] = new_email
    print(user_dict)
    # Save the updated data back to Firestore
    doc_ref.set(user_dict)
    
    return {"message": "Email has been updated successfully"}
    
    


@app.post("/api/v1/user/otp/")
async def send_otp(user:OTPUser):
    print(user)
    try:
        html_content = user.content
        to_email = user.email
        subject = user.subject
        response=send_email(to_email, subject, html_content)
        return response
    except Exception as e:
        print(f"error:{str(e)}")
        raise HTTPException(status_code=500, detail=str(e))




@app.post("/api/v1/student/signup/")
async def signup_user(user: StudentSignupUser):
    try:
        print(user)
        # Check if the user already exists
        user_type=user.user_type
        users_ref = db.collection(user_type)
        existing_user = users_ref.where("email", "==", user.email).get()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already exists")


        # Create a document with auto-generated ID
        doc_ref = db.collection(user_type).document()
        user_dict = user.dict()
        # Hash the password before storing
        user_dict["password"] = hash_password(user_dict["password"])
        user_dict["approved"]=False
        doc_ref.set(user_dict)
        return {"message": "User signed up successfully", "user": user_dict}
    except Exception as e:
        print(f"error:{str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/faculty/signup/")
async def signup_user(user: FacultySignupUser):
    try:
        # Check if the user already exists
        print(user)
        user_type=user.user_type
        users_ref = db.collection(user_type)
        existing_user = users_ref.where("email", "==", user.email).get()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already exists")
        # Create a document with auto-generated ID
        doc_ref = db.collection(user_type).document()
        user_dict = user.dict()
        # Hash the password before storing
        user_dict["password"] = hash_password(user_dict["password"])
        user_dict["approved"]=False
        doc_ref.set(user_dict)
        return {"message": "User signed up successfully", "user": user_dict}
    except Exception as e:
        print(f"error:{str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/user/login/")
async def login_user(user: LoginUser):
    try:
        user_type = user.userType
        # Use 'where' with keyword arguments to remove the warning
        users_ref = db.collection(user_type)
        user_query = users_ref.where(field_path="email", op_string="==", value=user.email).get()
        # Validate user existence
        if not user_query:
            raise HTTPException(status_code=404, detail="User not found")
        # Get the user document and extract the UID
        user_doc = user_query[0]
        user_data = user_doc.to_dict()
        user_uid = {"user_id":user_doc.id}
        user_data.update(user_uid)
        print(f"User Data: {user_data}")
        # Verify the password
        if hash_password(user.password) != user_data.get("password"):
            raise HTTPException(status_code=400, detail="Invalid password")
        if not user_data["approved"]:
            raise HTTPException(status_code=400, detail="User not approved")
        return {
            "message": "Login successful",
            "user_data": user_data
        }
    except Exception as e:
        print(f"error:{str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/admin/get_grievance/")
async def get_grievance():
    try:
        doc_ref=db.collection("Grievance")
        docs=doc_ref.stream()
        all_data=[]
        for doc in docs:
            doc_data=doc.to_dict()
            doc_data["ack_number"]=doc.id
            all_data.append(doc_data)
        return {"data":all_data}
    except Exception as e:
        raise  HTTPException(status_code=500,detail=str(e))



@app.post("/api/v1/user/add_grievance/")
async def add_grievance(grievance:GrievanceModel):
    try:
        doc_ref=db.collection("Grievance").document()
        grievance_dict=grievance.dict()
        grievance_dict["user_ref"]=grievance.user_ref
        doc_id = doc_ref.id
        grievance_dict["ack_number"]=doc_id
        grievance_dict["responded"]=False
        doc_ref.set(grievance_dict)
        return {"message": "Grievance added successfully","grievance": grievance_dict}
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))

@app.put("/api/v1/admin/approve_user/")
async def approve_user(user:approveUser):
    try:
        print(user)
        doc_ref = db.collection(user.user_type).document(user.user_id)
        user_dict = user.dict()
        user_dict["approved"]=user.approved
        doc_ref.update(user_dict)
        return {"message": "User updated successfully", "user": user_dict}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/api/v1/user/get_grievances/{user_id}")
async def my_grievances(user_id:str):
    try:
        doc_ref=db.collection("Grievance").where("user_ref","==",user_id)
        docs=doc_ref.stream()
        all_data=[]
        for doc in docs:
            doc_data=doc.to_dict()
            print(doc_data)
            all_data.append(doc_data)
        print(all_data)
        return{"message":"Grievance","data":all_data}
    except Exception as e:
        raise  HTTPException(status_code=500,detail=str(e))

@app.post("/api/v1/admin/reply_grievance/")
async def reply_grievance(reply:replyModel):
    try:
        ack_number=reply.ack_number
        doc_ref=db.collection("Grievance").document(ack_number)
        reply_dict=reply.dict()
        reply_dict["responded"]=True
        doc_ref.update(reply_dict)
        print(reply_dict)
        return {"message": "Replied to grievance successfully","ack_number":ack_number ,"reply": reply_dict}
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))


def get_approved_data(user_type:str):
    doc_ref = db.collection(user_type)
    docs = doc_ref.stream()
    data = []
    for doc in docs:
        doc_data = doc.to_dict()
        doc_data["user_id"] = doc.id
        if doc_data["approved"]:
            data.append(doc_data)
    return data

def get_not_approved_data(user_type:str):
    doc_ref = db.collection(user_type)
    docs = doc_ref.stream()
    data = []
    for doc in docs:
        doc_data = doc.to_dict()
        doc_data["user_id"] = doc.id
        if not doc_data["approved"]:
            data.append(doc_data)
    return data


@app.get("/api/v1/get_approved_users")
async def get_approved_users():
    try:
        data=[]
        student_data=get_approved_data("student")
        teacher_data = get_approved_data("teacher")
        staff_data = get_approved_data("staff")
        data.append(student_data)
        data.append(teacher_data)
        data.append(staff_data)
        return data
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))

@app.get("/api/v1/admin/get_pending_approval_users")
async def get_not_approved_users():
    try:
        data=[]
        student_data=get_not_approved_data("student")
        teacher_data = get_not_approved_data("teacher")
        staff_data = get_not_approved_data("staff")
        data.append(student_data)
        data.append(teacher_data)
        data.append(staff_data)
        return data
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))
