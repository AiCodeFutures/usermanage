class BMIService:
    @staticmethod
    def calculate_bmi(height, weight):
        """计算BMI值"""
        if height <= 0 or weight <= 0:
            return None
        return round(weight / ((height/100) ** 2), 2)
    
    @staticmethod
    def get_category(bmi):
        """根据BMI值返回分类"""
        if not bmi:
            return "无效数据"
        if bmi < 18.5:
            return "体重过轻"
        elif 18.5 <= bmi < 24.9:
            return "正常范围"
        elif 25 <= bmi < 29.9:
            return "超重"
        else:
            return "肥胖"
    
    @staticmethod
    def calculate_all(height, weight):
        """综合计算BMI值和分类"""
        bmi = BMIService.calculate_bmi(height, weight)
        return {
            "bmi_value": bmi,
            "category": BMIService.get_category(bmi),
            "suggestion": BMIService.get_suggestion(bmi)
        }
    
    @staticmethod
    def get_suggestion(bmi):
        """根据BMI给出建议"""
        if not bmi:
            return "请输入有效的身高体重数据"
        if bmi < 18.5:
            return "建议增加营养摄入和适度力量训练"
        elif 18.5 <= bmi < 24.9:
            return "保持当前健康生活方式"
        elif 25 <= bmi < 29.9:
            return "建议控制饮食并增加有氧运动"
        else:
            return "建议咨询专业医生制定减重计划"