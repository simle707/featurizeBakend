import asyncio
import json
import os
import time
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from api.schemas import CreateVMRequest, LoginRequest, PaddleBillingRequest, StandardResponse

router = APIRouter(prefix="/bus/api/v1")
security = HTTPBearer()

user_vms = {}
mock_users_db = {}

INTERNAL_AUTH_TOKEN = "aRuq0x72QkQsXbR2tnLXcgeJO6hvJego"

# 模拟充值记录存储
mock_transactions = [
    {
        "id": "9c497952-b76e-4a7b-a658-9476c01f43b5",
        "created": "2026-01-31T16:05:54.225073Z",
        "platform": "paddle",
        "status": "finished",
        "amount": 200.0,
        "invoice_sent": False
    },
    {
        "id": "8d508063-c87f-5b8c-b769-0587d12g54c6",
        "created": "2026-02-01T10:15:20.123456Z",
        "platform": "paddle",
        "status": "finished",
        "amount": 50.0,
        "invoice_sent": False
    }
]

# 模拟消费记录存储
mock_consumptions = [
    {
        "id": "27b45feb-9e8c-40ac-9c3d-fb8f4632b4aa",
        "user_id": "fb28259d-9f5b-4540-a7f8-8b40ba8d8c2b",
        "total_amount": 12.5,
        "coupon_amount": 0.0,
        "balance_amount": 12.5,
        "remark": "Instance rental: RTX 4090",
        "created": "2026-01-21T08:43:39.792834Z",
        "resource_id": "17435924-3d4d-418d-93eb-8590c36147b8",
        "resource_type": "BillingTracker"
    }
]

@router.post("/international/sessions", response_model=StandardResponse)
async def login_session(
    req: LoginRequest,
    auth: HTTPAuthorizationCredentials = Depends(security)
):
    # 1. 校验 IC 后端的 Token (Bearer Token)
    if auth.credentials != INTERNAL_AUTH_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid Service Token")
    
    sub = req.sub

    # 2. 模拟自动创建/获取用户
    # 实际生产中这里会查数据库，这里我们模拟生成一个
    user_id = "fb28259d-9f5b-4540-a7f8-8b40ba8d8c2b"

    # 模拟生成的 session token (格式参考你提供的示例)
    # 这里的 token 之后会被前端作为 featurize-hub-session cookie 使
    session_token = f"2|1:0|{int(time.time())}|21:featurize-hub-session|48:ZmIyODI1OW...fake_hash"

    user_info = {
        "id": user_id,
        "name": sub,
        "email": f"{sub}@gmail,com",
        "computing_center": "yaan_1",
        "short_id": "VZYK7pdi",
        "plain_api_token": "9fb1e8932f5f49f3a15f0d6a9c801a2b"
    }

    return {
        "status": 0,
        "data": {
            "token": session_token,
            "user": user_info
        },
        "message": "success"
    }

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "database.json")

def load_hosts():
    with open(DATABASE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def check_balance():
    balance = 0

def check_auth(request: Request):
    bus_token = request.headers.get("authorization"," ").split(" ")[-1]
    # print(f"token: {bus_token}",)
    # print("request: ", request.json)
    # print(bus_token!=INTERNAL_AUTH_TOKEN)
    if bus_token != INTERNAL_AUTH_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")
    

@router.get("/sessions", response_model=StandardResponse)
async def get_current_user_info(request: Request):
    check_auth(request)
    return {
        "data": {
            "id": "fb28259d-9f5b-4540-a7f8-8b40ba8d8c2b",
            "name": "Mock User",
            "category": "normal",
            "withdrawable_balance": 120
        }
    }

@router.get("/host_machine", response_model=StandardResponse)
async def get_host_machine(request: Request):
    # check_auth(request)
    hosts = load_hosts()
    return {
        "status": 0,
        "data": {
            "records": hosts,
            "pagination": {
                "page": 0,
                "total": len(hosts)
            }
        },
        "message": "success"
    }

@router.post("/virtual_machine", response_model=StandardResponse)
async def create_vm(req: CreateVMRequest, request: Request):
    check_auth(request)
    vm_id = str(uuid.uuid4())

    await asyncio.sleep(20)
    boot_time = time.time() + 20

    new_vm = {
        "id": vm_id,
        "status": "online",
        "gpu_type": "RTX 4090",
        "unit_count": req.units,
        "ssh_port": "22559",
        "featurize_password": "123123",
        "_boot_at": boot_time
    }
    user_vms[vm_id] = new_vm
    return {
        "status": 0,
        "data": new_vm,
        "message": "success"    
    }
    
@router.get("/virtual_machine", response_model=StandardResponse)
async def list_vms(request: Request):
    check_auth(request)       
    return {
        "data": {
            "records": list(user_vms.values()),
            "pagination": {
                "page": 0,
                "total": len(user_vms)
            }
        }
    }

@router.get("/virtual_machine/{vm_id}", response_model=StandardResponse)
async def get_vm_status(vm_id: str, request: Request):
    check_auth(request)

    if vm_id not in user_vms:
        raise HTTPException(status_code=404, detail="VM not found")
    
    vm = user_vms[vm_id]
    print("vm_id: ", vm_id)

    if vm["status"] == "pending":
        vm["status"] = "online"
        print(f"VM {vm_id} is now ONLINE")

    return {"data": vm}

@router.delete("/virtual_machine/{vm_id}", response_model=StandardResponse)
async def delete_vm(vm_id: str, request: Request):
    check_auth(request)
    if vm_id in user_vms:
        del user_vms[vm_id]
        return {"data": True, "message": "Instance returned successfully"}
    raise HTTPException(status_code=404, detail="Instance not found")

# 1. 充值接口
@router.post("/international/billing", response_model=StandardResponse)
async def create_billing(req: PaddleBillingRequest, request: Request):
    check_auth(request)
    print(f"Receive Paddle Payload: {req.paddle_payload}")
    return {
        "status": 0,
        "data": {"message": "Billing processed successfully"},
        "message": "success"
    }

# 2. 充值查询接口
@router.get("/transactions", response_model=StandardResponse)
async def get_transactions(request: Request, page: int=0):
    check_auth(request)
    return {
        "status": 0,
        "data": {
            "records": mock_transactions,
            "pagination": {
                "page": page,
                "total": len(mock_transactions)
            }
        },
        "message": "success"
    }

# 3. 消费查询接口
@router.get("/consumptions", response_model=StandardResponse)
async def get_consumptions(request: Request, page: int=0):
    check_auth(request)
    return {
        "status": 0,
        "data": {
            "records": mock_consumptions,
            "pagination": {
                "page": page,
                "total": len(mock_consumptions)
            }
        },
        "message": "success"
    }