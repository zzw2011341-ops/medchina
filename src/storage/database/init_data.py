"""
数据库初始化脚本 - 插入示例数据
"""
from sqlalchemy.orm import Session
from storage.database.shared.model import (
    User, Hospital, Doctor, Disease, TouristAttraction,
    DoctorDisease, UserStatus
)
from storage.database.db import get_session

def init_sample_data():
    """初始化示例数据"""
    db = get_session()
    
    try:
        # 创建示例医院
        hospitals = [
            Hospital(
                name="北京协和医院",
                name_en="Peking Union Medical College Hospital",
                city="北京",
                province="北京",
                address="北京市东城区东单帅府园1号",
                level="三级甲等",
                description="北京协和医院是集医疗、教学、科研于一体的大型三级甲等综合医院，是国家卫生健康委指定的全国疑难重症诊治指导中心。",
                specialties=["综合内科", "综合外科", "神经内科", "心血管外科", "肿瘤内科"],
                logo_url="",
                image_urls=["", ""],
                contact_phone="010-69156699",
                website="http://www.pumch.cn",
                is_featured=True
            ),
            Hospital(
                name="上海瑞金医院",
                name_en="Shanghai Ruijin Hospital",
                city="上海",
                province="上海",
                address="上海市黄浦区瑞金二路197号",
                level="三级甲等",
                description="上海瑞金医院是一所大型三级甲等综合性教学医院，拥有百年历史，是国内一流的医疗机构。",
                specialties=["内分泌科", "血液科", "消化内科", "心胸外科", "神经外科"],
                logo_url="",
                image_urls=["", ""],
                contact_phone="021-64370045",
                website="http://www.rjh.com.cn",
                is_featured=True
            ),
            Hospital(
                name="广州中山眼科中心",
                name_en="Zhongshan Ophthalmic Center",
                city="广州",
                province="广东",
                address="广州市天河区金穗路7号",
                level="三级甲等",
                description="中山大学中山眼科中心是中国最早的眼科专科医院，被誉为'中国眼科摇篮'。",
                specialties=["眼科", "白内障", "青光眼", "角膜病", "眼底病"],
                logo_url="",
                image_urls=["", ""],
                contact_phone="020-87654123",
                website="http://www.zoc.com.cn",
                is_featured=True
            ),
        ]
        
        for hospital in hospitals:
            db.add(hospital)
        db.flush()
        
        # 创建示例病种
        diseases = [
            Disease(
                name="白内障",
                name_en="Cataract",
                category="眼科疾病",
                description="白内障是晶状体混浊导致的视力障碍，是全球首位致盲眼病。",
                treatment_methods=["超声乳化术", "人工晶体植入术", "飞秒激光白内障手术"],
                recovery_time="术后1-2周"
            ),
            Disease(
                name="心血管疾病",
                name_en="Cardiovascular Disease",
                category="内科疾病",
                description="心血管疾病包括冠心病、高血压、心律失常等，是全球主要死因之一。",
                treatment_methods=["药物治疗", "介入治疗", "外科手术", "心脏搭桥手术"],
                recovery_time="术后2-8周"
            ),
            Disease(
                name="糖尿病",
                name_en="Diabetes",
                category="内分泌疾病",
                description="糖尿病是一种代谢性疾病，以高血糖为特征，需要长期管理和治疗。",
                treatment_methods=["药物治疗", "胰岛素治疗", "饮食控制", "运动疗法"],
                recovery_time="终身管理"
            ),
            Disease(
                name="肿瘤",
                name_en="Cancer",
                category="肿瘤疾病",
                description="肿瘤是机体细胞异常增生形成的肿块，良性肿瘤切除后不易复发，恶性肿瘤易转移和复发。",
                treatment_methods=["手术治疗", "化疗", "放疗", "靶向治疗", "免疫治疗"],
                recovery_time="术后3-12个月"
            ),
        ]
        
        for disease in diseases:
            db.add(disease)
        db.flush()
        
        # 创建示例医生
        doctors = [
            Doctor(
                hospital_id=hospitals[0].id,  # 北京协和医院
                name="张医生",
                name_en="Dr. Zhang",
                title="主任医师",
                department="眼科",
                specialties=["白内障", "青光眼", "角膜移植"],
                description="从事眼科临床工作30余年，擅长各类复杂白内障手术，完成手术超过2万例。",
                experience_years=32,
                education="北京医科大学博士",
                success_rate=98.5,
                rating=4.9,
                review_count=356,
                consultation_fee_min=500,
                consultation_fee_max=800,
                surgery_fee_min=8000,
                surgery_fee_max=15000,
                surgery_duration="20-40分钟",
                recovery_duration="术后1-2周",
                is_featured=True
            ),
            Doctor(
                hospital_id=hospitals[0].id,  # 北京协和医院
                name="李医生",
                name_en="Dr. Li",
                title="主任医师",
                department="心血管外科",
                specialties=["心脏搭桥手术", "瓣膜置换术", "先天性心脏病"],
                description="国内知名心血管外科专家，完成心脏手术5000余例，成功率高达99%。",
                experience_years=28,
                education="清华大学医学院博士",
                success_rate=99.0,
                rating=4.9,
                review_count=289,
                consultation_fee_min=600,
                consultation_fee_max=1000,
                surgery_fee_min=50000,
                surgery_fee_max=120000,
                surgery_duration="4-8小时",
                recovery_duration="术后4-8周",
                is_featured=True
            ),
            Doctor(
                hospital_id=hospitals[1].id,  # 上海瑞金医院
                name="王医生",
                name_en="Dr. Wang",
                title="副主任医师",
                department="内分泌科",
                specialties=["糖尿病", "甲状腺疾病", "肥胖症"],
                description="专注于糖尿病及内分泌疾病诊治20年，在糖尿病并发症防治方面有丰富经验。",
                experience_years=22,
                education="复旦大学医学院硕士",
                success_rate=95.0,
                rating=4.7,
                review_count=198,
                consultation_fee_min=400,
                consultation_fee_max=600,
                recovery_duration="终身管理",
                is_featured=True
            ),
            Doctor(
                hospital_id=hospitals[2].id,  # 广州中山眼科中心
                name="陈医生",
                name_en="Dr. Chen",
                title="主任医师",
                department="眼科",
                specialties=["视网膜脱离", "眼底病", "玻璃体切割术"],
                description="眼底病专家，擅长复杂视网膜脱离修复手术，年手术量超过800台。",
                experience_years=25,
                education="中山大学博士",
                success_rate=97.0,
                rating=4.8,
                review_count=267,
                consultation_fee_min=500,
                consultation_fee_max=800,
                surgery_fee_min=10000,
                surgery_fee_max=20000,
                surgery_duration="1-2小时",
                recovery_duration="术后2-4周",
                is_featured=True
            ),
        ]
        
        for doctor in doctors:
            db.add(doctor)
        db.flush()
        
        # 创建医生病种关联
        doctor_diseases = [
            # 张医生擅长白内障
            DoctorDisease(doctor_id=doctors[0].id, disease_id=diseases[0].id, 
                         expertise_level="expert", experience_years=30, success_rate=98.5),
            # 李医生擅长心血管疾病
            DoctorDisease(doctor_id=doctors[1].id, disease_id=diseases[1].id,
                         expertise_level="expert", experience_years=28, success_rate=99.0),
            # 王医生擅长糖尿病
            DoctorDisease(doctor_id=doctors[2].id, disease_id=diseases[2].id,
                         expertise_level="expert", experience_years=22, success_rate=95.0),
            # 陈医生擅长眼底病
            DoctorDisease(doctor_id=doctors[3].id, disease_id=diseases[0].id,
                         expertise_level="advanced", experience_years=25, success_rate=97.0),
        ]
        
        for dd in doctor_diseases:
            db.add(dd)
        
        # 创建示例旅游景点
        attractions = [
            TouristAttraction(
                name="故宫博物院",
                name_en="The Palace Museum",
                city="北京",
                province="北京",
                address="北京市东城区景山前街4号",
                category="历史人文",
                description="故宫是中国明清两代的皇家宫殿，也是世界上现存规模最大、保存最完整的木质结构古建筑之一。",
                highlights=["太和殿", "午门", "珍宝馆", "钟表馆"],
                ticket_price=60,
                opening_hours="8:30-17:00（4-10月）/8:30-16:30（11-3月）",
                recommended_duration="3-4小时",
                best_visit_season="春秋两季",
                rating=4.8,
                review_count=15234,
                is_featured=True
            ),
            TouristAttraction(
                name="长城（八达岭段）",
                name_en="Great Wall - Badaling",
                city="北京",
                province="北京",
                address="北京市延庆区八达岭镇",
                category="历史人文",
                description="八达岭长城是明长城的重要组成部分，地势险要，景色雄伟，是万里长城的精华所在。",
                highlights=["北楼", "南楼", "长城博物馆", "好汉坡"],
                ticket_price=40,
                opening_hours="7:30-18:00",
                recommended_duration="4-6小时",
                best_visit_season="春秋两季",
                rating=4.7,
                review_count=10876,
                is_featured=True
            ),
            TouristAttraction(
                name="上海外滩",
                name_en="The Bund",
                city="上海",
                province="上海",
                address="上海市黄浦区中山东一路",
                category="都市风光",
                description="外滩是上海最具代表性的地标之一，展现了上海作为国际大都市的风采。",
                highlights=["万国建筑博览群", "外白渡桥", "黄浦江夜景", "东方明珠"],
                ticket_price=0,
                opening_hours="全天开放",
                recommended_duration="2-3小时",
                best_visit_season="全年",
                rating=4.6,
                review_count=8932,
                is_featured=True
            ),
            TouristAttraction(
                name="广州塔",
                name_en="Canton Tower",
                city="广州",
                province="广东",
                address="广州市海珠区阅江西路222号",
                category="现代建筑",
                description="广州塔是中国第一高塔，世界第三高塔，集观光、餐饮、娱乐于一体。",
                highlights=["观景台", "摩天轮", "空中云梯", "极速云霄"],
                ticket_price=150,
                opening_hours="9:00-23:00",
                recommended_duration="2-3小时",
                best_visit_season="全年",
                rating=4.5,
                review_count=5678,
                is_featured=True
            ),
            TouristAttraction(
                name="西湖",
                name_en="West Lake",
                city="杭州",
                province="浙江",
                address="浙江省杭州市西湖区龙井路1号",
                category="自然风光",
                description="西湖是中国最著名的湖泊之一，以其秀美的湖光山色和众多的名胜古迹闻名于世。",
                highlights=["断桥残雪", "雷峰塔", "三潭印月", "苏堤春晓"],
                ticket_price=0,
                opening_hours="全天开放",
                recommended_duration="4-6小时",
                best_visit_season="春秋两季",
                rating=4.9,
                review_count=18234,
                is_featured=True
            ),
        ]
        
        for attraction in attractions:
            db.add(attraction)
        
        # 创建示例用户
        users = [
            User(
                email="john.smith@email.com",
                phone="+1-555-0101",
                name="John Smith",
                country="United States",
                language="en",
                status=UserStatus.ACTIVE
            ),
            User(
                email="marie.dupont@email.com",
                phone="+33-6-12-34-56-78",
                name="Marie Dupont",
                country="France",
                language="fr",
                status=UserStatus.ACTIVE
            ),
        ]
        
        for user in users:
            db.add(user)
        
        db.commit()
        print("✅ 示例数据初始化成功！")
        print(f"  - 医院数量: {len(hospitals)}")
        print(f"  - 医生数量: {len(doctors)}")
        print(f"  - 病种数量: {len(diseases)}")
        print(f"  - 景点数量: {len(attractions)}")
        print(f"  - 用户数量: {len(users)}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 初始化失败: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_sample_data()
