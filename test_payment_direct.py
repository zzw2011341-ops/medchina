"""
测试支付功能 - 直接调用函数
"""
import sys
sys.path.insert(0, '/workspace/projects')

from langchain.tools import ToolRuntime

# 创建一个假的runtime
class FakeRuntime:
    def __init__(self):
        self.context = {}

runtime = FakeRuntime()

# 导入工具模块
from src.tools.payment_tool import create_payment, process_payment, get_payment_status

# 测试创建支付订单
print("=" * 50)
print("测试1: 创建支付订单")
print("=" * 50)
result = create_payment._run(
    user_id=1,
    order_type="test",
    order_id=None,
    amount=100.0,
    currency="USD",
    payment_method="visa",
    remark="测试支付订单",
    runtime=runtime
)
print(result)
print()

# 提取支付订单ID
payment_id = None
if "支付订单ID:" in result:
    try:
        payment_id_str = result.split("支付订单ID: ")[1].split("\n")[0]
        payment_id = int(payment_id_str)
    except (ValueError, IndexError):
        pass

if payment_id:
    print("=" * 50)
    print("测试2: 查询支付状态")
    print("=" * 50)
    result = get_payment_status._run(payment_id=payment_id, runtime=runtime)
    print(result)
    print()
    
    print("=" * 50)
    print("测试3: 完成支付")
    print("=" * 50)
    result = process_payment._run(payment_id=payment_id, runtime=runtime)
    print(result)
    print()
    
    print("=" * 50)
    print("测试4: 再次查询支付状态")
    print("=" * 50)
    result = get_payment_status._run(payment_id=payment_id, runtime=runtime)
    print(result)
    print()
else:
    print("无法获取支付订单ID，跳过后续测试")
