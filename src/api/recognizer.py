class writingRecognizer:
    
    def __init__(self, model="model.pt"):
        self.model = self.load_model(model)  
        self.gpu_required = True
    
    def load_model(self, path):
        pass
    
    def recognize(self, image_path):
        result = self.model.predict(image_path)
        return result  
